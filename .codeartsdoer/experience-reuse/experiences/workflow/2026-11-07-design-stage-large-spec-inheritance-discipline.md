---
id: 2026-11-07-design-stage-large-spec-inheritance-discipline
title: SDD design 阶段承接大型规格三纪律（现状逐一实读、EARS 追溯表防漏、开放裁决预设承接）
category: workflow
nature: methodology
created_at: 2026-11-07T23:18:09
updated_at: 2026-11-07T23:51:11
tags: [sdd, design-stage, traceability, spec-inheritance, open-adjudication]
keywords: [design.md, EARS 条款, 需求-设计追溯表, 附录B, 预设方案, 可改判, 前置实读, 转述失真, 大型规格, 防遗漏]
problem_patterns: ["上游规格 600+ 行且派工单附转述事实包，直接按转述设计导致待改造对象细节失真或条款遗漏", "规格含多个未闭合裁决项，设计阶段自行拍板越权或干等裁决阻塞推进"]
source_sessions: [ses_e497892bfffehuppBc3pcJ5QEO]
project: Date
severity: low
quality_score: 88
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [workflow/2026-11-07-long-design-doc-chunked-write-structure-verify, workflow/2026-11-07-sdd-spec-stage-fact-verification-and-scope-bounding, workflow/2026-11-07-secondhand-summary-insufficient-verify-primary-source, workflow/2026-11-07-sdd-spec-to-tasks-coverage-mapping, agent-ops/2026-11-07-dispatch-brief-embedded-fact-pack, workflow/2026-11-07-overturned-closure-decision-revision-pattern]
---

# SDD design 阶段承接大型规格三纪律（现状逐一实读、EARS 追溯表防漏、开放裁决预设承接）

## Scenario

SDD 流水线 design 阶段（spec-design-agent 角色），上游是 v4 版大型规格（本例 701 行，含 EARS 条款、门禁定义、附录 A 覆盖映射与附录 B 待裁决项），且历经多轮用户裁决修订。派工单已附"项目关键事实（已实查）"转述包。设计的硬要求：严格承接全部 EARS 条款与门禁定义，"不得遗漏、不得私自更改需求口径"；规格中仍有 5 个未闭合裁决项（B2–B6）需在设计阶段处理。单人协作、单任务粒度，design 质量直接决定 tasks/实施阶段是否方向性返工。

## Key Signals

- 派工 prompt 明示"先完整读取该文档（含附录 A 覆盖映射与附录 B 待裁决项）……不得遗漏、不得私自更改需求口径"——承接完整性本身是验收项，不是默认诚意。
- 派工单嵌入的是**结论级转述**（如"出题官现状'按任意材料清单出题'"），而设计需要**逐字级现状**（SOP 步骤原文、frontmatter 字段、纪律红线措辞）——转述粒度与设计粒度不匹配。
- 规格自带"待用户裁决事项见附录 B"且其中一项（B1）曾依用户意见闭合后被新意见推翻重闭——裁决状态不稳定，设计若自行固化即埋返工点。

## Essence

design 阶段的忠实承接靠三条纪律合力：①**转述不替代实读**——派工事实包只是导航图，spec 正文引用的现状文件（尤其"待改造对象"原文）与能力翻译来源必须逐一实读，结论级转述撑不起逐字级设计；②**追溯表把"不得遗漏"变成可核对**——"EARS 条款→设计章节"追溯表先建骨架后回填章节号，遗漏在表上显形而非靠感觉；③**开放裁决预设承接**——未闭合裁决项按预设方案继续设计、单列承接章节逐项落位、每项标注"最终以用户裁决为准，可改判"，既不让设计阻塞在裁决悬置上，也不越权把预设固化成结论。

## Approach

