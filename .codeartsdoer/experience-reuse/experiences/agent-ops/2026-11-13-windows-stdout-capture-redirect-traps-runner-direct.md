---
id: 2026-11-13-windows-stdout-capture-redirect-traps-runner-direct
title: Windows 下脚本 stdout 落盘捕获双坑与截断存档恢复：bash 重定向不认 C:/ 盘符、PS `>` 产 UTF-16 双重编码——统一 runner 直连
category: agent-ops
nature: pitfall
created_at: 2026-11-13T13:23:45
updated_at: 2026-11-13T18:49:48
tags: [stdout捕获, shell重定向, 编码陷阱, runner直连, windows]
keywords: [bash重定向, 盘符路径, No such file or directory, UTF-16, 双重编码, PowerShell重定向, stdout截断, call_*.out存档, 编码探测, runner直连]
problem_patterns:
  - "bash 执行 .sh 内 `python 脚本 > C:/...json`：python 参数正常解析（Windows Python 认盘符路径），重定向目标却报 `line 1: C:/...json: No such file or directory`，误判为目录不存在或路径写错"
  - "PowerShell `>` 重定向落盘中文输出后读回全是 \\u0000 空字节交错乱码（UTF-16LE 特征），探测出 utf-16 并转存后中文仍失真——双重编码不可逆损坏"
  - "工具捕获的 stdout 超长约 51KB 被截断显示，误以为输出丢失，不知完整内容已自动存档于 codearts-data\\shell\\<hash>\\call_*.out 可恢复"
source_sessions: [ses_e2cb1b7b7ffe0zGnKiSyEBCaRk]
project: Date
severity: medium
quality_score: 88
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-09-wsl-bash-drive-letter-path-relativized, 2026-11-11-python-wrapper-json-job-runner, 2026-11-07-background-long-task-log-pipeline-pitfalls, 2026-11-06-powershell-inline-json-escaping-python-fallback, 2026-11-13-ps-redirect-utf16-structure-corruption-orchestrator-capture, 2026-11-10-python-print-redirect-gbk-mojibake-write-file-directly]
---

# Windows 下脚本 stdout 落盘捕获双坑与截断存档恢复：bash 重定向不认 C:/ 盘符、PS `>` 产 UTF-16 双重编码——统一 runner 直连

## Scenario

Windows 环境下 Agent 执行带多个长路径参数的 Python 脚本链（wiki 增量更新的 reverse_lookup / extract_sections / extract_changed_snippets 等），需要把脚本 stdout 落盘存档（供后续分步读取）或查看超长输出。两条直觉路径都踩坑：① bash 执行 .sh 命令文件，用 `> C:/...json` 重定向落盘；② PowerShell 里用 `>` 重定向落盘后回读。

## Key Signals

- 坑 1（路径层）：`.sh: line 1: C:/Users/.../reverse_lookup_out.json: No such file or directory` + `EXIT=False`——报错行级、指向重定向目标本身。同一条命令里 python 脚本与参数（含 `C:/` 盘符路径）本可被 Windows Python 正常解析（runner 模式同参数此前反复 success），只有 `>` 右侧的目标路径失败——**同一命令行的参数与重定向目标分属两个解析层**。
- 坑 2（编码层）：PowerShell `>` 落盘后回读内容呈 `\u0000=\u0000=\u0000=\u0000 \u0000J\u0000O\u0000B\u0000...` 空字节交错——UTF-16LE 编码特征（PS 5.1 的 `>` 默认 UTF-16）。Python 探测确认 utf-16 并转存后，中文仍是"涓存椂绱犳潗"类乱码——转存过程引入二次误编码，**双重编码损坏不可逆**。
- 坑 3（截断层）：脚本 stdout 超过约 51KB 时工具回显被静默截断（如 snippets 输出只显示前段），容易误判为输出残缺；实际完整输出已由平台自动存档于 `codearts-data\shell\<hash>\call_*.out`。

## Essence

落盘捕获失败与"文件/目录不存在"是两回事：Git Bash 层不把 `C:/...` 解析为可写路径（Windows 进程参数层认，shell 重定向层不认），PowerShell `>` 默认产 UTF-16 与下游 UTF-8 解读冲突——两条路径的修复动作统一：**禁用 shell 重定向做 stdout 落盘，脚本直连执行让工具捕获 stdout**（本环境直连捕获的中文输出正常）。确需落盘时由脚本内部自行写文件（Python `open(..., encoding='utf-8')`），绕开 shell 编码层；超长截断走存档恢复而非降参数重跑。

## Approach

