---
id: 2026-11-09-wsl-bash-drive-letter-path-relativized
title: WSL bash 子进程中 Windows 盘符路径被按相对路径拼接报 FileNotFoundError：命令文件内绝对路径统一改写 /mnt/c/ 前缀
category: agent-ops
nature: pitfall
created_at: 2026-11-09T13:56:12
updated_at: 2026-11-09T13:56:12
tags: [路径改写, WSL, bash子进程, FileNotFoundError, 环境适配]
keywords: [/mnt/c, 盘符路径, WSL bash, 相对路径拼接, extract_symbols, reverse_lookup, 脚本命令文件, 路径格式转换, can't open file, 环境探测]
problem_patterns:
  - 写入脚本命令文件执行时，命令参数中保留 Windows 盘符绝对路径（C:/...），bash 报 python: can't open file '/mnt/c/<工作目录>/C:/Users/...' 类 FileNotFoundError，误判为脚本缺失或路径写错
  - 同一项目在不同 bash 运行时（PowerShell 原生 vs WSL）间切换，命令文件里的路径格式未随运行时改写导致整条脚本链首步即失败
  - 把"盘符路径拼接"失败与"参数传内容非路径"失败混淆，走错排查方向
source_sessions: [ses_e412aeab2ffevse91wcDeqR5Mm]
project: Date
severity: medium
quality_score: 90
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-08-wiki-update-script-behavior-contract-blindspots, 2026-11-06-powershell-inline-json-escaping-python-fallback, 2026-11-07-powershell-command-construction-limits-script-fallback]
---

# WSL bash 子进程中 Windows 盘符路径被按相对路径拼接：命令文件内绝对路径统一改写 /mnt/c/ 前缀

## Scenario

通过"写命令文件再 `bash xxx.sh` 执行"的方式调用带多个长路径参数的 Python 脚本链（增量符号提取、反向影响查找等）。命令文件中的脚本安装路径与项目产物路径均按 Windows 盘符格式写为 `C:/Users/...`，执行环境是 WSL bash 子进程。Agent 不直接感知子进程运行时类型，命令文件写完后一次性执行，首条脚本即整链失败。

## Key Signals

- 报错形态：`python: can't open file '/mnt/c/Users/Administrator/Desktop/Date/C:/Users/Administrator/.codeartsdoer/.../extract_symbols.py': [Errno 2] No such file or directory`——目标路径呈现"`/mnt/c/<当前工作目录>/` + 原盘符路径"的拼接形态，这是本坑的指纹特征。
- 同一轮输出中 WSL 自身还打印主机名/DNS 配置类提示（如 `wsl: 检测到 localhost 代理配置...`），证明 bash 子进程确为 WSL 运行时。
- 报错文件实际存在（skill 安装目录下确实有该脚本），排除"脚本缺失"假设——问题出在路径解释层而非文件系统层。
- 与参数契约坑的区分：参数传内容非路径的报错是 `FileNotFoundError: '[docs/xxx.md]'`（带引号/方括号、路径即内容字面量）；本坑报错路径是"工作目录前缀 + 盘符路径"的拼接串。

## Essence

WSL 不会自动把命令参数中的 Windows 盘符路径（`C:/...`）映射为 `/mnt/c/...`：未以 `/` 开头的参数被当作相对路径，按当前工作目录拼接后变成不存在的路径。bash=WSL 运行时下，命令与文件中的绝对路径必须统一改写为 `/mnt/c/<盘符>/...` 格式；脚本内容只描述"要做什么"，路径格式随运行时改写，这属于"命令文件按当前客户环境展开"铁律的一部分（运行时环境也是"当前环境"的组成）。同一项目命令模板在 PowerShell 原生 bash 与 WSL bash 间复用时，路径格式必须随运行时切换。

## Approach

1. **执行前识别运行时**：命令文件执行报错或环境不确定时，先从输出指纹判定 bash 类型——出现 `wsl:` 前缀提示或报错路径呈 `/mnt/c/...` 形态即 WSL。
2. **全量改写路径格式**：重写命令文件，把其中所有 Windows 盘符绝对路径（`C:/...`）统一改为 `/mnt/c/...`（`C:` → `/mnt/c`）；相对路径与文件名保持不变。
3. **重跑并核对报错形态**：改写后重执行；若仍报 FileNotFoundError 但路径已无拼接形态，才转向"文件确实不存在/参数传错"假设。
4. **模板留档双形态**：维护命令模板时同时记录 PowerShell 形态（`C:/...`）与 WSL 形态（`/mnt/c/...`），按当次会话的 bash 运行时选用。

## Faster Next Time

- 判定表：报错路径 = 工作目录 + `C:/...` 拼接 → 盘符路径未改写（本坑）；报错路径 = 带引号内容字面量 → 参数传内容非路径；报错路径干净但仍找不到 → 真缺失/路径笔误。
- 快捷信号：输出里出现 `wsl:` 提示行 → 本会话 bash 为 WSL，后续所有命令文件直接按 `/mnt/c/` 写，省一轮试错。
- ROI：一次全量改写即可恢复整条脚本链（本例 extract_symbols + reverse_lookup 两条一并修复），误走"脚本缺失"排查方向的代价是整轮无效检索。
- 反模式：只在报错的那一条命令里改路径、其余条目保留盘符格式（下一脚本接着踩）；把报错归因于脚本安装位置而移动文件；在 WSL 会话里用 `C:/` 反斜杠混合格式（转义语义再次损坏）。

## Applicability Boundaries

- 适用：bash 子进程运行在 WSL、命令参数或脚本内容中含 Windows 盘符路径的任何场景（Python 脚本调用、git 命令、文件操作类 CLI 通用）；同一命令模板跨 PowerShell/WSL 运行时复用的场景。
- 不适用：bash 本身运行在 Windows 原生环境（盘符路径本就是正确格式，改写反而破坏）；路径以 `/mnt/c/` 或 `/` 开头的原生 POSIX 形态；WSL 内部启动的进程间传递已映射路径的场景。
- 平台边界：实证载体为 Windows 11 + WSL bash 子进程 + CodeArts Agent 沙箱"写命令文件再执行"模式；`/mnt/<盘符>/` 映射规则为 WSL 通用约定，不依赖特定 Agent 平台。
- 运行时差异：主 Agent 写文件与子进程执行分属两层——写文件工具按 Windows 路径写盘不受影响，仅 bash 子进程内的路径解释受本坑约束。

## Evidence or Examples

- 源会话 ses_e412aeab2ffevse91wcDeqR5Mm（docgen-apply fork #1，Date 项目 Wiki 增量更新，version_token 198）。
- 失败实测：`_wiki_cmd.sh` 首版内容含 `python C:/Users/Administrator/.codeartsdoer/cache/system/skills/repo-simple-wiki-update/scripts/extract_symbols.py ...`，WSL 下报 `can't open file '/mnt/c/Users/Administrator/Desktop/Date/C:/Users/Administrator/.../extract_symbols.py'`（工作目录拼接 + 盘符路径原样保留），extract_symbols 与 reverse_lookup 两条同批失败。
- 修复实测：重写命令文件，脚本安装路径与产物输出路径全部改为 `/mnt/c/Users/Administrator/...` 形态后，extract_symbols（0 符号 warning，纯 .md 仓库属预期）与 reverse_lookup（2 篇受影响文档命中）均 success。
- 关联佐证：同会话另一坑——extract_changed_snippets 的 `--changed-files` 传内联 JSON 报 FileNotFoundError，改传 JSON 文件路径后 success；两坑报错形态不同、根因不同（参数契约 vs 路径格式），排查方向应区分。