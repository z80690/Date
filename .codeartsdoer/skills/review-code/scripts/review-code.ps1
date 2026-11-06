param(
    [string]$RepoRoot = (Get-Location).Path,
    [string]$PmdClasses = "D:\refs\p3c\p3c-pmd\target\classes",
    [string]$PmdDep = "D:\refs\p3c\p3c-pmd\target\dep\*",
    [string]$OutReport = "$env:TEMP\p3c-review-report.txt"
)
$ErrorActionPreference = 'Stop'
$files = git -C $RepoRoot status --porcelain | ForEach-Object { $_.Substring(3).Trim('"') } | Where-Object { $_ -match '\.java$' } | ForEach-Object { Join-Path $RepoRoot $_ }
if (-not $files) {
    "no-java-changes: skip review"
    exit 0
}
$rulesetDir = Join-Path $PmdClasses "rulesets\java"
$rs = (Get-ChildItem $rulesetDir -Filter "ali-*.xml" -ErrorAction Stop | ForEach-Object { $_.FullName }) -join ","
if (-not $rs) { throw "no p3c rulesets found under $rulesetDir" }
"review-scope: $($files.Count) java file(s)"
"rulesets: $rs"
& java -cp "$PmdClasses;$PmdDep" net.sourceforge.pmd.PMD -d ($files -join ",") -f text -R $rs 2>&1 | Out-File -FilePath $OutReport -Encoding utf8
Get-Content $OutReport -Tail 20
exit $LASTEXITCODE