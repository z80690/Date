---
id: 2026-11-06-attachment-reference-unreachable-degrade
title: 用户引用附件不可达时的三步核实与诚实降级推进法
category: agent-ops
nature: technique
created_at: 2026-11-06T19:52:23
updated_at: 2026-11-06T19:52:23
tags: [agent-ops, 证据链, 多模态引用, 降级执行, 反编造]
keywords: [截图引用, File not found, 图片不可访问, 附件缺失, glob复核, 目录枚举, 证据缺口, 诚实声明, 降级推进, 反编造]
problem_patterns: [用户消息引用本地截图或附件路径但文件未落盘，直接读取报 File not found, 不确定附件是路径写错、未上传还是工具误报，不知道该重试还是继续主任务, 缺少图片佐证时容易编造图片内容补全叙事或空转等待用户]
source_sessions: [ses_e4f5c5a83ffefUFnzHFvOEFJCW]
project: Date
severity: medium
quality_score: 84
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: A
related_experiences: [agent-ops/2026-11-06-glob-empty-result-read-verify.md, workflow/2026-11-06-voice-dispatch-requirement-normalization.md]
---

# 用户引用附件不可达时的三步核实与诚实降级推进法

## Scenario

用户在派工单或对话中以文件名引用本地截图/附件（如 `image_20261106190014211.png`）作为需求佐证，但文件未随会话落盘到项目目录或路径失效。Agent 需要快速定论"到底有没有这个文件"，并在证据缺失时决定如何继续主任务。

## Key Signals

- `read` 直接返回 `error: File not found: <绝对路径>`——这是权威的存在性否定信号（区别于 glob 空结果的潜在误报）。
- 随后 `glob` 按文件名搜索两次均返回 `No files found`，目录枚举复核项目根与常见位置也无该文件——两次独立证据一致。
- 危险信号：开始产生"假设图片内容是……"的念头，即为编造前兆，必须立即停止。

## Essence

附件不可达 ≠ 主任务不可推进。关键约束是**证据链诚实**：用户在 Agent 运行环境中口头引用的本地资源不保证可用，正确目标不是"补全图片信息"，而是"快速定论 + 显式标注证据缺口 + 基于可用证据继续"。用想象内容补全叙事比缺口本身危害更大。

## Approach

1. **直查**：用 `read` 按用户原路径读取附件；失败即记录错误原文，不对同一路径反复重试（核实控制在 2-3 次调用内）。
2. **复核**：用 `glob` 按文件名（可加通配）在项目目录搜索，并用目录列举复核项目根与常见位置；两种独立证据一致才下"不可达"结论，单次空结果不下定论。
3. **声明并推进**：向用户显式声明缺口（模板句式："两张引用截图在项目目录和常见位置均未找到，无法读取图片内容，后续判断只基于文字与项目实际状态"），为用户重新提供材料留出通道；主流程随即基于文字与仓库实查继续，不阻塞、不编造。

## Faster Next Time

- 判定顺序固定：read 报 File not found（权威）→ glob/目录枚举复核 → 定论；全程 ≤3 次调用，不做无效重试。
- 警示信号：任何"脑补图片内容"的冲动出现时，立即转为显式缺口声明。
- 缺口声明要写进给用户的正式回复（而非只在内部记录），让用户有机会补发材料。

## Applicability Boundaries

- 适用：消息引用的本地附件/截图路径不可达的场景；通用 Agent 模式，不绑定特定平台（本例为 CodeArts Agent / win32）。
- 不适用：工具误报场景（glob 返回空但文件实际存在）——应改用"glob 空结果需 read 目录复核"的复核法，两者是互补边界；也不适用于网络资源不可达（属另一类降级，需区分报错来源）。

## Evidence or Examples

- 会话：ses_e4f5c5a83ffefUFnzHFvOEFJCW；用户引用 `image_20261106190014211.png` / `image_20261106191951310.png`。
- 实际执行：read ×2 报 `File not found: C:\Users\Administrator\Desktop\Date\image_20261106190014211.png`；glob ×2 返回 No files found；目录枚举确认项目根仅含 `.codeartsdoer/ .git/ .obsidian/ .workbuddy/ docs/ notes/`，无图片文件。
- 降级结果：助手声明"图片不可访问，后续判断只基于文字与项目实际状态"，随后完成现状盘点（docs/ 3 篇、notes/ 1 篇、skills/ 5 个）并生成 `.codeartsdoer/specs/kb_maintenance/spec.md`，流程未因图片缺失中断。
- 证据强度：核实三步法已被本会话验证有效；"用户接受该降级处理"尚未获反馈确认（会话处于门禁等待中）。