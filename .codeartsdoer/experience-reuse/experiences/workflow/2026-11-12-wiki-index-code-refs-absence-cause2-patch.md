---
id: 2026-11-12-wiki-index-code-refs-absence-cause2-patch
title: wiki-index 文档 code_refs 为空时 reverse_lookup 必然 unmatched：按 module_tree 归属判成因 2 补判
category: workflow
nature: methodology
created_at: 2026-11-12T08:03:10
updated_at: 2026-11-14T10:33:29
tags: [wiki增量更新, 影响分析, 索引漏建, 归属补判, 知识库]
keywords: [reverse_lookup, unmatched, section_code_paths, code_refs, 成因2, 索引漏建, module_tree, build_index, hash unknown, 增量更新]
problem_patterns:
  - "变更文件明确落在某既有 Wiki 文档的覆盖路径下，却出现在 reverse_lookup 的 unmatched 清单，误判为'不在关注层面'（成因 1）而跳过，导致该文档漏修"
  - "为解释 unmatched 去读 architecture.json 找依据，实际该产物缺失或已过期，判定失去立足点"
source_sessions: [ses_e3930e653ffejnN62cpj5ECw5v]
project: Date
severity: medium
quality_score: 87
hit_count: 8
last_hit_at: 2026-11-14T01:56:22
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-08-wiki-increment-update-unmatched-file-routing, 2026-11-11-wiki-arch-snapshot-stale-new-module-read-verify, 2026-11-11-wiki-added-mislabeled-merkle-reset-hash-triage, 2026-11-14-wiki-update-plan-clear-vs-crossround-prior-note-token]
---

# wiki-index 文档 code_refs 为空时 reverse_lookup 必然 unmatched：按 module_tree 归属判成因 2 补判

## Scenario

对既有 Wiki 执行增量更新的影响分析阶段（repo-simple-wiki-update 类流程）：state.json 报告 9 个变更文件，reverse_lookup 直接命中 3 篇 project-knowledge 文档后剩余 7 个 unmatched。其中 `workflow_base/tools/prepare.py`（modified）与 `tests/probe_tor_alt2.py`（added）明确落在既有模块文档"工作流底座（workflow_base）"的覆盖路径下，按三级路由框架第一级本应直接命中，却出现在 unmatched 清单——归属逻辑与 reverse_lookup 结果矛盾，需先定性矛盾成因再定修订面。

## Key Signals

- **决定性信号**：目标文档在 wiki-index.json 中 `section_code_paths` 为空（各小节 hash 全 unknown）——该文档从未进入过索引的 code↔wiki 映射，reverse_lookup 无 code_refs 可比对，其覆盖路径下的任何变更**必然**报 unmatched。
- 溯源信号：上轮流程曾为该文档新增内容并产出 .code-links.json，但未被当轮 build_index 吸收（增量吸收缺口的典型形态）。
- 环境信号：artifacts/repos 为空、无可用 architecture.json——试图按"产物判据"解释 unmatched 的路径天然关闭。
- 对照信号：同轮另有 `.workbuddy/memory/.../memory.md`（modified 且不命中任何 section_code_paths）——它不命中是因为真的不在关注层面（成因 1），与上述"文档存在但索引漏建"（成因 2）必须区分。

## Essence

unmatched 的成因不是文件与文档的关系问题，而是**索引侧缺口**：文档存在、归属清晰，但它的 code_refs 从未被 build_index 吸收，reverse_lookup 建立不起比对关系，覆盖路径下的变更必然 unmatched。此时判定依据应从架构产物切换到 module_tree 前缀归属——module_tree 是模块身份的现行账本，直接回答"该文件归哪篇文档"。成因 1（真不在关注层面）与成因 2（在关注层面但索引漏建）的区分判据就是目标文档 section_code_paths 是否为空：空 = 成因 2 补判入修订，非空且无命中 = 成因 1 跳过。

