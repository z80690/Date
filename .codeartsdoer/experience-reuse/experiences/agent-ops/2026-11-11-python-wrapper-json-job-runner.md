---
id: 2026-11-11-python-wrapper-json-job-runner
title: 多 bash 运行时并存下长路径脚本链的免坑执行通道：Python wrapper + JSON 任务单，执行命令恒短且路径不经 bash 转换
category: agent-ops
nature: methodology
created_at: 2026-11-11T11:04:29
updated_at: 2026-11-11T11:04:29
tags: [bash运行时, Python包装脚本, JSON任务单, 脚本链执行, 路径格式适配]
keywords: [_wiki_runner.py, _wiki_job.json, sys.executable, WSL bash, /mnt/c 拼接, can't open file, 多job一单, 短命令直连, repo-simple-wiki-update, 脚本链]
problem_patterns:
  - 按 skill 约定把多脚本链写入命令文件（.sh）后，WSL bash 报 python: can't open file '/mnt/c/<工作目录>/C:/...' 拼接错误，修复面临"运行时探测 + 路径双形态维护"的持续成本
  - 本机多个 bash 并存（System32 WSL bash 优先于 scoop git-bash 被解析），命令文件一次执行无法预判落点运行时，路径格式预选失效则整链首步即败
  - 多阶段流程逐脚本写命令文件逐次执行，往返多、每个命令文件都要重选一次路径格式
source_sessions: [ses_e37a7d04bffeGDy30227RzJmD2]
project: Date
severity: medium
quality_score: 88
hit_count: 11
last_hit_at: 2026-11-15T19:54:35
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-09-wsl-bash-drive-letter-path-relativized, 2026-11-07-powershell-command-construction-limits-script-fallback, 2026-11-08-wiki-update-script-behavior-contract-blindspots, 2026-11-09-companion-execution-skill-co-load-before-scripts]
---

# 多 bash 运行时并存下长路径脚本链的免坑执行通道：Python wrapper + JSON 任务单

## Scenario

沙箱对单条 bash 命令字符串有字符上限（约 231 字符，超限静默丢弃），且本机同时存在多个 bash 运行时（`where bash` 返回 System32 WSL bash、scoop git-bash、WindowsApps bash 三条）。执行 skill 的多阶段脚本链（每脚本带多个长路径参数，共 10 次调用贯穿全流程）时，按 skill 约定"把命令写进 .sh 文件再 `bash xxx.sh` 执行"，首条脚本即报路径拼接错误。约束：命令文件内的路径格式必须匹配实际 bash 运行时，但 Agent 无法预判 bash 落点，"先探测再写文件"的路线每轮都要重走且仍可能选错形态。

## Key Signals

- 报错指纹：`python: can't open file '/mnt/c/Users/Administrator/Desktop/Date/C:/Users/Administrator/.codeartsdoer/.../reverse_lookup.py': [Errno 2] No such file or directory`——"/mnt/c/<工作目录>/ + 原盘符路径"的拼接形态，证明 bash 子进程为 WSL 且脚本内 `C:/` 路径未被映射（与 2026-11-09-wsl-bash-drive-letter-path-relativized 同一指纹）。
- `where bash` 返回三条结果且 System32 WSL bash 排在 scoop git-bash 之前——多运行时并存，同一命令文件无法保证落到哪个运行时，"预选路径格式"失效。
- skill 约定的命令文件通道隐含假设"bash 运行时可预判"；本机环境打破该假设，路径改写修复从"一次改写"退化为"每轮探测 + 双形态维护"。

## Essence

把"执行命令"与"长路径参数载体"分离是免坑关键：bash 只负责启动一个固定短命令（如 `python .codeartsdoer/temp/_wiki_runner.py`，约 40-60 字符、不含任何盘符路径、远低于沙箱字符上限），所有脚本路径与参数写入 JSON 任务单文件，由 Python wrapper 以 `sys.executable`（Windows Python，原生认 `C:/` 正斜杠）+ 显式 cwd 逐 job 执行。执行命令本身无长路径 → bash 运行时是 WSL 还是 git-bash 完全无关 → "运行时探测 + /mnt/c 路径改写"环节整体消除；JSON 任务单天然支持多 job 一单顺序执行，输出按 `===== JOB: <name> =====` 分段、`ALL_JOBS_DONE` 收尾，一次执行覆盖多阶段并可直接分段核对结果。

## Approach

