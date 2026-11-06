---
id: 2026-11-06-parallel-tool-call-doom-loop
title: 批量并行调用纪律：验证类调用一次即止，防重复触发工具禁用
category: agent-ops
nature: pitfall
created_at: 2026-11-06T18:41:59
updated_at: 2026-11-06T18:45:59
tags: [tool-calling, parallel-execution, doom-loop, verification-discipline]
keywords: [并行调用, 工具循环, Doom Loop, listSkills, 重复调用, 工具禁用, 信息增量, 幂等验证, 批量执行]
problem_patterns: [单轮批量并行调用中同一验证工具被放入多个槽位, 首次成功返回后仍重复调用同一工具, 工具调用被系统禁用后无法继续执行]
source_sessions: [ses_e51adb269ffeqfVMdEGO1eP4xa]
project: Date
severity: low
quality_score: 80
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: A
related_experiences: []
---

# 批量并行调用纪律：验证类调用一次即止，防重复触发工具禁用

## Scenario
单轮任务含多项并行验证/落盘（如批量安装清单核验、多功能通道探测），把多个工具调用塞进同一批并行槽位时。

## Key Signals
- 前兆：同一验证工具在多个并行槽位中重复出现，且首个调用已成功返回完整结果。
- 触发症状：系统检测到同一工具连续重复调用（实测 listSkills ×3，三次返回完全相同的 49 技能清单），随后工具调用被禁用，仅剩纯文本输出。
- 恢复信号：系统提示"工具循环已检测到，本次仅文本回复"。

## Essence
并行槽位中每个调用都应有独立的信息增量目标。验证类调用（list/status/check 类）天然幂等——首次成功返回即已满足验证目标，冗余重复调用信息增量为零，累积触发平台的循环保护机制，导致整轮后续工具全部禁用。

## Approach
1. 并行调用前逐槽位自问"这个调用能带来什么新信息"，同目标验证只占一个槽位。
2. 某调用首次成功返回且已满足验证目标后立即停，不在后续批次重复调用它。
3. 一旦被禁用：不重试，直接切换为纯文本盘点——已完成事项（附实测证据）+ 未完成事项 + 工具恢复后的明确下一步。
4. 批量执行任务的顺序设计：落盘类（write）与验证类（list/read）分开批次，验证批次精简到最小必需调用数。

## Faster Next Time
- 幂等验证类调用是重复调用高发区——把"验证清单"收敛为单次调用或一次读取多个目标。
- 批量执行前先列槽位计划（每个槽位标注增量目标），避免边执行边往里塞重复验证。
- 被禁用后的正确动作是诚实盘点而非换工具绕路——循环保护触发说明信息增量已枯竭。

## Applicability Boundaries
- 适用于本平台（码道 CodeArts Agent）的并行调用与循环保护机制；"每次调用应有信息增量"的纪律对所有 Agent 平台通用。
- 机制细节（重复几次触发、是否跨轮累计）为单例观察，属推断级，需更多样本验证。
- 不适用于结果会随时间变化的轮询场景（如等待后台进程就绪）——那类重复调用有真实增量，但应有上限。

## Evidence or Examples
- 实测：listSkills 连续 3 次返回相同的 `{"count":49,...}` 清单（首次已满足"5 个项目级技能是否 enabled"的验证目标），随后系统禁用工具调用并提示 Doom Loop。
- 实测对照：同批次中首次成功返回的 queryUserSkillList（total=0）没有被重复调用，未触发任何异常——重复才是触发条件，而非调用本身。