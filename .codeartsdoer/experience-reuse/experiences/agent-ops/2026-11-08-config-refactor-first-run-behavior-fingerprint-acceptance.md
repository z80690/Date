---
id: 2026-11-08-config-refactor-first-run-behavior-fingerprint-acceptance
title: 配置/SOP 改造生效验收：首跑返回摘要按新 SOP 步骤逐条对齐行为指纹
category: agent-ops
nature: methodology
created_at: 2026-11-08T01:52:44
updated_at: 2026-11-08T02:20:00
tags: [改造验收, 行为指纹, SOP升级, 可运行验证, 子智能体]
keywords: [配置改造验收, 首跑实测, SOP步骤对齐, 行为指纹比对, 新旧行为差异, 返回摘要自述, 落盘不等于生效, 可运行验证轮, 持久化子智能体, 改造门禁]
problem_patterns: [改造子智能体SOP后仅核对文件落盘与静态清单即宣布完成，运行时实际仍按旧SOP执行无人察觉, 验收只验"能跑"不区分新旧行为，新增步骤未发生、旧形态未消失都发现不了, listSkills 等静态清单查不到改造对象，找不到可行的生效验证手段]
source_sessions: [ses_e48ebbb57ffeJeA6mFP69qRHLs]
project: Date
severity: medium
quality_score: 89
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [agent-ops/2026-11-08-listskills-enum-excludes-persistent-agents.md, workflow/2026-11-08-compare-test-old-logic-isolated-run.md, agent-ops/2026-11-07-write-receipt-not-proof-of-persistence.md]
---

# 配置/SOP 改造生效验收：首跑返回摘要按新 SOP 步骤逐条对齐行为指纹

## Scenario

改造持久化子智能体或流程配置（重写 SOP、收窄触发条件、增删步骤）后，需要验收"新配置真实生效"。文件落盘只能证明写入成功；对 listSkills 枚举不到的实体（如 agents/*.md 持久化子智能体），静态清单根本无法作为验收手段。

## Key Signals

- 改造后仅核对文件内容与清单状态即宣布完成。
- 运行时返回摘要仍按旧 SOP 结构叙述，或新旧行为差异点（新增步骤/删除步骤）无人核对。
- 门禁记录写"listSkills 核对通过"，但该清单根本不覆盖改造对象，验证方法本身无效。

## Essence

改造验收的权威证据 = **改造后首次真实派工（可运行验证轮）的返回摘要与产物行为，逐条对齐新 SOP 的步骤结构**。新增步骤实际发生、旧步骤的旧形态消失，才是"生效"的充分证据；落盘与清单状态都只是必要条件。

## Approach

1. 改造完成后发起首跑派工（独立验证轮次），任务参数与正式轮同构（同知识域、同产物结构），保证结果可比。
2. 派工 prompt 中直接要求"返回摘要按 SOP 步骤编号逐条自述 + 每步附证据指针"——首跑即得到可与新 SOP 逐条比对的指纹。
3. 逐条比对返回摘要：是否按新 SOP 步骤编号给出执行结果；每步是否有可核对的证据（产物指针/计数/自检结论）。
4. 核对新旧行为差异点：新版独有的步骤（如前置门禁自检、末步事件追加）确实发生；旧版形态（旧步骤数、缺事件行为）未复现。
5. 产物侧旁证：新 SOP 要求的产物（如完成事件行）在流水文件中实际存在；旧版不会产生的行为不再出现。
6. 若返回摘要与旧 SOP 结构吻合 → 配置未生效（缓存/加载延迟/改错文件），停驻排查而非宣布完成。

## Faster Next Time

- 验收清单三问：新步骤发生了吗？旧步骤的旧形态消失了吗？产物旁证齐吗？三问全过才签"改造生效"。
- 在派工 prompt 里预埋"逐条自述"要求，比事后人工比对话语摘要省一轮往返。
- 改造类任务的完成判据写成"首跑指纹对齐通过"，而不是"配置文件已更新"。

## Applicability Boundaries

- 适用：agents/*.md 持久化子智能体 SOP 改造、SKILL.md 流程改版、任何"改配置后需证明运行时生效"的场景；对静态清单枚举不到的实体，是唯一可行验收法。
- 不适用：无行为差异的纯文案修改（首跑验证过度）；一次性临时 Worker（无"现行配置"概念，直接验收产物即可）。
- 前置约束：首跑轮任务须与正式轮同构，否则指纹没有可比基线。

## Evidence or Examples

- 本会话 M3 改造门（ses_e48ebbb57ffeJeA6mFP69qRHLs）：examiner/grader 由五段 SOP 升级为六步 SOP 后，V1 验证轮首跑返回"①参数接收②自检前置（门禁证据在档+前轮已闭环）……⑥完成事件已追加"六段逐条自述，且新版独有的 E2 完成事件行实际出现在 exam/V1/events.md；对照 OLD 轮（旧版配置检出运行）无事件步骤——新旧行为差异核对成立（gates/m3-agent-gate.md）。
- 平台行为注记：listSkills 返回清单不单列持久化子智能体，故首跑指纹对齐同时承担"注册生效"与"改造生效"的双重权威验证。