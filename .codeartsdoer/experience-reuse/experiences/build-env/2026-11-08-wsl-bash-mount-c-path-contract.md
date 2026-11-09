---
id: 2026-11-08-wsl-bash-mount-c-path-contract
title: WSL bash 通道的可执行分支：Windows 盘符路径改写 /mnt/c/ 即可保留 .sh 约定流程，无需降级 ps1
category: build-env
nature: technique
created_at: 2026-11-08T03:26:16
updated_at: 2026-11-10T00:39:14
tags: [WSL, bash通道, 路径契约, 环境怪癖, 脚本执行]
keywords: [WSL bash, /mnt/c, 盘符路径, _wiki_cmd.sh, cd No such file, 通道形态判别, wsl 前缀乱码, UTF-16 泄漏, 路径改写, .sh 流程保留]
problem_patterns:
  - 按 skill 约定"写 .sh 后 bash 执行"，报错含 wsl: 前缀乱码与 cd: No such file or directory，误判为通道吞命令而整轮降级为 ps1 改写
  - 脚本内写 C:/Users/... 形态的 Windows 盘符路径，WSL bash 内不存在该路径，首条命令即失败
  - 不知 WSL 通道下"乱码报错"究竟意味着命令未执行还是已执行但路径语义不同，选错处置分支
source_sessions: [ses_e488e3ea4ffeibxmS5KxTmxPRl]
project: Date
severity: medium
quality_score: 93
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-08-wsl-bash-channel-mismatch-ps1-fallback, 2026-11-09-wsl-bash-drive-letter-path-relativized, 2026-11-06-shell-session-state-not-persistent]
---

# WSL bash 通道的可执行分支：Windows 盘符路径改写 /mnt/c/ 即可保留 .sh 约定流程

## Scenario

Windows 环境下执行系统 skill 的既定流程：把多条长命令写入 `<仓库>/.codeartsdoer/temp/_wiki_cmd.sh`（每行一条），再以短命令 `bash .codeartsdoer/temp/_wiki_cmd.sh` 执行（规避单条命令字符上限）。首条命令报错，输出为一段 UTF-16 乱码加一条脚本自身的行级错误，需要判定该走"通道降级"还是"路径修复"分支。

## Key Signals

- 报错含 `w\u0000s\u0000l\u0000:` 形态的 UTF-16 逐字节泄漏（即 `wsl:` 前缀报错）+ Windows DNS/Server 报错文本——bash 解析到的是 WSL 通道。
- **决定性信号**：乱码之后紧随脚本自身的行级错误 `.codeartsdoer/temp/_wiki_cmd.sh: line 1: cd: C:/Users/Administrator/Desktop/Date: No such file or directory`——报错指向脚本第 1 行的 cd 命令，证明命令**实际已被 WSL bash 执行**，失败仅因脚本内的 Windows 盘符路径在 WSL 内不存在。
- 与"吞命令"形态的判别：吞命令时报错与脚本内容毫无关联、无任何脚本行号、无副作用；已执行形态的报错必然携带脚本行号与具体命令名。

## Essence

本机 bash=WSL 通道存在两种形态：① 吞命令（报错与脚本无关、无副作用）→ 只能走 ps1 等价降级；② 正常执行但 Windows 路径语义失效（报错含脚本行级错误）→ **不必降级**，把脚本内所有 Windows 盘符路径改写为 WSL 挂载形态 `/mnt/<盘符小写>/`（如 `C:/Users/...` → `/mnt/c/Users/...`）即可整轮保留原 .sh 约定。误判形态会把本可一次修复的流程错误地整体改写为 ps1，浪费改写成本并引入 PS5.1 语法陷阱。

## Approach

