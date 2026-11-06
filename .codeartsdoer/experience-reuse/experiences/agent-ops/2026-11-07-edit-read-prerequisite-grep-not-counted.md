---
id: 2026-11-07-edit-read-prerequisite-grep-not-counted
title: edit 的"已读"前置只认 read 工具记录，grep/glob 命中不算已读
category: agent-ops
nature: pitfall
created_at: 2026-11-07T06:42:01
updated_at: 2026-11-07T06:49:07
tags: [edit, read, 工具契约, 乐观并发, 批量编辑]
keywords: [edit 被拒, modified since last read, grep 不算已读, 读取记录, 乐观并发校验, 批量追加, 锚点确认, 重放编辑, 工具前置条件, read 刷新基线]
problem_patterns: [grep 已确认文件内容与锚点一致但 edit 仍报 modified since last read, 批量修订时部分文件反复 edit 失败不知差在哪, 不理解 edit 前置校验的"已读"判定范围导致反复改 oldString 无效重试]
source_sessions: [ses_e4f5c5a83ffefUFnzHFvOEFJCW]
project: Date
severity: medium
quality_score: 88
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-06-edit-conflict-reread-then-reapply, 2026-11-06-glob-empty-result-read-verify]
---

# edit 的"已读"前置只认 read 工具记录，grep/glob 命中不算已读

## Scenario

会话中对多个文件做批量追加/修订（如给 design.md、注册表、机制文档分别追加章节）。执行顺序常是：grep 定位锚点并确认内容 → 直接 edit。当文件在此期间被平台 hook 触碰（mtime 变化）或本就未经 read 工具读过时，edit 被乐观并发校验拒绝；此时若再用 grep 复核"内容无损"后重放 edit，**仍会被拒**，形成同一批文件部分成功、部分反复失败的尴尬局面。

## Key Signals

- 报错形态一：`File ... has been modified since it was last read. Please read the file again before modifying it.`（mtime 基线失效）。
- 报错形态二：`Could not find oldString in the file`（文件被外部真实改动，锚点失配——与形态一的处置不同）。
- 关键混淆点：grep 明明刚命中了锚点原文，edit 却仍报"未读/已变更"，让人怀疑是工具误报而反复重试。

## Essence

edit 的前置校验以 **read 工具的读取记录**为准：grep/glob 的命中结果不建立读取基线。文件被 hook 触碰后，"grep 知道内容"不等于"edit 认为你读过"。这不是误报，是契约——重放 edit 前必须用 read 真实读取目标文件（读锚点附近区域即可刷新基线）。

## Approach

1. edit 被拒且**不是** oldString 失配时：不要反复改 oldString 或怀疑内容，直接用 read 读取该文件（可只读目标区域），随后立即重放同一 edit。
2. 批量场景按"读一个、改一个"节奏推进；多个文件被同一 hook 批量触碰时，先并行 read 全部目标文件，再并行 edit。
3. 报 oldString 失配时先 read 全文比对：内容被外部真实更新（如 hook 追加了新行）则基于最新内容重写锚点合并，而非强行重放旧锚点。
4. 若 read 后文件又被触碰导致再次被拒（罕见），重复 read→edit 一轮；连续两轮仍失败才升级为异常排查。

## Faster Next Time

- 一句话纪律：**"要 edit 的文件，动笔前必经 read；grep 只能帮你找锚点，不能替你建立读取基线"**。
- 批量修订的稳妥顺序：并行 read（拿锚点+建立基线）→ 并行 edit（基于刚读的内容），把"确认内容"和"建立基线"合并成一步，省掉失败重试轮次。
- 失败信号早识别：同一 edit 第二次被拒时立即切 read→edit 路径，第三次重试原命令纯属浪费。

## Applicability Boundaries

- 适用：本 Agent 平台的 read/edit 工具契约；其他平台若 edit 有类似乐观并发前置，判别方法相同（看报错措辞是否要求 read again）。
- 不适用：oldString 真失配（内容被外部实质修改）——那条路要合并外部变更，重放旧锚点无效。
- 与 2026-11-06-edit-conflict-reread-then-reapply 的分工：那篇处理「edit 报已修改后如何核实再重放」（时间戳漂移 ≠ 内容变更），本篇处理「读取基线如何建立」（只有 read 工具算已读）；两者衔接使用。
- read 大文件时可用 offset/limit 只读锚点区域，基线刷新同样生效；但锚点在文件尾部时注意 offset 覆盖到位。

## Evidence or Examples

- 本会话实例：对 注册表.md、复用评估表.md、知识库维护机制.md 三文件，grep 已确认内容无损，edit 连续两轮被拒；改用 read 逐个读取后，三个 edit 一轮全部成功。
- 对照实例：项目事实表.md 同轮报的是 `Could not find oldString`——read 后发现 hook 已追加"refs 环境行"，属真实内容变更，按合并路径处理成功。
- 工具报错原文（形态一）留痕：`Last modification: ...T20:27:33.613Z / Last read: ...T20:18:46.981Z`——时间差即 hook 触碰窗口。