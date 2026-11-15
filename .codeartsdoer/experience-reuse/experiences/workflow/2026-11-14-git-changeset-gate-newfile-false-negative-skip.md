---
id: 2026-11-14-git-changeset-gate-newfile-false-negative-skip
title: 审查门禁默认变更集对新文件假阴性：verdict 含 skip 字样是"未审"不是"通过"，新文件须 -Files 显式补审
category: workflow
nature: pitfall
created_at: 2026-11-14T12:15:23
updated_at: 2026-11-14T12:26:15
tags: [审查门禁, 变更集盲区, 假阴性, 显式列表, skip语义]
keywords: [no-python-changes skip review, gate-exit 0, 假阴性, 未暂存新文件, ruff-review -Files, git 变更集筛选, verdict 判读, 显式补审, fail-closed, 提交前兜底]
problem_patterns:
  - 新建 .py 文件尚未 git add 就调用默认变更集驱动的审查门禁，返回 exit 0 被误读为"门禁通过"，实际 verdict 是 skip（未审任何文件）
  - 只看 exit 数值不读 verdict 文本，把"无可审对象"与"审过无违规"两种 exit 0 混为一谈
source_sessions: [ses_e27c4dc39ffekQ77OksGO0tXru]
project: Date
severity: medium
quality_score: 85
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [build-env/2026-11-09-ruff-exit-code-fail-closed-gate-mapping, debugging/2026-11-14-edit-trailing-newline-false-success-byte-patch, build-env/2026-11-14-vercel-python-zero-dep-wsgi-entry-pattern]
---

# 审查门禁默认变更集对新文件假阴性：verdict 含 skip 字样是"未审"不是"通过"，新文件须 -Files 显式补审

## Scenario

编码任务中用 Write 新建 `.py` 文件后立即执行审查门禁（ruff-review 脚本）。门禁脚本默认从 git 变更集筛选 `.py` 文件作为审查范围——新文件尚未 `git add`，不在变更集内。个人开发流程、单文件小任务，门禁调用发生在提交前。

## Key Signals

- 触发痛点信号：默认调用返回 `gate-verdict: no-python-changes: skip review`、`gate-exit: 0`——形态上与"通过"完全一致（exit 0），实质是"没有审查任何文件"。
- 判别信号：verdict 字段含 `skip` 字样而非 `pass`。同一 exit 0 背后是两种完全不同的裁决语义。
- 后续实证：用 `-Files` 显式指定新文件补审，立即检出违规（W292）——证明默认调用的 skip 确实漏掉了待审对象，若据此放行则违规文件直接入库。

## Essence

门禁脚本的"审查范围来源"（git 变更集筛选）存在结构性盲区：新文件在 `git add` 之前不属于变更集，筛选结果为空，脚本走 skip 分支并返回 exit 0。skip 语义 = "无可审对象"，pass 语义 = "审过且无违规"——exit 数值相同但裁决含义相反。对"刚落盘的新文件"这一高频场景，默认调用必然假阴性。消除方式是以显式文件列表覆盖变更集来源：`-Files` 参数直指待审文件，绕过筛选盲区。

## Approach

1. **落盘新 .py 后调用门禁，先读 verdict 再读 exit**：verdict 含 `skip`/`no-python-changes` 字样 → 判"未审"，不得当"通过"；只有 `pass` + exit 0 才是放行。
2. **显式补审**：立即以 `-Files <新文件路径>` 重新调用门禁，显式列表优先于变更集筛选。
3. **以显式补审结果为最终裁决**：补审报告的 verdict/exit 才是本轮编码产物的门禁结论；发现违规则按正常修复-复审循环处理。
4. **提交前兜底**：即便中途已显式补审过，git 提交动作前再跑一次门禁（此时新文件已入暂存区，变更集覆盖），双保险防漏。

## Faster Next Time

- 新文件落盘后直接跳过默认调用，一步到位 `-Files` 显式列表补审——省掉一次必然 skip 的空转调用。
- 自检口诀："verdict 含 skip = 没审过"。exit 0 只有绑定 `pass` 才可放行，这是读门禁输出的第一眼动作。
- 该盲区形态可迁移自查：任何"默认从 VCS 变更集取审查范围"的工具（lint、format、security scan）对未暂存新文件都有同构假阴性，遇到 skip 类输出一律补显式列表。

## Applicability Boundaries

- 适用：ruff-review 脚本（默认 git 变更集筛选模式）+ 新建文件未暂存场景（2026-11-14 本机实测）；推广到同类"变更集驱动"审查门禁的新文件场景。
- 不适用：已修改（非新增）文件——它们本就在变更集内，默认调用可覆盖；显式列表模式是对新文件的补位，不是对默认模式的替代。
- 与相邻经验分工：`build-env/2026-11-09-ruff-exit-code-fail-closed-gate-mapping` 管门禁 exit 通道语义（违规/异常同走非零、非零即不过的映射设计），本条管审查范围来源的覆盖盲区（skip≠pass）——同属 fail-closed 门禁主题，门禁设计与执行时配套使用。

## Evidence or Examples

- 来源会话：ses_e27c4dc39ffekQ77OksGO0tXru（2026-11-14，Date 项目 Vercel 部署修复）。
- 默认调用原文：`gate-verdict: no-python-changes: skip review` / `gate-exit: 0`（新文件 `api/index.py` 未暂存时）。
- 显式补审检出：12:03:51 报告 `gate-verdict: violations-found` / `gate-exit: 4`，检出 `api\index.py:33:23: W292`——同一文件默认调用跳过、显式列表即检出，假阴性实证。
- 修复-复审闭环：字节级修补后 12:04:29 报告 `gate-verdict: pass` / `gate-exit: 0`。