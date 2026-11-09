---
id: 2026-11-08-specs-precedent-naming-inheritance-artifact-non-collision
title: specs 先例继承命名法：同构推导特性名与产物级不重名核查
category: workflow
nature: technique
created_at: 2026-11-08T03:43:09
updated_at: 2026-11-08T03:43:09
tags: [sdd, requirements-spec, naming-convention, precedent-inheritance, collision-check]
keywords: [特性命名, 命名惯例, 先例继承, specs 目录, 重名核查, 产物冲突, 编号递增, 降级备选, 落点缺口, 同构推导]
problem_patterns: ["新特性命名靠自创规则导致与项目既有惯例割裂", "不重名约束只查特性目录级漏掉先例规格中的既有产物名", "派工单指定落点目录不存在且无备选落点约定"]
source_sessions: [ses_e48932ce0ffeSzE5rhD9ms2eU8]
project: Date
severity: low
quality_score: 82
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: A
related_experiences: ["2026-11-07-sdd-spec-stage-fact-verification-and-scope-bounding"]
---

# specs 先例继承命名法：同构推导特性名与产物级不重名核查

## Scenario

SDD 需求规格阶段需为派工单新建特性目录与产物文件，specs 目录非空且存在同类先例（此前派工的可视化规格、上一派工单的执行规格）。派工单明确要求"文件不重名、编号递增"。命名与落点若临场自创，会与项目既有惯例割裂，且"不重名"只查目录级会漏掉产物级冲突。

## Key Signals

- specs 目录已有同类先例目录（任务类型相似，如同样要产出可视化产物）；
- 派工单出现"如目录已有 003，本单为 004""文件名自定，不重名"等编号与重名约束；
- 先例规格正文中已产出过与本次同类型的产物文件（如同名 HTML 可视化）。

## Essence

特性命名的最高效路径不是套通用规则，而是从 specs 目录先例同构推导——新名继承先例的命名结构与编号语义。"不重名"约束的核查深度必须到产物级：先例规格正文列出的既有产物名同样构成新产物的重名约束，仅查特性目录名会漏检。

## Approach

1. **先例盘点**：glob specs 目录列出全部既有特性目录，识别与本次任务类型相似的先例；
2. **三项提取**：读先例 spec.md，一次提取命名格式、既有产物清单、文档结构风格；
3. **同构推导特性名**：按先例惯例生成新特性名，保持编号递增与语义结构一致（如 pd003_exec → pd004_html_viz），同时完成长度合规检查与 glob 重名检查；
4. **产物级不重名比对**：新落盘产物逐一与先例规格中列出的既有产物名比对（先例已有同名类型产物则另起新名）；
5. **落点缺口带备选定义**：派工单指定落点目录不存在时，在规格中写"主落点（缺失则创建）+ 降级备选落点"，不由实现阶段临场决定。

## Faster Next Time

- 先例读取一轮完成命名惯例、产物清单、风格三项提取，避免边写规格边补查；
- 特性名合规（长度）与重名（glob）检查合并为一轮完成；
- 反模式：自创新命名体系（与既有派工编号断档）；只查目录级重名漏掉产物级冲突（实现阶段撞名返工）；落点缺失时留空由实现阶段拍板。

## Applicability Boundaries

- 适用：specs 目录已有先例的项目；派工单含编号递增/不重名约束；SDD 规格阶段的命名与落点决策；
- 不适用：specs 目录为空（退化为项目通用命名规则检查）；无 specs 惯例的仓库；先例与本次任务类型完全不同（仅作结构参考，命名惯例需另行判断）。

## Evidence or Examples

- 来源会话：ses_e48932ce0ffeSzE5rhD9ms2eU8（2026-11-08，Date 项目，spec-requirement-agent）；
- 实例：先例 `pd003_exec`（派工 003 执行规格）与 `20261107_P001_spec_workflow_visual`（同类可视化规格）被读取；新特性名 `pd004_html_viz` 同构推导（13 字符合规、glob 无冲突）；
- 产物级约束实例：先例已产出 `sdd-workflow-visual.html`，派工单要求新 HTML 不重名，故在规格中写明产物须另起名；
- 落点实例：派工单指定 `.codeartsdoer/agent-team/`（当时不存在），spec 5.1 写明"主落点缺失则创建，降级备选为规格目录"。