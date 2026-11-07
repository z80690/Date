---
id: 2026-11-07-sdd-spec-stage-fact-verification-and-scope-bounding
title: SDD 规格阶段前置核实三件套与落点缺口显式定义法
category: workflow
nature: methodology
created_at: 2026-11-07T17:56:54
updated_at: 2026-11-07T18:28:47
tags: [sdd, requirements-spec, fact-verification, scope-bounding, spec-stage]
keywords: [需求规格, EARS 格式, 单一事实源, 现状核实, 落点定义, 范围边界, 异常兜底, 特性命名, specs 目录, 防虚构]
problem_patterns: ["需求方要求基于项目现状产出规格但智能体缺乏现状认知", "用户口头指定产出落点在项目中不存在", "规格范围与后续实施阶段纠缠不清"]
source_sessions: [ses_e4a9ab4d4ffeJVCHGwEfNM2P06]
project: Date
severity: low
quality_score: 88
hit_count: 4
last_hit_at: 2026-11-08T02:03:41
low_quality_hit_count: 0
utility_score: 100
tier: S
related_experiences: ["2026-11-07-external-web-material-fidelity-bounding", "2026-11-06-verify-claimed-prerequisites-before-research", "2026-11-07-stage1-evidence-baseline-and-halt-reporting"]
---

# SDD 规格阶段前置核实三件套与落点缺口显式定义法

## Scenario

需求规格设计阶段（SDD 流水线 spec-requirement-agent 角色），输入为用户语音转写的自然语言需求（如"制定优化计划并生成 md 到计划文件夹"），可能附带外部背景材料。智能体对项目现状缺乏认知，却要产出可让用户独立审阅决策的 EARS 格式规格。单人协作、单任务粒度，规格质量直接决定后续 design/tasks 阶段是否返工。

## Key Signals

- 需求方明确要求"自行读文件核实，不要凭空推断"——现状断言若无实证来源即失真。
- 用户口头指定产出落点（如"计划文件夹"）但项目中不存在该目录——落点缺口若不处理，规格产出即无处安放或被随意创建。
- 需求同时含"本次做什么"与隐含的"后续做什么"（如获批后的实施），范围若不切开，规格会越界膨胀。

## Essence

规格可信度取决于两个前提：①所有现状断言都有实证来源（来自事实源而非推断）；②一切"用户说了但项目里没有"的约定（落点、机制）在规格中显式定义默认值并交用户裁决，而非自行拍板或留空。范围边界先于内容展开，是防止规格越界的根约束。

## Approach

1. **前置核实三件套**（写规格前必做，顺序固定）：
   - 项目根目录结构扫描（read 目录）——确认用户指定落点是否存在；
   - 单一事实源文档——获取 git/机制/环境等核心状态的实证值；
   - 知识库索引——获取既有结论（避免重做已完成的调研）与在册机制清单。
2. **特性命名合规检查**：按项目命名规则检查长度；用 glob 检查 specs 目录无重名冲突，冲突则换名。
3. **落点缺口显式定义**：用户指定落点不存在时，在规格中写明"落点 = 项目根目录 `<默认名>/`（现不存在，首次产出时创建；可由用户裁决调整）"，不擅自创建、不留空。
4. **范围边界先行**：规格开头单列"做什么 / 不做什么"，将获批后的实施、规矩层改动等明确排除为后续需求。
5. **异常兜底清单**：对"关键依据不可得、依据冲突、目录创建失败"三类异常各预设一个兜底动作（如列待补充清单、走三层仲裁留痕、重试后降级告知）。

## Faster Next Time

- 核实三件套可直接清单化执行，避免边写规格边补查导致的断言失真。
- 落点缺口用固定句式定义，省去与用户的多轮确认（用户偏好全权授权时尤其有效）。
- 范围边界先行可显著减少 design/tasks 阶段的方向性返工——本例规格概览一次成稿即获提交审阅。

## Applicability Boundaries

- 适用：SDD 需求规格阶段；需求引用项目现状断言；用户指定落点/机制在项目中无实体。
- 不适用：常规小型编码任务（无需完整规格）；项目现状已充分在上下文中（三件套可精简）；需求不含落点指定或范围歧义。

## Evidence or Examples

- 本例实证（来自会话轨迹）：spec-requirement-agent 先 read 根目录 + notes/项目事实表.md + notes/知识库索引.md，确认关键事实——根目录无"计划"文件夹（落点缺口）、2026-11-06 既有调研结论（经验与记忆最优先、代码库索引次优先）可直接继承、单一事实源/注册表/五步准入机制均在册。
- 特性名 `optimization_plan`（17 字符合规），glob 确认 specs 目录无重名。
- 产出 `.codeartsdoer/specs/optimization_plan/spec.md` 经 glob 确认落盘，规格概览 5 要点含范围边界、落点定义、异常兜底。