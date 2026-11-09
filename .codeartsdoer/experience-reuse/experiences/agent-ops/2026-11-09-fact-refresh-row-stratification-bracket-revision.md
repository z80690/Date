---
id: 2026-11-09-fact-refresh-row-stratification-bracket-revision
title: 状态刷新变更行的行级再分层：纯值刷新行只刷行号、机制结构口径行联动简介括注，replace 限括注级增量
category: agent-ops
nature: decision
created_at: 2026-11-09T00:34:16
updated_at: 2026-11-09T01:21:36
tags: [wiki修订, 状态刷新判定, 行级再分层, 括注级修订, 简介文档]
keywords: [line_number_only, replace_content, 值刷新, 结构口径, 括注修订, 字数净增上限, 模块简介, 架构设计小节, code_refs 原行号基线, patch JSON, 只读 subagent]
problem_patterns:
  - 状态事实源值刷新（日期/哈希/任务号/核验记录）触发简介类 Wiki 小节修订派工，默认全零修订会漏掉变更行中夹带的机制结构口径变化，架构设计小节括注残留旧结构描述
  - 简介类小节 replace_content 时整段重写导致篇幅膨胀或误写入项目状态值，不知如何限定修订粒度
source_sessions: [ses_e440a1070ffevPz9KMBCv7S4AC]
project: Date
severity: low
quality_score: 84
utility_score: 80
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: A
related_experiences: [2026-11-08-wiki-section-tiered-revision-judgment-contract, 2026-11-08-wiki-section-same-layer-action-criteria, 2026-11-08-wiki-section-revision-patch-json-mode, 2026-11-09-glossary-status-refresh-zero-revision-criterion]
---

# 状态刷新变更行的行级再分层：纯值刷新行只刷行号、机制结构口径行联动简介括注

## Scenario

以只读修订 subagent 身份接收模块简介类 Wiki 文档（描述"模块提供什么能力/如何组织"的索引型文档）的小节级修订派工：本例受影响小节为概述与架构设计，变更源是项目状态事实表的刷新（提交历史、核验日期、机制状态、环境事实、特性进度）。派工单预判概述→line_number_only、架构设计→replace_content，并给出兜底约束（状态值一律不写入正文）与字数净增上限。任务边界：只输出结构化 patch JSON，禁止写文件。

## Key Signals

- 概述小节关注"各文件提供什么能力"：状态值刷新不改变任何文件职责 → 预判 line_number_only 成立，无需改正文。
- 架构设计小节正文以括注承载各机制的内部结构（如"某运行规则（七态枚举 ST0–ST5+SX 与迁移守卫）"）：事实表中"事件钩子 3 类通道结构生效（通道 A 平台原生+通道 B 动作检查点别名+通道 C 迁移守卫别名；载体=运行规则 §4）"这一行不是值刷新，而是机制结构口径变化，与该括注同层面。
- 同一变更文件里两种形态并存：第 21 行仲裁顺序、第 25/26 行定时任务与交付物等是纯值刷新；第 22 行事件钩子通道结构是结构口径刷新——"状态刷新派工"不等于全部零修订。
- code_refs 基线：未变更文件的引用行号维持 wiki-index 原值（如 :3），变更文件用实读核对行号（导语 :3、仲裁顺序 :21、事件钩子 :22、维护机制 §9 溯源 :24）。

## Essence

**状态刷新派工要做行级再分层，而非文档级二分。** 状态事实源的变更行逐行分两类：纯值刷新行（日期、哈希、ID、进度、环境事实——回答"状态是多少"）不触发任何简介类正文修订，小节仅 line_number_only；机制结构口径行（描述"机制如何组织/由几部分构成/载体在哪"）才可能波及简介类文档中对应机制的结构括注。命中时修订粒度限定为**括注级增量**：保留原文表述框架与既有口径（七态枚举照写），仅在括注内补新结构口径（三类通道），并设字数净增上限防止简介膨胀。简介类文档（概述/架构设计）与术语表类文档在状态刷新下的结论可以不同：前者可能局部 replace，后者倾向全零修订——差异来源是正文承载物不同（机制结构描述 vs 领域概念定义）。

## Approach

