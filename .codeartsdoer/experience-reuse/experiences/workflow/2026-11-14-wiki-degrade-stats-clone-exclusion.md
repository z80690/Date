---
id: 2026-11-14-wiki-degrade-stats-clone-exclusion
title: 降级判定统计先剔除第三方克隆文件集：变更占比与新模块计数清洗后再比阈值，防误触发全量重建
category: workflow
nature: pitfall
created_at: 2026-11-14T11:00:24
updated_at: 2026-11-14T11:18:16
tags:
  - wiki
  - 降级判定
  - 第三方克隆
  - 全量重建
  - 流程纪律
keywords:
  - 降级判定
  - 变更占比
  - 新模块计数
  - 第三方克隆剔除
  - 全量重新生成
  - 误降级
  - 次生损失
  - 文件集清洗
  - state.json 变更检测
  - 伴随加载
problem_patterns:
  - 增量更新的降级判定把第三方克隆大目录全额计入变更占比与新模块计数，双指标"超阈值"误触发全量重新生成，剔除克隆后实际占比远低于阈值本应走增量
  - state.json 变更检测基于文件系统哈希而非 git 跟踪状态，git ls-files 计数为 0 的未跟踪目录（第三方克隆/新自研模块）全额进入 changed_files，用 git 跟踪状态预判变更规模必然失真
  - 误触发全量重建后按新模块树清理 docs 目录，既有树中仍有归属价值的主题文档被当旧残留一并误删，产生索引之外的次生资产损失
source_sessions:
  - ses_e2d2f7062ffe4MwhDPtvKkbwi2
project: Date
severity: high
quality_score: 91
hit_count: 1
last_hit_at: 2026-11-15T15:47:24
low_quality_hit_count: 0
tier: S
related_experiences:
  - 2026-11-11-third-party-repo-clone-vetting-not-a-module
  - 2026-11-12-wiki-zero-revision-round-full-short-circuit
  - 2026-11-09-companion-execution-skill-co-load-before-scripts
  - 2026-11-14-wiki-subagent-artifact-defects-pre-build-index
---

# 降级判定统计先剔除第三方克隆文件集：变更占比与新模块计数清洗后再比阈值，防误触发全量重建

## Scenario

`/repo-simple-wiki-update` 增量更新入口的降级判定节点：阶段 0 读取 state.json 的 changed_files 与仓库总文件数，按双指标判定是否降级为全量重新生成（变更文件占比 > 50%，或新增模块数 > 3）。当仓库混入第三方开源项目克隆大目录（DVWA 类靶场）时，该判定节点被污染。单个执行者、周期性流程。

## Key Signals

- state.json 报 239 个变更文件（238 added / 1 modified），其中 DVWA/ 约 217 文件、adapter/ 约 14 文件，均为"新增"。
- `git ls-files` 核对：DVWA 与 adapter 均未被 git 跟踪（计数为 0）。变更检测器基于文件系统哈希（FileHashDetector unified mode），**git 未跟踪目录全额计入变更集**——不能拿 git 跟踪状态预判变更规模。
- 降级判定输出：239/349 = 68.5% > 50%，新增模块 4+ > 3，双指标同时"超阈值"，触发全量。
- 反事实核算：剔除 DVWA 克隆文件后仅 22/349 ≈ 6.3%，本应走常规增量更新。

## Essence

"第三方开源克隆大目录不建模块、剔除统计"这条裁决的适用面不只在增量更新的 unmatched 归属判定（见关联条目），**在降级判定的一切统计口径（变更占比、新模块计数、档位分档）上同样成立**——克隆文件必须先从文件集清洗掉，再与阈值比较。本例同时暴露根因：经验检索 hook 按关键词注入的条目未覆盖克隆剔除裁决（该裁决锚定在"unmatched 归属"场景词下），执行者又未执行"伴随加载执行适配契约经验/技能"纪律，导致既有裁决失守、同型误判复现。

## Approach

1. 降级判定计算前先清洗变更文件集：把 changed_files 按顶层目录聚合计数，对体量异常的大目录做所有权三查（README 多语言、.github/workflows、CHANGELOG/LICENSE、目录名与知名上游项目同形）。
2. 确认为第三方克隆的目录，从变更占比分子与新模块候选清单中剔除，再重算占比、再数新模块，然后才与阈值（50% / 3 个）比较。
3. 若全量已被误触发：执行重建前对照既有 module_tree 生成"旧残留清理候选清单"，凡属既有树且仍有归属价值的主题/文档移出清理集；清理动作放在 build_index 之前并逐项留痕。
4. 周期性流程开工前，先主动检索并伴随加载该流程的执行适配契约类经验/技能（克隆剔除、零修订短路、runner 执行形态等），勿把检索 hook 的关键词命中当作全部可用经验的保证。

## Faster Next Time

- 预检清单：changed_files 按顶层目录聚合 → 大目录所有权三查 → 剔除克隆 → 重算占比与新模块数 → 再比阈值。
- 警告信号：变更占比"突然超阈值"且新增大目录与知名开源项目同名/同构时，先怀疑克隆混入，而非仓库结构突变。
- ROI：本例误全量重建消耗 9 篇 codebase 文档 + 6 篇规范文档的重新生成与三轮校验，并误删 5 个既有主题文档；清洗后走增量本可只修订极少量文档。

## Applicability Boundaries

- 适用：repo-simple-wiki-update / repo-simple-wiki 的降级判定；任何以"变更文件占比""新增目录数"为分档输入的流程（批次分档、扫描分档、更新档位）。
- 不适用：确为本仓库新增的自研大模块（有构建声明、包入口、符号骨架证据支撑），不得被克隆剔除规则误伤；一次性小仓库无克隆混入风险时可跳过清洗步骤。

## Evidence or Examples

- 本例来源：session ses_e2d2f7062ffe4MwhDPtvKkbwi2（2026-11-13，Date 仓库）。
- state.json：239 changed（238 added / 1 modified）；`git ls-files` 计 DVWA=0、adapter=0、仓库总数 349。
- 降级判定原文记录：68.5% 与"4+ 个新模块"；剔除 DVWA 217 文件后 22/349 ≈ 6.3%。
- 次生损失实证：误删 project-knowledge 下 5 个旧主题目录（business_glossary、codearts_skills_reference、collaboration_conventions、documentation_system、tooling_and_environment）与 codebase-knowledge 下 2 个旧文档。
- 关联裁决：克隆识别与归属的完整判定法见 `workflow/2026-11-11-third-party-repo-clone-vetting-not-a-module`；伴随加载纪律见 `agent-ops/2026-11-09-companion-execution-skill-co-load-before-scripts`。