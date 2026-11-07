---
id: 2026-11-07-pre-commit-final-status-scan-hook-increment
title: 提交前最终 status 终扫与 hook 运行时增量的资产定性
category: agent-ops
nature: technique
created_at: 2026-11-07T08:51:58
updated_at: 2026-11-07T08:51:58
tags: [git-staging, agent-hooks, snapshot-staleness, asset-classification, commit-gate]
keywords: [git status, 终扫, hook 增量, 经验库, 精确暂存, 资产零遗漏, 运行时痕迹, 提交门禁]
problem_patterns: [暂存清单制定后工作区又发生变化, 提交时发现来历不明的未跟踪文件]
source_sessions: [ses_e4c8a78edffee772ytCDqwOSfb]
project: Date
severity: medium
quality_score: 90
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: ["2026-11-06-precise-staging-bidirectional-consistency-gate", "2026-11-06-git-baseline-gitignore-precheck-before-commit-planning", "2026-11-07-sensitive-credential-file-commit-gate-env-block"]
---

# 提交前最终 status 终扫与 hook 运行时增量的资产定性

## Scenario

长会话（数十至上百轮）中做过工作区盘点并编好逐文件精确暂存清单；从清单定稿到实际执行 `git commit` 之间，工作区又出现了清单外的新增/修改文件。直接按旧清单提交会漏资产或留下未解释的漂移。

## Key Signals

- `git status --porcelain` 输出与此前快照不一致：出现此前不存在的 `M`/`??` 条目。
- 新增文件集中在经验库目录（新经验文档、`.archived/` 归档、索引修改）——这是 Agent 平台 hook（经验提炼、索引维护）在会话运行期间持续工作的痕迹，**是合法增量而非异常入侵**。

## Essence

两个判断：

1. **工作区快照有时效性**：在带后台 hook 的 Agent 平台上，任何"暂存清单"从定稿那一刻起就开始过期；提交前的最终 status 终扫必须作为独立步骤，不能沿用制定清单时的快照。
2. **hook 增量需要定性而非一律拒绝**：按资产属性二分——运行时痕迹（会话日志 `.jsonl`、锁文件、缓存）排除且确认被 `.gitignore` 覆盖；提炼产物（经验文档、归档目录、索引更新）是知识资产，按"资产零遗漏"原则并入暂存与呈报。

## Approach

1. 按清单完成精确暂存后、`commit` 前，执行一次 `git status --porcelain` 终扫。
2. 逐项与暂存清单 diff，列出差异项。
3. 对每个差异项定性：知识资产 → 补 `git add` 并同步更新清单与呈报文本；运行时痕迹 → 确认忽略规则覆盖，无需动作；来历不明 → 先查来源再定性，禁直接暂存。
4. 终扫与提交之间**不再插入**会产生文件的新动作（防再次被 hook 打洞）；若被迫中断，重扫后再提交。
5. 终报中透明列出"hook 增量 N 项一并入库"，保证审计链完整。

## Faster Next Time

- 把"提交前终扫"固化进提交门禁检查单，与"暂存清单双向一致"核对并列执行（一次 status 输出同时服务两项）。
- 判别捷径：差异项路径落在经验库/索引目录 → 默认按资产处理；落在 temp/cache/session 目录 → 默认按运行时痕迹处理。
- 不要在暂存完成后继续做会引文件变更的大动作；确需继续则完成后重新走终扫。

## Applicability Boundaries

- 适用：带后台 hook/后台任务的 Agent 平台上的长会话提交；多批次精确暂存 + 分阶段提交的工作流。
- 不适用：无后台写手的干净环境（快照不会漂移，终扫退化为普通复核）；单人一次性 `git add -A` 流程（本就不做精确暂存）。
- 与既有经验的关系：精确暂存双向一致门禁管"暂存了什么"，本经验管"清单定稿后世界又变了怎么办"——互补而非重复。

## Evidence or Examples

- 实例一（2026-11-07，提交 da11a01 前）：终扫发现 5 篇 hook 新增经验文档，定性为资产并入，最终 65 文件提交且 `.env` 敏感文件被成功拦截排除。
- 实例二（提交 e02afc3 前）：索引文件在清单定稿后被 hook 修改，终扫捕获并入。
- 实例三（后续批次）：`.archived/` 归档目录为 hook 新建，定性资产并入 15 文件提交（2a83004）。
- 反例教训（同会话早期）：曾因 `.obsidian/` 混入暂存区与清单不符而被迫移出——若先终扫再暂存，此类返工可避免。