---
id: 2026-11-07-sop-five-section-standard-flow-format
title: 智能体 SOP 标准流程五段格式：输入→步骤→输出→完成判据→升级路径，正文即 SOP 载体
category: agent-ops
nature: technique
created_at: 2026-11-07T07:27:01
updated_at: 2026-11-07T07:32:02
tags: [SOP, 格式统一, 子智能体, 派工契约, 流程定义]
keywords: [SOP五段格式, 输入步骤输出, 完成判据, 升级路径, SKILL.md正文, agents正文, 派工契约, 载体选择, 格式统一, 可机械核验]
problem_patterns: ["需要为多个智能体/角色定义标准流程，格式各异导致不可对比、不可验收", "运行时 Worker 无持久化文件，SOP 无处落", "SOP 只有步骤没有完成判据与升级路径，验收凭感觉、卡壳无出口"]
source_sessions: [ses_e4cdf992cffeY5nxZpoxvM1wZ2]
project: Date
severity: low
quality_score: 86
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [agent-ops/2026-11-07-agents-md-persistent-subagent-format-contract, agent-ops/2026-11-07-worker-grader-exam-gate-pattern, agent-ops/2026-11-07-subagent-roster-restraint-nonmerge-argument]
---

# 智能体 SOP 标准流程五段格式：输入→步骤→输出→完成判据→升级路径，正文即 SOP 载体

## Scenario

需要为一个多智能体体系**逐个**定义标准作业流程（SOP）时，若各角色流程写法各异，会导致流程不可横向对比、完成与否不可判定、角色卡壳时无升级出口。本篇给出一套统一五段格式与载体选择规则，实证于"重构后子智能体编队 SOP 定义"任务。

## Key Signals

- 用户要求"每个子智能体的 SOP 标准流程定义……格式统一"——多角色流程定义场景的第一信号是**先定格式再填内容**，而不是逐角色自由发挥。
- 既有载体实证在档：两个既有 SKILL.md 的编号步骤正文（拉取→三查→沉淀→考核→留痕）就是"标准流程"的可执行形态——证明 SKILL.md 正文可承载 SOP。
- 运行时 Worker（Task 派工）没有持久化文件，SOP 只能活在其派工提示词里——需要第三种载体形态。

## Essence

SOP = 五段固定结构：**输入→步骤→输出→完成判据→升级路径**。载体按角色形态三选一：

- 持久化子智能体 → `agents/*.md` 正文（YAML frontmatter 之外的提示词区即 SOP 区）
- 技能化能力 → `SKILL.md` 正文（编号步骤即 SOP）
- 临时运行时 Worker → 五字段派工契约（在 Task 提示词中显式写五段）

"完成判据"与"升级路径"是让流程从叙事变成可验收流程的关键：完成判据必须可机械核验（文件在档 / grep 校验 / 工具回读），升级路径必须指定升级给谁（用户裁决 / 主智能体 / 门禁）——缺这两段，SOP 只是动作描述，卡壳即死循环。

## Approach

1. **先定格式后填内容**：宣布五段结构为全部成员的统一模板，逐成员套写，禁止各写各的。
2. **五段逐段要求**：输入=接什么（文件/指令/上下文）；步骤=编号动作序列；输出=交什么（文档/报告/状态）；完成判据=可机械核验的完成条件；升级路径=搞不定时升级给谁。
3. **载体三选一**：持久化成员写 agents/*.md 正文；可技能化的能力写 SKILL.md 正文（注册即分发）；纯临时的运行时 Worker 把五段压进派工契约五字段。
4. **写完全量校验**：按章节标题 grep 确认每个成员的 SOP 章节都在档，再呈报。

## Faster Next Time

- 直接复用五段模板一次成型，无需设计讨论轮次；五段顺序即工作顺序，无需再发明结构。
- 完成判据写成"可 grep / 可回读 / 可计数"的证据形态，验收时零争议。
- 警告信号：SOP 缺升级路径 = 角色卡死无出口；缺完成判据 = 验收凭感觉。

## Applicability Boundaries

- 适用：有多角色/子智能体机制的平台（主 Agent + Subagent + 技能分发），需要批量定义或重构角色流程。
- 不适用：单体无派工 Agent（五段可保留但"派工契约"载体不适用）；一次性脚本任务（写 SOP 纯开销）。
- 平台相关性：五段格式通用；三个载体形态实证于码道 CodeArts Agent 平台（SKILL.md / agents/*.md / Task 派工契约），跨平台时载体名需映射。

## Evidence or Examples

- 实录（2026-11-07，ses_e4cdf992cffeY5nxZpoxvM1wZ2）：子智能体体系 spec v3 修订中，按五段格式为编队全员（2 持久化子智能体 + 平台内置 Worker + 按需 Worker）逐个定义 SOP，完成后 grep 校验章节标题行号在档（SOP 章起于 Line 583），呈报通过。
- 载体实证：learn-gate SKILL.md 9 行正文 = 五步流程（拉取→材料三查→学习沉淀→考核→留痕）；register-feature SKILL.md = 五步准入；实验品 agents/*.md 正文 = 一段角色指令（"仅响应派工……完成即退"即其 SOP 极简形态）。
- 运行时形态：平台内置 spec 三代理与 bug-fix Worker 均为运行时 Worker，其 SOP 以五字段派工契约在派工时实例化。