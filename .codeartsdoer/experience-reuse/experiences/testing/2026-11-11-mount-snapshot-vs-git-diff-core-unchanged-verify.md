---
id: 2026-11-11-mount-snapshot-vs-git-diff-core-unchanged-verify
title: "动作级零改动验收用前后文件快照对比，git diff 是分支级口径在开发期必然误判"
category: testing
nature: technique
created_at: 2026-11-11T00:24:41
updated_at: 2026-11-11T00:50:39
tags: [零改核心, 文件快照, git diff 误判, 验收判据, 动作级验证]
keywords: [零改核心验收, git diff --stat, 文件内容快照, hash 清单, 挂载前后对比, 分支级口径, 动作级口径, 开发期非空, DFX 验证, 插件式挂载]
problem_patterns: ["挂载新类目零改核心模块"的验收用 git diff 判核心目录为空，开发期 diff 必然包含本轮开发变更导致验收恒失败, 想验证"某一次运行时动作没有修改某些文件"，却用了面向整个分支/工作区的差异工具, 快照对比的文件遍历范围与豁免规则（数据目录、缓存）不清导致快照本身抖动]
source_sessions: [ses_e3a9c97a3ffeCp9OO263dGGrPC]
project: Date
severity: medium
quality_score: 90
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-10-arch-redline-as-core-purity-scan, 2026-11-10-persistence-reveals-idempotency-gaps-registration, testing/2026-11-11-dependency-ready-state-branch-assertion]
---

# "动作级零改动"验收用前后文件快照对比，git diff 是分支级口径在开发期必然误判

## Scenario

插件式架构的 DFX 验收含"挂载一个与业务无关的桩类目，断言核心模块文件零改动"。初版实现用 `git diff --stat -- <核心目录>` 判输出为空；开发期（核心代码本轮刚写完、尚未提交）diff 必然非空，验收恒失败，且失败信息无法区分"挂载改了核心"与"开发本身改了核心"。

## Key Signals

- 失败时 diff 列出的文件全是本轮开发刚写过的文件——被测动作（挂载）根本没碰它们。
- 判别问题：验收条款的宾语是"这次挂载动作"还是"这个分支/工作区"？前者是动作级口径，后者是分支级口径，git diff 只提供后者。

## Essence

验收判据必须与被测对象的时间窗对齐。git diff 对比的是工作区与 HEAD（或指定基线），时间窗覆盖整个开发周期；而"挂载动作零改核心"的时间窗只有"挂载前→挂载后"。正确手段是在动作前后各做一次核心目录文件内容快照（相对路径 + 内容哈希的字典），对比两份快照——时间窗被压缩到动作本身，开发期变更天然被排除。快照口径是任何"某动作不改某资产"验收的通用形式。

## Approach

1. 定义快照函数：遍历受保护目录，产出 `{相对路径: 文件内容哈希}` 字典；排除数据/缓存/持久化目录（运行时合法写入区）。
2. 动作前取快照 `before`，执行被测动作（挂载/导入/初始化），动作后取快照 `after`。
3. 断言 `before == after`；不等时输出差集（新增/删除/变更的路径清单）直接定位违规文件。
4. 验收脚本用快照结论作为判据，删除 git diff 判据；如需 git 佐证仅作人工参考不进自动断言。

## Faster Next Time

- 模板：`_snapshot(root) = {p: sha256(read(p)) for p in 遍历(root) if p not in 豁免}`，两行核心，任何项目可直接搬。
- 更早识别：验收条款写成"X 动作不得改动 Y"（动作级宾语）时，立即排除工作区级差异工具（git diff/svn diff），选前后快照。
- 快照抖动预防：豁免清单里必须包含运行时持久化/日志目录，否则挂载自身的合法落盘会污染快照。

## Applicability Boundaries

- 适用于"单次动作不改受保护资产"类验收：挂载不改核心、导入不改配置、安装不改系统目录等。
- 不适用于跨会话/跨提交的变更审计（那正是 git 的本职）；也不适用于内容语义审查（快照只判"变没变"，不判"变得对不对"）。
- 大目录快照有 IO 成本，万级文件内可接受；再大需收缩到关键子目录。

## Evidence or Examples

- 本会话 DFX 验收（组 8）：初版 `git diff --stat -- 02_软件源码/workflow_base/core` 判空失败；改为 `_core_snapshot()` 挂载桩类目前后对比，快照一致 + 挂载耗时 0.0ms（≤1s）+ 树查询 0.0ms（≤500ms），`dfx_perf_and_stub` 通过，`final_summary.json` all_pass=true。
- 配套豁免：`workflow_base/data/`（持久化目录）不入快照，避免类目持久化落盘污染"零改核心"断言。