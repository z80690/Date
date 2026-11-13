---
id: 2026-11-11-root-dir-consolidation-fallback-and-path-regression
title: 根目录平铺归拢三级降级迁移（git mv→Move-Item→robocopy /MOVE）+ 归拢后路径推导回归验证
category: build-env
nature: technique
created_at: 2026-11-11T02:34:42
updated_at: 2026-11-11T02:41:19
tags: [build-env, 目录归拢, 迁移降级链, 路径推导, 回归验证]
keywords: [根目录平铺, 中文目录归拢, git mv 静默失败, Move-Item 拒绝访问, robocopy /MOVE, dirname 层级, 路径推导回归, 迁移后自检, 文件锁, 收敛目录]
problem_patterns:
  - "项目根目录被大量平铺目录占满需要收敛到子目录，git mv 无输出静默失败不知原因"
  - "Move-Item 迁移部分目录报'访问被拒绝'，失败原因随目录内容不同而不同（缓存锁/只读对象）"
  - "目录迁移完成后代码里 dirname 重复次数按旧层级写死，自检项（日志可写探测）开始失败但不易联想到迁移"
source_sessions: [ses_e3a9c97a3ffeCp9OO263dGGrPC]
project: Date
severity: medium
quality_score: 86
utility_score: 97
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: ["build-env/2026-11-07-reference-assets-cross-drive-relocation-path-sync", "agent-ops/2026-11-11-edit-tool-mtime-conflict-reread-resubmit"]
---

# 根目录平铺归拢三级降级迁移（git mv→Move-Item→robocopy /MOVE）+ 归拢后路径推导回归验证

## Scenario

项目根目录积累了大量业务目录（如 00_项目管理～09_归档 十个中文目录）平铺，要求归拢到统一子目录（如 `workspace/`）且不得破坏既有功能。同盘符批量目录迁移，目录内容混杂（git 仓库、Python 缓存、只读对象文件、未跟踪产物）。

## Key Signals

- `git mv <dir> <dst>` 对含未跟踪文件的目录**无任何输出、不执行迁移**——静默失败，极易误以为成功。
- `Move-Item` 逐目录迁移时部分目录报"对路径 X 的访问被拒绝"（IOException）：被锁原因与内容相关——Python `__pycache__` 被进程占用的目录、含 `.git` 只读对象文件的目录会失败，其余正常。
- 归拢完成后跑测试，自检项"日志可落盘"（向固定相对层级目录写探测文件）报 `FileNotFoundError`——探测路径落在迁移前的旧层级上。

## Essence

同盘目录迁移有一条可靠性递增的三级降级链，失败模式各不相同须逐级换用；**迁移改变目录树深度后，所有按 `dirname` 重复次数推导根路径的代码都隐式失效**——这是迁移类任务最高频的隐藏破坏点。`os.path.dirname` 首次作用在**文件路径**上（去掉文件名），之后每层去掉一级目录，改层级前必须从文件出发逐级数到目标，不能凭"少了一层目录就减一"的直觉改。

## Approach

1. 迁移第一级用 `git mv`（保留 git 历史）；执行后立即 `Test-Path` 验证目标存在——**git mv 对含未跟踪文件的目录会静默跳过，无输出≠成功**。
2. 失败目录转 `Move-Item`（同盘原子重命名）；对报"访问被拒绝"的目录，先判原因：缓存锁类（`__pycache__`）换进程空闲时重试或清缓存，git 只读对象类直接跳第三级，不纠缠。
3. 第三级兜底 `robocopy <src> <dst> /MOVE /E`——robocopy 忽略文件锁与只读属性，是 Windows 目录强迁的最终手段；完成后核对源目录已清空。
4. 归拢后全库 grep 路径推导点（`dirname` 连写、`os.path.join(root, ...)`、硬编码相对层级），从**文件路径**出发逐级数 `dirname` 次数修正；拿不准时在目标环境打印 `derived root` 实证。
5. 收口判据：迁移后跑全量回归三件套（单元测试 + 闭环验证 + 终验脚本）全绿，才允许汇报"归拢完成"；只迁移不回归等于未完成。

## Faster Next Time

- 一句话判据：**git mv 静默失败 → Move-Item 逐个迁 → 锁死目录 robocopy /MOVE 兜底；迁移完成 ≠ 任务完成，全量回归绿才算数**。
- `git mv` 无输出时第一反应查 `git status` 确认是否真迁移，不要重发同一命令。
- `dirname` 重复次数修正口诀：从**文件**开始数（第一次 dirname 去掉的是文件名），每上一层加一次；改完在真实环境打印推导结果验证，不信口算。
- 迁移类任务的验收清单：目标树存在、源已清空、路径推导点已修、回归全绿——四项缺一即返工。

## Applicability Boundaries

- 适用：同盘符目录归拢/搬迁，目录内容含 git 仓库、语言缓存、只读产物等混合体；迁移后存在按相对层级推导路径的代码。
- 不适用：跨盘符搬家（用复制→验证→清源三段式，见关联经验）；无任何代码引用的纯静态资料搬迁（可直接 robocopy 一步到位）。
- 边界：robocopy /MOVE 迁移 git 仓库会丢失部分属性语义，迁移后建议跑一次 `git status` 核对仓库完整性；平台对长路径/中文名的支持差异以实测为准。