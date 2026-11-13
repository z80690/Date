---
id: 2026-11-11-wiki-added-mislabeled-merkle-reset-hash-triage
title: 增量更新遇变更状态全量 added 失真先以 hash_status 与骨架规模甄别真变更：数据库重置误标不启动无效修订
category: workflow
nature: pitfall
created_at: 2026-11-11T11:31:19
updated_at: 2026-11-11T11:31:19
tags: [增量更新, 状态失真, hash短路, added误标, 甄别流程]
keywords: [state.json, added, hash_status, unchanged, 骨架符号数, merkle, version_token, subagent, 误标甄别, 增量更新]
problem_patterns:
  - 增量更新报告大规模全 added 变更（数百文件无一 modified），误以为发生大规模新增而启动大范围修订或误触发降级评估
  - 底层扫描数据库重置/重建导致文件状态语义失真，把未变文件当新增文件处理，对内容未变的文档启动无效 subagent 修订
  - 只看变更状态字段定真伪，缺少"内容级独立证据"（小节 hash、符号骨架规模）交叉验证环节
source_sessions: [ses_e37c7267cffewyCyg5XHZYfAwm]
project: Date
severity: medium
quality_score: 92
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-09-repeat-changed-set-reuse-prior-round-verdicts, 2026-11-08-wiki-increment-update-unmatched-file-routing, 2026-11-11-wiki-verbatim-consistency-line-number-only]
---

# 增量更新遇变更状态全量 added 失真先以 hash_status 与骨架规模甄别真变更

## Scenario

基于 state.json → reverse_lookup → 小节级修订的增量更新流程：本轮 version_token 前进（393→408），state.json 报告 247 个变更文件且**全部为 added**、无一 modified。若按状态字面语义处理，需为 247 个"新增"文件做归属判定并可能大范围修订；本轮规模已达降级评估阈值边缘（247/763≈32%）。约束：判定错误会把未变文档送进无效修订（浪费 subagent 与合并成本），或把真变更漏掉。

## Key Signals

- 反直觉信号：数百文件全部 added、零 modified——健康增量轮次极少出现"只增不改"的完整集合，优先怀疑状态语义失真而非真实全量新增。
- 内容级证据①：reverse_lookup 对命中文件（17 个）输出的各小节 hash_status **全部 unchanged**——added 状态与内容 hash 直接矛盾。
- 内容级证据②：阶段 1 符号骨架提取结果（201 符号/23 文件）与上一轮完全一致——若真有大量新代码文件，符号数应显著增长。
- 外部佐证：底层扫描数据库的 WAL 文件异常巨大（约 918KB）且本轮 version_token 与上轮记录断档，指向数据库重置/重建把既有文件重新登记为 added。

## Essence

变更状态字段（added/modified）只反映**扫描器视角**，不等于内容真相；当状态分布反常（全量 added、零 modified）时，先以两个内容级独立证据交叉甄别——**小节 hash_status（未变=unchanged）与骨架符号规模（与上轮持平）**——再决定修订面。hash unchanged 的命中文件走"仅刷行号、正文不动"的短路分支；unmatched 的 added 文件才进入归属判定。数据库重置导致的误标，不应转化为对未变文档的无效修订。

## Approach

1. **状态分布体检**：读 state.json 后先统计 added/modified/removed 分布；出现"全量 added"或与常识明显不符的分布即进入甄别流程，不直接按字面语义推进。
2. **跑 reverse_lookup 取 hash_status**：对状态失真轮次，hash_status 是第一裁决字段——unchanged 的小节即使文件标 added 也判定内容未变。
3. **骨架规模做独立佐证**：重跑符号骨架提取，符号数/文件数与上轮一致 → 强化"内容未变"结论；显著增长 → 存在真新增，对增长部分单独定位。
4. **按甄别结果分流通稿**：hash 全 unchanged 的命中文件 → 跳过 subagent 修订，仅刷新 code_refs 行号与 source_hashes；真新增文件 → 走三级归属判定与常规修订。
5. **留痕甄别结论**：把"误标根因 + 甄别证据 + 分流结果"写入本轮 update_plan/报告，使下轮可直接审计而非重复排查。

## Faster Next Time

- 一条判据先行：全量 added + 任一命中文件 hash unchanged → 立即怀疑状态失真，两个证据（hash、骨架规模）10 分钟内可完成甄别。
- ROI：本轮 17 个命中文件因此全部免于无效 subagent 修订（3 个 subagent 只服务真变更文档），并避免把 247/763≈32% 当真实变更占比做错误降级决策（剔除误标与第三方克隆后有效占比仅约 4%）。
- 反模式：按状态字面语义对全量 added 启动大规模归属判定与修订；把"骨架符号数一致"单独当充分证据（须与 hash_status 交叉）；不区分"真新增"与"误标 added"一概刷新行号（真变更会漏改）。

## Applicability Boundaries

- 适用：任何"扫描状态 → 影响分析 → 小节修订"的增量更新流程（Wiki 增量更新、文档索引增量），凡底层扫描数据库可能重置/重建的场景。
- 不适用：状态分布正常（added/modified 混合且占比合理）的常规轮次；首轮全量生成（无上轮基线可比）；真的大规模新增分支（此时 added 语义为真，直接走归属判定）。
- 与相邻经验分工：repeat-changed-set 条管"变更集合与上轮完全重复时复用先验"；本条管"集合全新但状态语义失真时以内容证据甄别"——两者覆盖增量更新轮次的两类状态异常；unmatched-file-routing 条管甄别后真新增文件的路由。

## Evidence or Examples

- 源会话 ses_e37c7267cffewyCyg5XHZYfAwm（docgen-apply fork #1，Date 项目）：state.json token 408 报 247 文件全 added；reverse_lookup 唯一命中文档（工作流底座.md）5 个小节 hash_status 全 unchanged；骨架提取 201 符号/23 文件与上轮一致 → 判定 merkle 数据库重置误标，17 个命中文件仅刷行号，未启动无效修订。
- 分流实证：247 = 17 命中（hash 短路）+ 8 软件源码真新增 + 216 第三方克隆 + 4 项目管理 md + 2 评估报告 md，总数闭合无遗漏。
- 收敛验证：merge 5/5 success、validate_code_links 3/3 passed、build_index reused 5/updated 3——甄别分流未引入漏改。