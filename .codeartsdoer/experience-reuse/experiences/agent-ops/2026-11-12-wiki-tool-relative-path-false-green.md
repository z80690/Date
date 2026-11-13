---
id: 2026-11-12-wiki-tool-relative-path-false-green
title: 校验链工具相对路径参数以进程 cwd 为基准——扫错对象仍可能全绿（假绿）
category: agent-ops
nature: pitfall
created_at: 2026-11-12T07:48:12
updated_at: 2026-11-12T07:53:40
tags: [agent-ops, cli-path-resolution, false-green, wiki-update, validation-chain]
keywords: [merge_section_patch, validate_code_links, lint_wiki, redact_secrets, wiki-root, FileNotFoundError, files_checked, 假绿, 相对路径, cwd 基准, repo-simple-wiki-update]
problem_patterns: ["校验类 CLI 工具相对路径参数静默扫错对象仍报成功（假绿）", "技能文档路径简写示例与运行时 cwd 解析基准不一致"]
source_sessions: ["ses_e3302fce2ffe5bQ32J65w6nefV"]
project: Date
severity: high
quality_score: 92
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: ["2026-11-08-wiki-update-script-behavior-contract-blindspots", "2026-11-09-wsl-bash-drive-letter-path-relativized", "2026-11-11-python-wrapper-json-job-runner"]
---

# 校验链工具相对路径参数以进程 cwd 为基准——扫错对象仍可能全绿（假绿）

## Scenario
执行增量 Wiki 更新链路（merge_section_patch.py → validate_code_links.py / lint_wiki.py / redact_secrets.py → build_index.py）时，脚本参数为相对路径，技能文档示例以简写形式出现（如 `--wiki-root docs`），执行者容易按"产物目录名"理解并照抄简写，在仓库根 cwd 下运行。

## Key Signals
两类信号，严重性不同：
1. **显性失败（假红）**：merge_section_patch.py rc=1，stderr 报 `FileNotFoundError: No such file or directory: 'docs/codebase-knowledge/知识库笔记.md'`——路径被解析到仓库根的 docs/ 源文档目录。
2. **隐性失败（假绿）**：validate_code_links / lint_wiki / redact_secrets 以 `--wiki-root docs` 简写运行 rc=0 全绿，但实际扫描的是仓库根源文档目录（3 篇）而非 wiki 产物目录（12 篇）。识别特征：`files_checked`（3）远小于产物实际篇数（12）；文件清单出现源目录命名特征（如 `-desktop0003` 后缀）。

## Essence
多参数 CLI 脚本的相对路径解析基准是进程 cwd（仓库根），不是技能文档示例中简写暗示的产物目录。校验类工具对"目标目录存在但内容不对"的场景通常无法报警——它只校验它看到的东西，看到什么就什么全绿。文档简写口径本身是踩坑源：主技能原文即写 `--wiki-root docs` 示例，本轮已同步修正技能文档为完整产物路径口径。

## Approach
1. 校验/合并类脚本传相对路径参数时，一律写**从仓库根出发的完整相对路径**（如 `.codeartsdoer/.codebase/branches/<分支>/docs/...`），不照抄文档简写。
2. 执行前对目标路径做存在性预检（Test-Path / 目录列举），确认指向产物目录而非同名源目录。
3. 校验链跑完后核对数量口径：`files_checked` 必须与产物实际篇数一致；不一致即扫错对象，结果作废重跑。
4. rc=0 不等于校验了正确对象——把"扫了什么"（files_checked、文件清单抽样）纳入验收项，与"是否通过"同权重。

## Faster Next Time
- 快捷判断：校验输出里 files_checked ≪ 产物篇数 → 第一反应是 --wiki-root 传错目录，而不是产物没问题。
- 假红（FileNotFoundError）反而安全——它强制修正路径；假绿才会污染后续决策。为校验环节固定建立"数量断言"可一次封堵两类。
- 加载技能文档后，先把其中路径简写展开为当前环境的完整路径再写命令，防止示例口径直接入参。

## Applicability Boundaries
- 适用：任何以 `--root/--wiki-root` 类目录参数定位产物的校验/扫描/合并类 CLI；本实例为 Windows PS5.1 + bash wrapper（Python 脚本经 .sh 调用）环境下的 repo-wiki-update 脚本族。
- 不适用：绝对路径参数场景（无解析基准歧义）；工具自身会校验路径合法性并报错的场景（假红已自带防御）。
- "相对路径以进程 cwd 为基准"是通用规律，跨 shell 成立；files_checked 数量断言依赖工具输出该字段。

## Evidence or Examples
- 本轮实证（2026-11-12 Wiki 每日同步，token 414→422）：merge_notes/merge_docsys 首轮 rc=1，stderr traceback 终止于 `_read_file` 打开 `'docs/codebase-knowledge/知识库笔记.md'` 失败；修正为 `.codeartsdoer/.codebase/branches/master/docs/...` 完整相对路径后两单 rc=0，hash 基线刷新成功（8cade6051e5c / dd7743c822bb）。
- 校验链首轮 rc=0 但扫的是仓库根 docs/ 源文档目录（3 篇，含 `官方文档-码道热门Skills清单-desktop0003.md` 等源文件）；修正后 lint `files_checked=12`、0 error / 10 orphan warning（全库遗留），redact 0 可疑。
- 根因侧证：仓库根 docs/ 下确有 3 篇源文档，路径形似度掩盖指向错误，validate/lint/redact 对"目录存在但内容不对"零报警。
- 相关条目：2026-11-08-wiki-update-script-behavior-contract-blindspots（同脚本族 merge 覆盖盲区：H1/frontmatter 需人工补正）、2026-11-09-wsl-bash-drive-letter-path-relativized（同族路径解析基准问题）、2026-11-11-python-wrapper-json-job-runner（本轮 wrapper 执行环境）。