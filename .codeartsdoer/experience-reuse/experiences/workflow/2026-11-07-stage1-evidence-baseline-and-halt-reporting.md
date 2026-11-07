---
id: 2026-11-07-stage1-evidence-baseline-and-halt-reporting
title: 多阶段流程第一阶段的产出纪律：实查基线固化 + 三段式停驻呈报
category: workflow
nature: methodology
created_at: 2026-11-07T06:27:00
updated_at: 2026-11-07T22:28:41
tags: [SDD, 门禁, 呈报, 证据基线, 阶段停驻]
keywords: [第一阶段, 证据基线, discovery基线, 停驻呈报, 结论前置, 已实查声明, 非编造, 多轮沟通, 阶段门禁, 派工单, 反编造, 单一事实源]
problem_patterns: [第一阶段派工内嵌大量声称已核实的事实且禁反问，不知哪些能直接采信哪些必须实查, 产出第一阶段文档后"要不要顺手继续做下一阶段"的停驻点被忽略或处理成反问, 呈报只有产出摘要没有证据声明，用户无法判断结论是实查所得还是编造]
source_sessions: [ses_e4d11ce50ffesKQFm6qpmDfFP0]
project: Date
severity: medium
quality_score: 86
utility_score: 97
hit_count: 8
last_hit_at: 2026-11-08T01:01:30
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-06-verify-claimed-prerequisites-before-research, 2026-11-06-dispatch-order-conflict-gating, 2026-11-06-voice-dispatch-requirement-normalization, 2026-11-06-annotated-incremental-revision-grep-verify, 2026-11-07-stage-gate-split-table-rework-degrade, 2026-11-07-claimed-count-vs-fact-source-conflict]
---

# 多阶段流程第一阶段的产出纪律：实查基线固化 + 三段式停驻呈报

## Scenario

多阶段规范驱动流程（SDD 等）中，执行代理接到第一阶段派工：派工单内嵌一份"已核实事实"清单供调研基线，同时带硬门禁——"产出第一阶段文档后必须停下呈报，等用户多轮沟通确认，未确认禁进下一阶段"；项目规则又禁止反问。三个约束叠加时容易两头出错：要么把派工单事实直接抄进文档（前提未自证），要么产出后不知如何体面停驻（继续做违反门禁、停下又像反问）。

## Key Signals

- 派工单含"已核实事实/discovery 基线"段落，但无逐条证据指针。
- 门禁条款与"禁反问"并存，看似冲突。
- 需求点分散在派工单多条叙述里（本次为①~⑥六大项），存在漏覆盖风险。

## Essence

第一阶段产出的可信度取决于证据基线而非文档措辞；停驻本身是门禁的自执行动作，不是反问。有效路径 = 并行实查交叉核验 → 固化 discovery 基线并显式落盘 → 三段式呈报（结论前置概要 + 已实查基线声明 + 明确停驻点）。"已实查基线（非编造）"声明把采信依据交还给用户，"当前停在 X 阶段、确认后才放行"把决策权显式归还用户——两者都不构成反问。

## Approach

1. 一轮批量并行实查：把派工单"已核实事实"逐条对应到本地锚点（单一事实源文件、配置文件、目录实存性、平台工具输出），一次并行调用完成，不逐条串行核对。
2. 固化基线：实查通过项写入产出文档的显式小节（如"本轮已实查基线"），未核验项标"待查"，绝不混写；实查结果与派工单声称冲突时不擅自采信任一侧，按口径冲突仲裁通道处置（见 related 2026-11-07-claimed-count-vs-fact-source-conflict）。
3. 覆盖编号组织：把派工单需求点编成显式清单（①~⑥），产出文档逐项映射，防漏防编造；含硬性核查要求的（如"案例禁编造、不足即降级"）写成验收条款。
4. 三段式呈报：a) 结论前置概要（≤300 字，逐项点出产出覆盖什么）；b) "本轮已实查基线（非编造）"清单（列证据来源：工具输出、文件实存）；c) 停驻声明（当前阶段 + 每轮意见→更新→再呈报的循环 + 确认后才放行下一阶段）。
5. 停驻即收尾：呈报发出后不再执行任何下一阶段动作，等待用户确认事件。

## Faster Next Time

- 实查一轮并行完成，避免逐条核对的串行开销。
- 基线小节可被后续阶段直接活引用，免得每阶段重新核验一遍。
- 停驻声明模板化（当前阶段/放行条件/循环方式三要素），防"顺手做下去"。
- 需求编号清单在动笔前先列，覆盖映射比事后检查省一轮返工。

## Applicability Boundaries

- 适用于显式设定"第一阶段产出即停、等确认"的多阶段流程与强约束派工单。
- 不适用于用户全权授权"一把到底"的场景（该场景走门禁自执行+事实性阻塞才呈报的例外通道，见 related 2026-11-07-full-authorization-self-gated-execution）。
- 不适用于无阶段门禁的常规任务；门禁条款本身仍须按派工单原文转写，不得本经验替代。
- "已实查基线"声明只列本次实查确有证据的项；派工单声称但本次未实查的项必须归入"待查"，禁止搭车声明。

## Evidence or Examples

- 本会话（ses_e4d11ce50ffesKQFm6qpmDfFP0，spec-requirement-agent 子智能体执行）：Phase1 glob 唯一性检查（specs/ 不存在→无命名冲突）→ Phase2a 单轮并行实查项目事实表、注册表、阶段状态机规则、mem-exp-config.json、experience 库结构、listSkills 平台清单 → Phase2b spec.md 一次成型落盘 → Phase2c 三段式呈报并停驻在需求阶段。
- 呈报原文结构：六章节覆盖概要（对应派工①~⑥）→ "本轮已实查基线（非编造）"（listSkills 50 技能实证、注册表 12 挂载项、H1–H7 触发表、经验库目录结构）→ "请审阅……确认后才会进 design，当前停在需求阶段"。
- 效果：write 一次成功无返工，呈报后主动停驻未触发任何下一阶段动作，多轮沟通循环已显式建立。