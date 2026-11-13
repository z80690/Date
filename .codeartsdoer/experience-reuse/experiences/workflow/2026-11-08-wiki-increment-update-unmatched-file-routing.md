---
id: 2026-11-08-wiki-increment-update-unmatched-file-routing
title: Wiki 增量更新中 unmatched 变更文件的三级归属判定：模块树路径匹配→架构产物新模块判定→关注面外跳过
category: workflow
nature: methodology
created_at: 2026-11-08T02:46:17
updated_at: 2026-11-08T02:51:21
tags: [wiki增量更新, 归属判定, 变更路由, 影响分析, 知识库]
keywords: [reverse_lookup, unmatched, changed_files, module_tree, architecture.json, 关注层面, 入库排除清单, affected_docs, 增量更新, S2修订]
problem_patterns:
  - Wiki 增量更新影响分析产出大量 unmatched 变更文件，不知道该归入哪篇既有文档、生成新文档还是直接跳过
  - 把 module_tree 的 file_count 当现状依据做归属判定，实际计数已过时导致误判
  - 对 temp/ 内部记忆等非模块目录一刀切处理：要么全部生成文档造成 orphan，要么静默跳过无判定留痕
source_sessions: [ses_e48b8e01dffeFrd2wwOBkoqJtt]
project: Date
severity: medium
quality_score: 87
hit_count: 6
last_hit_at: 2026-11-11T09:35:17
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-08-wiki-section-revision-patch-json-mode, 2026-11-08-wiki-update-script-behavior-contract-blindspots, 2026-11-06-verify-before-write-knowledge-docs, 2026-11-06-doc-repo-zero-extraction-knowledge-gen, 2026-11-08-ghost-reference-path-precheck]
---

# Wiki 增量更新中 unmatched 变更文件的三级归属判定

## Scenario

对既有 Wiki（progress.json + wiki-index.json + 两维度目录）执行增量更新：state.json 报告 21 个变更文件（19 added / 2 modified / 0 removed），reverse_lookup 只直接命中少量受影响文档，剩余约 20 个 unmatched 文件需要逐个判定归属。约束：不重跑全量生成，判定结果直接决定本次修订面（哪些文档进 S2 修订、哪些文件显式跳过），判定错误会漏改或制造无主文档。

## Key Signals

- reverse_lookup 输出两类结果：`affected_docs`（小节级命中，含 impact_level 与 affected_sections）与 `changed_files` 全集——两者的差集即 unmatched，是判定的真正输入。
- module_tree 的 `file_count` 停留在全量生成时刻（如 notes=1），与磁盘现状（notes 已 16 篇）严重不符——计数字段只可用作身份标识，不可用作现状依据。
- architecture.json 的 `modules` 数组为空：架构产物没有识别出新模块，意味着"新增目录 → 生成新模块文档"这条路径天然关闭。
- unmatched 中混杂三类性质完全不同的文件：既有模块路径下的新增内容、内部工具目录的运行时产物、临时缓冲目录的过程稿。

## Essence

unmatched 文件的归属判定必须三级收敛，且每级以结构性产物（module_tree、architecture.json、事实源排除清单）为判据而非直觉：第一级用 module_tree 路径包含关系把文件路由进既有模块文档；第二级用 architecture.json 判定是否构成新模块（modules 空 = 无新模块可建，不生成新文档）；第三级对仍无归属的文件按"是否在 Wiki 关注层面"裁定跳过，跳过必须附判定理由（如登记在事实表入库排除清单的 temp/、内部记忆目录 .workbuddy）而非静默丢弃。

## Approach

1. **先做变更规模分级**：统计 changed_files 的 added/modified/removed 计数，与仓库文件总数求占比；低于阈值（本例 21/288≈7.3% < 30%）走常规档，超高占比才考虑重建——这决定后续判定成本预算。
2. **第一级（模块路径匹配）**：读取 progress.json 的 module_tree，凡变更文件路径落在某模块 `path` 前缀下 → 归入该模块对应的 codebase-knowledge 文档做小节修订（本例 17 个 notes/* 全部归入知识库笔记.md）。
3. **第二级（新模块判定）**：不在任何模块路径下的文件，读 architecture.json 的 `modules`；为空则不构成新模块，禁止为孤立目录新建模块文档。
4. **第三级（关注面裁定）**：非模块目录逐类定性——内部工具运行时产物（如 .workbuddy 记忆，且未命中 wiki-index 任何 section_code_paths）按"不在 Wiki 关注层面"跳过；临时缓冲目录（如 temp/）须在事实源（项目事实表入库排除清单）找到佐证后跳过；两类跳过都要在判定结论中留一行理由。
5. **modified 文件单独处理**：命中 wiki-index section_code_paths 的走小节级修订；modified 但不命中任何小节映射的按成因 1（不在关注层面）跳过，不为其强行制造修订。
6. **判定结果落盘**：把"归属→修订面 / 跳过→理由"写入 update_plan（progress.json），后续派工与校验都以它为准。

## Faster Next Time

- ROI：三级判定全部用已存在的结构性产物做判据，20 个 unmatched 一次收敛，无需逐文件人工裁量；漏判/错判的返工集中在派工前而非合并后。
- 快捷信号：unmatched 文件路径前缀与 module_tree 模块 path 做前缀比对即可完成大多数路由；`file_count` 一律不读；temp/ 类目录先查事实源排除清单再定性。
- 反模式：给 architecture.json 未识别的目录新建模块文档（产生 orphan-page）；跳过时不留判定理由（后续校验或复盘无法区分"有意跳过"与"漏判"）；用变更文件数直接等于修订文档数（一对多/多对一路由未拆分）。

## Applicability Boundaries

- 适用：基于 progress.json/wiki-index.json 的派生产物增量更新（repo-simple-wiki-update 类流程）的影响分析环节；一般化到"批量变更文件 → 既有产物文档"的路由判定。
- 不适用：全量首次生成（无 unmatched 问题）；代码仓库的符号级影响分析（需先跑骨架提取，纯文档仓库骨架恒空属正常，见 doc-repo-zero-extraction-knowledge-gen）。
- 相邻分工：本条管"变更文件路由到哪篇文档"；patch-json-mode 条目管"路由确定后小节修订如何产出与合并"，两者衔接不重叠。

## Evidence or Examples

- 源会话 ses_e48b8e01dffeFrd2wwOBkoqJtt（docgen-apply，Date 项目）：changed_files 21 项，affected_docs 4 篇（全部 S2、hash 全 unknown → 走 subagent 修订），unmatched 20 个。
- 第一级实证：17 个 notes/* 新增文件按 module_tree notes 模块路径归入 codebase-knowledge/知识库笔记.md（1 篇 → 16 篇，S2 修订）。
- 第二级实证：architecture.json `modules: []` → temp/* 4 个 SDD 临时稿不构成新模块，不生成文档。
- 第三级实证：`.workbuddy/memory/.../memory.md`（modified，不命中任何 section_code_paths）成因 1 跳过；temp/ 有项目事实表"入库排除项"佐证。
- 收敛验证：修订面确定后 merge 5/5 success、validate_code_links 5/5 passed、build_index 77 个 code_paths 验证通过——判定面无遗漏、无误报。