---
id: 2026-11-06-codeartsdoer-docs-retrieval
title: 码道官方文档检索通道：llms.txt 索引直达全文
category: agent-ops
nature: technique
created_at: 2026-11-06T18:41:59
updated_at: 2026-11-06T18:45:59
tags: [codeartsdoer, official-docs, documentation-retrieval, llms-txt]
keywords: [码道, CodeArts Agent, 官方文档, support.huaweicloud.com, llms.txt, 文档索引, 知识库为空, 文档站不可达, webfetch]
problem_patterns: [docs.huaweicloud.com 上找不到码道文档或连接失败, 项目知识库/企业知识库为空无结果, 需要官方口径核实平台配置项却无检索入口]
source_sessions: [ses_e51adb269ffeqfVMdEGO1eP4xa]
project: Date
severity: low
quality_score: 93
hit_count: 3
last_hit_at: 2026-11-06T19:43:20
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-06-codeartsdoer-rule-init, 2026-11-06-codeartsdoer-rule-vs-skill, 2026-11-06-network-direct-connect-diagnosis]
---

# 码道官方文档检索通道：llms.txt 索引直达全文

## Scenario
需要核实码道（CodeArts Agent）平台功能的官方口径——配置项约束、最佳实践、机制说明（如规则数量、SKILL.md 规范、优先级）——而常规入口全部失灵时。

## Key Signals
- `docs.huaweicloud.com` 对码道内容不可达：webfetch 多次报 `Unable to connect`（该域不含码道文档）。
- 本地 Knowledge 工具报 "Wiki documents not found"、企业 RagSearch 报 "No relevant content found"——知识库为空，属正常现象而非故障。
- 可靠信号：本地系统技能 `codeartsagent-doc-guide` 自带官方文档索引链接，这是预授权检索入口。

## Essence
码道官方文档实际托管在 `support.huaweicloud.com`（不是 docs 域），且提供机器友好的索引文件 `llms.txt`：一个文件列出全部文档的标题、链接（.md 直链）与摘要，逐篇可直接拉取全文，无需逐页爬取。

## Approach
1. 读本地系统技能 `codeartsagent-doc-guide` 的 SKILL.md，获取官方索引 URL。
2. webfetch 拉取 `https://support.huaweicloud.com/codeartsagent/llms.txt`（约 68KB，覆盖产品介绍/计费/用户指南/FAQ/最佳实践全部分类）。
3. 将索引存为本地临时文件，用 grep 按关键词定位目标文档条目（如搜"规则""技能""经验"）。
4. 按定位到的 `.md` 直链逐篇 webfetch 拉取全文；大文档可存本地临时文件供后续 grep 复用。

## Faster Next Time
- 一次索引（68KB）替代全网试错：先拿 llms.txt 再定位，比直接猜 URL 快一个数量级。
- 拉到的官方原文存本地文件后可反复 grep，避免重复请求。
- FAQ 类问题（报错信息）优先在索引里搜 FAQ 分类，官方 FAQ 常有现成解。

## Applicability Boundaries
- 适用于华为云码道 CodeArts Agent 产品文档；其他华为云产品（ECS/OBS/RDS 等）走各自文档域，此通道不通用。
- 外网受限环境下实测 support 域仍可达（与 GitHub 直连被重置并存）；若 support 域也不通，则该通道失效，如实报告不可编造。
- 知识库为空是状态不是错误，不要重复探测知识库。

## Evidence or Examples
- 实测：llms.txt 拉取成功（68527 字节）；`codeartsagent_ug_0019.md`（规则）、`codeartsagent_ug_0024.md`（技能）、`codeartsagent_bp_0006.md`（规则实战）全文到手。
- 实测失败对照：docs.huaweicloud.com 三次 `Unable to connect`；raw.githubusercontent.com `socket closed`；GitHub API readme 端点 403/rate limit——多通道齐备便于交叉验证。