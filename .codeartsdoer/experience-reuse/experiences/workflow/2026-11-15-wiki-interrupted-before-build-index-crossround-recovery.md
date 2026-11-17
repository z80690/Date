---
id: 2026-11-15-wiki-interrupted-before-build-index-crossround-recovery
title: 增量更新中断于索引重建前的跨轮恢复链：半成品资产继承消费而非清理重做，wiki_root 陈旧由 build_index 重建覆盖修正
category: workflow
nature: methodology
created_at: 2026-11-15T20:19:23
updated_at: 2026-11-16T00:01:54
tags: [wiki增量更新, 中断恢复, 跨轮状态, 索引重建, 半成品资产]
keywords: [wiki_root 陈旧, code-links 残留, 跨轮恢复, 中断续跑, build_index 消费, module_tree pending, version_token 落后, 旧分支指向, wiki-index.json, 恢复链]
problem_patterns:
  - "上轮 wiki 增量更新中断于 build_index 之前：merge 已把修订写进 .md 与 .code-links.json，但索引未重建，新轮启动面对 token 落后+陈旧索引+残留文件+pending change 四重半成品，不知按全新轮清理还是按恢复轮继承"
  - "wiki-index.json 的 wiki_root 指向旧分支目录（分支迁移/改名遗留），误以为要手工改索引文件"
  - "docs 树发现 .code-links.json 残留，误判为脏数据手工删除，导致本轮 merge 产生的 code_refs 丢失、索引吸收出现缺口"
source_sessions: [ses_e20e3529dffeTnb2pIjC6FE8dB]
project: Date
severity: medium
quality_score: 92
hit_count: 1
last_hit_at: 2026-11-16T15:36:43
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-12-wiki-update-version-token-expiry-restart, 2026-11-14-wiki-update-plan-clear-vs-crossround-prior-note-token, 2026-11-14-wiki-build-index-stats-absorption-reconciliation, 2026-11-12-wiki-index-code-refs-absence-cause2-patch, 2026-11-15-edit-asymmetric-replacement-drops-json-closing-structure]
---

# 增量更新中断于索引重建前的跨轮恢复链：半成品资产继承消费而非清理重做，wiki_root 陈旧由 build_index 重建覆盖修正

## Scenario

Wiki 增量更新流程（repo-simple-wiki-update 类多阶段流水：预提取 → 影响分析 → 小节修订 → merge 合并 → 校验 → build_index 索引重建）中，上一轮执行**中断于 Stage 6（build_index）之前**——merge 已把修订合并进 .md 正文与 .code-links.json，但索引重建未跑。新轮次启动时面对四重半成品状态：progress.json 的 update_context.version_token 落后于 state.json（触发"过期重开"字面规则）、wiki-index.json 仍是旧产物且 wiki_root 指向旧分支目录、docs 树残留 .code-links.json、module_tree 存在未合并的 pending change。流程字面规则只覆盖"token 过期 → 重新开始更新"，未覆盖"重开时如何处置上轮半成品"；直接照字面清空重跑会把有效资产当垃圾，带着陈旧索引做影响分析则会漏判。

## Key Signals

诊断清单（五项并存即判定"上轮中断于 build_index 前"，走恢复链）：

1. `update_context.version_token < state.json.version_token`——上轮未走完，state 又已推进。
2. wiki-index.json 的 `built_at` 明显陈旧（早于最近一次 wiki 修订日期）。
3. wiki-index.json 的 `wiki_root` 指向不存在或旧的分支目录（分支迁移/改名后遗留）。
4. docs 树存在 `.code-links.json` 残留（merge 已吸收、build_index 未消费的中间产物）。
5. module_tree 存在 pending changes 未合并。

## Essence

"过期重开"重开的是**工作面**（update_plan、stage 状态、pending 列表），不是**资产**——上轮已 merge 进 .md 与 .code-links.json 的修订内容、pending change 承载的模块树意图，均为有效资产，处置原则是**继承消费**而非清理重做。索引类产物（wiki-index.json）陈旧与错向不需要手工修：build_index 本身是全量重建，跑一次自然覆盖修正。判断本质：按产物的消费链路（merge → .code-links.json → build_index 吸收）延续执行，凡处在链路上的残留都是待消费资产，凡链路外的才可清。

## Approach

