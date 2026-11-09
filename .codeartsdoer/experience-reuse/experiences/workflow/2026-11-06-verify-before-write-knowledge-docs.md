---
id: 2026-11-06-verify-before-write-knowledge-docs
title: 知识库生成规范文档先核实仓库实际状态再动笔（零编造法）
category: workflow
nature: methodology
created_at: 2026-11-06T19:25:40
updated_at: 2026-11-06T19:45:16
tags: [零编造, 核实先行, 规范文档生成, 行号溯源, 知识库]
keywords: [project-knowledge, code-links, 行号溯源, glob 核实, 外部参考文档, 纯文档仓库, 反编造, 字数约束, wiki_section, code_refs]
problem_patterns: [生成规范文档时派工单背景描述与仓库实际状态不符, 参考文档内容需要可溯源到源文件行号]
source_sessions: [ses_e4f704706ffe9zCUbnmwlEAtH8]
project: Date
severity: medium
quality_score: 85
hit_count: 1
last_hit_at: 2026-11-08T02:17:44
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-06-verify-claimed-prerequisites-before-research, 2026-11-06-project-knowledge-provenance-format, 2026-11-06-doc-repo-zero-extraction-knowledge-gen]
---

# 知识库生成规范文档先核实仓库实际状态再动笔（零编造法）

## Scenario
为纯 Markdown 知识库仓库（Obsidian 库，无源代码）生成"外部平台参考"类 project-knowledge 规范文档。派工单给出主题、数据源路径、输出路径、模板与格式约束（全文 ≤5KB、每节 ≤250 字）。此类任务由 subagent 独立执行，无法中途向派工方确认，背景描述与仓库实际状态可能不一致。

## Key Signals
- 派工单声称"本仓库已有 find-skills、grill-me、lazy-exec、ruleinit、skill-writer 等技能（位于 .codeartsdoer/skills/）"，但这是背景叙述而非核实过的事实。
- 输出文档若照抄该叙述，会把不存在的目录/文件写成现状，污染知识库。
- 触发核实动作：对 `.codeartsdoer/` 做 glob，实际仅发现 mem-exp-config.json、package.json、.gitignore 三个文件——skills/ 技能目录尚未落地。

## Essence
派工单中的背景描述只是"声称"，不是证据。文档现状性表述必须以当日 glob/read 核实结果为准；所有概念性内容必须溯源到数据源文档的具体行号。零编造 = 现状核实 + 源文行号双重锚定。本次据此把表述从"已有技能"改为"技能目录尚未落地"，文档与仓库真实状态保持一致。

## Approach
1. 动笔前先对涉及目录做 glob（必要时 read），核实派工单声称的目录/文件是否真实存在。
2. 完整阅读全部指定数据源文件，记录关键结论所在行号；禁止引用文档中不存在的 Skills 或概念。
3. 现状性表述（"已有 X"）只写核实过的事实；与派工单叙述冲突时以核实结果为准。
4. 同步生成 .code-links.json 溯源：`wiki_section` 逐字复制文档中 `##` 后的标题文本、`code_refs` 为 `"文件路径:行号"`（路径相对仓库根，行号必填）等格式细则见关联经验 project-knowledge-provenance-format；凡某小节阅读/引用过的文件都记入该小节。
5. 遵守粒度约束（全文 ≤5KB、每节 ≤250 字），交付时汇报各小节字数概要与 code_refs 总数，便于验收。

## Faster Next Time
- 把"glob 核实 → 读源标行号 → 据实表述 → 行号溯源"固定为知识库文档生成的四步前置检查，可一次避免返工与编造风险。
- 警惕信号：派工单中出现"本仓库已有/已存在……"类现状断言且未附证据时，必须先核实再写。
- 溯源 JSON 在写文档时同步整理行号，比写完后回头补行号省一轮通读。

## Applicability Boundaries
- 适用：纯文档/知识库仓库的规范文档、参考文档、project-knowledge 类生成任务；subagent 独立执行的派工场景。
- 不适用：代码仓库中与代码结构强绑定的文档（应直接以代码为准）；用户在线交互可即时确认事实的场景（可直接询问，无需此流程）。
- 反模式：把派工单描述直接当作事实写入文档；为凑溯源数量引用未实际阅读的文件。
- 与《派工单声称"已核实"的结构性前提，动手前仍用特征检索秒级复核》的分工：那条管调研/借鉴类任务链启动前的结构性前提证伪；本条管知识文档生成过程中的现状核实与行号溯源。

## Evidence or Examples
- 项目 Date（Obsidian 知识库）：派工单称 `.codeartsdoer/skills/` 已有 5 个技能，glob 核实仅 mem-exp-config.json、package.json、.gitignore；文档按"技能目录尚未落地"表述写入。
- 数据源：docs/官方文档-码道热门Skills清单-desktop0003.md（15 个 Skills 分五大类，总览表在第 6-22 行）、docs/官方最佳实践-如何写好一个Skill-bp0010.md（三要素/三层架构/三类资源在第 25-66 行）。
- 交付验证：全文约 3.4KB（≤5KB 达标）、三小节各 ≤250 字、code-links.json 覆盖 2 小节共 12 条 code_refs、行号逐条核对、无敏感信息。