---
id: 2026-11-06-doc-repo-zero-extraction-knowledge-gen
title: 纯文档仓库知识生成：零预提取产物属正常，数据源逐字核对防编造
category: agent-ops
nature: technique
created_at: 2026-11-06T19:16:59
updated_at: 2026-11-06T19:19:17
tags: [doc-only-repo, project-knowledge, hallucination-prevention, subagent-task]
keywords: [纯文档仓库, 零预提取, endpoints, imports, pkg_deps, symbols, Obsidian, 知识库生成, 禁止编造, 逐字核对, 溯源]
problem_patterns: [纯 Markdown 仓库预提取产物 0 条被误判为异常, 生成规范知识文档时无代码索引可依赖, 同一规范存在多个同源文件需确认以哪个为准]
source_sessions: [ses_e4f72f611ffeUG3O7qZ4WymsNB]
project: Date
severity: medium
quality_score: 90
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-06-project-knowledge-provenance-format, 2026-11-06-codeartsdoer-docs-retrieval]
---

# 纯文档仓库知识生成：零预提取产物属正常，数据源逐字核对防编造

## Scenario
对纯 Markdown 文档仓库（如 Obsidian 知识库，无任何源代码）执行 project-knowledge / 规范知识文档生成任务（典型为派工单形式的 subagent 任务）时，预提取产物（endpoints/imports/pkg_deps/clients/symbols）全部为 0 条，且没有代码索引可依赖。

## Key Signals
- 仓库状态显示 0 源文件、仅有 .md 文档——这是仓库形态信号，不是任务异常信号。
- 预提取产物 0 条与"仓库无源码"自洽；若误判为故障，会陷入无意义的代码索引排错循环，甚至编造不存在的 endpoint/symbol。
- 同一规范可能存在多个同源文件（如 docs 下的最终稿与 .codeartsdoer/rule/ 下的 .mdc），须确认一致性后才能定稿。

## Essence
零源码仓库的静态预提取产物必然为 0，知识文档的真实数据源是 docs/、规则文件等 Markdown 本身。生成前完整阅读全部数据源并逐字核对同源文件一致性，是防编造（hallucination）的硬约束；每条结论回溯到"文件:行号"形成兜底。

## Approach
1. 先判定仓库形态（0 源文件/仅 .md → 纯文档仓库），据此把"预提取产物为 0"判为正常，不进入排错循环。
2. 完整阅读派工单指定的全部数据源文件，不留节选。
3. 多个同源文件逐字对比：一致则以该内容为准一次成稿；不一致时以派工单指定的"最终稿"为准并如实记录差异。
4. 只写数据源中存在的规则/事实，禁止编造不存在的条目；每条规则在溯源 JSON 中落到"文件路径:行号"。
5. 交付前用 bash 校验输出文件大小并汇报各小节字数概要，作为完成证据。

## Faster Next Time
- 看到"0 endpoints / 0 symbols"先查仓库形态再决定是否报警，可避免对文档仓库做无效排错。
- 同源文件逐字一致即无需再向用户求证，直接定稿。
- 用溯源行号兜底防编造：每条规则都能回溯到原文行，检查成本极低。

## Applicability Boundaries
- 适用：无源代码的纯文档仓库上的知识/规范文档生成；CodeArts Agent 及一般 subagent 派工模式，平台无关。
- 不适用：有源代码的仓库——预提取产物为 0 在那里可能真是索引故障，需另行排查。

## Evidence or Examples
- 实测：docs/项目协作公约-最终稿.md 与 .codeartsdoer/rule/项目协作公约.mdc 逐字一致（同为 7 条协作规则），一次定稿。
- 产物验证：collaboration_conventions.md（3121B）与 collaboration_conventions.code-links.json（1976B）写入成功，bash 大小校验通过，未编造任何规则。