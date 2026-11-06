---
id: 2026-11-06-terminal-gates-in-task-dependency-graph
title: 任务依赖图中的收尾门禁编排（验证后才固化、提交必为末位）
category: workflow
nature: technique
created_at: 2026-11-06T20:16:59
updated_at: 2026-11-06T20:24:59
tags: [gating, task-graph, commit-discipline, workflow]
keywords: [门禁, 归档时机, 提交末位, 依赖图, 串行收尾, 并行编组, 放行条件, 封存, 测试后归档, gating, irreversible actions, commit discipline]
problem_patterns: ["验证不充分即执行归档或提交等固化动作", "门禁条件散落在约束文字中未进入任务依赖"]
source_sessions: [ses_e4f3dbe70ffeQ2k0pNEQHUQilW]
project: Date
severity: low
quality_score: 82
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: A
related_experiences: ["2026-11-06-dispatch-order-conflict-gating", "2026-11-06-spec-to-tasks-decomposition-pipeline"]
---

# 任务依赖图中的收尾门禁编排（验证后才固化、提交必为末位）

## Scenario
多任务流水线中存在不可逆或难以回退的收尾动作（档案归档、版本提交、发布）。此类动作若排在依赖链中段、或无显式门禁放行，会在验证不充分时产生脏归档与违规提交。

## Key Signals
- 任务清单中同时出现"验证类任务"（测试/审查）与"固化类任务"（归档/提交）；
- 协作公约对提交有门禁要求（如精确暂存、提交前过门禁）；
- 拆解产物以依赖图表达任务顺序。

## Essence
把门禁从"约束文字"升级为"依赖图显式节点"：每个收尾动作前置一个门禁节点，门禁未过则相关任务全部封存。验证类任务全部完成后才允许固化类任务启动，固化动作之间也强制串行（归档先于提交，提交必为末位）。

## Approach
1. 盘点收尾动作，按不可逆程度确定串行顺序（归档 → 提交，提交永远末位）；
2. 为每个收尾动作定义显式门禁节点并写清放行条件（如"测试报告通过放行归档""提交门禁项全部通过放行提交"）；
3. 门禁未过时的处置写进任务描述：相关任务零写入、状态标"封存中"；
4. 与收尾链无依赖的任务并行编组（记法：(3,4)∥(5,6)）压缩总周期，但编组不得横跨门禁节点；
5. 汇报时单独列出全部显式门禁位置，供用户复核放行点。

## Faster Next Time
- 判别口诀：动作不可撤销（归档、提交、删除、发布）→ 必须有门禁节点 + 末位串行；
- 评审拆解产物时先看门禁位置再看任务内容；
- 并行编组只放在门禁之前的区段，避免并行任务互相踩到放行条件。

## Applicability Boundaries
- 适用：含"验证→固化"链条的多任务拆解；有提交纪律/门禁公约的项目；
- 不适用：纯只读任务（审查、盘点）无需门禁；单步任务直接执行；门禁条件未定义时先向用户确认放行标准，不得自造门禁。

## Evidence or Examples
- 来源会话：ses_e4f3dbe70ffeQ2k0pNEQHUQilW（2026-11-06，Date 项目 kb_maintenance 任务规划阶段）；
- 实际编排：依赖主线 1→2→(3,4)∥(5,6)→7→8→9→10；两处显式门禁——任务 7 技能测试（1 正 1 反 ×5）报告通过方放行任务 8 派工单归档，任务 9 首次提交前置"精确暂存、入库清单呈批、提交门禁三项"；
- 关联公约：项目协作公约第四条"禁全量暂存，精确暂存，提交前过门禁"。