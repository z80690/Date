# ruff-review Python 审查门禁脚本（IF-1~IF-4，特性 20261109_ruff_review_gate）
# exit 取值域 {0,4}：0=放行留痕 / 4=未过不完工（公约第 6 条绑定，fail-closed）
# 裁决唯一依据 = design 2.1.3.2 裁决矩阵 D1~D8；禁用项 --exit-zero / -w / --fix

param(
    [string]$RepoRoot = (Get-Location).Path,
    [string[]]$Files = @(),
    [string]$OutReport = ""
)

# 子进程输出按 UTF-8 解码（Ruff 输出为 UTF-8，PS5.1 默认 ANSI 解码会致中文诊断失真）
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch { }

$script:VerdictTag = "unknown"
$script:ScopeKind = ""
$script:DiagText = ""
$script:CmdText = "(Ruff 未调用)"
$script:RuffExit = $null
$script:FindingCount = 0
$script:SeverityCodes = @()
$script:ReviewState = "未复核"
$script:FileList = @()
$script:Exempted = @()
$gate = 4

function Write-GateReport {
    $sb = New-Object System.Text.StringBuilder
    [void]$sb.AppendLine("==== Ruff 审查门禁报告（ruff-review）====")
    [void]$sb.AppendLine("生成时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')")
    [void]$sb.AppendLine("[要素①审查范围] scope: $($script:ScopeKind)")
    if ($script:FileList.Count -gt 0) { [void]$sb.AppendLine("  审查文件清单: $($script:FileList -join '; ')") }
    if ($script:Exempted.Count -gt 0) { [void]$sb.AppendLine("  非 Python 豁免项(不审查): $($script:Exempted -join '; ')") }
    [void]$sb.AppendLine("[要素②发现项数] finding_count: $($script:FindingCount)")
    if ($script:SeverityCodes.Count -gt 0) { [void]$sb.AppendLine("[要素③严重级别] severity 规则代码: $($script:SeverityCodes -join ', ')") }
    else { [void]$sb.AppendLine("[要素③严重级别] severity 规则代码: (无)") }
    [void]$sb.AppendLine("[要素④复核状态] review_state: $($script:ReviewState)")
    [void]$sb.AppendLine("[要素⑤命令与结果原文] evidence:")
    [void]$sb.AppendLine("  命令: $($script:CmdText)")
    [void]$sb.AppendLine("  Ruff exit: $(if ($null -eq $script:RuffExit) {'(未调用)'} else {$script:RuffExit})")
    [void]$sb.AppendLine("  结果原文(禁删减):")
    foreach ($l in ($script:DiagText -split "`r?`n")) { [void]$sb.AppendLine("    $l") }
    [void]$sb.AppendLine("门禁裁决: exit=$gate verdict_tag=$($script:VerdictTag)")
    [void]$sb.AppendLine("(exit 0=放行留痕 / 4=未过不完工，绑定公约第 6 条'编码必审未过不完工')")
    Set-Content -LiteralPath $OutReport -Value $sb.ToString() -Encoding UTF8
}

