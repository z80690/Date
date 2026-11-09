---
id: 2026-11-06-constraint-dispatch-to-ears-gated-spec
title: 强约束派工单的需求规格化：硬约束转 EARS 条款与编号门禁
category: workflow
nature: methodology
created_at: 2026-11-06T21:56:59
updated_at: 2026-11-06T21:56:59
tags: [workflow, requirement-spec, ears, gating, hard-constraints]
keywords: [派工单, 硬约束, EARS, 门禁, 需求规格, 负分纠偏, 验收条款, 阶段确认, SDD, 红线]
problem_patterns: [强约束派工单直接照抄进规格导致后续阶段无法验收, "禁反问"与"阶段确认"两种要求冲突不知如何兼容, 顺序依赖要求散落在约束叙述中未成为显式门禁]
source_sessions: [ses_e4ee545ecffetg5iXD9Tdm4vgS]
project: Date
severity: medium
quality_score: 84
hit_count: 10
last_hit_at: 2026-11-08T23:47:22
low_quality_hit_count: 0
tier: A
related_experiences: [2026-11-06-voice-dispatch-requirement-normalization, 2026-11-06-dispatch-order-conflict-gating, 2026-11-06-terminal-gates-in-task-dependency-graph]
---

# 强约束派工单的需求规格化：硬约束转 EARS 条款与编号门禁

## Scenario
用户以"派工单"下达含大量硬约束与纠偏语义的任务（如"负 100 分起步""不许反问""不许自判学会""不删文件""不新建目录""先考核修复再设计，经确认后实施"），并要求按 SDD 产出需求规格。此类派工单的约束散落在任务叙述、红线清单、执行环境备注多处；规格阶段若只做内容搬运，design/tasks/实施阶段会丢失约束或无法验收。

## Key Signals
- 派工单出现"负分纠偏""禁反问""禁自判"等约束执行行为本身（而非仅约束产出）的语义；
- 顺序依赖（先 X 后 Y）以叙述句存在，未编号、无通过标准；
- 红线以"不许/禁止/严禁"句式在多个章节重复出现，存在遗漏风险。

## Essence
硬约束的价值在后续阶段兑现：必须逐条转译为可判定的 EARS 验收条款，并把顺序要求升级为编号门禁（通过标准 + 未过后果）。"禁反问"与"阶段确认"并不冲突——反问是对模糊处的自问自答（执行层禁止），确认是阶段产物呈报用户拍板（保留有限个门禁确认点）。在 spec 中显式写明保留几个确认点，后续代理就不必在两难中自行取舍。

## Approach
1. 约束盘点建索引：通读派工单全文，把所有约束/红线/顺序要求按原文分章逐条编号（如①–⑤），确保零遗漏；
2. 约束→条款翻译：每条约束写成 EARS 句式（When/While/Where + 系统行为），附可判定的验收标准，禁止原句照抄；
3. 门禁编号切分：按时间/依赖顺序切为编号门禁（前置考核门 → 设计门禁 → 规则门禁 → 流程门禁），每门禁写明放行条件与未过后果（任务封存/禁止进入下一阶段）；
4. 确认点显式化：在 spec 中写明"执行层禁反问，仅保留 N 个门禁确认点"，逐个列出确认点位置；
5. 数据约束章定义可验证字段（考核记录、草稿、环境登记、产物的字段契约），供后续阶段核验；
6. 摘要呈报：结论前置、限定字数（如 ≤300 字），列出门禁全景，等待用户确认后再进入下一阶段。

## Faster Next Time
- 先做"约束→条款"对照清单再写正文，对照清单本身就是查漏工具；
- "禁反问"类指令必须配"确认点白名单"，否则后续阶段会因不敢确认而卡死，或因擅断而违规；
- 反模式：把红线原句复制进 spec 不做条款化；把门禁写成"应当"式软建议；为凑覆盖数把常识写成条款。

## Applicability Boundaries
- 适用：含强约束/纠偏语义/顺序依赖的派工单，SDD 流水线的需求规格阶段，单用户强确认文化；
- 不适用：松散探索性任务（门禁是纯开销）；用户未定义约束的常规小需求；已高度结构化且无行为约束的书面需求（常规规格化即可）。

## Evidence or Examples
- 来源会话：ses_e4ee545ecffetg5iXD9Tdm4vgS（2026-11-06，Date 项目，spec-requirement-agent）；
- 实例：负 100 分纠偏派工单（架构重构前置考核）转化为 `.codeartsdoer/specs/kb_arch_foundation/spec.md`，6 章结构覆盖派工单①–⑤全部要求；门禁编号 M1–M7（前置考核 M1–M4 → 架构设计 M5 → 规则草稿 M6 → SDD 永久生效 M7）；"执行层禁反问（仅保留 4 个门禁确认点）"写入硬约束条款章；
- 证据强度说明：spec 已落盘（write 成功）但截至采集时点尚待用户确认；方法有效性的旁证是同项目此前 spec（kb_maintenance、pd003_exec）已走通 spec→design→tasks 闭环。