1. **逐行分类变更内容**：对状态事实源的每行变更问"这行回答的是状态值还是机制结构"——日期/哈希/ID/进度/环境 → 纯值刷新；通道构成/载体归属/条数组织/顺序规则 → 结构口径。
2. **纯值刷新行处理**：验证简介小节正文是否只做职责/组织级描述（未写入任何状态值）→ 该小节 line_number_only，new_content 为 null，仅核对 code_refs。
3. **结构口径行处理**：在小节正文中定位该机制对应的括注/短语，逐字比对与事实表新口径是否同层面；命中 → replace_content，修订仅落在括注内。
4. **括注级修订三保留**：保留原文段落框架、保留既有正确口径（枚举、四要素等表述原样）、只在括注内补新口径；修订后篇幅与原文等量，净增量控制在派工单上限内（本例原文约 380 字、净增 ≤50 字）。
5. **code_refs 与禁令**：变更文件引用用实读行号，未变更文件维持原索引行号不动；状态值（条数、门禁状态、交付物路径、环境行、定时任务号）一律不写入简介正文，不据此新增编码规范条目。

## Faster Next Time

- 判定口诀：变更行先问"状态值还是机制结构"——状态值 → 只刷行号；结构 → 查简介括注是否同层面。
- 括注修订三保留一上限：保留框架、保留既有口径、只补新口径、净增量设上限——防止简介文档随状态刷新轮次逐步膨胀。
- 警惕信号：见到"状态刷新触发派工"不要照搬术语表场景的"全零修订"结论——先做行级再分层，架构设计类小节可能藏有结构口径联动；反之也不要因个别结构行把概述等职责型小节一起重写。
- 行号成本低：一轮实读即可核对变更文件行号，未变更文件直接沿用原索引行号，不要重新推断。

## Applicability Boundaries

- 适用：状态事实源（事实表/索引/进度台账）值刷新触发的简介类/模块简介 Wiki 小节修订派工；patch JSON 只读 subagent 场景；派工单预置判定预判+兜底约束的判定验证式执行。
- 不适用：术语表/领域概念类小节（走零修订逐条排除与新增术语禁令，见 glossary-status-refresh-zero-revision-criterion）；领域概念或条目口径本身的大改版（走 tiered-revision-judgment-contract 节级分流）；授权直改的普通文档编辑。
- 与相邻经验分工：`wiki-section-tiered-revision-judgment-contract` 管"改与不改"的通用节级分流与判定预判式派工，本条是其前置细化——把"变更是否同层面"下沉到变更行的行级再分层；`wiki-section-same-layer-action-criteria` 管逐句比对细则与格式失真自查；`wiki-section-revision-patch-json-mode` 管建议-合并分离与落盘契约；`glossary-status-refresh-zero-revision-criterion` 与本条构成配对——同一状态刷新源在不同文档类型下结论不同（术语表零修订 vs 简介括注级增量），选型以正文承载物为准。
- 证据等级：单次实战闭环（2 小节判定 + 括注级 replace + code_refs 实读核对 + patch JSON 结构合规）；合并应用结果在本 trace 之外，判据在"状态刷新×简介文档"场景下的稳定性待复用检验。

## Evidence or Examples

- 源会话 ses_e440a1070ffevPz9KMBCv7S4AC（@general 修订 subagent，trace 内联提供，修订 codebase-knowledge/知识库笔记.md 概述与架构设计两小节）。
- 行级再分层实证：notes/项目事实表.md 第 21 行（三层仲裁顺序）、第 25/26 行（Wiki 定时任务、pd004 交付物）判纯值刷新；第 22 行（事件钩子 3 类通道结构生效，载体=notes/阶段状态机运行规则.md §4）判结构口径刷新。
- 括注级修订实证：架构设计小节"阶段状态机运行规则（七态枚举 ST0–ST5+SX 与迁移守卫）"更新为保留七态枚举、括注补"事件钩子三类通道：平台原生/动作检查点/迁移守卫别名，载体 §4"；知识库维护机制括注补"§9 钩子定义溯源"；概述判 line_number_only（状态刷新未改变任何文件职责）。
- 字数控制实证：架构设计原文约 380 字，修订净增量控制在 50 字内（上限 430 字），未写入 6 条规矩、M1-M7 门禁、pd004、Maven/P3C 等任何状态值。
- code_refs 实证：patch 输出 notes/项目事实表.md:3/:21/:22/:24（实读核对），notes/知识库索引.md:3、notes/知识库维护机制.md:3、notes/阶段状态机运行规则.md:3 均维持 wiki-index 原行号（三个文件未变更）。