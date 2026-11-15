---
id: 2026-11-14-wiki-build-index-stats-absorption-reconciliation
title: build_index 增量统计的吸收对账回验：updated 计数对齐修订面、code_paths 增量对齐新增引用清单
category: workflow
nature: methodology
created_at: 2026-11-14T13:10:48
updated_at: 2026-11-14T13:14:22
tags: [wiki增量更新, 索引吸收回验, 统计对账, build_index, 阶段7回验]
keywords: [build_stats, reused, updated, added, code_paths, 增量对账, 吸收缺口, code-links.json 消费, 修订面, wiki-index.json]
problem_patterns:
  - "正常修订轮完成后不确定索引是否正确吸收本轮修订，转而逐条人工抽查 code_refs，费时且不可靠"
  - "build_index 输出后不对账统计数字，patch 产出未被当轮索引吸收的缺口静默漏过，下轮 reverse_lookup 才暴露"
source_sessions: [ses_e2fb0871affelu6jBOtwd3ki79]
project: Date
severity: low
quality_score: 84
hit_count: 3
last_hit_at: 2026-11-15T15:47:24
low_quality_hit_count: 0
tier: A
related_experiences: [2026-11-12-wiki-zero-revision-round-full-short-circuit, 2026-11-12-wiki-index-code-refs-absence-cause2-patch, 2026-11-14-wiki-subagent-artifact-defects-pre-build-index, 2026-11-13-wiki-transfer-impact-empty-crosscheck-wiki-relations]
---

# build_index 增量统计的吸收对账回验：updated 计数对齐修订面、code_paths 增量对齐新增引用清单

## Scenario

Wiki 增量更新（repo-simple-wiki-update 类流程）的正常修订轮收尾：阶段 3/4 完成若干文档的 patch→merge 修订，阶段 6 执行 build_index 增量重建 wiki-index.json，进入阶段 7 回验。此时需要回答"本轮修订是否已被索引正确吸收"——逐条人工抽查 wiki-index 中的 section_code_paths 既费时又容易漏。build_index 的输出本身就携带免费的对账证据（build_stats 与 code_paths 总数），用统计对账代替逐条抽查即可闭环。工作流规模：单轮修订 1~N 篇文档、索引 8~10 篇的中小型增量轮。

## Key Signals

- **build_stats 三元组**：`reused / updated / added` 直接可读——updated 计数应等于本轮实际 merge 成功的去重文档数；reused 应等于本轮未动的既有文档数；added 在纯增量轮（无新模块）应为 0。
- **code_paths 总数变化**：输出中 `code_paths_verified`（或累计 code_paths 数）应相对上轮单调不减，且增量与本轮新增 code_refs 清单的去重路径规模同数量级（不必精确等号——新旧文档可能共享部分既有引用路径）。
- **附属产物信号**：`.code-links.json` 被 build_index 消费删除（"已删除 N 个"输出）；overview.md / WikiRetrieval.md 重新生成且检索标记完整、无占位符残留。
- **反向警示信号**：updated < 修订文档数，或 code_paths 零增量——提示存在吸收缺口（正是"上轮产出未被当轮 build_index 吸收"的典型形态，见相邻经验）。

## Essence

build_index 的增量统计是"修订→索引吸收"闭环的定量对账依据，不需要逐条抽查：`updated == 本轮修订文档数` 验证吸收的覆盖面，`code_paths 增量 ≈ 新增引用去重路径数` 验证吸收的深度，`reused == 未动文档数` 验证无越界改动。三个数字对上即判定吸收闭环。它与零修订轮经验构成互补的两面：零修订轮看"全 reused 属正常、无操作即正常证据"（防止把正常空转误判为异常）；正常修订轮看"updated N + code_paths 增长属预期形态"（防止吸收缺口静默漏过）。两个方向的误判都源于把 build_stats 当噪声而非对账数据。

## Approach

1. **读修订面基线**：merge 阶段结束时记下本轮实际合并成功的去重文档数 M 与新增 code_refs 的去重路径数 R（直接从 merge 输出的 merged_sections/hashes_updated 汇总）。
2. **执行 build_index 后对账 updated**：`build_stats.updated == M`；不等则先回查 merge 输出确认哪些文档未进入吸收面。
3. **对账 code_paths**：总数 ≥ 上轮值，且增量与 R 同数量级（允许既有引用交集造成的偏差）；零增量即吸收缺口红旗。
4. **核对 added**：纯增量轮 added 应为 0；非 0 说明出现了规划外的"新文档"，检查是否漏走了模块规划。
5. **复核附属产物**：.code-links.json 已被消费删除、overview/WikiRetrieval 重新生成且标记完整——三项同过即完成阶段 7 回验。
6. **对账不过的处理**：回查 merge 输出与 patch 文件定位缺口文档，按缺口成因（索引漏吸收 / patch 未交付）修复后重跑 build_index，不盲目整体重跑。

## Faster Next Time

- 一行对账公式：`updated = 修订文档数 ∧ code_paths 增量 ≈ 新增引用数 ∧ added = 0 → 吸收闭环`，三个数字一次读完即收尾。
- ROI：把阶段 7 回验从逐条抽查（分钟级、易漏）降为三次数值对账（秒级、定量）；吸收缺口从"下轮 reverse_lookup 才暴露"提前到"本轮收尾即发现"。
- 反模式：把 build_stats 当作仅供展示的输出忽略；在 updated=0 时先怀疑索引构建异常（应先确认本轮修订面是否真的非空）；把 code_paths 增量与新增引用条数强求精确等号（共享既有引用路径会自然产生偏差）。

## Applicability Boundaries

- 适用：带 build_index 增量重建的 Wiki 增量更新流程的正常修订轮收尾回验；patch→merge→build_index 闭环。
- 不适用：零修订轮（hash 全 unchanged 的全短路特例，build_stats 全 reused 属正常，见相邻经验）；全量重建轮（build_stats 语义变为全量 added，对账公式不适用）；subagent patch 产物的缺陷拦截（发生在 build_index 之前，见相邻经验）。
- 与相邻经验分工：`2026-11-12-wiki-zero-revision-round-full-short-circuit` 管零修订轮的"全 reused 属正常"；`2026-11-12-wiki-index-code-refs-absence-cause2-patch` 管 code_refs 空导致的成因 2 补判（本条对账不过时的下游定位依据之一）；`2026-11-14-wiki-subagent-artifact-defects-pre-build-index` 管 build_index 之前的产物缺陷拦截；本条管 build_index 之后的吸收闭环定量回验——四者按"修订前后时间轴"互补。

## Evidence or Examples

- 源会话 ses_e2fb0871affelu6jBOtwd3ki79（docgen-apply，Date 项目，version_token 423→453 重开轮，变更 10/349≈2.9%，常规档）。
- 修订面 M=2：codebase-knowledge/知识库笔记.md（概述+架构设计两小节）+ project-knowledge/documentation_system/documentation_system.md（关键文件与位置一小节）。
- 新增引用 R≈13 个去重路径（知识库笔记.md 两小节各 7 条 refs + documentation_system.md 6 条 refs，去重交集后 13 个路径）。
- build_index 实际输出：`reused 6 / updated 2 / added 0 / total 8`，`code_paths_verified 82`（上轮 69，增量 +13），"已删除 2 个 .code-links.json"，overview.md 与 WikiRetrieval.md 已生成——updated=2 与 M 对账一致、code_paths 增量与 R 对账一致，吸收闭环判定成立，阶段 7 未做逐条抽查。