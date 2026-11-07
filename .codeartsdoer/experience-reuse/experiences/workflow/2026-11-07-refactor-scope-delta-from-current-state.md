---
id: 2026-11-07-refactor-scope-delta-from-current-state
title: 改造类规格的现状差集定界：读被改造对象现状，改造范围=目标-现状
category: workflow
nature: methodology
created_at: 2026-11-07T22:01:54
updated_at: 2026-11-07T22:24:32
tags: [workflow, refactor-spec, current-state-baseline, scope-bounding, requirement-spec]
keywords: [改造类需求, 现状基线, 改造范围, 差集, 过度改造, 智能体改造, 前置核实, 需求规格, 现状保留, spec阶段]
problem_patterns:
  - 改造类派工单不读被改造对象现状直接按叙述写"全面改造"，把既有合规特性误当新增需求重做
  - 改造范围凭派工单叙述长度而非"目标-现状"差集界定，导致过度改造
  - 现状已满足的要求仍写入改造条款，实施阶段重复建设并引入回归风险
source_sessions: [ses_e49c076a2ffeNbrHwiDi9S5CEP]
project: Date
severity: low
quality_score: 84
utility_score: 95
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-07-sdd-spec-stage-fact-verification-and-scope-bounding, 2026-11-06-constraint-dispatch-to-ears-gated-spec, 2026-11-06-ruling-regression-precheck]
---

# 改造类规格的现状差集定界：读被改造对象现状，改造范围=目标-现状

## Scenario

派工单要求**改造既有实体**（智能体、机制、流程——"出题官只出 X""批改官只按 Y"）而非新建。规格阶段若只按派工单叙述转条款、不实读被改造对象的现行定义，改造范围会被派工单叙述长度绑架：既有已满足的特性被写成"新增需求"，实施阶段重复建设甚至破坏既有合规特性。

## Key Signals

- 派工单动词是"改造/收窄/剥离/只做"，而非"建立/新建"；
- 被改造对象在项目中有现行定义文件（智能体 frontmatter+SOP、机制文档）；
- 派工单未逐条说明"哪些既有特性保留、哪些删除"。

## Essence

改造范围由 **"目标态 − 现状"的差集**决定，不由派工单叙述长度决定。实读现状后改造点通常**收窄**：部分要求现状已满足（应标为"现状保留"而非改造项），部分"新增"实为对既有合规特性的误认。漏读现状的典型事故是把既有合规红线当新需求重做——重做本身是回归风险源。

## Approach

1. 从派工单识别全部被改造实体，逐个实读现行定义全文（不只读摘要/描述）；
2. 逐条比对：派工单要求 × 现状行为，分三类——已满足 / 部分满足 / 未满足；
3. 差集定界：只有"未满足"与"部分满足"进入改造条款；"已满足"项在规格中显式标注"现状保留"（防后续阶段误删）；
4. 规格中写明改造范围差集及其依据（现状文件路径 + 读到的关键行为），供 design/tasks 直接承接。

## Faster Next Time

- 改造类派工单的前置核实清单在"三件套"之外固定加一件：**被改造对象现状**；
- 警告信号：规格中出现"从零建立/全面改造"字样而实体已存在 → 过度改造信号，回查现状差集；
- ROI 实测：实读两智能体现行 SOP 后，批改官"独立批改"被确认为现状已含红线（禁协商改判、禁倾向暗示），改造范围从"建立独立批改机制"收窄为"仅收窄出题官出题范围"，规格条款数显著减少且零误重做。

## Applicability Boundaries

- 适用：改造/收窄/剥离类派工单 + 被改造对象有可实读的现行定义 + SDD 规格阶段；
- 不适用：纯新建类任务（无现状可读，直接按三件套流程）；派工单明示"推倒重来"且被改造对象确需整体替换（此时差集退化为全集，但现状仍需实读以确认替换边界）；
- 是《SDD 规格阶段前置核实三件套与落点缺口显式定义法》的**第四件扩展**：三件套核实"环境与落点"，本条核实"改造对象"；两者可在同一实查轮并行完成。

## Evidence or Examples

- 本 session 实测（派工单"两智能体改造"）：实读 .codeartsdoer/agents/examiner.md（现状"按任意材料清单出题"→改造点收窄为"只出规范驱动 50 题"）与 grader.md（现状已含"禁与执行代理协商改判、禁受主智能体倾向性暗示"独立批改红线→"独立打分"标为现状保留，非新增改造项）；
- 佐证：grader.md 纪律红线行、examiner.md SOP 步骤①–④均为实读内容，非推断。