## Approach

1. **遇 unmatched 先查索引缺口**：找到文件按 module_tree 应归属的文档，读 wiki-index.json 中该文档的 `section_code_paths` 是否为空。
2. **空 → 判成因 2 补判**：把文件路由进该文档的修订面，hash 全 unknown 按 subagent 修订档处理（需实读源文件取证，不依赖索引行号）。
3. **留痕**：在 update_plan note 中记一行"该文档 code_refs 空，按 module_tree 归属判成因 2 补判"，供本轮校验与复盘追溯；轮末 Stage 6 清空 update_plan 前，判定依据须迁移至 stage_2 的 `note_<version_token>` 追加式留痕供跨轮复用（update_plan 是单轮工作面、轮末会被清空，跨轮先验禁寄存其上——修正载体见 2026-11-14-wiki-update-plan-clear-vs-crossround-prior-note-token）。
4. **修订形态分档**：常规变更写入正文小节；一次性诊断探针类新增文件（如临时 probe/alt 脚本）不构成正文知识增量，仅在架构设计小节以 line_number_only 登记 code_refs。
5. **build_index 回验**：修订合并完成后跑增量索引重建，验证 code_paths 数量显著回升（漏建缺口应被一次性补齐），同时确认 .code-links.json 零残留。

## Faster Next Time

- 一行决策规则：unmatched 文件先查其应归属文档的 section_code_paths——空 = 索引漏建（成因 2，补判入修订），非空且无命中 = 关注面外（成因 1，跳过并留理由）。
- ROI：一次 JSON 字段读取（秒级）即可避免把真实受影响文档整轮漏修；漏修后果由下一轮同类变更反复 unmatched 来偿还，且 code_paths 覆盖缺口持续累积。
- 反模式：机械套用"modified 不命中任何小节映射 → 成因 1 跳过"，把索引漏建误当关注面外；为解释 unmatched 去读缺失/过期的 architecture.json；对补判文档沿用索引中陈旧行号（hash unknown 场景必须实读重取证）。

## Applicability Boundaries

- 适用：基于 wiki-index.json + reverse_lookup 的增量影响分析流程；凡文档经 subagent/派工新增或修订但 code-links 未被 build_index 吸收的场景。
- 不适用：code_refs 非空但行号/内容漂移的场景（那是 hash 短路与 merkle 误标问题）；全量首次生成（索引与变更同源，无此缺口）。
- 与相邻经验分工：2026-11-08-wiki-increment-update-unmatched-file-routing 管 unmatched 三级路由总框架（本条是其 modified 文件处置分支的成因细分补充——其原口径"modified 不命中 → 成因 1 跳过"须先排除成因 2）；2026-11-11-wiki-arch-snapshot-stale-new-module-read-verify 管"第二级新模块判据的产物时效"；2026-11-11-wiki-added-mislabeled-merkle-reset-hash-triage 管"索引全量 added 误标的甄别"——四者按成因类型互补不重叠。

## Evidence or Examples

- 源会话 ses_e3930e653ffejnN62cpj5ECw5v（docgen-apply fork #1，Date 项目 Wiki 增量更新，version_token 393）。
- 实证链路：wiki-index 中"工作流底座（workflow_base）"与"工具链与环境配置"两文档 section_code_paths 为空 → 7 个 unmatched 补判（prepare.py/probe_tor_alt2.py 归工作流底座文档；06 开发工具三个 md 归 tooling_and_environment；架构反思与建议.md 归知识库笔记文档；.workbuddy 记忆判成因 1 跳过）→ 6 篇文档并行修订 merge 6/6 success、validate 6/6 passed → build_index success，code_paths_verified **56 → 98**，reused 2 / updated 6，.code-links.json 零残留。
- 探针脚本处置实证：tests/probe_tor_alt2.py 仅以 line_number_only 登记进架构设计小节 code_refs，正文零改动。