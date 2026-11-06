---
id: 2026-11-06-third-party-framework-model-config-bypass
title: 借骨架弃心脏：第三方框架模型配置层的剔除与平台能力对接
category: architecture
nature: decision
created_at: 2026-11-06T23:22:11
updated_at: 2026-11-06T23:31:00
tags: [framework-adoption, model-config-removal, bypass, platform-capability, orchestration-skeleton]
keywords: [模型配置, API key, per-role model, 环境变量注入, 旁路, 零模型默认路径, 编排骨架, Router, Worker, Watchdog, 平台模型端口, 确定性规则]
problem_patterns: [引入编排框架后被迫配置外部模型API密钥与平台自带模型能力重复, 框架的可选模型开关被误当必配项, 剔除模型层时误伤框架原生的确定性非模型路径]
source_sessions: [ses_e4ea45cd3ffeUDYx5ChB6gH84o]
project: Date
severity: medium
quality_score: 86
hit_count: 1
last_hit_at: 2026-11-07T04:39:23
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-06-oss-reference-pattern-scan-method, 2026-11-06-integration-route-inventory-constraint-conflict-precheck]
---

# 借骨架弃心脏：第三方框架模型配置层的剔除与平台能力对接

## Scenario

采用第三方编排框架（Router/Worker/triggers/Watchdog 类骨架）增强本地多智能体能力时，框架内置外部模型配置层（API key、model id、per-role 模型环境变量）要求接入方提供模型凭据。当目标平台（如 Agent IDE）自带大模型能力时，外部模型层既重复又添运维负担——需要"剔除或旁路模型配置，整体打通后直接用平台自带模型"。

## Key Signals

- 接入框架的前置条件是填 API key / model config / 模型 env 变量。
- 框架文档把模型配置写成必配项，但源码里存在可选开关与默认路径。
- 用户/平台方提出"剔除或旁路模型配置"诉求，而框架没有官方的"无模型模式"开关。

## Essence

编排框架的价值在**编排逻辑**（路由/派工/触发/看护），模型调用只是其可替换的执行引擎。正确动作是源码级盘点全部模型配置点，并做**二分类**：外部模型依赖点（剔除/替换）与框架原生零模型默认路径（旁路保留，不误伤）——后者常被误当必配项，实际是确定性的非模型实现。

## Approach

1. **源码实查模型配置点清单**：逐类排查——模型工厂函数、env 变量（全局与 per-role 覆盖）、runtime 注入点、可选策略开关、网关层、provider 适配层、embedding 端口。
2. **二分类**：
   - 外部模型依赖点（需 API key / 指定 model id）→ 列入剔除清单；
   - 框架原生零模型默认路径（如确定性规则策略、无 embedding 的默认实现）→ 旁路保留。
3. **保留编排骨架**：Router/Worker/triggers/Watchdog、存储、看护、UI 等编排设施原样保留；模型调用层统一替换为平台模型端口适配器。
4. **运行义务复验**：剔除后在目标平台上可运行性不降级（本例 Windows 可运行义务不变）。

## Faster Next Time

- 引入框架先 grep 模型配置关键词（model / apikey / provider / embedding / llm）盘点依赖面，再决定接入方式。
- "可选模型开关"≠必配——默认路径往往是零模型的确定性实现（如 `mode: 'rules'` 策略、无 embedding 默认），先查默认值再谈"必须配模型"。
- 平台有自带模型能力时，把框架的模型层一律视为**可替换端口**而非框架资产；评估标准是"编排逻辑与模型调用的耦合度"，不是框架文档的配置清单。
- 警告信号：框架核心流程里模型调用与编排状态机深度交织（无清晰边界）——剔除成本可能超过收益，先评估耦合度再动手。

## Applicability Boundaries

- 适用于：目标平台自带模型能力，且框架的模型调用层可端口化替换（接口清晰）的场景。
- 不适用于：模型调用与编排逻辑深度耦合、无清晰边界的框架（剔除成本>收益）；平台无自带模型能力的环境（此时框架模型层反而是必要的）。
- 重新评估条件：平台模型端口能力不足（不支持框架所需的角色分工/流式语义）、或框架升级改变模型配置面。

## Evidence or Examples

- 实证会话：2026-11-06 kb_arch_foundation spec v3 修订（ses_e4ea45cd3ffeUDYx5ChB6gH84o），用户要求 Super-agent 框架中需配置模型的功能剔除或旁路。
- deepseek-super-agent 实查（本地浅克隆，HEAD=e705e87，TypeScript）确认 **9 处模型配置点**：`harness/model.ts` 的 `createModelFromEnv`/`HttpOpenAI`/`roleModelsFromEnv`；`DS_AGENT_ROUTER_MODEL` 等 per-role env（router/worker/watchdog）；runtime `models` 注入点；ingest SlowPath 可选模型策略（`mode: 'rules' | 'model'`，默认确定性规则）；EmbeddingPort；gateway；`providers.ts`。
- 二分类结果：外部模型依赖点（#1–#6）列入剔除；2 处框架原生零模型默认（ingress `mode='rules'` 确定性策略、无 embedding 默认实现，#7/#9）旁路保留。
- 定稿方案：保留 Router/Worker/triggers/Watchdog 编排骨架，模型调用层对接码道平台大模型能力端口，纳入 spec v3 架构设计与实施范围；Windows 可运行义务不变。- 验证状态（防误引）：源码级实查（9 处配置点、二分类清单）可复现；"剔除后可运行性不降级"属实施期运行义务，截至本经验沉淀时**尚未运行验证**——引用本条时须区分"已定稿"与"已运行验证"。