1. **先判形态再选分支**：看报错是否含脚本自身行级错误（`_wiki_cmd.sh: line N: <命令>:`）——有 → 已执行形态，走路径改写；无且报错与脚本无关 → 吞命令形态，走 ps1 降级。
2. **盘符路径全量改写**：脚本内所有 `C:/...`、`C:\\...` 形态路径改为 `/mnt/c/...`（盘符小写）；相对路径（如 `scripts/xxx.py`、`.codeartsdoer/...`）不受影响，保持原样。
3. **保持"写文件后执行"结构**：多条命令仍合并写入同一个 `_wiki_cmd.sh`（每行一条），执行命令 `bash .codeartsdoer/temp/_wiki_cmd.sh` 足够短，天然满足字符上限约定。
4. **输出即验证**：脚本输出为 JSON 时直接解析关键字段（status/summary）确认执行成功，不因首段 wsl: 前缀噪声而否定整个结果。
5. **后续阶段沿用同通道**：影响分析、合并、校验、索引重建各阶段脚本均走同一"改写路径→bash 执行→读 JSON"循环，中途不再切换通道。

## Faster Next Time

- 首查信号：bash 报错出现 `wsl:` UTF-16 乱码时，**先看乱码后有无脚本行级错误**——5 秒完成分支判定，避免无意义的整轮 ps1 改写。
- 判定表：`wsl:` 乱码 + `line N: cd: C:/...: No such file or directory` → 路径改写分支（本条）；`wsl:` 乱码 + 报错与脚本无关、无脚本行号 → 吞命令分支（ps1 降级，见相邻经验）；无 wsl 前缀 → 可能是 git-bash，原约定直接可用。
- ROI：路径改写是一次性 sed/编辑成本（每处 1 行），换来全部后续阶段零改写复用；ps1 降级则每条命令都要做 bash→PS 语义翻译且易踩 PS5.1 陷阱。
- 反模式：见到 wsl 乱码一律判定"命令未执行"而整体降级；只改脚本内第一处路径漏掉后续行；把脚本输出 JSON 里的 wsl 前缀噪声当执行失败重跑。

## Applicability Boundaries

- 适用：Windows 机器、bash 解析到 WSL 的 Agent 环境，且脚本命令在 WSL 内有 POSIX 等价语义（cd/python/git 等通用命令）的场景；路径契约对脚本中任意 Windows 绝对路径通用。
- 不适用：吞命令形态的通道（见 2026-11-08-wsl-bash-channel-mismatch-ps1-fallback 的 ps1 降级路径）；bash 实为 git-bash 的机器（盘符路径原样可用，无需改写）；命令依赖 Windows 原生二进制且无 WSL 等价物时。
- 与相邻经验分工：2026-11-09-wsl-bash-drive-letter-path-relativized 管参数路径拼接指纹（`python: can't open file '/mnt/c/<工作目录>/C:/...'`）与命令文件全量改写纪律；本条管通道形态判别与 .sh 流程保留，报错形态为 cd 行级错误（`line N: cd: C:/...`）——同一根因（WSL 不映射盘符路径）的两种症状面，按报错形态选条目。
- 平台边界：以 CodeArts Agent 沙箱 bash 工具为实证载体；WSL 的盘符挂载约定（/mnt/<盘符>）为 WSL 通用行为，非本机专属。

## Evidence or Examples

- 源会话 ses_e488e3ea4ffeibxmS5KxTmxPRl（docgen-apply fork #1，Date 项目 Wiki 增量更新）。
- 失败实证：首条命令输出 `w\u0000s\u0000l\u0000: ...`（wsl 报错 UTF-16 泄漏）+ `.codeartsdoer/temp/_wiki_cmd.sh: line 1: cd: C:/Users/Administrator/Desktop/Date: No such file or directory`。
- 修复实证：同一脚本仅把 `cd C:/Users/Administrator/Desktop/Date` 与脚本内路径改为 `/mnt/c/...` 后，reverse_lookup（影响分析）、extract_changed_snippets、merge_section_patch×4、validate_code_links/lint_wiki/redact_secrets、build_index 全流程经 WSL bash 跑通，全部返回预期 JSON（如 build_index `total_docs: 7, code_paths_verified: 80`）。
- 对照佐证：相邻经验 2026-11-08-wsl-bash-channel-mismatch-ps1-fallback 记录的是吞命令形态（脚本无执行痕迹），本条记录已执行形态——同一机器两种形态均实证存在，形态判别信号（有无脚本行级错误）是分流依据。