1. **留痕迁移**：清空旧轮 update_plan 前，把其中仍有复用价值的判定依据迁移到 `note_<旧token>` 键追加式留痕（沿用 note_<token> 跨轮先验纪律，见相邻经验）。
2. **pending change 继承执行**：module_tree 中上轮遗留的 pending 修改（如 extra_paths 追加新路径）在本轮对应的合并节点（Stage 6.2 合并 module_tree）照常执行，不丢弃、不重算。
3. **残留 code-links 交 build_index 消费**：docs 树的 .code-links.json **不手工删**——它们承载本轮依赖的 code_refs，build_index 会读取、吸收进 wiki-index 并自动删除（输出中"已删除 N 个 .code-links.json"即消费确认信号）。
4. **build_index 重建覆盖修正**：以当前分支真实 wiki_root 跑 build_index，重建的 wiki-index.json 自然修正 wiki_root 的旧分支指向；随后核对 built_at 与 wiki_root 字段确认修正生效。
5. **恢复验收**：照常完成本轮修订后，用对账口径（`build_stats.updated == 本轮 merge 成功文档数 M`、code_paths 增量与新 code_refs 去重路径数 R 同量级）作为恢复正确性的验收证据。

## Faster Next Time

- 开轮先验 30 秒清单：读 state.json version_token、progress.json update_context.version_token、wiki-index.json 的 built_at/wiki_root 三处，即可判定本轮是"全新轮"还是"中断恢复轮"，再决定走字面重开还是恢复链。
- ROI：恢复链把"误删有效产物导致重做修订"与"带陈旧索引做影响分析导致漏判"两类事故降为零；实测上轮修订面（2 篇文档 + 2 个新 code_refs 路径）经恢复全部存活进新索引（updated=2==M，uniq_paths 增量=R）。
- 反模式：见 .code-links.json 残留就手工删（丢失 code_refs，索引吸收缺口）；见 wiki_root 指向旧分支就手改 wiki-index.json（下次 build_index 会冲掉手改，且该字段关联多处内容，手改必漏）；只按"token 过期重开"字面清空重跑（半成品资产被当垃圾）。

## Applicability Boundaries

- 适用：多阶段流水且末段为"全量重建索引"式增量的更新流程；上轮中断点在索引重建之前（merge 完成、build_index 未跑）。
- 不适用：上轮已完整跑完 build_index 的轮次（无残留，按常规 token 过期重开即可，见相邻经验）；中断点在 merge 之前的轮次（修订面未定型，按全新轮处理更稳）；索引更新为增量 patch 式（非全量重建）的流程（覆盖修正假设不成立，需另行评估）。
- 与相邻经验分工：2026-11-12-wiki-update-version-token-expiry-restart 管"token 过期 → 重新开始"的判定与重开本身，本条管重开时对上轮半成品的处置；2026-11-14-wiki-update-plan-clear-vs-crossround-prior-note-token 管留痕迁移的载体纪律（本条第 1 步引用）；2026-11-14-wiki-build-index-stats-absorption-reconciliation 管恢复后的对账验收口径（本条第 5 步引用）；2026-11-15-edit-asymmetric-replacement-drops-json-closing-structure 管恢复轮内的结构化状态文件编辑事故（本恢复轮实际遭遇：多处状态翻转中 Edit 范围不对称漏删闭合层）——恢复轮叠加高频状态文件编辑，两条经验构成"恢复链 × 编辑纪律"的组合风险面。

## Evidence or Examples

- 源会话 ses_e20e3529dffeTnb2pIjC6FE8dB（docgen-apply fork #1，Date 项目 wiki 增量更新，version_token 23→36 恢复轮）。
- 诊断实录：wiki-index.json built_at=2026-11-13 且 wiki_root=".../branches/master/docs"（当前分支 main）；docs 树 2 个 .code-links.json 残留（P003演练适配器与 build_system，上轮 merge 产物）；update_context.version_token=23 vs state.json version_token=36。
- 恢复实录：note_23 留痕迁移 → stage 重开 → 本轮 merge（M=2，R=2：api/index.py 与 vercel.json）→ build_index 输出"已删除 2 个 .code-links.json"、wiki_root 修正为 main/docs、build_stats.updated=2==M、uniq_paths=83（增量 2 与 R 同量级）、format_errors=[]。
- 稀缺性佐证：既有经验库 grep "wiki_root" 零命中——该诊断信号此前无任何沉淀，本条为首次入库；相邻 token 过期经验只覆盖"无残留的全量重开"形态。