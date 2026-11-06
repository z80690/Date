---
id: 2026-11-06-precise-staging-bidirectional-consistency-gate
title: 精确暂存的 G2 核对程序：分批 add 后与批准清单双向一致，异常混入立即移出
category: agent-ops
nature: technique
created_at: 2026-11-06T21:16:59
updated_at: 2026-11-06T21:59:51
tags: [git, staging, gate, precise-commit, consistency-check]
keywords: [精确暂存, git add 分批, diff --cached --name-only, 双向一致性, 暂存区混入, 未批准文件, 经验库hook增量, untracked扫描, 门禁核对, 提交纪律]
problem_patterns: [分批精确暂存后无法确认暂存区与用户批准清单完全一致, 未列入清单的文件混入暂存区险些违规入库, 会话期间平台hook自动新增的运行时文件在提交时未被察觉]
source_sessions: [ses_e4f5c5a83ffefUFnzHFvOEFJCW]
project: Date
severity: high
quality_score: 90
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-06-terminal-gates-in-task-dependency-graph, 2026-11-06-git-baseline-gitignore-precheck-before-commit-planning]
---

# 精确暂存的 G2 核对程序：分批 add 后与批准清单双向一致，异常混入立即移出

## Scenario

按"入库范围清单经用户确认后方可暂存"的门禁纪律执行提交。清单有 50+ 文件需分批 `git add`；门禁要求"暂存区与批准清单双向一致"（清单内无一遗漏、暂存区无一多入）。

## Key Signals

1. 某批 add 命令未显式列出 `.obsidian/`，但 `git diff --cached --name-only` 中出现该目录 4 个文件——文件经外部操作或路径展开混入，暂存动作与暂存结果脱节。
2. 终核时 `git status --porcelain` 出现会话期间未见的 untracked 新文件与 modified 文件——平台经验库 hook 在会话运行期间自动提炼并写入了新经验文档（含新分类目录），提交基线在会话中被静默扩充。
3. 仅凭"我 add 过哪些文件"的记忆核对不可靠——多批命令、路径展开、外部写入都会造成记忆与实际暂存区偏差。

## Essence

精确暂存纪律的执行核心不是"add 时小心"，而是**以暂存区实际状态为唯一事实源做双向核对**：正向（清单→暂存区，逐条在位）+ 反向（暂存区→清单，逐条受批）。两类高频偏差源必须显式处置：①未经清单的外部/展开路径混入（发现即 `git restore --staged` 移出并记录原因）；②会话期间平台 hook / 后台进程产生的运行时增量（属自动产物，须按"资产零遗漏"原则明示裁决：一并入库并在汇报中透明说明，或明确排除）。

## Approach

1. 分批暂存：按目录/类别把清单分成 3-4 批，每批 `git add` 显式逐文件列出，不用目录通配、不用 `git add .`。
2. 正向核对：`git diff --cached --name-only` 取实际暂存清单，逐条对照批准清单确认在位。
3. 反向核对：逐条确认暂存区每个文件都在批准清单内；发现未列入项（如 .obsidian/）立即 `git restore --staged <path>` 移出并记录原因。
4. 增量扫描：暂存完成后跑一次 `git status --porcelain`，对剩余 untracked/modified 逐项分类（hook 自动产物 / 临时产物 / 遗漏资产），按项目纪律决定处置并透明上报。
5. 终核计数：核对通过后以 `git diff --cached --name-only | wc` 类计数交叉验证总数（如 58 = 批准 53 + hook 增量 5），计数不符即回到第 3 步。
6. 三项全过（正向齐、反向纯、增量明示）才允许 `git commit`。

## Faster Next Time

- 把"暂存后必跑 `git diff --cached --name-only`"固化为提交流程固定步骤，禁止凭记忆宣布"已精确暂存"。
- 看到"本批没 add 的文件出现在暂存区"→ 立即意识到路径展开/外部写入，先移出再查明来源，不要顺手提交。
- 长会话提交前必跑一次 `git status --porcelain`：会话期间 hook/后台写入的文件是静默出现的，不扫描就会漏报或错报。
- 计数交叉验证是最快的终核手段：总数对不上时才做逐条比对，省时。

## Applicability Boundaries

- 适用：任何有"精确暂存、禁全量 add"纪律的 git 仓库与 Agent 执行环境（观察于 CodeArts Agent + win32 PowerShell）；多批次暂存、长会话（hook 活跃）场景尤其必要。
- 不适用：允许全量提交的仓库（直接 `git add -A` 无此核对需求）；暂存策略由平台强制托管、不可查看暂存区的环境（此时应上报约束）。
- 与方案预检经验互补：基线与 .gitignore 预检发生在方案制定前，本核对程序发生在暂存执行后、提交前，两者不可互替。

## Evidence or Examples

- 实录：清单 53 文件分 3 批暂存 → G2 发现 `.obsidian/` 4 文件混入（未列入任何 add 命令）→ `git restore --staged .obsidian` 移出。
- 实录：终核 `git status` 发现 hook 自动新增 5 篇经验文档 + 2 处修改 + 新分类目录 → 按"资产零遗漏"一并入库（58 文件），终报透明说明"工作区剩余增量由变更日志追溯、随下次提交入库"。
- 实录：最终暂存计数 58 与"批准 53 + hook 增量 5"吻合，双向一致成立后提交，提交后无未跟踪残留（除明示的运行时增量）。