---
id: 2026-11-07-sop-event-nesting-sequence-diagram-hard-order
title: 四步主干×考核事件嵌套链在 design 层补时序图：sequenceDiagram 全嵌套+图下硬序约束条款，防编码偏序
category: workflow
nature: technique
created_at: 2026-11-07T23:41:56
updated_at: 2026-11-07T23:41:56
tags: [sequence-diagram, event-nesting, design-stage, coding-drift-prevention, gate-loop]
keywords: [时序图, 嵌套顺序, 硬序约束, 唯一唤醒信号, 门禁回环, sequenceDiagram, 事件箭头, 四步SOP, 编码偏差, 分支出边]
problem_patterns: [spec 已条款化触发时机但 design 层无时序图，多段 SOP 与异步事件嵌套时实施者按直觉排序导致先后关系偏离条款, 时序图画了主干和事件链但门禁分支（达标/不达标回环）画成普通流程分支，出现"门禁不过仍继续"的错误出边, 时序图无配套文字约束，图与条款两处口径不一致时无仲裁依据]
source_sessions: [ses_e49654e32ffewFPnJSiwmXkHvn]
project: Date
severity: medium
quality_score: 82
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: A
related_experiences: [agent-ops/2026-11-07-event-trigger-timing-clause-pattern, workflow/2026-11-07-rejection-reasons-to-revision-actions-mapping, agent-ops/2026-11-06-codeartsdoer-event-trigger-channel-inventory]
---

# 四步主干×考核事件嵌套链在 design 层补时序图：sequenceDiagram 全嵌套+图下硬序约束条款，防编码偏序

## Scenario

spec 已把子智能体触发时机条款化（唯一唤醒事件+场景枚举+三禁+移交分支，R1–R7），但进入 design 层时出现新问题：主干是多段 SOP（建需求→建设计→建任务→执行），每段内部又嵌套子智能体事件链（出题→作答→批改→置信度分支回环）。仅凭条款编号，实施者仍可能在编码时排错嵌套先后（如批改未完成就推进主干下一步、门禁不过仍继续往下走）。用户在审阅 design.md 时明确提出："四步 SOP 与事件的嵌套顺序，是否需补一张时序图确保编码不偏？"

## Key Signals

- spec 层已有触发时机条款（R 编号），但 design 层没有可视化的嵌套顺序表达——条款是"规则集合"，不是"时间线"。
- 流程含门禁分支与回环（置信度 ≥80% 进下一门 / <80% 重发上游事件）——分支语义若只写在条款里，画图时最易出错。
- 用户疑问中出现"嵌套顺序""先后关系""确保编码不偏"字样——这是要求把条款顺序转译为可照抄的执行时间线。

## Essence

条款解决"可判定性"，时序图解决"顺序可视化"——两者是互补层而非重复层。design 层时序显式化的固定两件：

1. **全嵌套 sequenceDiagram**：一张图覆盖"会话启动→主干四步（标注各步内嵌的子智能体调用点）→考核事件链全环（出题事件→出题官 SOP→完成事件→作答归档→完成事件→批改官 SOP→完成事件）→置信度分支（达标/回环重发上游事件）"。事件箭头与四步推进的先后关系必须逐条对齐 spec 触发时机条款（R1–R7），不得自创新顺序。
2. **图下硬序约束条款**：图本身不承载判定语义，须在图下附文字条款把关键时序约束写死——"批改官唯一唤醒信号=作答完成事件""门禁不过无'未过继续'出边，回环只能重发上游事件""主干某步的门禁未过不得进入下一步"。图与条款不一致时以 spec 条款为准仲裁。

## Approach

1. 从 spec 提取触发时机条款全集，列事件清单与四步主干各步的子调用点，形成"节点-箭头"底稿。
2. 画 Mermaid sequenceDiagram：参与者=主智能体/各子智能体/门禁；按时间轴排全嵌套；门禁分支用 alt/else 表达，回环箭头显式指回上游事件发布点。
3. 逐箭头核对 spec 条款编号：每个事件箭头旁可标注对应 R 条款，对不上的箭头即设计越权，删除或回 spec 修订。
4. 图下写硬序约束条款（每条一句话、可判定）：唯一唤醒关系、无继续出边、回环只走事件、步间门禁绑定。
5. 修订摘要中把时序图列为独立落点，声明"事件箭头与四步推进先后关系与 spec 5.x R1–R7 一致"，供审阅者按条款抽查。

## Faster Next Time

- 画图前先列"事件→R 条款"对照行，画完逐行核销——图的正确性核验从通读比对降为逐行对号。
- 固定硬序约束三条起步：唯一唤醒信号、门禁不过无继续出边、回环只重发上游事件——三条缺一，嵌套图必有歧义。
- 反模式：把门禁回环画成流程图式"不通过→重试"自循环（变相轮询，违反事件驱动公约）；只画主干不画嵌套事件链（链条断头，实施者靠猜）；图与条款各自表述不一致且无仲裁声明。

## Applicability Boundaries

- 适用：门禁式多智能体协作链、主干 SOP 与异步事件嵌套、spec 已条款化触发时机而 design 需防编码偏序的场景；事件驱动公约（禁定时/禁轮询）下回环语义必须显式。
- 不适用：线性单代理流程（无嵌套无分支，画图纯开销）；spec 尚未条款化触发时机时（先做条款化，再画图，顺序不能反——否则图没有对齐基准）。
- 边界：时序图是 design 层防偏序手段，不替代 spec 条款的判定效力；图的颗粒度到"事件箭头+调用点"即可，不展开到子智能体内部 SOP 细步（那属于各 SOP 文档）。

## Evidence or Examples

- 来源会话：ses_e49654e32ffewFPnJSiwmXkHvn（2026-11-07，Date 项目 sdd_agent_refactor design.md v2，疑问4 修订）。
- 落点：design.md 新增 §2.1.3-8 端到端时序图——Mermaid sequenceDiagram 覆盖"会话启动→四步主干（含 C1/C3/C4 调用点）→E1→S1 出题官六步→E2→主智能体作答归档→E3→S2 批改官六步→E4→置信度分支（≥80% 进 M3／<80% 回环 E1 重考）"，图下附 7 条硬序约束（含"批改官唯一唤醒=作答完成事件 E3""门禁不过无'未过继续'出边"），事件箭头先后关系对齐 spec 5.6 R1–R7 与 5.5 R5。
- 效果佐证：用户疑问4 原文点名"嵌套顺序……确保编码不偏"，修订后该疑问随修订摘要逐条闭合；头部修订说明、追溯表同步更新该落点。