try {
    # ===== 第 1 段：报告可写预检（先于一切审查动作，矩阵 D6：留痕先行）=====
    if ([string]::IsNullOrWhiteSpace($OutReport)) {
        $d = Get-Date -Format "yyyy-MM-dd"
        $OutReport = Join-Path $env:TEMP "ruff-review-$d.txt"
        if (Test-Path -LiteralPath $OutReport) {
            $ts = Get-Date -Format "HHmmss"
            $OutReport = Join-Path $env:TEMP "ruff-review-$d-$ts.txt"
        }
    } elseif (Test-Path -LiteralPath $OutReport) {
        $rdir = Split-Path -Parent $OutReport
        $rbase = [System.IO.Path]::GetFileNameWithoutExtension($OutReport)
        $rext = [System.IO.Path]::GetExtension($OutReport)
        $ts = Get-Date -Format "yyyyMMdd-HHmmss"
        $OutReport = Join-Path $rdir "$rbase-$ts$rext"
    }
    $reportDir = Split-Path -Parent $OutReport
    if ([string]::IsNullOrWhiteSpace($reportDir)) { $reportDir = (Get-Location).Path }
    if (-not (Test-Path -LiteralPath $reportDir)) {
        try { New-Item -ItemType Directory -Force -Path $reportDir -ErrorAction Stop | Out-Null }
        catch { Write-Host "report-unwritable"; exit 4 }
    }
    try {
        $probe = Join-Path $reportDir ("ruff-gate-probe-" + [guid]::NewGuid().ToString("N") + ".tmp")
        Set-Content -LiteralPath $probe -Value "probe" -Encoding UTF8 -ErrorAction Stop
        Remove-Item -LiteralPath $probe -Force -ErrorAction SilentlyContinue
    } catch { Write-Host "report-unwritable"; exit 4 }

    # ===== 第 2 段：文件集确定（矩阵 D5/D8）=====
    $skipEngine = $false
    if ($Files.Count -gt 0) {
        # 显式列表模式（D8，服务自测）：不读 git；仅 .py 入审查集，非 .py 如实豁免
        $script:ScopeKind = "显式文件列表"
        foreach ($f in $Files) {
            if ($f -match '\.py$') { $script:FileList += $f } else { $script:Exempted += $f }
        }
    } else {
        # git 变更集模式：git 可用性检查 fail-closed（D5）
        $script:ScopeKind = "增量(git变更集)"
        $gitCheck = & git -C $RepoRoot rev-parse --is-inside-work-tree 2>&1
        if ($LASTEXITCODE -ne 0 -or ("$gitCheck" -notmatch 'true')) {
            $script:VerdictTag = "git-unavailable"
            $script:DiagText = "git 可用性检查失败:`n$($gitCheck | Out-String)"
            $skipEngine = $true
        } else {
            $porcelain = & git -C $RepoRoot status --porcelain 2>&1
            if ($LASTEXITCODE -ne 0) {
                $script:VerdictTag = "git-unavailable"
                $script:DiagText = "git status --porcelain 失败:`n$($porcelain | Out-String)"
                $skipEngine = $true
            } else {
                foreach ($line in @($porcelain)) {
                    if ([string]::IsNullOrWhiteSpace($line) -or $line.Length -lt 4) { continue }
                    $p = $line.Substring(3).Trim('"').Replace('/', '\')
                    if ($p -match '\.py$') { $script:FileList += (Join-Path $RepoRoot $p) }
                }
            }
        }
    }

    # ===== 第 3 段：空集短路（D7 + 非 Python 豁免，Ruff 不执行，禁虚假"已审查"）=====
    if (-not $skipEngine -and $script:FileList.Count -eq 0) {
        $script:ReviewState = "已豁免留痕"
        $script:RuffExit = $null
        if ($Files.Count -gt 0) { $script:VerdictTag = "exempt-not-python(非 Python 豁免)" }
        else { $script:VerdictTag = "no-python-changes: skip review" }
        $script:DiagText = "审查集无 .py 文件，Ruff 未调用（豁免语义如实标注）"
        $gate = 0
        $skipEngine = $true
    }

    # ===== 第 4 段：Ruff 引擎调用（IF-2：ruff check --output-format concise [--isolated]）=====
    if (-not $skipEngine) {
        $repoFull = [System.IO.Path]::GetFullPath($RepoRoot).TrimEnd('\')
        $outside = $false
        foreach ($f in $script:FileList) {
            $ff = [System.IO.Path]::GetFullPath($f)
            if (-not $ff.StartsWith($repoFull, [StringComparison]::OrdinalIgnoreCase)) { $outside = $true }
        }
        $ruffArgs = @("check", "--output-format", "concise")
        if ($outside) { $ruffArgs += "--isolated" }
        # 扩展位：[--config <ruff.toml>]（附录 B2 预留，本特性不创建不启用；启用时在此追加 --config 参数）
        # 禁用项（design 2.1.3.2）：--exit-zero（弱化门禁）/ -w --watch（轮询，公约第 5 条）/ --fix（门禁只审不改）
        $ruffArgs += $script:FileList
        $script:CmdText = "ruff " + ($ruffArgs -join " ")
        $ruffOut = & ruff @ruffArgs 2>&1
        $script:RuffExit = $LASTEXITCODE
        $script:DiagText = $ruffOut | Out-String
        $script:SeverityCodes = @([regex]::Matches($script:DiagText, '\b([A-Z]{1,4}[0-9]{3})\b') | ForEach-Object { $_.Groups[1].Value } | Select-Object -Unique)
        if ($script:DiagText -match 'Found (\d+) error') { $script:FindingCount = [int]$Matches[1] }
        elseif ($script:RuffExit -eq 0) { $script:FindingCount = 0 }

        # ===== 第 5 段：映射裁决（矩阵 D1~D4/D8："Ruff 非零(1/2)→门禁 4"铁律）=====
        if ($script:RuffExit -eq 0) {
            $script:VerdictTag = "pass"; $gate = 0
        } elseif ($script:RuffExit -eq 1) {
            if ($script:SeverityCodes -contains 'E902') { $script:VerdictTag = "file-error(fail-closed)" }
            else { $script:VerdictTag = "violations-found" }
            $gate = 4
        } else {
            $script:VerdictTag = "ruff-execution-error"; $gate = 4
        }
    }
} catch {
    $script:VerdictTag = "unexpected-error"
    $script:DiagText = "未预期异常: $($_.Exception.Message)`n$($_.ScriptStackTrace)"
    $gate = 4
}

# ===== 落盘后才允许以门禁码退出（IF-3 后置条件）=====
try {
    Write-GateReport
} catch {
    Write-Host "report-unwritable"
    exit 4
}
Write-Host "gate-verdict: $script:VerdictTag"
Write-Host "gate-exit: $gate"
Write-Host "report: $OutReport"
exit $gate