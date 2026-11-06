---
id: 2026-11-06-independent-examiner-capability-gate
title: "禁自判"能力门禁的角色分离设计：独立评审员代考
category: agent-ops
nature: methodology
created_at: 2026-11-06T21:56:59
updated_at: 2026-11-06T21:56:59
tags: [agent-ops, capability-gate, role-separation, assessment, subagent]
keywords: [禁自判, 旁人出题, 出题官, 批改官, 独立subagent, 能力考核, 门禁, 自信度阈值, 角色分离, 利益冲突]
problem_patterns: [要求"旁人出题、禁自判学会"时单一Agent无法自证达标, 被考核者自出自判使考核门禁形同虚设, 考核标准不量化导致门禁不可判定]
source_sessions: [ses_e4ee545ecffetg5iXD9Tdm4vgS]
project: Date
severity: medium
quality_score: 81
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: A
related_experiences: [2026-11-06-constraint-dispatch-to-ears-gated-spec, 2026-11-06-dispatch-order-conflict-gating]
---

# "禁自判"能力门禁的角色分离设计：独立评审员代考

## Scenario
派工单要求"学不会禁止开工""旁人出题、出题官批改、禁自判学会"——Agent 必须通过能力考核才能进入下一阶段，但 Agent 自出自考存在利益冲突，门禁形同虚设。考核类门禁（知识认证、第三方评审、验收把关）普遍遇到此问题。

## Key Signals
- 约束含"旁人/第三方/禁自判"字样，而执行主体是单一 Agent；
- 通过标准不量化（"学懂了""差不多了"）时门禁不可判定；
- 考核材料本身有获取风险（如网络依赖），材料不可得时门禁会死锁。

## Essence
"旁人"在多 Agent 系统中的等价物是**角色分离的独立 subagent**：出题官、批改官与被考核 Agent 上下文隔离，复刻人类组织的利益冲突隔离。门禁必须同时量化两个参数才可判定：**作答率**（逐题硬标准，如 100%）与**综合自信度阈值**（如 80%）。门禁是放行条件而非软建议：不达标则下一阶段任务封存。

## Approach
1. 角色转译：把"旁人"落为独立 subagent（出题官、批改官），与被考核方无共享上下文，禁止自出自判；
2. 维度拆题：按学习材料（论文/项目）× 审视角度拆分题目维度，每维度固定题量（如 10 题），题量与阈值写入 spec 供用户对齐；
3. 双参数门禁：定义逐题作答率硬标准 + 综合自信度阈值，二者同时满足才放行；
4. 硬性后果：不达标时后续阶段任务全部封存，禁止以"自评已学会"代替考核结果；
5. 材料降级路径：为考核材料（论文/项目）预设获取失败时的降级途径（多渠道、可替代来源），防止门禁死锁；
6. 结果留痕：考核记录写入 spec 定义的可验证字段，作为门禁放行证据。

## Faster Next Time
- 遇"禁自判/第三方验证"类要求，先找"独立 subagent 角色分离"落地方案，不要拒绝执行也不要假装已验证；
- 题量、通过率、自信度阈值三个参数必须显式成文，主观"自信"不可作为门禁依据；
- 反模式：被考核 Agent 自出自判；考核未量化即放行；材料获取无降级路径导致门禁死锁。

## Applicability Boundaries
- 适用：有 subagent/多角色机制的 Agent 平台上的能力认证、评审把关类门禁；单用户强确认文化的工作流；
- 不适用：无 subagent 能力的单角色 Agent（退化为用户人工出题判卷）；非考核类的常规任务（角色分离是纯开销）。

## Evidence or Examples
- 来源会话：ses_e4ee545ecffetg5iXD9Tdm4vgS（2026-11-06，Date 项目，spec-requirement-agent）；
- 实例：派工单"强制学习"条款（5 篇论文多角度 + 5 个项目正反例）落为 `.codeartsdoer/specs/kb_arch_foundation/spec.md` 前置考核门 M1–M4：出题官=独立 subagent、每角度 10 题、100% 作答、出题官批改禁自判、综合自信度 ≥80% 方可进入架构设计（§5.1–5.4）；
- 证据强度说明：设计已写入 spec（write 成功）但考核本身尚未执行，无通过/失败运行数据；"独立 subagent 可担任出题官/批改官"来自派工单执行环境备注，未实测。