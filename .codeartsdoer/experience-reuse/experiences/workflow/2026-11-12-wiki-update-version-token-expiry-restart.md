---
id: 2026-11-12-wiki-update-version-token-expiry-restart
title: 增量更新进度快照与变更集令牌不匹配：判定重开更新流程而非断点续开
category: workflow
nature: decision
created_at: 2026-11-12T07:28:11
updated_at: 2026-11-12T07:28:11
tags: [增量更新, 令牌校验, 断点续开, 流程状态机, wiki]
keywords: [version_token, progress.json, state.json, 令牌不匹配, 断点续开, 重开更新流程, 变更集过期, 阶段0判定, update_plan 清理, 骨架重提取]
problem_patterns: ["progress.json 存在旧一轮 update 记录时误按断点续开，把过期 update_plan 与新变更集混在一起", "只看 stages 全 completed 就认为无需重开，未核对上轮消费的令牌与当前变更令牌是否同一"]
source_sessions: ["ses_e37dbc6ffffew3OvscR4pcK9Pe"]
project: Date
severity: medium
quality_score: 88
hit_count: 1
last_hit_at: 2026-11-12T08:12:47
low_quality_hit_count: 0
tier: S
related_experiences: ["2026-11-11-wiki-added-mislabeled-merkle-reset-hash-triage", "2026-11-08-wiki-increment-update-unmatched-file-routing", "2026-11-10-prior-reuse-recheck-checklist-baseline-drift"]
---

# 增量更新进度快照与变更集令牌不匹配：判定重开更新流程而非断点续开

## Scenario

知识库/Wiki 增量更新流程的**阶段 0（执行模式判定）**：仓库已有上一轮增量更新的 `progress.json`（含 module_tree、stages、update_context），同时状态文件（state.json）报告了新一轮变更集。此时有两条可选路径：断点续开（沿用旧 stages 继续）或重开更新流程（在旧 module_tree 基础上重启全部阶段）。误选断点续开会让旧 update_plan 与新变更集错位，后续阶段产出混入过期计划。

## Key Signals

- **令牌不匹配是最早可见信号**：`progress.json.update_context.version_token`（上轮消费时记录，本例 393、对应 9 个变更文件）≠ `state.json.version_token`（本轮变更集，本例 408、对应 247 个变更文件）。令牌不同说明上轮更新消费的变更集与本次完全不同，中间又发生过批量变更。
- stages 全部 completed 不是"无需重开"的证据——它只表示上一轮跑完了，不能证明对本轮变更集仍有效。
- 错误做法的诱惑点：旧 stages 记录完整、module_tree 现成，直接续开省事；但旧 update_plan 的 affected_docs/unmatched 裁决全部基于旧令牌的 9 文件清单，与 247 文件清单无关。

## Essence

`progress.json` 是"上轮更新对某个变更集快照的执行账本"，其有效性严格绑定记录在其 update_context 里的令牌。令牌 = 本轮变更集令牌才允许断点续开；令牌 ≠ 则快照对本次变更集无意义，必须重开：保留 module_tree（模块结构不因变更轮次作废）、重写 update_context、把 stages 重置为 update 模式并按新 update_plan 重新分配 pending/completed。判定的唯一依据是令牌比对，不得以 stages 完成度、文档新鲜度等间接信号替代。

## Approach

1. **读取两个令牌**：从 `progress.json.update_context.version_token` 取上轮令牌，从变更状态文件（state.json）取本轮令牌，直接数值比对。
2. **令牌相等** → 断点续开：沿用 stages 与 update_plan，仅从上次中断处继续。
3. **令牌不等** → 重开更新流程（本例路径）：
   - 重写 `progress.json`：mode=update、写入新 update_context（新令牌、新变更文件数、scale_note）；
   - 保留 `module_tree` 原样（模块树不随令牌过期作废，是否新增模块由本轮实读裁决另行判定）；
   - stages 重置：阶段 1 重新执行（骨架重提取），阶段 2 重新生成 update_plan 后覆盖写入。
4. **重开后做一次规模自检**：新旧变更文件数差异巨大（本例 9 → 247）时，重新跑降级判定（变更占比是否触发全量降级），不得沿用旧 scale_note 的降级结论。
5. **阶段 1 结果回验重开正确性**：骨架提取符号数与上轮一致（本例 201 符号/23 文件）可佐证部分内容未变，但不能反推变更集相同——重开决策以令牌为准，证据仅作交叉参考。

## Faster Next Time

- 一行决策规则：阶段 0 先比对 `progress.json.update_context.version_token` 与 state.json 令牌——相等才续开，不等必重开，不读其他任何信号替代此判定。
- ROI：一次 JSON 字段比对（秒级）即可避免整轮混入过期 update_plan 的返工；若误续开，阶段 3/4 会基于旧 affected_docs 派工，产出与真实变更错位，返工成本是整轮。
- 反模式：看到 stages 全 completed 就跳过阶段 0；把"骨架符号数与上轮一致"当作变更集未变的证据；重开时顺手清掉 module_tree 导致新模块判定失去对照基线。

## Applicability Boundaries

- 适用：任何"进度快照文件 + 变更集令牌"双状态结构的增量流程（wiki 增量更新、增量索引构建、断点续跑型流水线）的阶段 0 模式判定。
- 不适用：无令牌机制的流程（此时以快照时间戳 vs 变更检测时间比对替代）；首轮更新（无旧 progress.json 可比）。
- 前提约束：重开 ≠ 全量重新生成——降级与否由变更占比阈值独立判定，令牌不匹配只触发"流程重开"，不直接触发"降级全量"。
- 证据等级：单次成功样本（重开后 7 阶段全部完成、校验全过），令牌不匹配的成因（merkle 重建/多轮变更叠加）在本次 trace 中未深究，属可复用决策规则但成因归因待同类样本补充。