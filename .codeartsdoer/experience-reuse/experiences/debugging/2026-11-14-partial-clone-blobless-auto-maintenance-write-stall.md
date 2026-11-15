---
id: 2026-11-14-partial-clone-blobless-auto-maintenance-write-stall
title: partial clone（blobless）仓库写操作全卡死：auto maintenance 按需批量拉缺失 blob，写前须禁 gc 并防僵尸进程混战
category: debugging
nature: pitfall
created_at: 2026-11-14T18:44:44
updated_at: 2026-11-14T18:44:44
tags: [partial-clone, git-maintenance, gc, index-lock, 写卡死]
keywords: [partial clone blobless, auto maintenance 批量拉取, write-tree 卡死, gc.auto 0, maintenance.auto false, index.lock File exists, 僵尸 git 进程, promisor fetch, 对象写挂死, 强杀混战]
problem_patterns:
  - blobless 仓库中 commit/write-tree 等本地写操作 90s+ 挂死转后台，误判为通道问题或仓库损坏，反复强杀重试形成死循环
  - 多次超时转后台导致多个 git 进程并发互等 index.lock，提交报 fatal: Unable to create index.lock: File exists
  - 强杀后残留 index.lock 未清理，后续每次提交恒失败，误判为权限或仓库损坏
source_sessions: [ses_e2663e19effewWyExkRIOfefi6]
project: Date
severity: high
quality_score: 88
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [debugging/2026-11-14-github-large-transfer-stall-readwrite-split-partial-clone-data-api, agent-ops/2026-11-07-background-long-task-log-pipeline-pitfalls, debugging/2026-11-14-git-init-soft-reset-empty-index-empty-tree-commit-hazard]
---

# partial clone（blobless）仓库写操作全卡死：auto maintenance 按需批量拉缺失 blob，写前须禁 gc 并防僵尸进程混战

## Scenario

用 partial clone（`--filter=blob:none`）拉取仓库基线用于修复。读取正常，随后在仓库内执行提交（`git commit`）时挂死超时；改用底层命令（`git write-tree`）想绕过也挂死；多次强杀重试后提交开始报 index.lock 冲突，修复链路整体卡死。

## Key Signals

- **分型信号**：读操作（status/log/diff/ls-files）全部秒回，写操作（commit/write-tree）全部 90s+ 卡死并转后台——"读快写挂"与通道问题形态相似但成因不同（本条是写后的隐式拉取）。
- **超出通道解释的反例**：`write-tree` 是纯本地索引操作、不触网络也卡死——说明卡点不在命令本身而在其**后置动作**。
- git 进程表出现多个并发实例（启动时间集中在数秒窗口内）——每次超时转后台的命令都留下了一个互等锁的僵尸进程。
- `fatal: Unable to create '<repo>/.git/index.lock': File exists`——锁被先前僵死进程持有。

## Essence

git 写操作完成后自动触发 auto maintenance/gc；在 blobless（partial clone）仓库中，gc 会**按需批量拉取全部缺失 blob**（promisor fetch，几百 MB 量级）——传输在卡死通道上全部挂起，表现即"写操作卡死"。真凶不是写本身，而是写之后的隐式 gc。叠加因素：超时转后台的命令并未终止，多个 git 进程并发争持 index.lock 形成混战；反复强杀还可能使临时仓库对象库处于可疑状态。

## Approach

1. **写前置**：blobless 仓库任何写操作前先禁用隐式维护——`git config gc.auto 0` + `git config maintenance.auto false`；
2. **挂死处置**：写操作超时转后台后先查进程表（`Get-Process git` 按启动时间识别批量僵尸），`Stop-Process` 全部清理；
3. **锁清理**：删除残留的 `.git/index.lock` 后再重试；
4. **止损判据**：禁用 maintenance 后若纯索引写（write-tree）仍挂死（临时仓库经多次强杀疑似损坏），放弃本地对象写入路线，改走远端 API 建提交（见大传输降级链篇）；
5. **收尾**：整目录删除临时仓库，不留半损坏状态。

## Faster Next Time

- "partial clone 是为读而生的"——写前两行配置是固定前置，先把这两行写进操作模板；
- 分型判据升级：读秒回 + 写全挂 + **纯索引写也挂** = gc 批量拉取形态，不再按通道问题排查；
- 同一仓库强杀累计 3 次即触发止损，换 API 路线；继续强杀只会加剧 index.lock 混战与对象库可疑状态。

## Applicability Boundaries

- 适用：partial/blobless clone（`--filter=blob:none` 等）仓库内的写操作场景；git ≥2.x 带 maintenance 子系统的版本；
- 不适用：完整 clone 仓库的写卡死（应先查通道、hook 与杀毒锁，不适用本条 gc 解释）；只读不写的 partial 仓库（无触发面）；
- auto maintenance 的触发时机与拉取范围随 git 版本可能变化，禁用双配置（gc.auto / maintenance.auto）为实测有效组合。

## Evidence or Examples

- 来源会话：ses_e2663e19effewWyExkRIOfefi6（2026-11-14）。
- 僵尸进程实证：并发 6 个 git 进程（Id 3084/8120/8388/10024/15184/15692，启动时间集中 18:14:59–18:15:05），全杀后索引完好（M .gitignore + A ×3 四项暂存未丢）。
- 卡死实证：`commit --amend` 超时转后台 110s+ 无完成；禁 maintenance 后 `write-tree` 仍卡死——触发弃本地改走 Git Data API 的止损。
- 锁冲突原文：`fatal: Unable to create 'C:/.../mydate-fix-repo/.git/index.lock': File exists.`