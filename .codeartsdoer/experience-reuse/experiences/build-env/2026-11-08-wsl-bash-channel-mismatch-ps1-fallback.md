---
id: 2026-11-08-wsl-bash-channel-mismatch-ps1-fallback
title: 本机 bash 命令实为 WSL 通道：.sh 约定流程静默失效的判定信号与 ps1 等价改写降级
category: build-env
nature: pitfall
created_at: 2026-11-08T02:46:17
updated_at: 2026-11-08T02:46:17
tags: [WSL, bash通道, 环境怪癖, 脚本降级, PowerShell]
keywords: [bash WSL, git-bash, _wiki_cmd.sh, ps1 脚本, ExecutionPolicy Bypass, 通道错配, UTF-16 乱码, 命令静默失效, 环境探测, NativeCommandError]
problem_patterns:
  - 按 skill/文档约定"写 .sh 文件后 bash 执行"，命令返回乱码报错且目标脚本从未被执行，误判为脚本内容错误反复改写
  - 不确定本机 bash 到底解析到 git-bash 还是 WSL，选错执行通道导致流程卡死
  - .sh 流程改写为 PowerShell 时按 .sh 语义直译（&&、$? 判成败）再次踩 PS5.1 语法陷阱
source_sessions: [ses_e48b8e01dffeFrd2wwOBkoqJtt]
project: Date
severity: medium
quality_score: 85
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-07-powershell-command-construction-limits-script-fallback, 2026-11-06-shell-session-state-not-persistent, 2026-11-07-powershell-stderr-native-command-error-false-failure]
---

# 本机 bash 命令实为 WSL 通道：.sh 约定流程静默失效的判定信号与 ps1 等价改写降级

## Scenario

本机 Windows 环境执行系统 skill 的既定流程：skill 强制约定"把多条长命令写入 `<仓库>/.codeartsdoer/temp/_wiki_cmd.sh`，再以短命令 `bash .codeartsdoer/temp/_wiki_cmd.sh` 执行"（规避单条命令字符数硬上限）。按约定写好 .sh 后执行，得到的是一段与脚本内容无关的乱码报错——脚本根本没有被 bash 以预期语义执行。

## Key Signals

- `bash --version 2>&1 | Select-Object -First 1` 返回 `NativeCommandError` 包装 + 乱码 `w\u0000s\u0000l\u0000:`（UTF-16 字符逐字节泄漏，即 "wsl:"）——bash 解析到的是 WSL 的 bash，输出走 UTF-16 管道，且报错主体是 WSL 子系统而非目标命令。
- 写入的 `_wiki_cmd.sh` 内容与报错毫无关联：命令被 WSL 通道吞掉，无执行、无副作用——"脚本内容写错"与"通道错配"用报错文本是否与脚本相关即可区分。
- 本机 `python` 直连可用（`python --version` 返回 Python 3.11.9），PowerShell 5.1 是稳定的原生执行通道。

## Essence

Windows 机器上 `bash` 的解析目标不是常量：可能是 git-bash，也可能是 WSL bash——后者跨子系统调用在 Agent 工具沙箱中不执行预期命令（输出 WSL 乱码且无副作用）。凡依赖"写 .sh 后 bash 执行"约定的流程，在此类环境整体失效；正确处置不是修脚本内容，而是通道切换：把 .sh 中的命令逐条改写为等价 PowerShell 语句，落盘为 `.ps1`，用 `powershell -ExecutionPolicy Bypass -File` 执行——执行命令本身足够短，同样绕开单条命令字符上限。

## Approach

1. **先探测通道再归因**：执行 `bash --version 2>&1 | Select-Object -First 1`；输出含 `wsl` 乱码/NativeCommandError → 判定 bash=WSL，停止改写 .sh 内容（改多少遍都不会被执行）。
2. **确认原生通道**：`python --version`、`powershell` 版本各验一次，确定可用的降级载体（本例两者皆可用，选 PowerShell）。
3. **等价改写而非直译**：把 .sh 每行命令翻译为 PS5.1 语义——`&&` 改 `;` 或分步执行；命令成败用 `$LASTEXITCODE -ne 0` 判定（原生命令 stderr 有输出不等于失败，勿用 `$?`）；带引号/特殊字符的参数按 PS 转义规则重写。
4. **保持"写文件后执行"结构**：多条命令合并写入一个 `_wiki_cmd.ps1`（每行一条），用 `powershell -ExecutionPolicy Bypass -File <短路径>` 执行——执行命令字符数极短，天然满足长度限制约定。
5. **分阶段复用同一模式**：后续每个阶段的脚本（影响分析、合并、索引重建）沿用"写 ps1 → -File 执行 → 读输出"循环，全程不再触碰 bash。

## Faster Next Time

- 首查命令：任何 .sh 约定流程报"乱码/不执行"时，先跑 `bash --version` 看通道，再看脚本内容——通道判定 5 秒完成，避免无意义的内容级排查。
- 判定表：报错含 UTF-16 泄漏乱码（形如 `w\u0000s\u0000l`）或与脚本内容无关 → 通道错配；报错指向脚本具体行/语法 → 内容问题，才值得修脚本。
- ROI：一次通道切换（约 1 次改写）解锁后续所有阶段的脚本执行；不切换则每个阶段都会重复失败。
- 反模式：把 WSL 乱码报错当"脚本编码问题"反复重写 .sh；改写成 ps1 后沿用 bash 语法（&&、$?）再踩 PS5.1 陷阱；绕开"写文件后执行"约定直接拼超长单条命令（触发字符上限静默丢弃）。

## Applicability Boundaries

- 适用：本机 Windows（bash 解析到 WSL）环境下任何"写 .sh 后 bash 执行"的流程约定；判定与降级方法对其他"约定通道不可用"场景同构（探测 → 确认原生通道 → 等价改写 → 保持写文件后执行结构）。
- 不适用：bash 解析到 git-bash 的机器（原约定直接可用）；脚本确有 POSIX 专属语义无法等价改写时（需另找 WSL 侧落盘执行方案，不在本条范围）。
- 环境边界：Windows + PowerShell 5.1 + 沙箱单条命令字符上限（约 231 字符）；PS 语法细节陷阱见 powershell-command-construction-limits-script-fallback 与 stderr 假失败条目。

## Evidence or Examples

- 源会话 ses_e48b8e01dffeFrd2wwOBkoqJtt（docgen-apply，Date 项目）。
- 通道错配实证：`bash --version 2>&1` → `bash : w\u0000s\u0000l\u0000: ... NativeCommandError`，`_wiki_cmd.sh` 无任何执行痕迹。
- 降级实证：改写为 `_wiki_cmd.ps1`/`_wiki_cmd2.ps1` 等后经 `powershell -ExecutionPolicy Bypass -File` 执行，阶段 1（extract_symbols）/阶段 2（reverse_lookup）/阶段 3.5（merge+validate+lint+redact）/阶段 6（build_index）全部成功跑通。
- 改写要点实证：`if (-not $?) { throw ... }` 形态在 PS5.1 下因 stderr 包装产生假失败，改用 `$LASTEXITCODE` 语义后判定稳定。