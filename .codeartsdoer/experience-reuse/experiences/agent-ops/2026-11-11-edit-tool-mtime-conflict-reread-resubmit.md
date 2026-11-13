---
id: 2026-11-11-edit-tool-mtime-conflict-reread-resubmit
title: Edit 工具 mtime 冲突一律重读后原样重发，勿改写方案勿排查外部修改
category: agent-ops
nature: pitfall
created_at: 2026-11-11T00:24:41
updated_at: 2026-11-11T00:30:54
tags: [edit-tool, mtime-conflict, 重读重发, agent工具链, windows, edit冲突, 文件时间戳, 平台hook, 乐观并发]
keywords: [Edit 工具, modified since last read, mtime 基线, mtime漂移, 重读刷新, 原样重发, 误判外部修改, 文件触碰, 恢复一次成功, 多文件并行编辑, 持久会话, 乐观并发校验, hook触碰, 批量编辑, 重读核实, 重放编辑, 整文件重写反模式, 追加锚点]
problem_patterns: [Edit 报"File has been modified since it was last read"但文件内容并未被外部实质修改，误判为并发修改而放弃编辑或改走 write 全量重写, 长会话中文件被运行时触碰 mtime（自身此前的 bash/格式化动作或平台扫描）后基线过期, 一次并行发多个 edit 部分被 mtime 拦截，不知道如何低成本恢复, 批量追加类编辑被拦后不确定追加锚点是否仍在原位]
source_sessions: [ses_e3a9c97a3ffeCp9OO263dGGrPC, ses_e4f5c5a83ffefUFnzHFvOEFJCW]
project: Date
severity: medium
quality_score: 91
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-09-parsererror-silent-skip-downstream-absence-illusion, 2026-11-07-edit-read-prerequisite-grep-not-counted, 2026-11-06-shell-session-state-not-persistent]
---

# Edit 工具 mtime 冲突一律重读后原样重发，勿改写方案勿排查外部修改

## Scenario

Agent 在同一会话内对已读过的文件执行 Edit 落盘（补登记行、修代码、改测试断言、多文件批量追加），返回：`error: File <path> has been modified since it was last read. Last modification: <T1>. Last read: <T2>. Please read the file again before modifying it.`（T1 晚于 T2，差值常只有一两分钟到几分钟）。高频出现在：长会话中此前对该文件有过 bash/脚本触碰、一次并行发多个 edit、或文件被平台 hook（索引维护、经验注入、trace 记录）与 Windows Defender/索引服务扫描触碰。

## Key Signals

- 错误原文固定含三段：`has been modified since it was last read` + `Last modification` 时间戳 + `Last read` 时间戳。
- 判别信号：时间差小（分钟级）且本会话无人为改该文件的动作 → 大概率是 mtime 被触碰而非内容被改；若时间差大或确有外部进程写该文件，才需要真排查内容变化。
- mtime 变化 ≠ 内容漂移：平台 hook 与扫描服务常常只 touch 时间戳不改内容。

## Essence

Edit 工具以"上次 Read 的时刻"做 mtime 基线做防覆盖保护（乐观并发校验），基线是时刻不是内容摘要——文件被任何动作触碰（哪怕内容不变）基线即失效。恢复的本质是用一次 Read 重新校准基线，Edit 的防覆盖语义随之满足；与内容是否被外部修改无关。误判为"并发修改"而放弃编辑或改 write 全量重写，会丢失 edit 的精确替换保护并引入覆盖风险。

## Approach

1. 收到 mtime 冲突报错后，立即对同一路径执行 Read（可只读目标区域，目的是刷新基线）。
2. Read 成功后，原样重发与上次完全相同的 edit（oldString/newString 不做任何改写——文件内容大概率没变，重发即命中）。
3. 若重发报 oldString not found，才说明内容真的变了：先核实新内容与待编辑内容的合并关系（如追加锚点是否仍在原位），再基于最新读取重新定位替换点；禁止覆盖式重写整文件。
4. 多文件/并行多 edit 场景：按报错顺序对每个被拦的文件独立走"重读→重发"，互不影响；未被拦的 edit 不需要重做。

## Faster Next Time

- 把该报错当作固定两步恢复模式（重读→原样重发），恢复成本≈两次工具调用，不要先花时间排查"谁改了文件"。
- 预防一：对刚被 bash 脚本/其他工具写过的文件动 edit 前，先 Read 一次再编辑。
- 预防二：批量编辑把"读→改"间隔压到最短、同轮完成，降低 hook 触碰窗口。
- 追加类编辑（append-only）天然抗冲突：锚点稳定，重放即可，无需重新设计编辑。
- 警告信号：同一会话第二次对同一文件 edit 前若中间隔了任何写该文件的动作，预期会有 mtime 冲突，直接先读后改。

## Applicability Boundaries

- 适用于内置 Edit 工具（基于 last-read 时刻做基线的乐观并发校验实现）；若某平台 Edit 用内容哈希做基线则不会出现本现象。
- 不适用于：文件确实被用户或外部进程实质修改的场景（此时重发会 not found，走第 3 步）；文件正被用户同时手工编辑（应停下询问，避免覆盖用户改动）。
- 本证据来自 Windows + 长会话环境；行为本身与操作系统无关，但"mtime 被扫描服务触碰"的触发概率在 Windows（Defender/索引服务）更高。
- 与 2026-11-07-edit-read-prerequisite-grep-not-counted 的分工：那篇处理「读取基线如何建立」（只有 read 工具算已读，grep/glob 不算）；本篇处理「报已修改后如何恢复」（时间戳漂移 ≠ 内容变更）；两者衔接使用。

## Evidence or Examples

- 会话 ses_e3a9c97a3ffeCp9OO263dGGrPC（2026-11-11）：4 次命中（notes/知识库索引.md、workflow_base/core/security.py、workflow_base/adapters/embedded.py、tests/test_adapters.py），全部走"重读→原样重发"一次恢复，无一例 oldString not found——支持"内容未变、仅 mtime 失效"的判别口径。
- 会话 ses_e4f5c5a83ffefUFnzHFvOEFJCW（2026-11-06）：多文件批量追加时两处 edit 同轮报错（Last modification 2026-11-06T12:18:54.642Z / .562Z，Last read 12:17:24.921Z / 12:15:00.361Z），重读后内容与预期一致（hook 仅触碰时间戳），重放成功、追加内容无损落盘。
- 典型报错：`File C:\...\知识库索引.md has been modified since it was last read. Last modification: 2026-11-10T13:53:49.549Z. Last read: 2026-11-10T13:52:25.661Z.`（时间差约 84 秒）。