1. **写通用 runner**：在仓库 temp 目录（如 `.codeartsdoer/temp/`）建 `_wiki_runner.py`——读取同目录 `_wiki_job.json`（结构 `[{name, script, args, cwd}, ...]`），以 `sys.executable` 启动各 script、显式传 cwd，逐 job 执行并按 `===== JOB: <name> =====` 分段打印，全部完成后打印 `ALL_JOBS_DONE`。
2. **写任务单**：每阶段 job 的脚本绝对路径与参数全部用 Windows 风格（`C:/` 正斜杠）写入 JSON——路径由 Windows Python 解释，完全不经 bash 转换层，无需任何 `/mnt/c` 改写。
3. **执行命令恒短**：`python .codeartsdoer/temp/_wiki_runner.py`（仓库相对路径，直连执行，不再写 .sh 命令文件）。
4. **分段解析输出**：按 JOB 分段核对各 job 的 status；`ALL_JOBS_DONE` 出现即全链完成；某 job 失败只需修该 job 的 JSON 条目重跑，不牵连其他 job。
5. **多 job 合并**：同一阶段的多个脚本（如 merge×2 + validate、redact + lint）并入同一任务单一次执行，把 N 次往返压成 1 次。

## Faster Next Time

- 快捷信号：bash 报 `/mnt/c/<工作目录>/C:/...` 拼接指纹 → 不再走"改写 /mnt/c 重跑"路线，直接切 Python wrapper 通道，一次切换整链免坑。
- 判定表：脚本命令 ≤231 字符短命令 → 直连执行；长参数多脚本链 → Python wrapper + JSON 任务单；必须依赖 bash 语法（管道/变量/条件）→ 回退 .sh 通道并全量改写 /mnt/c（2026-11-09 经验）。
- ROI：一次通道切换替代逐文件路径格式维护与每轮运行时探测；多 job 一单显著减少工具往返次数（实证一轮 10 次脚本调用零失败）。
- 反模式：在 wrapper 的 JSON 条目里混入 bash 语法（管道、`&&`）——JSON 里只放脚本路径与参数数组；用盘符绝对路径经 bash 调 wrapper 本身——wrapper 用仓库相对路径定位即可；把 wrapper 当一次性降级手段每次重写——应作为模板固化复用。

## Applicability Boundaries

- 适用：沙箱单命令长度受限 + 多 bash 运行时并存的环境下，执行带长路径参数的 Python 脚本链（repo-simple-wiki-update 类多阶段流程、批量提取/校验脚本链）；同一命令模板需跨 WSL/原生 bash 复用的场景。
- 不适用：必须依赖 bash 特有语法（管道、循环、变量展开）的任务；单条 ≤231 字符短命令可直连的场景无需引入 runner；目标脚本非 Python 且无对应解释器直启方式时需另行适配。
- 平台边界：实证载体为 Windows 11 + CodeArts Agent 沙箱（bash 子进程运行时不确定）+ System32/scoop/WindowsApps 多 bash 并存；模式本身平台无关——任何"执行命令长度受限、路径解释层不确定"的 Agent 环境均可套用，runner 细节随平台微调。
- 相邻分工：2026-11-09-wsl-bash-drive-letter-path-relativized 管"必须走 bash 通道时命令文件内路径全量改写 /mnt/c"；2026-11-07-powershell-command-construction-limits-script-fallback 管 PowerShell 构造长度限制的脚本降级；本条是通道级替代（bash 仅作启动器、路径改写环节整体消除），三者构成"命令长度/路径格式"问题的三层处置。
- 技能联动留痕：本模式已随本会话后台技能演进写入 generated-skills 的 repo-wiki-update-execution（"推荐执行模式：Python wrapper + JSON 任务单"条目，与 /mnt/c .sh 通道二选一、优先本模式）；经验库层面独立留档以保证经验检索通道可达。

## Evidence or Examples

- 源会话 ses_e37a7d04bffeGDy30227RzJmD2（docgen-apply fork #1，Date 项目 Wiki 增量更新，version_token 414）。
- 失败实测：按主技能约定写 `_wiki_cmd.sh`（内含 `python C:/Users/Administrator/.codeartsdoer/cache/system/skills/repo-simple-wiki-update/scripts/reverse_lookup.py ...`），执行报 `python: can't open file '/mnt/c/Users/Administrator/Desktop/Date/C:/Users/Administrator/.../reverse_lookup.py': [Errno 2] No such file or directory`。
- 修复实测：切换 `_wiki_runner.py` + `_wiki_job.json` 后，全流程 10 次脚本调用零失败（reverse_lookup、extract_sections×2、extract_changed_snippets、merge_section_patch×2、validate_code_links、redact_secrets、lint_wiki、build_index）；修订报告"降级记录"表留痕："bash 路径转换 | WSL bash 将 C:/ 路径错误拼接 | 改用 Python wrapper（_wiki_runner.py）统一调用 | 无影响"。
- 多 job 一单实证：merge_kb_notes + merge_docsys + validate 三 job 单次执行完成（输出含 `===== JOB: sections_kb_notes =====` 等分段标记与 `ALL_JOBS_DONE` 收尾），validate 结果 passed 2/2、0 错误。