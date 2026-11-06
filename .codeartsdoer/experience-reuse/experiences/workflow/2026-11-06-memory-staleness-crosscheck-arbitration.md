---
id: 2026-11-06-memory-staleness-crosscheck-arbitration
title: 记忆引用前与规则/知识库交叉核验，仲裁顺序写死（规则>最新知识库>记忆>推断）
category: workflow
nature: decision
created_at: 2026-11-06T20:46:59
updated_at: 2026-11-06T20:55:56
tags: [记忆过时, 三层协同, 仲裁顺序, 交叉核验, 修正优先]
keywords: [记忆vs知识库, 记忆vs规则, 核验日期, 新者胜, 一致性检查, 记忆让位, 人层面, 项目事实, 过时信号, 裁决顺序]
problem_patterns: [自动提炼的记忆条目落后于规则文件或知识库现状仍被引用, 记忆偏好与知识库文档要求冲突时不知信哪个, 记忆清理时分不清该修正还是该删除]
source_sessions: [ses_e4f5c5a83ffefUFnzHFvOEFJCW]
project: Date
severity: high
quality_score: 92
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-06-design-stage-self-serve-evidence-decisions, 2026-11-06-dispatch-order-conflict-gating, 2026-11-06-platform-memory-file-inventory-channel]
---

# 记忆引用前与规则/知识库交叉核验，仲裁顺序写死

## Scenario
多阶段规格流水线中需引用历史记忆指导当前行为；工作区同时存在三层信息源：规则文件（用户界面创建）、知识库文档（带核验日期维护）、平台记忆（Agent 自动提炼，无核验日期强制）。

## Key Signals
- 引用前实查发现记忆条目仍写"七节稿待粘贴、五条仍生效"，而规则 .mdc 与 metadata.properties 实查均为七节已生效（triggerType=always）——记忆落后现状至少一个阶段。
- 记忆中出现"待粘贴 / 待确认 / 进行中"字样即为过期高危信号。

## Essence
记忆是三层信息源中最软的一层：自动提炼、无核验日期强制、可能整段过时。矛盾时的裁决顺序应写死：**规则文件 > 知识库最新文档（核验日期新者胜）> 记忆偏好 > 自行推断**。记忆清理遵循"修正优先于删除"；记忆只保留"人"层面结论（偏好、教训），项目事实归知识库（判据："换个项目还成立吗"）。

## Approach
1. 引用记忆前做一次交叉核验：记忆断言 vs 规则文件现状（读 .mdc/metadata）vs 知识库最新文档（按核验日期取新）。
2. 判定矛盾类型：记忆↔规则 / 记忆↔知识库（含"过时"子类）/ 记忆↔规则+知识库双冲突。
3. 按裁决顺序执行：服从规则并标记待修订呈报；信知识库并将记忆进清理队列；不采信过时记忆。
4. 记忆修正遵循"修正优先于删除"：改写为现状描述，保留原教训的合理内核。
5. 定期（如夜间反思窗口）加入"记忆 vs 知识库一致性检查"环节。
6. 用"换个项目还成立吗"判据决定条目留在记忆还是迁入知识库。

## Faster Next Time
- 引用记忆的固定前置动作是"规则文件秒级实查"，成本极低、可避免整条错误决策链。
- 发现记忆过时立即改写，不让同一条过时记忆被后续会话反复引用。
- 记忆含"待粘贴/待确认/进行中"字样即触发核验，不等矛盾爆发。

## Applicability Boundaries
- 适用：规则、记忆、知识库三层并存的 Agent 工作区；引用历史记忆指导当前决策的场景。
- 不适用：记忆与现状无法交叉验证（无规则文件或知识库）时——此时记忆只能降级为线索而非依据；用户明确要求以记忆为准的场合。

## Evidence or Examples
- 实例：记忆 collab-rules-and-m1-ruling 称规则"五条仍生效、七节稿待粘贴"；实查 `项目协作公约.mdc` 七节齐全且 metadata.properties 已注册 triggerType=always → 判定记忆过时，按仲裁顺序以规则文件为准。
- 该实例作为三层协同机制设计（T2 类矛盾）的实证，登记为待用户确认的记忆修正项；极端测试三场景（记忆偏好 vs spec 要求 / 假设规则禁自启 vs 旧 spec / 记忆"Obsidian 失败" vs 知识库"已可用"）均按写死顺序仲裁通过。