1. **纪律一（现状实读清单）**：动笔前从 spec 正文提取全部文件引用与来源引用，逐一实读——本例含两个待改造子智能体 SOP 原文、项目事实表、知识库索引、注册表、状态机运行规则、MCP 配置，另查看参考仓库顶层结构（能力翻译 C1/C3/C4 的来源实证）。转述包只当索引用，不当依据用。
2. **纪律二（追溯表防漏）**：design 固定设"需求-设计追溯表（EARS 条款→设计章节）"章节；写前先从 spec 列出条款/门禁清单作表骨架，每写完一章立即回填章节号；收工时表上不得有空行——空行即漏承接。
3. **纪律三（预设承接句式）**：对每个开放裁决项用固定三段式落位——"预设方案=X；设计落位=design 第 N 章；最终以用户裁决为准，可改判"；全部裁决项集中单列一章"承接 spec 附录 B 预设方案"，使评审者一眼区分"已定口径"与"待改判口径"。
4. **承接约束传导**：设计正文只做"怎么实现"，不重述更不改需求口径；发现 spec 内部矛盾或预设不可行时，登记为设计风险/待确认项回呈，不静默偏离。

## Faster Next Time

- 动笔前三问：spec 正文引用了哪些文件？都读过原文吗？哪些裁决项未闭合？三问有答案才动笔。
- 追溯表骨架在建 design 骨架时同步建好，与章节分块写入并行回填，成本近零；事后补表必漏。
- 裁决承接句式直接复用，禁写成"待定"或留空——"可改判"标注就是阻塞解除器。
- 派工单说"已实查"≠自己免查：主智能体实查的粒度服务于派工摘要，不是服务于你的设计细节。

## Applicability Boundaries

- 适用：SDD design 阶段承接 500+ 行含 EARS 条款/门禁/附录裁决项的规格；派工单附转述事实包；规格经多轮修订裁决状态不稳定。
- 不适用：小型特性（条款十余条内，追溯表是负担）；spec 无开放裁决项（纪律三整体省略）；一次性原型（不需追溯与承接章）。
- 与相邻经验的边界：`2026-11-07-sdd-spec-stage-fact-verification-and-scope-bounding` 管 spec 动笔前的现状核实三件套（需求侧）；本条管 design 动笔前的承接实读（设计侧）。`2026-11-07-secondhand-summary-insufficient-verify-primary-source` 管外部网页材料依据等级；本条管项目内部转述包仍需实读原文。`2026-11-07-long-design-doc-chunked-write-structure-verify` 管"怎么写"（分块落盘与结构自检）；本条管"写什么、怎么承接"——两条互补，同一会话可同时适用。`2026-11-07-overturned-closure-decision-revision-pattern` 管 spec 阶段闭合裁决项被推翻后的重新闭合处置（本条 Evidence 中 B1 被 U5 推翻事件即其应用案例）；本条纪律三管 design 阶段对开放裁决项的预设承接——同一裁决项生命周期的上下游环节。
- 反模式：按派工转述直接设计（细节失真）；design 抄一段 spec 条款算"承接"却无追溯表（遗漏不可见）；把预设方案写成定论（用户改判时整章返工）；干等裁决不开工（进度阻塞且用户并未要求等待）。

## Evidence or Examples

- 来源会话：ses_e497892bfffehuppBc3pcJ5QEO（2026-11-07，Date 项目 sdd_agent_refactor 特性 design 阶段，spec-design-agent 子智能体执行，17 条消息）。
- 实读清单实录：spec.md 全文 701 行（分两次读，含附录 A/B）；examiner.md（30 行，SOP/红线原文）；grader.md（27 行）；notes/项目事实表.md；notes/知识库索引.md；notes/注册表.md；notes/阶段状态机运行规则.md；.codeartsdoer/mcp/mcp_settings.json；D:\refs 三参考仓库顶层结构（Cairn/p3c/deepseek-super-agent）。
- 产物与核验：design.md 645 行落盘，bash 一次核验（68558 字节 + 645 行 + 8 个章节标题清单）通过；第六章即"EARS 条款→设计章节"追溯表；第五章"承接 spec 附录 B 预设方案"将 B1–B6 逐项落位并统一标注"可改判"。
- 裁决不稳定性实证：附录 B1 曾依用户意见 U4 闭合（v3），后被 U5 推翻重新闭合（v4）——印证"可改判"标注的必要性。
- ROI：一次成稿无返工，完工核验一次通过，设计摘要直接可呈报；对比 spec 阶段多轮修订成本，前置实读约 8 次文件操作换取零方向性偏差。