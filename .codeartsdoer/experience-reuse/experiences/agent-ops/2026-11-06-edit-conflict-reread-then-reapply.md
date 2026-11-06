---
id: 2026-11-06-edit-conflict-reread-then-reapply
title: 编辑报"文件已被外部修改"时先重读核实再重放编辑（时间戳漂移≠内容变更）
category: agent-ops
nature: technique
created_at: 2026-11-06T20:46:59
updated_at: 2026-11-07T06:52:33
tags: [edit冲突, 文件时间戳, 重读重放, 平台hook, 乐观并发]
keywords: [modified since last read, 乐观并发校验, mtime漂移, hook触碰, 批量编辑, 重读核实, 重放编辑, 整文件重写反模式, 追加锚点, 内容无损]
problem_patterns: [edit 工具报文件自上次读取后被修改导致批量追加中断, 无法判断文件内容真的变了还是仅被后台进程触碰了时间戳, 处置不当可能整文件重写覆盖或放弃落盘]
source_sessions: [ses_e4f5c5a83ffefUFnzHFvOEFJCW]
project: Date
severity: medium
quality_score: 88
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-06-shell-session-state-not-persistent, 2026-11-07-edit-read-prerequisite-grep-not-counted]
---

# 编辑报"文件已被外部修改"时先重读核实再重放编辑

## Scenario
多文件批量 edit 向知识库文档追加内容时，两处编辑同时报错 `File ... has been modified since it was last read`，错误信息给出 Last modification 与 Last read 两个时间戳（相差约 90 秒到 4 分钟）。

## Key Signals
- 错误自带时间戳对比：文件在本会话上次读取之后 mtime 被更新，但更新方不明。
- 本机存在平台 hook（索引维护、经验注入、trace 记录等）会触碰工作区文件——这是"读取后被改"的高概率来源。

## Essence
edit 工具以"上次读取时间 vs 文件 mtime"做乐观并发校验；平台 hook 可能只 touch 文件而不改内容。**mtime 变化不等于内容漂移**。正确动作是"重读→核实→重放"三步，而不是整文件重写（有覆盖风险）或放弃编辑（丢产物）。

## Approach
1. 按报错顺序逐个重读目标文件全文（工具会因重读刷新基线）。
2. 对照待追加内容确认：原文完好、追加锚点（oldString）仍在原位。
3. 基于最新读取重新执行同一 edit，oldString 不变。
4. 若重读发现内容确实被改动，先解决新内容与追加内容的合并关系再编辑；禁止覆盖式重写整文件。

## Faster Next Time
- 批量编辑把"读→改"间隔压到最短、同轮完成，降低 hook 触碰窗口。
- 遇该报错直接走"重读→重放"两步，不做诊断性猜测；报错自带时间戳，分钟级内的漂移大概率是 hook touch。
- 追加类编辑（append-only）天然抗冲突：锚点稳定，重放即可，无需重新设计编辑。

## Applicability Boundaries
- 适用：有平台 hook / 后台进程会触碰工作区文件的 Agent 环境（本机为 CodeArts 系 Agent）；多文件批量 edit 场景。
- 不适用：文件正被用户同时手工编辑（此时应停下询问，避免覆盖用户改动）；编辑工具无乐观并发校验的环境（不会报此错）。
- 与 2026-11-07-edit-read-prerequisite-grep-not-counted 的分工：本篇处理「报已修改后如何核实再重放」（时间戳漂移 ≠ 内容变更），那篇处理「读取基线如何建立」（只有 read 工具算已读，grep/glob 不算）；两者衔接使用。

## Evidence or Examples
- 实例：`notes/档案区/kb_maintenance/执行记录.md` 与 `notes/知识库索引.md` 同轮 edit 双双报错（Last modification 2026-11-06T12:18:54.642Z / .562Z，Last read 12:17:24.921Z / 12:15:00.361Z）。
- 重读后两文件内容与预期完全一致（结论：hook 仅触碰时间戳），重放 edit 成功，追加内容无损落盘。