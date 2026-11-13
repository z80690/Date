---
id: 2026-11-13-wiki-transfer-impact-empty-crosscheck-wiki-relations
title: 脚本聚合的 transfer_impact 为空不构成无传递影响结论：回 wiki_relations 事实源交叉核对依赖边
category: workflow
nature: decision
created_at: 2026-11-13T12:06:03
updated_at: 2026-11-13T12:06:03
tags: [传递影响, 依赖边核对, wiki增量更新, 双源交叉, 关系小节同步]
keywords: [transfer_impact 为空, wiki_relations 交叉核对, 传递影响判定, 依赖文档修订面, 关系小节并入, 聚合输出非事实源, 反向查找快捷通道, 导入清单同步, 完工门禁并列项]
problem_patterns:
  - "reverse_lookup 输出 transfer_impact=[] 时直接下'无传递影响'结论，跳过 wiki_relations 核对，依赖文档的关系小节滞留旧导入描述并随索引固化"
  - "只查被依赖方向漏依赖方向，或把聚合空输出当最终事实而不回另一数据源验证"
source_sessions: [ses_e2d1aefc4ffeVoyvJy3USpU211]
project: Date
severity: medium
quality_score: 83
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: A
related_experiences: [2026-11-11-wiki-arch-snapshot-stale-new-module-read-verify, 2026-11-12-batch-routing-closure-check, 2026-11-08-wiki-increment-update-unmatched-file-routing, 2026-11-12-wiki-index-code-refs-absence-cause2-patch]
---

# 脚本聚合的 transfer_impact 为空不构成无传递影响结论：回 wiki_relations 事实源交叉核对依赖边

## Scenario

Wiki 增量更新流水线的阶段 2 变更影响分析：编排者运行 reverse_lookup.py 得到 affected_docs（code_refs 命中面）与 transfer_impact（传递影响聚合），同轮还要补判 unmatched added 文件。规模：6 个变更文件（2 added / 4 modified）→ 5 篇文档直接命中、2 个 added 待路由，transfer_impact 输出为空列表。传递影响判定是每轮增量更新的固定环节，只要修订面里存在被其他文档依赖的文档，就会遇到本场景。

## Key Signals

- 易误判信号：脚本输出 `transfer_impact: []`，直觉结论是"本轮无传递影响，阶段 2 完工"——聚合字段为空看似闭环。
- 决定性信号：wiki-index.json 的 wiki_relations 中存在指向修订面文档的依赖边——临时素材与知识萃取.md 依赖 P003演练适配器.md（drill_round01.py:16-20 导入 adapter 包）；且该依赖文档已因 added 补判进入本轮修订面，其"关系"小节记录的 adapter 导入清单已因本次新增脚本（drill_round06_captured.py、verdict_round08.py）过时。
- 结构性信号：transfer_impact 是脚本从 code_refs 命中推导的聚合快捷通道，wiki_relations 才是文档间依赖关系的事实源——两个数据源在本轮恰好给出不同答案。

## Essence

脚本聚合输出是"从锚点命中推导的传递项"，为空只说明本轮没有从锚点推出传递项，**不等于**依赖图里不存在指向修订面文档的边。传递影响的事实源是 wiki_relations（文档间依赖关系），聚合通道为空时必须回事实源核对，否则依赖文档的"关系"小节滞留旧导入描述，随 build_index 固化成失真知识，下游按关系小节检索时引用断链。本场景的低成本处理路径：依赖文档已在修订面 → 其"关系"小节顺势并入同轮修订面，一次派工同步完成，不新增独立传递影响条目。

## Approach

