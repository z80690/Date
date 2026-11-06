---
id: 2026-11-06-mid-execution-append-subtask-freeze-commit
title: 执行中段收到范围追加：append-only 扩展现有 spec 流程并冻结固化动作
category: workflow
nature: methodology
created_at: 2026-11-06T20:46:59
updated_at: 2026-11-06T20:46:59
tags: [范围变更, 追加子任务, append-only, 冻结提交, 规格流水线]
keywords: [执行阶段, 任务组追加, 设计章节追加, 不新建spec, 变更日志, 未决事项登记, 待确认合并呈批, 门禁冻结, 只增不删, 单一确认点]
problem_patterns: [任务执行中段用户叫停当前流程并追加新任务不知如何续接, 重开 spec 会割裂上下文且违反不跳流程约束, 追加任务期间原提交方案处于悬空状态易被误执行]
source_sessions: [ses_e4f5c5a83ffefUFnzHFvOEFJCW]
project: Date
severity: medium
quality_score: 80
hit_count: 1
last_hit_at: 2026-11-06T23:38:52
low_quality_hit_count: 0
tier: A
related_experiences: [2026-11-06-dispatch-order-conflict-gating, 2026-11-06-terminal-gates-in-task-dependency-graph]
---

# 执行中段收到范围追加：append-only 扩展现有 spec 流程并冻结固化动作

## Scenario
规格流水线（spec→design→tasks→实现）执行到"提交前呈批"节点时，用户叫停入库流程并追加全新设计子任务，附带硬约束：不跳过规范流程、不新建 spec、不改规则文件、不删任何现有文件。范围变化发生在任务执行中段而非阶段边界。

## Key Signals
- 用户指令同时包含"停掉当前流程"+"追加新任务"+"就在当前 spec 流程里追加章节"——续接方式已被限定。
- 原流程存在待执行的不可逆动作（git 提交），与新任务并行推进有误执行风险。

## Essence
执行中段的范围追加不需要重开 spec：以 append-only 方式在现有 tasks.md 增任务组、在 design.md 增章节，同时把不可逆固化动作（提交/归档）保持冻结，等用户对新范围确认后再恢复；增量登记走索引变更日志，全程可追溯、零删除。

## Approach
1. 响应范围变更的第一动作：冻结所有不可逆动作（暂存/提交/删除），并在状态中明示"入库保持冻结"。
2. 读现有 tasks.md / design.md 确定追加锚点，只增不删：新任务组、新设计章节。
3. 派生未决事项（如新编号 U7）登记进索引变更日志区。
4. 新子任务的执行记录追加进档案区既有执行记录，不另开档案。
5. 呈报时把"恢复原流程的待确认项"与"新子任务的待确认项"合并为单一清单，一次呈批，减少往返。

## Faster Next Time
- 先冻结固化动作再动笔设计，避免边写新章节边持有过期的提交方案。
- append-only 使 tasks/design 的行号锚点稳定，追加后无需全文重排，后续编辑报错率更低。
- 两类待确认项合并成一个确认点，避免用户多次裁决同一批次产物。

## Applicability Boundaries
- 适用：多阶段规格流水线执行中段收到范围追加；存在不可逆动作需要门禁的协作模式；用户已限定"不新建 spec"的续接方式。
- 不适用：追加任务与已确认规格存在实质冲突时——应先走冲突裁决流程（选项化裁决单+门禁）而非直接追加；追加任务规模大到足以独立立项时。

## Evidence or Examples
- 实例：kb_maintenance 执行至任务 9 呈批入库清单时，用户叫停并追加"三层协同机制设计"；执行方追加 tasks.md 任务组 11、design.md 第十章（10.1–10.6 含极端测试三场景）、索引 U7 与变更日志区、执行记录追加，全程零删除零提交。
- 终报并列两项待确认（记忆修正 / 恢复入库及可选裁决项），入库清单在冻结期间未被触碰。