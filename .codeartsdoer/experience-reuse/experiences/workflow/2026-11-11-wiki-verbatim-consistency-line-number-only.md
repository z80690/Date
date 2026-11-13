---
id: 2026-11-11-wiki-verbatim-consistency-line-number-only
title: 术语表同步修订的零漂移分支：逐字比对全一致时两小节均 line_number_only
category: workflow
nature: decision
created_at: 2026-11-11T02:55:27
updated_at: 2026-11-11T10:46:07
tags: [术语表同步, 零漂移判定, patch决策, 逐字比对, code_refs刷新]
keywords: [line_number_only, replace_content, code_refs, 逐字比对, 口径一致, 影响级别, 术语表, 目录池, 归档流向, patch JSON]
problem_patterns:
  - 源权威文件新增整节内容且影响级别高（S2、多小节 hash changed）时，误以为术语表/知识文档必须重写正文
  - 同层面小节在口径零漂移场景下误判 replace_content，引入冗余改写噪声
source_sessions: [ses_e393d8e0bffe21Q1PQChRZzqDX]
project: Date
severity: low
quality_score: 84
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: A
related_experiences: [2026-11-08-wiki-section-same-layer-action-criteria, 2026-11-11-replace-content-merge-integrity, 2026-11-08-wiki-section-revision-patch-json-mode, 2026-11-06-verify-before-write-knowledge-docs, 2026-11-11-append-only-zero-drift-prefill-dispatch]
---

# 术语表同步修订的零漂移分支：逐字比对全一致时两小节均 line_number_only

## Scenario

知识库/Wiki 的业务术语表随源权威文件（如 README）变更做小节级同步修订派工：修订者以 patch JSON 交付，action 为 `replace_content` 或 `line_number_only`，且被明确禁止直接修改 wiki .md。本例源文件新增了三个整节内容（目录池十目录表格、运行方式、红线摘要），影响级别 S2、概述与术语列表两个小节 hash 均为 changed——表面信号强烈指向"必须重写正文"。

## Key Signals

- 高影响信号（易误判）：影响级别 S2、多个小节 hash changed、源文件新增整节表格/章节。
- 实际判定信号（须实读才能获得）：新增章节与术语表现有定义逐字比对后口径完全一致——概念未变，只是行号位移与佐证内容变多。

## Essence

影响级别与变更规模不是 patch 动作的决策依据，逐字比对结论才是。"同层面"只把小节列为 replace 候选；当候选小节与新口径比对零漂移时，最终动作仍是 `line_number_only` 仅刷 code_refs。与权威载体实文逐字比对一致之前不动笔，是防误改的闸门。

## Approach

1. 实读源权威文件全文与 wiki 现有正文，禁凭派工单片段动笔。
2. 把源文件新增内容拆成"锚点实体"逐项对照：数量型定义按条目数核对（如目录池十个目录及其归档流向）、枚举口径逐项核对（如红线四项+白名单口径）、能力清单逐项核对（如底座四类能力）。
3. 判表述归属：源文件新增章节若仍落在概述已引用的表述范畴（如"依据 README 项目定位提炼"），概述正文仍准确，不改。
4. 按比对结论选动作：全部一致 → 每个 affected 小节都出 patch 条目但 action=line_number_only、new_content=null，仅把 code_refs 刷到实文新行号（格式 `文件路径:行号`，行号必填）；发现实质不一致 → 仅对不一致条目 replace_content。
5. section_title 逐字复制 `##` 后标题文本；两个 affected 小节都必须有 patch 条目（即使零正文改动）。

## Faster Next Time

- ROI：两轮读取（源文件全文 + wiki 现文）即可完成全部 action 决策，零正文改写、零合并风险；patch 合并方只需刷行号。
- 快捷判据：术语/定义型文档中，若变更源是"新增佐证章节"而非"修改定义"，优先怀疑零漂移，逐字比对确认后全线刷 code_refs。
- 反模式：见 S2 + hash changed 就条件反射重写正文；跳过逐字比对直接 line_number_only（行号刷新的前提是确认口径未漂移）；把派工单片段当实文。

## Applicability Boundaries

- 适用：patch JSON 小节级修订派工中"口径型文档"（术语表、定义清单、公约摘要）随源文件新增内容同步的场景。
- 不适用：源文件口径实质变更或结构性增删（须 replace_content 或整节重写）；全新文档生成（无既有小节可比）；授权直改的普通文档编辑（无 action 选项）。
- 与相邻经验分工：wiki-section-same-layer-action-criteria 管"同层面/不同层面"的逐节候选分流（公约大改版场景，结论多为混合 action）；本条管其零漂移分支——同层面候选经逐字比对全一致后回落为全线 line_number_only，并补充锚点实体拆解与表述归属判断两个操作化方法；replace-content-merge-integrity 管 replace 分支的原文保全；append-only-zero-drift-prefill-dispatch 管位置型零漂移（登记区末尾追加、行号不动），本条管口径型零漂移（逐字比对一致），两者是零漂移判据的两个来源分支。

## Evidence or Examples

- 源会话 ses_e393d8e0bffe21Q1PQChRZzqDX（修订业务术语表派工）：执行方实读 README 全文 32 行与术语表现文，对"目录池（十目录与归档流向）/通用工作流底座（四类能力）/四不红线（四项+白名单）/评估报告/回执"逐字比对全部一致，概述与术语列表两小节均判 line_number_only，仅刷 code_refs（README.md:1、7、9、15、32），patch 落盘成功零返工。
- 判据来源：派工单既有规则"实读比对变更结果，与权威载体实文逐字比对一致后才按新口径动笔"；本次执行验证并细化出锚点拆解与表述归属两个可复用操作。