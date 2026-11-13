---
id: 2026-11-12-grader-finish-and-exit-execution-loop
title: 批改官"完成即退"的落盘验证与事件流水执行闭环及 PARTIAL 触发判据
category: agent-ops
nature: methodology
created_at: 2026-11-12T22:54:46
updated_at: 2026-11-13T00:09:37
tags: [批改官, 完成即退, 落盘验证, 事件流水, PARTIAL判据]
keywords: [grader, 批改官, 完成即退, 落盘验证, 双验证, 事件流水, events.md, 事件行, PARTIAL, 触发条件, key显式定义, 口径漂移, 摘要格式, 禁复述key, 门禁证据链]
problem_patterns:
  - 批改官写完报告即返回，未验证文件存在非空、未向事件流水追加完成事件行，门禁证据链断裂
  - 批改时凭"感觉缺了点东西"对作答降档 PARTIAL，判据未锚定 key 显式条件导致口径漂移、PARTIAL 异常偏高
  - 批改返回摘要复述 key 答案内容，判分标准经摘要链路泄露给作答方
source_sessions: [ses_e3047a7f0ffe5D9A7OCo4P61Jy]
project: Date
severity: low
quality_score: 87
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [agent-ops/2026-11-07-worker-grader-exam-gate-pattern.md, workflow/2026-11-07-independent-exam-grading-rubric.md, agent-ops/2026-11-08-examinee-key-contact-disclosure-independence.md, agent-ops/2026-11-08-examiner-precheck-evidence-parallel-audit.md, agent-ops/2026-11-07-write-receipt-not-proof-of-persistence.md]
---

# 批改官"完成即退"的落盘验证与事件流水执行闭环及 PARTIAL 触发判据

## Scenario

- 通用多代理考核流程：独立批改官（grader subagent，与出题方/作答方上下文隔离）受派工执行一轮考核批改，派工契约约定"完成即退"（禁改题目/key/作答三件、禁出题、禁作答）。
- 典型触发：主智能体按"先流水记行后派工"契约维护 events.md 事件流水，批改官是流水中的执行者之一；批改报告是门禁放行的唯一证据文件。
- 规模参考：5 题/50 题量级语义作答，逐题三值判定（PASS/PARTIAL/FAIL），每题固定分值折算综合自信度。

## Key Signals

- 批改官写完报告后直接返回摘要——无落盘验证时，"写成功回执"≠"文件确实存在非空"，门禁证据可能断链；
- 派工单出现"落盘后用列目录+读文件验证存在非空，验证结果写入返回摘要"——验证被显式写进契约，是闭环必须执行的信号；
- 作答卷缺了某个细节要点，批改官犹豫是否降 PARTIAL——若凭"感觉缺了点东西"降档，PARTIAL 会异常偏高（批改官擅自收紧了口径）；
- 批改摘要若复述 key 答案内容，判分标准会经摘要链路泄露。

## Essence

"完成即退"不是"写完就走"，而是一个固定执行闭环：**判定 → 落盘 → 双验证 → 流水留痕 → 机械可核对摘要**。三条纪律支撑：

1. 落盘必须双验证（列目录看字节数 + 读文件看内容），验证结果写进返回摘要，成为门禁证据链的一环；
2. 批改官是事件流水的执行者，完成后必须向 events.md 追加自己的完成事件行（编号顺延/时间/事件/执行者/产物状态），保持"先流水记行后派工"契约的对称性；
3. PARTIAL 只能由 key 显式定义的缺项触发（key 判分依据里写明"PARTIAL=缺什么"才可降档），单项细节缺失而主体语义已覆盖时不降档——判据锚定在 key 文本，不锚定在批改官感觉。

## Approach

1. 完整读取批改包三件（questions/key/answers），前置自检：三件齐备、题号一一对应、key 未混入题目/作答文件、作答覆盖率 100%（独立于质量的第一道门禁）。
2. 逐题三值判定，仅援引 key：每题给判定三值/得分/一句判分依据（引用作答卷原文短语作证据）/来源指针；判 PARTIAL 前先对照 key 显式 PARTIAL 条件，不在条件内即不降档。
3. 落盘批改报告，固定结构：头部（轮次/判分口径/独立性声明/接触范围声明如实转录/红线核验记录）→ 逐题判定表 → 得分汇总与自信度算式 → 门禁二值结论 → 遗留改进项。
4. 落盘后双验证：列目录确认文件存在且字节数非零 + 读文件确认内容可读；把验证结果写进返回摘要。
5. 向事件流水文件追加完成事件行（编号顺延、执行者=批改官、产物与状态），再返回。
6. 返回摘要 ≤200 字、结论前置：逐题三值分布 + 总分/满分 + 自信度% + 门禁二值结论；禁复述 key 答案内容。

## Faster Next Time

- 把本闭环六步直接写进批改官派工契约（尤其"列目录+读文件验证存在非空，验证结果写入返回摘要"一句），批改官照单执行，无需每次重新约定收口方式；
- 警示信号：批改返回摘要缺"验证结果"或"三值分布"任一项 → 视为闭环未完成，主智能体打回补记；
- PARTIAL 异常偏高时，先查是否违反"key 显式条件才降档"，再怀疑作答质量（与 rubric 经验的口径漂移警示互补）；
- 摘要格式固定为"三值分布+总分+自信度%+门禁二值"，主智能体可机械核对门禁，不重跑批改过程。

## Applicability Boundaries

- 适用：有参考 key 的考核批改轮（grader subagent 独立上下文）、主智能体维护事件流水的 spec 流程、门禁结论需证据留痕的多代理协作。
- 不适用：代码类产出（跑测试即验证，无需批改报告闭环）；无事件流水契约的自由任务（第 5 步跳过）；批改官与主智能体同上下文的自判场景（先修架构，见关联经验）。
- 前提：判分口径、分值折算、门禁阈值由派工契约预先冻结，批改官只执行不制定标准。

## Evidence or Examples

- 实例（2026-11-12，P003 G0 考核轮 R1，ses_e3047a7f0ffe5D9A7OCo4P61Jy）：批改官六步闭环执行——前置自检 5/5 作答覆盖率 100%；逐题判定 PASS×5；review-report.md 落盘 6197 B/40 行；列目录验证（questions 4340 B / key 8281 B / answers 10003 B / review-report 6197 B）+ 读文件复核后把结果写入摘要；向 events.md 追加 E4 完成事件行；摘要"PASS×5/PARTIAL×0/FAIL×0、100/100、自信度 100%、门禁=放行"≤200 字且未复述 key。
- PARTIAL 判据实例：题 5 作答缺"Docker 更新只换程序不换镜像"细节，但 key 的 PARTIAL 条件为"处置或开关理由缺一"，不在条件内 → 判 PASS 不降档，仅在遗留改进项记录"可补 Docker 更新机制细节，不阻塞"。