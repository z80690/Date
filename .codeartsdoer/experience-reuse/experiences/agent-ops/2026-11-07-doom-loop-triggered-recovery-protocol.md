---
id: 2026-11-07-doom-loop-triggered-recovery-protocol
title: 验证工具触发 Doom Loop 禁用后的处置协议：零工具调用声明+首成功结果采信+零依赖下一步规划
category: agent-ops
nature: technique
created_at: 2026-11-07T09:38:26
updated_at: 2026-11-11T02:39:00
tags: [Doom Loop, 工具禁用, 验证采信, 处置协议, 验证焦虑]
keywords: [工具禁用恢复, listSkills, 冗余确认, 首次成功结果, 权威源采信, 零工具依赖, 检测声明, 用户拒绝授权, 跨轮串行重复, 收尾验证]
problem_patterns: [首次调用已成功返回全部所需信息，却不信任结果而跨轮反复调用同一验证工具直至被平台禁用, 工具被禁用后继续发起调用，既被系统拒绝又消耗用户多次手动授权拒绝, 禁用发生时剩余收尾工作被误判为无法继续，实际首次结果已足以支撑全部落盘动作]
source_sessions: [ses_e4f5c5a83ffefUFnzHFvOEFJCW]
project: Date
severity: medium
quality_score: 86
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-06-parallel-tool-call-doom-loop, 2026-11-06-tool-language-filter-false-empty-result, agent-ops/2026-11-11-user-interrupt-loop-rollback-rechannel-protocol]
---

# 验证工具触发 Doom Loop 禁用后的处置协议：零工具调用声明+首成功结果采信+零依赖下一步规划

## Scenario

长会话收尾阶段需要核验若干实体（如新技能的平台注册状态）作为登记依据。首次 listSkills 调用已成功返回完整结果（技能总数、scope、status、agents 挂载），但执行方对"是否已确认"缺乏确定感，跨多个轮次以 tool_call 与直接调用交替方式重复调用同一工具约二十次，触发平台 Doom Loop 保护：工具被禁用至下一轮用户输入，且部分调用被用户手动拒绝授权。

## Key Signals

- 同一验证目的的调用在第 2 次及以后开始返回与首次完全相同的数据——信息增量为零是停止的硬信号。
- 出现 `The user rejected permission to use this specific tool call`——用户拒绝授权即"系统+用户"双重停止信号。
- 平台输出 Doom Loop 检测提示并禁用工具；此时继续调用只会刷拒绝记录。

## Essence

根因是**验证焦虑**：不把"首次成功返回"当作终态证据，试图用重复调用获得"再确认一次"的心理保障。正确认知是：幂等验证类调用的首次成功结果即权威源，重复调用不产生信息增量、只产生禁用风险。禁用发生后，正确动作不是换工具硬绕，而是盘点存量数据是否已覆盖目的——验证类调用通常一次就够，故收尾工作几乎总是可以零工具完成。

## Approach

1. 停止信号出现（重复数据/用户拒绝/平台禁用提示）后，立即发出**零工具调用**的检测声明：说明哪个工具因何种重复被禁、禁用范围（至下一轮用户输入）。
2. 盘点首次成功结果：逐项核对本次验证目的所需字段（数量/状态/挂载关系）是否已在首次结果中齐备——通常齐备。
3. 基于首次结果完成全部落盘动作（登记、呈报、定案），规划**零工具依赖**的下一步并明确告知用户"一句确认即解除禁用"。
4. 复盘根因并在回复中如实记录：本次重复的动机是什么（如"未信任首次结果"）、对应哪条既有纪律，供后续同类场景对照。

## Faster Next Time

- 幂等验证的第一原则：首次成功结果＝终态证据，写入产出文档即完成采信，不做二次确认调用。
- 同一验证工具在单会话内超过 2 次调用且无新参数/新目的，即为危险信号，强制自问"首次结果缺了什么字段"——答不出就停。
- 收尾阶段的验证需求尽量合并为一次调用（或单命令批量断言），避免多轮零散核验。
- 禁用不可怕：验证数据早已在手，剩余工作多为文件编辑；声明+盘点+零依赖规划三步即可无损收尾。

## Applicability Boundaries

- 适用：幂等验证/盘点类工具（listSkills、状态查询、存在性检查）在长会话收尾阶段的跨轮冗余确认；触发禁用后的处置。
- 不适用：非幂等操作（写文件、提交）——首次失败后按重试纪律（≤3 次）正常重试，与本协议无关；亦不覆盖同轮并行槽位重复的预防（见 parallel-tool-call-doom-loop 既有经验，本条为其"跨轮串行形态+触发后处置"的补充）。

## Evidence or Examples

- 会话 ses_e4f5c5a83ffefUFnzHFvOEFJCW 收尾链：listSkills 首次成功返回 56 技能（含 3 个待登记技能 scope=project/status=enabled），随后跨轮重复调用约二十次，平台禁用+用户多次拒绝授权。
- 处置实录：发出零工具调用检测声明 → 盘点确认首次结果已含 U16 登记全部依据 → 声明下一步为纯文件编辑（U15/U16/关闭三项落盘+记忆修正+提交）且零 listSkills 依赖 → 用户回复"继续"后一轮完成收尾（提交 d4e57a7）。