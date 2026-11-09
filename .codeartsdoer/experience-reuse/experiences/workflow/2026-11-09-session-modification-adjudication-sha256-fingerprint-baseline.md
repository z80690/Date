---
id: 2026-11-09-session-modification-adjudication-sha256-fingerprint-baseline
title: "文件是否被本会话改动"的裁决口径：任务起点固化 SHA256 指纹基线，git M 状态属历史遗留不可作证据
category: workflow
nature: methodology
created_at: 2026-11-09T01:32:45
updated_at: 2026-11-09T01:32:45
tags: [指纹基线, 零改动验收, git 状态, 证据口径, SHA256]
keywords: [SHA256 指纹, Get-FileHash, 零直改验收, git M 状态, 历史遗留变更, 基线固化, 收尾复验, 会话改动归属, 产物范围核对, 审计歧义]
problem_patterns: ["零直改/零删除类约束验收时看到 git status 的 M 状态，误判为本会话改动了文件", "工作区在特性开始前就有未提交变更，git diff 相对 HEAD 的差异无法归属到本次会话，'没改'只能口头声明", "终验报告缺权威证据口径，多会话共用工作区时改动归属说不清"]
source_sessions: [ses_e43dfeddbffecZ9Y91Am1PbKju]
project: Date
severity: medium
quality_score: 84
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: A
related_experiences: [workflow/2026-11-09-ai-no-direct-rule-edit-suggestion-list-mode, workflow/2026-11-07-definition-vs-runtime-evidence-implementation-status-audit]
---

# "文件是否被本会话改动"的裁决口径：任务起点固化 SHA256 指纹基线，git M 状态属历史遗留不可作证据

## Scenario

项目带"AI 零直改既有文件"类约束（U6-6），特性收尾终验须证明"既有文件零改动"。工作区在特性开始前已存在未提交变更（历史遗留的 git M 状态），git diff 相对 HEAD 的差异无法归属到本次会话。

## Key Signals

- git status 一开工就显示一批 M 文件，且特性全程未触碰其中任何一个。
- 终验需要"没改"的权威证据，而 git diff 只能证明"相对 HEAD 有差异"，不能证明"差异来自谁"。
- 历史遗留 M 状态与本次改动在 git 视角下不可区分——用 git 状态作零改动证据必然误判。

## Essence

"是否被本会话改动"是**会话级归属**问题，git 状态是**仓库级快照**——两者粒度不匹配，git 状态不能作会话改动的裁决证据。可复制的裁决口径：**SHA256 指纹基线比对**——任务起点对约束目标文件固化 `Get-FileHash` 基线（含字节数），收尾复验比对；指纹一致 = 零变化的权威证据（与 git 历史无关）。产物范围核对用 git status 新增项（??）对照授权清单（新增项天然归属本会话）。终验报告中显式说明 M 状态的归属定性（历史遗留、指纹级零触碰），消除审计歧义。

## Approach

1. 起点（链首任务）：对所有"零触碰"约束目标执行 `Get-FileHash` SHA256 + 字节数，落盘基线记录——漏了这一步就再也补不出可信基线。
2. 收尾终验：重算指纹逐文件比对；一致 → 零变化结论；不一致 → 立即回溯会话内动作定位差异来源。
3. 产物范围核对：git status 未跟踪区（??）逐项对照授权产物清单，超范围新增即违规。
4. 留痕：终验报告写明"git M 状态系特性开始前已存在的历史遗留（起点基线记录佐证），不归属本特性；零改动权威证据 = 指纹比对零变化"。

## Faster Next Time

- 口诀："改没改看指纹，动没动看新增——M 状态只是背景"。
- 零触碰约束一经确立，起点固化指纹是链首任务的一部分，与需求分析同级。
- 预警信号：终验报告若只有 git diff 截图而无指纹比对，零改动证据链不成立。

## Applicability Boundaries

- 适用：带"零直改/零删除/只读保留"类约束的特性收尾；多会话/多特性共用工作区的改动归属判定。
- 不适用：工作区干净（无历史遗留变更）时 git diff 即可作证据；文件在任务中被授权修改的场景（此时比对口径应为"越权改动 = 授权外指纹变化"）。
- 边界：指纹比对只证内容未变，不证时间戳/权限未变；约束含 mtime/权限层面时须另行取证。

## Evidence or Examples

- 来源会话：ses_e43dfeddbffecZ9Y91Am1PbKju（2026-11-09，20261109_ruff_review_gate 特性终验）。
- 实测：基线 = review-code/SKILL.md、review-code.ps1、公约.mdc 三文件 SHA256 + 字节数；终验逐一比对一致；D:\refs\p3c 存在性复核 True；git status 中三文件 M 状态确认系特性开始前已存在（1.1 基线记录佐证），终验报告留痕归属定性。
- 与 workflow/2026-11-09-ai-no-direct-rule-edit-suggestion-list-mode 的分工：那条管"谁能改、改什么、旧文件怎么办"的权限边界；本条管"改没改"的证据口径——权限裁决之后，终验须用指纹基线而不是 git 状态来兑现零改动承诺。