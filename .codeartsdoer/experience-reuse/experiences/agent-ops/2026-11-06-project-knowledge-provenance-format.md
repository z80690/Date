---
id: 2026-11-06-project-knowledge-provenance-format
title: project-knowledge 文档粒度与 code-links 溯源格式清单
category: agent-ops
nature: technique
created_at: 2026-11-06T19:16:59
updated_at: 2026-11-06T19:19:17
tags: [project-knowledge, provenance, code-links, wiki-format]
keywords: [code-links.json, wiki_section, code_refs, module_id, 行号必填, 5KB, 250字, 粒度控制, 溯源, collaboration_conventions, 敏感信息自查]
problem_patterns: [生成带溯源 JSON 的知识文档时 wiki_section 与正文标题不一致, code_refs 缺行号或路径不相对仓库根导致溯源无效, 知识文档超长导致检索信噪比下降]
source_sessions: [ses_e4f72f611ffeUG3O7qZ4WymsNB]
project: Date
severity: low
quality_score: 85
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-06-doc-repo-zero-extraction-knowledge-gen]
---

# project-knowledge 文档粒度与 code-links 溯源格式清单

## Scenario
生成带溯源文件（.code-links.json）的 project-knowledge wiki 文档（如 collaboration_conventions 等主题类别）时，需同时满足文档粒度上限与机器可解析的溯源格式约定，否则下游模块判溯源无效或检索信噪比下降。

## Key Signals
- 派工单给出的格式模板中明确：wiki_section 须逐字复制文档中 "## " 后的标题文本；code_refs 格式为 "文件路径:行号"，行号必填。
- 若 wiki_section 与正文标题不一致、code_refs 缺行号或路径写成绝对路径，溯源即失效。

## Essence
溯源文件的价值取决于机器可解析性：wiki_section 必须逐字等于正文小节标题，code_refs 必须是"仓库相对路径:行号"；粒度上限（全文 ≤5KB、每节 ≤250 字，清单类小节豁免）保证检索信噪比。凡某小节阅读或引用过的文件都要登记到该小节 code_refs。

## Approach
1. frontmatter：kind=project_knowledge、category、title、scopes=["**"]、updated_at；中文语言下保留中文标题、删除英文标题。
2. 正文小节标题即 wiki_section 来源，生成 JSON 时逐字复制（如"概述""关键文件与位置""架构与约定""开发者应遵守的规则"）。
3. code_refs 写"文件路径:行号"，路径相对仓库根目录，行号必填；按小节登记阅读/引用过的所有文件。
4. 无对应模块时 module_id 置 null。
5. 粒度：全文 ≤5KB、每节 ≤250 字（规则/条目清单类豁免）；定稿前做敏感信息自查（密钥/密码/token 零出现）。
6. 交付时汇报文档与 JSON 路径及各小节字数概要，作为完成证据。

## Faster Next Time
- 边写正文边登记 code_refs（读了哪个文件、用于哪个小节），比写完再补查更快且不漏。
- 一次成稿顺序：读数据源 → 定标题 → 逐节填写并同步登记 code_refs → 尺寸校验 → 敏感信息自查。

## Applicability Boundaries
- 适用：project-knowledge 生成派工单模板（collaboration_conventions 等类别）及同类"wiki + 溯源 JSON"双产物任务；格式约定平台无关。
- 不适用：无溯源要求的普通 README/文档撰写；module_id 是否为 null 取决于各仓库的模块划分方式，需按派工单确认。

## Evidence or Examples
- 实测产物：collaboration_conventions.md（3121B，四节）+ collaboration_conventions.code-links.json（1976B，module_id=null，4 个小节均含逐行 code_refs，如 "docs/项目协作公约-最终稿.md:1"），全部 ≤ 限额。