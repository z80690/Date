---
id: 2026-11-09-wiki-hash-shortcut-requires-merge-pass
title: hash_status=changed 小节即使零修订判定也必须发 line_number_only patch 走合并：source_hashes 只在 merge 时刷新，跳过合并则 hash 永不短路
category: agent-ops
nature: technique
created_at: 2026-11-09T02:05:58
updated_at: 2026-11-09T02:16:06
tags: [wiki增量更新, hash短路, source_hashes, 零修订, 合并闭环]
keywords: [hash_status changed, source_hashes, merge_section_patch, line_number_only, 零修订, hash 短路, reverse_lookup, hashes_updated, 增量更新闭环, 状态值刷新, 判定落盘]
problem_patterns:
  - reverse_lookup 报某小节 hash_status=changed，逐条比对后判定正文无需修订，于是不发任何 patch 直接收尾——下轮增量更新同一小节仍报 changed，hash 短路机制永远无法生效
  - 误以为"判定为零修订"等于"流程闭环"，不知道 hash 基线的推进依赖合并动作本身
  - 合并后未核对 hashes_updated 覆盖面，部分 changed 源文件 hash 未刷新导致下轮重复判定成本
source_sessions: [ses_e4405534affeu8pLGAbuG7Iwh9]
project: Date
severity: medium
quality_score: 89
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-08-wiki-update-script-behavior-contract-blindspots, 2026-11-09-glossary-status-refresh-zero-revision-criterion, 2026-11-09-subagent-patch-code-refs-baseline-fallback, 2026-11-08-wiki-section-tiered-revision-judgment-contract]
---

# hash_status=changed 小节即使零修订判定也必须发 line_number_only patch 走合并：source_hashes 只在 merge 时刷新，跳过合并则 hash 永不短路

## Scenario

Wiki 增量更新流程：reverse_lookup 按小节比对源文件 hash（source_hashes），报出 hash_status=changed 的受影响小节；编排者派只读修订 subagent 判定修订动作。某小节经逐条比对判定为"状态值刷新、正文零修订"（结论 line_number_only、new_content 为 null）。关键在于：零修订判定之后，该小节的 hash 基线如何推进到当前源文件状态。

## Key Signals

- reverse_lookup 的 affected_sections 报 hash changed——源文件当前 hash 与 wiki-index 记录的 source_hashes 不一致。
- 零修订判定的产出形态是 line_number_only patch（`new_content: null` + 核对后的 code_refs），而非"不发 patch"。
- 合并输出 `hashes_updated` 列出每个小节实际刷新的源文件 hash——它是 hash 基线推进的唯一权威回执。
- hash 刷新按**最终 code_refs 集合**重算：合并中未被修订正文触及、但出现在 code_refs 里的源文件，其 hash 同样被刷新（实证：术语列表小节零正文修订，但其 code_refs 涉及的 3 个源文件 hash 全部刷新）。

## Essence

source_hashes 只在 merge_section_patch 执行时刷新——"判定为零修订"若不落地为 patch 并走合并，hash 基线就停留在旧值，下轮 reverse_lookup 对同一小节永远报 changed，hash 短路机制失效，每轮增量更新都要重复同一批判定。零修订判定的正确闭环形态是：**判定结果以 line_number_only patch 落进合并**，让合并按最终引用集合把 hash 推进到当前状态。"不改"是判定结论，"发 patch 走合并"是判定结论的落盘方式，二者不矛盾——跳过后者等于判定结论没有进入持久化状态。

## Approach

1. **零修订 ≠ 不发 patch**：判定为 line_number_only 后，仍产出结构合规的 patch（`action: line_number_only`、`new_content: null`、`code_refs` 为核对后的行号集合）交合并。
2. **code_refs 覆盖全部 changed 源文件**：核对行号时确保每个 hash_status=changed 的源文件都被某条 code_refs 覆盖——hash 刷新按最终引用集合重算，漏引用即漏刷新。
3. **合并后核对 hashes_updated 覆盖面**：对照 reverse_lookup 报告的 changed 源文件清单，确认每个文件的 hash 都出现在 `hashes_updated` 中；缺失即漏引用信号，补 patch 重合并。
4. **next-run 短路验证**：下一轮增量更新时，已刷新小节不应再出现在 affected_sections 中——这是 hash 短路生效的最终验收。

## Faster Next Time

- 判定表：hash changed + 零修订判定 → 仍发 line_number_only patch；hash changed + 需改写 → replace_content patch；两者都必须走 merge。
- 快捷核对：reverse_lookup 的 changed 文件清单 vs 合并输出 hashes_updated 的文件清单，做一次差集即为漏刷新项。
- ROI：零修订小节发一个空 patch 的成本几乎为零，换取下轮起该小节永久短路；跳过的代价是每轮重复判定 + 重复派工。
- 反模式：把"逐条比对确认零修订"当作流程终点；零修订小节不进 patch 清单；合并后不看 hashes_updated 直接跑索引重建。

## Applicability Boundaries

- 适用：以 source_hashes 做增量短路判定的 Wiki/文档索引体系（merge_section_patch + reverse_lookup 链路）；一切"判定动作"与"基线推进动作"分离的两段式流程。
- 不适用：全量生成场景（hash 由生成流程统一写入，无短路问题）；基线机制本身被旁路的直接写文件场景（绕过合并即绕过 hash 推进，属另一类流程违规）。
- 机制依赖：merge_section_patch 按 patch 的最终 code_refs 集合重算并写回 source_hashes——若脚本版本行为不同（如只刷新被正文改写的源文件），以实际输出 `hashes_updated` 为准调整覆盖策略。
- 与相邻经验分工：`2026-11-08-wiki-update-script-behavior-contract-blindspots` 管合并作用域盲区（H1/frontmatter 不在 patch 表达范围内），本条管零修订判定的 hash 推进闭环；`2026-11-09-glossary-status-refresh-zero-revision-criterion` 管零修订判据本身（subagent 侧），本条管判据成立后的流程闭环（编排者侧）。

## Evidence or Examples

- 源会话 ses_e4405534affeu8pLGAbuG7Iwh9（docgen-apply fork #1，Date 项目 Wiki 增量更新，version_token 171→187）。
- 实证链：reverse_lookup 报知识库笔记.md 概述/架构设计与 business_glossary.md 术语列表 hash changed（变更源 notes/项目事实表.md）；概述与术语列表均判定零正文修订仍以 line_number_only patch 走合并；合并输出 `hashes_updated`：概述刷新 2 个源文件、术语列表刷新 3 个源文件（均含变更源 项目事实表 → `07c81808c3e0`，另含未被正文触及的 阶段状态机运行规则 → `f162df773fe6`），证实刷新按最终引用集合重算。
- 下游全绿：validate_code_links 2/2 passed、lint_wiki 0 errors、build_index reused 5/updated 2——零修订小节的空 patch 不引入任何回归。