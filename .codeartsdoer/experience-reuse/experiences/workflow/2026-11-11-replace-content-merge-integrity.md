---
id: 2026-11-11-replace-content-merge-integrity
title: replace_content 整节替换的原文保全模式：脚本提取原文 + 计数断言验证
category: workflow
nature: technique
created_at: 2026-11-11T00:59:52
updated_at: 2026-11-11T01:13:34
tags: [document-revision, patch, replace-content, integrity-check, merge-safety]
keywords: [replace_content, 整节替换, 原文保留, 小节修订, wiki 文档, patch json, 完整性校验, 脚本提取, 合并修订, 断言验证]
problem_patterns: ["整节替换类文档修订需保留原有条目时，手工复制原文易丢段漏段且无校验手段", "replace_content 覆盖式合并缺乏可验证的原文完整性防线"]
source_sessions: [ses_e39b13292ffen9kaFrNthTsWmm]
project: Date
severity: medium
quality_score: 85
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-11-repo-form-fact-drift-minimal-patch-s1, 2026-11-08-wiki-section-revision-patch-json-mode, 2026-11-08-utf8-nobom-write-verify-first-byte]
---

# replace_content 整节替换的原文保全模式：脚本提取原文 + 计数断言验证

## Scenario

修订知识库/Wiki 文档中的"集合型小节"（术语表、条目清单、规则列表），修改方式为 replace_content 整节替换，约束是"原有 N 个条目原文不动，只在末尾追加新条目"。典型规模：单文档单节，既有条目十几条，新增条目若干，原文散布在数百行文档中。

## Key Signals

触发本模式的信号：派工单明确要求"new_content 必须包含原有条目的完整原文（从当前文档复制），确保合并后不丢失原内容"。痛点在于 replace_content 是覆盖式写入，手工复制原文没有任何校验手段，一旦丢段，合并即不可逆，只能靠合并后人工逐条比对才能发现。

## Essence

把"确保原文不丢"从主观确认变成落盘前的可执行断言：原文不由人写，由脚本从当前文档动态提取作为合并基底；提取是否完整，用"原条目计数 + missing_original 空列表"断言验证。新内容只描述增量，原文完整性交给提取与断言两道机械防线。

## Approach

1. 写一次性构建脚本：解析当前文档，按小节结构提取原有全部条目原文作为合并基底（不手工复制）。
2. 脚本内拼接：原文全文 + 新增条目 → 目标小节 new_content；概述类小节直接用新写文本并同步统计字数。
3. 产物（patch JSON）用 json.dump(ensure_ascii=False) + 二进制写落盘，保证 UTF-8 无 BOM 与合法转义。
4. 落盘后四重验证：BOM 标志=False；JSON 可解析；字数/长度约束达标（如概述 ≤200 字）；原条目计数与 missing_original=[] 断言通过（如原 13 条 + 新 7 条 = 合并 20 条）。
5. 对 patch 结构做二次校验（section 标题、action、各节内容长度、code_refs 数量）后，删除临时构建脚本，只保留产物。

## Faster Next Time

- 合并类 patch 动笔前三问：原文从哪来（当前文档提取，不凭记忆）；完整性怎么证明（计数断言 + missing_original）；落盘编码怎么保证（json.dump + 二进制写 + BOM 校验）。
- 警告信号：发现自己开始手工粘贴超过一屏的"原有内容"进 new_content，立即停手改用脚本提取。
- ROI：本模式实测一次通过零返工，且验证输出（BOM/字数/计数/missing_original）可直接作为交付证据附在汇报里。

## Applicability Boundaries

- 适用：replace_content/整节替换且需保留原内容的文档合并修订；术语表、清单、表格类小节追加条目；以结构化 patch 文件（JSON）为载体的修订流水线。
- 不适用：全新小节（无原文可保留，直接撰写即可）；单点局部修改（精确 edit 更轻量）；原文本身已损坏或需整体重写的场景（提取旧文无意义）。
- 与相邻经验分工：repo-form-fact-drift-minimal-patch-s1 管"动笔前影响级别收缩与漂移类型判定"；wiki-section-revision-patch-json-mode 管"patch 载体契约与口径逐字比对"；utf8-nobom-write-verify-first-byte 管"BOM 字节级验证手段本身"；本条管"整节替换中原文保全的脚本提取与计数断言机制"。

## Anti-pattern

- 手工复制原内容拼进 new_content，声称"我保留了原文"但无任何断言验证。
- 只验证 JSON 合法性，不验证业务约束（条目计数、字数上限、missing_original）。

## Evidence or Examples

- 来源会话 ses_e39b13292ffen9kaFrNthTsWmm（2026-11-11）：修订知识库业务术语表，13 个既有术语原文不动 + 追加 7 个新术语，概述改写且限 200 字。
- 实测验证输出：`size: 7603 BOM: False / overview_len: 189 / original_terms: 13 total_terms: 20 / missing_original: []`；二次校验 `[('概述','replace_content',189,1), ('术语列表','replace_content',2589,7)]`。
- 产物为 UTF-8 无 BOM 的 patch JSON；临时构建脚本在验证通过后即删除。