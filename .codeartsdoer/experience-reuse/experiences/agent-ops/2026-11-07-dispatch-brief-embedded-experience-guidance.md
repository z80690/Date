---
id: 2026-11-07-dispatch-brief-embedded-experience-guidance
title: 派工单内嵌经验库指导段（条目+来源+tier，采用时保留来源的溯源闭环）
category: agent-ops
nature: technique
created_at: 2026-11-07T10:26:32
updated_at: 2026-11-07T17:46:41
tags: [dispatch-contract, experience-reuse, subagent, context-transfer, 溯源]
keywords: [派工单, 经验库指导段, 经验条目注入, 来源保留, tier标注, 溯源闭环, 经验复用, 主子协作, 方法迁移, 产物内回标]
problem_patterns: ["子智能体不知道经验库已有可复用方法，凭空自创流程或重复踩坑", "经验被采用后无产物级溯源，refine 阶段无法核实命中质量", "经验注入不加来源与权威度标注，下游无法判断可信深度"]
source_sessions: [ses_e4c4ab601ffeAcQ27JTLZDUpL8]
project: Date
severity: medium
quality_score: 90
utility_score: 95
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-07-dispatch-brief-embedded-fact-pack, 2026-11-06-spec-to-tasks-decomposition-pipeline, 2026-11-07-sdd-spec-to-tasks-coverage-mapping, 2026-11-07-stage1-evidence-baseline-and-halt-reporting, 2026-11-07-stage-gate-split-table-rework-degrade]
---

# 派工单内嵌经验库指导段（条目+来源+tier，采用时保留来源的溯源闭环）

## Scenario

主代理向隔离会话的子代理（spec-task-agent 等）派工 SDD 中间阶段任务。子代理无法访问主代理会话中的经验库检索结果；若派工单只给任务目标，子代理要么凭空自创流程（重复踩坑），要么花时间重查经验库。经验库中已有命中条目（如 spec→tasks 拆解流水线、门禁编号切分、覆盖编号组织）时，需要一种低噪声方式注入派工单。

## Key Signals

- 派工单正文出现"经验库指导（实际采用时保留来源）"专段，每条格式为"方法名：一句话执行要求（来源：<经验 id>，tier=X）"。
- 下游产物中显式回标来源（如"按经验库'覆盖编号组织'方法……符合经验库 <id>"），说明注入被实际采用且溯源链在产物内闭环。
- 经验条目带 tier 标注，下游可自行判断权威度并决定采用深度。

## Essence

事实包迁移"实证基线"（是什么），经验指导段迁移"方法"（怎么做）——两者是派工单上下文注入的互补双通道。经验指导段的三个关键设计：①只注入与本次任务相关的命中条目（控制信噪比）；②每条带来源 id 与 tier（下游可复核、可判权威度）；③"实际采用时保留来源"义务让经验溯源链在下游产物中闭合——产物内回标成为经验命中的可审计证据，为后续经验 refine 提供真实命中样本（命中质量可核实），而非仅靠 hit_count 计数。

## Approach

1. **派工单模板增设专段**："经验库指导（实际采用时保留来源）"，置于任务要求之后、项目硬约束之前。
2. **按相关性挑选条目**：取 2~4 条与本次任务强相关的命中经验，每条一行"方法名：执行要求一句话（来源：<经验 id>，tier=X）"；不相关条目一律不注入。
3. **明示采用义务**：写明"实际采用时保留来源"——要求下游在产物引用处标注经验 id，形成产物级溯源。
4. **下游执行侧纪律**：采用则按条目执行并在产物对应位置回标来源；不适用则不采用、不必声明（避免为留痕而留痕）。
5. **派工前刷新**：确认注入条目仍与当前任务形态匹配（规格结构、阶段类型变化时更换条目）。

## Faster Next Time

- 派工前检索经验库一次，命中即按模板注入；零命中则整段省略，不硬凑。
- 警示信号：下游产物出现与注入经验相悖的自创流程，或产物内无任何来源回标——检查采用义务是否在派工单中明示。
- 与事实包段配合使用：事实=基线结论（防重调研），经验=方法路径（防自创流程），两段并列、不混写。

## Applicability Boundaries

- 适用：主→子智能体 Task 派工（隔离会话）；经验库已有结构化条目且与任务强相关的场景。
- 不适用：同一会话直接协作（经验已共享，注入是噪声）；经验库无相关条目或条目与任务形态错配时。
- 边界：注入的 tier 是创建时初始等级，不代表经生命周期验证的 utility；来源保留义务依赖派工单明示，未明示时产物溯源可能缺失。
- 平台标注：实证于 CodeArts（码道）平台主子智能体派工机制；注入结构为通用 Agent 模式，可迁移至其他平台。
- 相邻经验边界：2026-11-07-stage-gate-split-table-rework-degrade 是本条注入条目"门禁编号切分"在 tasks 阶段的强化落地版（三要素+降级规则+只读任务支线化）；本条独有点是派工单注入通道与产物级溯源闭环，互补不重叠。

## Evidence or Examples

- 来源会话：ses_e4c4ab601ffeAcQ27JTLZDUpL8（2026-11-07，Date 项目 P001 spec_workflow_visual 编码任务规划派工）。
- 派工单注入段摘录：①spec-to-tasks 分解流水线——任务须映射能力编号 + EARS 验收对照，可判定（来源 2026-11-06-spec-to-tasks-decomposition-pipeline，tier=A）；②门禁编号切分——每门禁写明放行条件与未过后果（来源 2026-11-06-constraint-dispatch-to-ears-gated-spec）；③覆盖编号组织——任务逐项映射需求点 ①~⑥，防漏防编造（来源 2026-11-07-stage1-evidence-baseline-and-halt-reporting）。
- 采纳溯源实证：下游产物出现"按经验库'覆盖编号组织'方法，将 spec.md 核心能力编成显式清单""全部基于本轮批量并行实查（符合经验库 2026-11-07-stage1-evidence-baseline-and-halt-reporting）"等回标，注入条目均被实际采用。