1. reverse_lookup 输出 `transfer_impact: []` 时，**不下"无传递影响"结论**，将其视为待核对项而非完工依据；与 unmatched 补判并列作为阶段 2 完工门禁的两个检查项。
2. 读 wiki-index.json 的 wiki_relations，双向筛选：依赖（Depends On）与被依赖（Depended By）两个方向都指向本轮修订面文档的边都要取（只查单向会漏）。
3. 命中且依赖文档**已在修订面**（因 added 补判、成因 2 补判等原因进入）→ 将该文档的"关系"小节追加进其 affected_sections，由修订 subagent 一并同步导入清单等依赖描述，update_plan note 留痕一句（如"transfer_impact 空，经 wiki_relations 核对 temp→adapter 依赖边命中，关系小节并入修订面"）。
4. 命中但依赖文档**不在修订面** → 须实读变更文件确认依赖语义是否真的变化，再决定是否新增 transfer_impact 条目；无实证不强行扩散派工（本分支本轮无实证，属待验证路径）。
5. 完工判定：wiki_relations 核对完毕 + unmatched 闭合 + 分组求和闭合三项齐备，阶段 2 才允许进入派工。

## Faster Next Time

- 一行决策规则：`transfer_impact=[]` 不是结论而是核对触发器——回 wiki_relations 双向筛依赖边，核对完才算阶段 2 完工。
- ROI：读一次 wiki_relations（分钟级）避免的是关系小节滞留旧依赖清单、随索引固化成失真知识、下游检索断链的整链返工；且并入同轮修订面零额外派工成本。
- 同构记忆串成组："脚本聚合输出为空不构成否定结论，须回事实源核对"——`modules=[]` 不构成无新模块依据（2026-11-11-wiki-arch-snapshot-stale-new-module-read-verify，实读抽验定新模块）、`transfer_impact=[]` 不构成无传递影响（本条）、unmatched 需逐文件归因闭合（2026-11-12-batch-routing-closure-check，求和闭合）。三类同构坑共用一个心智模型：快捷通道空 → 事实源补判。
- 反模式：把脚本空输出当最终事实；双向核对只查"被依赖"漏"依赖"；为凑完整性给不在修订面的文档强行加派工（无实证扩散）；把 wiki_relations 核对推迟到派工之后（那时修订面已冻结，返工成本翻倍）。

## Applicability Boundaries

- 适用：任何"脚本聚合传递影响 + 文档间依赖关系数据（wiki_relations 类）"双源结构的增量更新流水线；凡聚合输出与关系事实源可能分叉的判定环节。
- 不适用：wiki_relations 本身为空或缺失（此时须先重建基线，或如实记录核对缺口并降级为人工复核）；单文档小项目（依赖面为空，交叉核对无增益）；修订面为空的零修订轮次（应走全短路，见 2026-11-12-wiki-zero-revision-round-full-short-circuit）。
- 证据等级：单次实战闭环，仅覆盖"依赖文档已在修订面"分支的实证；"依赖文档不在修订面须新增传递影响"分支为推演路径，跨项目复用稳定性待同类任务检验。

## Evidence or Examples

- 源会话 ses_e2d1aefc4ffeVoyvJy3USpU211（docgen-apply，Date 项目 Wiki 增量更新，6 变更文件触发 6 篇文档修订，2026-11-13）。
- 分叉实证：reverse_lookup.py 输出 transfer_impact 为空；wiki_relations 显示 临时素材与知识萃取.md → P003演练适配器.md 依赖边（drill_round01.py:16-20 导入 adapter），temp 文档已因 2 个 added（drill_round06_captured.py、verdict_round08.py）经 module_tree 第一级匹配进入修订面。
- 修订实证：temp 文档"关系"小节列入 S2 修订面，subagent 以 replace_content 同步新增依赖——drill_round06_captured.py:16-20 导入 adapter.capture/pairing/portaudit/proxycheck/verdict/whitelist、verdict_round08.py:10 导入 adapter.verdict，另补外部工具 tshark（pcap 取证）依赖；该小节 patch 合并 rc=0。
- 流程位置佐证：本 trace 同时沿用 2026-11-12-wiki-index-code-refs-absence-cause2-patch 的成因 2 补判处理 adapter/capture.py（漏建 code_refs），wiki_relations 交叉核对与成因 2 补判是同阶段并列的两个完整性检查，均须在 update_plan note 留痕。