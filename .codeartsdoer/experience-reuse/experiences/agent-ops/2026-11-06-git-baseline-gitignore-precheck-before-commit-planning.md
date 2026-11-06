---
id: 2026-11-06-git-baseline-gitignore-precheck-before-commit-planning
title: 提交方案制定前的 git 基线与 .gitignore 预检（防基线假设失效与通配符静默屏蔽）
category: agent-ops
nature: pitfall
created_at: 2026-11-06T20:46:59
updated_at: 2026-11-06T20:46:59
tags: [git, gitignore, 提交规划, 基线核实, 静默排除]
keywords: [git log, git ls-files, 通配符忽略, 零提交假设, 提交范围清单, 精确暂存, 子目录gitignore, 入库方案, 门禁预检, check-ignore]
problem_patterns: [设计文档假设的仓库基线与实际 git 状态不符导致提交方案失真, 子目录 .gitignore 含通配符 * 使整个目录对 git 静默不可见, 制定入库范围清单时未察觉部分目标文件被 ignore 永远进不了库]
source_sessions: [ses_e4f5c5a83ffefUFnzHFvOEFJCW]
project: Date
severity: high
quality_score: 87
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-06-terminal-gates-in-task-dependency-graph, 2026-11-06-verify-claimed-prerequisites-before-research]
---

# 提交方案制定前的 git 基线与 .gitignore 预检

## Scenario
按规格流水线执行"首次版本提交"类任务时，设计文档基于早前盘点假设"仓库零提交"，且入库清单计划纳入某系统目录下 30+ 文件。提交动作尚未执行，先做提交前预检。

## Key Signals
1. `git log` 输出已存在提交 f6ed489（"初始提交：项目基线"），与"零提交"假设直接矛盾——盘点阶段从未实际运行过 git 查询，基线是靠上游文档断言的。
2. `git status` 中目标目录整体不出现（连 untracked 都没有），而该目录下确有大量应入库文件；打开子目录级 `.gitignore` 发现内容仅一个 `*`，整个子树被静默忽略。

## Essence
提交方案失真的两个根因：①基线靠"记忆/上游文档断言"而非 git 实查，其他执行者可能早已提交过；②子目录级 `.gitignore` 的通配符 `*` 让整个子树对 git 完全隐形——`git status` 不报错、不提示，入库清单上的文件"一个都进不了库"，且不改写 ignore 文件则后续任何暂存动作都无效。这两类问题在方案评审阶段不可见，只有在提交前实查才会暴露。

## Approach
1. 制定任何提交方案前先跑三条只读命令：`git log --oneline`（核实提交基线）、`git ls-files`（核实已跟踪清单）、`git status --porcelain`（核实未跟踪/已修改）。
2. 收集提交范围内所有 `.gitignore`（根级 + 各级子目录）并逐个读内容；发现 `*`、`!` 反向规则或目录级排除时，把"改写 ignore 文件"列为提交方案的第 0 步硬前置。
3. 用 `git check-ignore -v <候选文件>` 抽查入库清单中的代表文件，确认未被任何 ignore 规则命中。
4. 把"基线核实结果 + ignore 改写步骤"写回提交方案/设计文档，替代原假设，再进入门禁呈批。

## Faster Next Time
- 提交方案模板第 0 项固定为"git 三连实查"（log / ls-files / status）；凡上游文档说"零提交""已提交"一律以命令输出为准。
- 见到 `git status` 里"本该有很多文件却什么都没有"立即联想到通配符 ignore，第一时间读子目录 `.gitignore`，而不是反复重跑 status。
- 入库清单定稿前用 `git check-ignore -v` 批量抽查一次，秒级证伪整个方案。

## Applicability Boundaries
- 适用：任何 git 仓库的提交规划、首次提交、入库范围呈批类任务；多执行者接力的仓库尤其必要。
- 不适用：无 `.git` 目录的纯文档工作区；ignore 规则由平台强制托管且禁止查看的场景（此时应上报约束而非改写）。

## Evidence or Examples
- 实查输出：`git log` 显示 `f6ed489 初始提交：项目基线（码道协作规则、docs 参考文档与平台配置）`（2026-11-06 提交，4 文件 246 行），而 spec/design 均写"零提交"。
- `.codeartsdoer/.gitignore` 实际内容仅 1 字节：`*`；该目录 48+ 文件全部不在 git 视野内。修正方案将其改写为精确忽略清单（temp/、.codebase/、turbocontext.db/ 等）后才可能提交其余 30+ 文件。
- 该发现来自提交前门禁预检阶段，未造成实际错误提交——预检前移的价值即在于此。