1. **落盘捕获需求** → 改用 runner 模式（json 任务单 + python wrapper，见 2026-11-11-python-wrapper-json-job-runner）：脚本 stdout 由工具捕获，或脚本内部用 UTF-8 显式写输出文件，绝不写 `> C:/...` 形式的 shell 重定向。
2. **查看完整输出** → runner 直连执行（如 `python .codeartsdoer/temp/_wiki_runner.py`），工具捕获 stdout 的中文编码正常，不引入任何转换层。
3. **stdout 被截断** → 用 Python 二进制读平台存档 `codearts-data\shell\<hash>\call_*.out`，编码探测（utf-8 → utf-16 → gbk 顺序）后转存 UTF-8 分发；优于降 `--max-chars` 重跑（重跑浪费一次完整执行）。
4. **已被 PowerShell `>` 污染的文件** → 检测 `\u0000` 空字节/BOM 判 UTF-16，但若中文已呈双重编码乱码（GBK→UTF-8 类形态）则不可逆——不浪费轮次做恢复，直接直连重跑获取干净输出。

## Faster Next Time

- 判定表：报错 `line N: C:/...: No such file or directory` 且同命令 python 参数含盘符路径 = 重定向层不认盘符（本坑，非目录问题）；回读含 `\u0000` 交错 = UTF-16 编码；中文乱码 + 探测多编码仍失真 = 双重编码损坏，放弃恢复直接重跑；回显在 ~51KB 处截断 = 去存档 .out 恢复。
- 一行决策：**Windows 下 stdout 落盘/回看一律直连捕获（runner 或脚本内部写文件），shell 重定向只用于 POSIX 相对路径且不承载中文。**
- ROI：直连捕获一次成功（本例 reverse_lookup 直连即 success），重定向路径要连踩"路径层失败→编码损坏→重跑"三连坑，至少浪费两轮。
- 反模式：把重定向报错归因于目标目录不存在而先建目录；对双重编码文件反复换编码转存；为绕截断把 `--max-chars` 调小导致关键 JSON 被截断。

## Applicability Boundaries

- 适用：Windows 主机 + Git Bash / PowerShell 双 shell 环境，Agent 工具层执行带长路径参数的脚本并需捕获/落盘 stdout 的任何场景；CodeArts Agent 类"stdout 回显截断 + 自动存档"的平台行为。
- 不适用：WSL bash 运行时（另有参数路径拼接坑，见 2026-11-09-wsl-bash-drive-letter-path-relativized——`/mnt/c/` 改写纪律）；Linux/macOS 原生 POSIX shell（重定向认相对路径，无盘符问题，但中文编码仍需注意 LANG）；脚本自身落盘（不经过 shell 层，无本坑）。
- 与相邻经验分工：wsl-bash-drive-letter 管"WSL 把参数路径按相对路径拼接"（报错形态 `can't open file '/mnt/c/<cwd>/C:/...'`），本条管"Git Bash 重定向目标不认盘符"（报错形态 `line 1: C:/...: No such file or directory`）——按报错形态选条目；background-long-task-pitfalls 管后台任务管道缓冲不落盘（后台模式），本条管前台直连/落盘（前台模式）。
- 与"PS 重定向编码坑家族"两条部分重叠（保留独立、按形态分流）：`2026-11-13-ps-redirect-utf16-structure-corruption-orchestrator-capture` 管 PS `>` 下 JSON 结构被管道破坏（utf-16 解码后 json.loads 报 Invalid control character）与 orchestrator capture_output 二进制捕获模式；本条坑 2 管双重编码不可逆损坏的判定与"放弃恢复直连重跑"决策——按"结构破坏 vs 编码损坏不可逆"分流。`2026-11-10-python-print-redirect-gbk-mojibake-write-file-directly` 管 GBK 单重乱码形态与脚本内直写 UTF-8 修复；本条坑 2 是其 UTF-16/双重编码升级形态，修复动作同源（绕开 shell 编码层）。

## Evidence or Examples

- 源会话 ses_e2cb1b7b7ffe0zGnKiSyEBCaRk（docgen-apply fork #1，Date 项目 Wiki 增量更新，version_token 523→540）。
- 坑 1 实测：`_wiki_cmd.sh` 首行 `python <script> ... > C:/Users/Administrator/Desktop/Date/.codeartsdoer/temp/reverse_lookup_out.json` → `line 1: C:/...json: No such file or directory`，EXIT=False；改 runner 直连后 reverse_lookup success（7 个变更文件、4 篇受影响文档命中）。
- 坑 2 实测：PowerShell `>` 落盘 sections 提取输出 → 回读 `LEN 15025` 全为 `\u0000` 交错；Python 探测 `DETECTED utf-16`；转存 `_sections_all.txt` 后中文呈"涓存椂绱犳潗"双重编码乱码；放弃落盘直连重跑后同脚本输出中文完全正常（"架构设计"、"关系"等小节标题/内容可读）。
- 坑 3 实测：extract_changed_snippets 输出 51KB 被工具截断显示；存档转存验证 `OK utf-8 34785`（34785 字节完整 JSON 可用）。
- 存档恢复路径（`codearts-data\shell\<hash>\call_*.out` + utf-8→utf-16→gbk 探测转存）为同会话演化审查阶段的归纳结论，实测转存成功一次，多编码探测顺序的完备性待更多场景检验。