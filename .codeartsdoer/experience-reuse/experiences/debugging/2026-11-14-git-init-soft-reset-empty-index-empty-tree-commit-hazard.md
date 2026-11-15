---
id: 2026-11-14-git-init-soft-reset-empty-index-empty-tree-commit-hazard
title: git init 后 HEAD 未出生禁用 reset --soft：索引清空致"只剩新文件"空树提交，险覆盖远端基线
category: debugging
nature: pitfall
created_at: 2026-11-14T18:44:44
updated_at: 2026-11-14T18:44:44
tags: [git-reset, 空索引, 空树提交, 空仓回填, 覆盖风险]
keywords: [reset --soft, HEAD 未出生 unborn, 索引清空, 只剩新文件的提交, 空树提交险覆盖远端, reset --mixed FETCH_HEAD, git init, 空仓回填基线, 索引文件数断言, 提交事故补救]
problem_patterns:
  - 往空仓库回填既有项目基线（init→fetch→reset）时用了 reset --soft，git status 把基线文件全部显示为"已暂存删除"
  - 按此损坏索引 add 少量新文件后 commit，产出"只剩新文件"的提交树——若推送将把远端仓库变成近乎空仓
  - 事故发生后误判为 clone 残缺或文件丢失，在错误方向上继续排查
source_sessions: [ses_e2663e19effewWyExkRIOfefi6]
project: Date
severity: high
quality_score: 86
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [debugging/2026-11-14-partial-clone-blobless-auto-maintenance-write-stall, agent-ops/2026-11-06-git-baseline-gitignore-precheck-before-commit-planning, agent-ops/2026-11-06-precise-staging-bidirectional-consistency-gate]
---

# git init 后 HEAD 未出生禁用 reset --soft：索引清空致"只剩新文件"空树提交，险覆盖远端基线

## Scenario

目标：向一个远端快照仓库（仅 1 个基线提交）补入几个修复文件。因 clone 卡死改走"本地 `git init` + partial fetch + reset"路线回填基线，然后在回填结果上提交新文件。

## Key Signals

- **危险信号**：`reset --soft FETCH_HEAD` 之后 `git status` 把基线全部文件列为 `D`（已暂存删除）——这不是文件丢了，是**索引被清空**（工作树文件还在，索引与 HEAD 没有基线）。
- `git log` 显示 HEAD 已指向新创建的错误提交，但该提交的树只含刚 add 的几个文件——基线内容全部不在树内。
- 事故提交**尚未推送**（本地 ahead 但未 push）——这是唯一的安全垫，推送即成灾。

## Essence

`git init` 之后的仓库 HEAD 尚未指向任何提交（unborn HEAD）。`reset --soft <commit>` 的语义是"移动 HEAD 到目标提交、保留索引与工作树"；在 HEAD 未出生时，索引无从"保留"，等效于清空。据此索引 commit 产出的树仅含后续 add 的文件——即"空树提交"。若按此推送，远端基线将被近乎空仓覆盖。正确姿势是 `reset --mixed FETCH_HEAD`：把索引与 HEAD 对齐到拉取的基线树（工作树文件自动回归"未修改"态），在此之上 add 修复文件再提交，树结构完整。

## Approach

1. **预防**：空仓回填固定用 `git fetch --filter=blob:none --depth 1 origin <branch>` + `git reset --mixed FETCH_HEAD`（禁 --soft）；
2. **事故确认**：出现大面积 `D` 暂存删除时立即停手，`git log --oneline` 核对 HEAD 是否已产生错误提交、`git ls-files | 计数` 核对索引规模；
3. **补救**（错误提交未推送时）：`git reset --mixed <基线提交>` → HEAD 回退到基线、索引恢复完整树（实测 1198 个文件）→ 重新 `git add` 目标修复文件 → 单独 commit；
4. **提交前断言**：索引文件数与基线规模一致 + `git log` 确认 parent 是基线提交 + 暂存清单与目标修复集双向一致；
5. 补救期间的提交操作若挂死，按僵尸进程纪律处理（见 partial clone gc 篇），勿并发重试。

## Faster Next Time

- "init 后回填"场景看到 status 出现**大面积 D = 索引被清空**的指纹信号，立即停手换 --mixed，不进入 add/commit；
- soft reset 只适用于"已有 HEAD 的撤销提交"场景（保留改动重新组织）；unborn HEAD 场景的一律 --mixed；
- 提交前三道兜底断言：索引文件数、parent 链、暂存清单双向一致——空树提交在推送前可被全部拦截。

## Applicability Boundaries

- 适用：`git init` + fetch 回填、仓库 repair、往空远端仓重建基线等 unborn HEAD 场景；
- 不适用：正常仓库（已有 HEAD）的撤销提交——那里 --soft 是合法语义（移动 HEAD、保留索引），照搬"禁 soft"会错杀正常用法；
- `--mixed` 不会丢工作树改动（只重置索引）；但工作树中未提交的既有修改会被并入"未暂存"集合，回填场景需先确认工作树干净。

## Evidence or Examples

- 来源会话：ses_e2663e19effewWyExkRIOfefi6（2026-11-14）。
- 事故实证：错误提交 `dd466d4`（树仅 4 文件：.gitignore/.vercelignore/api/vercel.json），`git status` 曾显示基线全部文件 `D`（.codeartsdoer/.gitignore、AGENTS.md、agents/examiner.md 等整页 D 清单）。
- 补救实证：`reset --mixed 645ef8a` 后 HEAD 回基线、`git ls-files` 计数 1198 与基线一致；重新 add 4 文件后暂存区恰为 `M .gitignore + A .vercelignore + A api/index.py + A vercel.json`。
- 最终落地：修复以 Git Data API 远端提交 `f34fe22825` 完成后，本地临时仓库与错误提交一并清理，事故未触达远端。