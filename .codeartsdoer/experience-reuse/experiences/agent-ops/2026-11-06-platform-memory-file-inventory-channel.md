---
id: 2026-11-06-platform-memory-file-inventory-channel
title: 平台记忆层实查通道：无接口时降级为文件式记忆库盘点
category: agent-ops
nature: technique
created_at: 2026-11-06T20:46:59
updated_at: 2026-11-06T20:52:37
tags: [平台记忆, 文件式记忆库, 记忆盘点, frontmatter, 降级路径]
keywords: [memory目录, 工作目录哈希, MEMORY.md索引, type/from字段, 记忆接口缺失, 记忆权威源, 项目级记忆, 个人级记忆, 记忆条目结构, 一致性检查]
problem_patterns: [派工单要求调接口拉取平台记忆列表但平台未提供记忆 API 工具, 需要盘点项目级与个人级记忆却不清楚记忆的真实存储结构, 记忆盘点结果需要权威源而非凭会话印象罗列]
source_sessions: [ses_e4f5c5a83ffefUFnzHFvOEFJCW]
project: Date
severity: medium
quality_score: 91
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-06-codeartsdoer-docs-retrieval, 2026-11-06-memory-staleness-crosscheck-arbitration]
---

# 平台记忆层实查通道：无接口时降级为文件式记忆库盘点

## Scenario
派工单要求盘点三层信息源，其中记忆层指令为"平台记忆列表（项目级+个人级，你调接口拉）"。工具检索确认平台未提供独立的记忆 API 工具，需要找到记忆的真实落盘形态。

## Key Signals
- `tool_search` 检索记忆相关工具，仅返回无关工具——记忆接口确实不存在。
- 用户目录下存在 `~/.codeartsdoer/memory/` 且按工作目录哈希命名的子目录内有成体系的 .md 条目。

## Essence
该平台的记忆层是**文件式记忆库**而非接口服务：按 `<盘符-路径-项目名>` 哈希命名的子目录隔离各项目（如 `C--Users-Administrator-Desktop-Date`），条目为带 frontmatter 的 Markdown（`name` / `description` / `type: project|feedback` / `from: Agent`），`MEMORY.md` 充当索引。"调接口拉记忆"应降级为"实查记忆文件库"，文件库即记忆层的权威源。

## Approach
1. 探查 `~/.codeartsdoer/memory/` 下与当前工作目录对应的哈希子目录（路径转 `C--Users-...-项目名` 形式）。
2. 枚举其中 .md 条目并读 frontmatter：`type` 直接当分类依据，`from` 区分来源。
3. 读 `MEMORY.md` 索引与目录实查双向对照，防孤儿条目。
4. 个人级记忆在本部署中无独立目录，按条目 `type`/`from` 区分层级；确无个人级时如实标注 unknown，不臆造清单。
5. 把文件库作为记忆层权威源输出盘点结论。

## Faster Next Time
- 需要"拉记忆"时直接探查 memory 目录，跳过接口搜索一步。
- frontmatter 的 `type`/`from` 字段可直接用于记忆分类统计与让位判断。
- 子目录名与工作目录的映射规律（`C--Users-Administrator-Desktop-Date`）可复用于跨项目记忆定位。

## Applicability Boundaries
- 适用：CodeArts 系 Agent 平台、Windows 用户目录布局；记忆盘点、记忆维护、记忆 vs 知识库一致性检查类任务。
- 不适用：以服务端存储为主的 Agent 平台（先做一次 tool_search 证实有无记忆接口再定路径）；记忆目录被重定位或改名的部署。

## Evidence or Examples
- 实查：`C:\Users\Administrator\.codeartsdoer\memory\` 下含 `C--Users-Administrator-Desktop-Date/`（14 条目：MEMORY.md + 9 篇带 frontmatter 记忆 + 4 个状态 json）、`C--Users-Administrator-Desktop-Agent/`、status.json。
- 条目示例：`learn-before-claim-failure.md`（type: feedback）、`hyra-results-reference-repo.md`（type: project），均 `from: Agent`。
- `tool_search "+记忆 接口"` 无记忆 API 命中，证实降级路径必要。