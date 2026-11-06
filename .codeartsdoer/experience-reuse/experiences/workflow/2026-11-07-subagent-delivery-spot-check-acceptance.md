---
id: 2026-11-07-subagent-delivery-spot-check-acceptance
title: subagent 交付转呈前先做秒级抽验：grep 验关键条款落位，bash 验产物实存
category: workflow
nature: methodology
created_at: 2026-11-07T06:42:01
updated_at: 2026-11-07T06:42:01
tags: [subagent, 验收, 抽验, 交付质量, 转呈纪律]
keywords: [subagent 交付, 抽验, 占位条款, 产物核实, 转呈失真, 验收复核, spec 落盘验证, 秒级成本, 禁猜禁编, 摘要与实存对照]
problem_patterns: [subagent 返回"已完成"摘要但不知关键验收条款是真落位还是占位, 直接转述 subagent 摘要给用户存在失真或未实证风险, 对 subagent 产出全量重做成本高不抽验又怕翻车]
source_sessions: [ses_e4f5c5a83ffefUFnzHFvOEFJCW]
project: Date
severity: medium
quality_score: 86
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-06-verify-claimed-prerequisites-before-research, 2026-11-07-worker-grader-exam-gate-pattern]
---

# subagent 交付转呈前先做秒级抽验：grep 验关键条款落位，bash 验产物实存

## Scenario

把 spec 生成、出题、调研等任务委托给 subagent 后，会收到"已完成 + 摘要"的返回。摘要可能与实际产物存在三类偏差：关键验收条款只写了占位（如规格里写了"≥5 个真实案例"硬门槛，但调研并未真做、没有真实 URL）、声明的产物文件未实际落盘、摘要转述与文件内容不符。用户对"禁猜禁编"高度敏感，未抽验的转呈一旦被推翻，返工与信任成本远高于秒级抽验。

## Key Signals

- subagent 摘要中出现"硬门槛/必须/≥N"字样的验收条款——最容易出现"条款在、实做无"。
- 摘要声称"已落盘/已实证/已生成"但未附文件路径或路径可疑。
- 交付物将直接呈报用户（而非继续内部加工）——失真会直达用户。

## Essence

转呈前在主会话做**针对性抽验**：用 grep 验证关键验收条款是否真实落位（有实质内容而非空壳），用 read/bash 验证声明的产物真实存在、目录语义与摘要一致。抽验目标是"最可能翻车的点"，不是全量重做——成本秒级，换来转呈可信。

## Approach

1. 从 subagent 摘要中挑出 2–3 个"若不实则整体结论失效"的关键点（硬门槛条款、核心实证声明、关键产物路径）。
2. 条款抽验：grep 关键词于产物文件，确认命中处有实质内容（如案例调研应见真实 URL 与日期字段），非占位描述。
3. 产物抽验：对声明落盘的文件做 read/存在性检查；对声明"目录为配置载体"类语义，用计数实查补证（空目录 count=0 也是有效证据）。
4. 抽验发现缺口：缺口小（个别占位）→ 派回 subagent 或主会话补做后转呈；缺口大（核心未做）→ 如实向用户呈报缺口，不包装。
5. 抽验通过再转呈，且转呈内容以抽验后的事实为准，不照抄 subagent 措辞。

## Faster Next Time

- 一句话纪律：**"subagent 说完成 ≠ 完成；转呈前花 30 秒 grep 一下最要命的条款"**。
- 优先抽验带数字的硬承诺（≥N、100%、全绿）——数字最容易被占位也最容易被用户复核。
- 抽验证据顺手留痕（grep 命中数、计数结果），用户质疑时直接引用，免二次核查。

## Applicability Boundaries

- 适用：任何经 Task/subagent 产出且将进入用户视野或下游流程的交付物（spec/design/调研报告/题目/代码）。
- 不适用：subagent 产出仅作内部草稿、下游还有多道加工与最终验证的场景（终验自然覆盖，无需双重抽验）；对 subagent 全量复核（成本失控，违背抽验本意）。
- 抽验点选择依赖对任务验收标准的理解；上游 spec 中已量化的验收条款是最可靠的抽验清单来源。

## Evidence or Examples

- 本会话实例一：spec-requirement-agent 返回主/子智能体 spec v1 摘要后，主会话 grep"案例"命中 36 处，确认 5.2 社区案例章节已结构化落位；另对 `.codeartsdoer/agent-team/` 与 `agents/` 实查 count=0，把摘要中"疑为配置载体"的推测补成实证（空目录语义存疑入未决）。
- 本会话实例二：出题官返回"50 题已生成"后，先 read 题目文件确认题干真实落盘才开始作答——防"摘要称已出题、文件实际为空"的断链。
- 反面成本参照：若未经抽验直接转呈"5 个社区案例已调研"，而实际条款占位无 URL，用户一句"链接呢"即触发返工与信任折损。