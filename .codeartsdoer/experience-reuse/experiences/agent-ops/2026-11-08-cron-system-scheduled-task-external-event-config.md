---
id: 2026-11-08-cron-system-scheduled-task-external-event-config
title: 平台系统级定时任务配置法：cronList 先核实防重复建，cronCreate 承接禁自建定时的外部事件合规路径
category: agent-ops
nature: technique
created_at: 2026-11-08T10:06:13
updated_at: 2026-11-08T10:06:13
tags: [cron, scheduled-task, external-event, deferred-tools, no-polling]
keywords: [cronCreate, cronList, 定时任务, 外部事件, 禁自建定时, 禁轮询, deferred 工具, tool_describe, durable, recurring, 无人值守 prompt, 事实表登记, 约束语义裁决]
problem_patterns: ["规则层禁止自建定时与轮询，每日周期任务不知走哪条合规通道", "平台定时类工具是 deferred 工具，直接调用会因未加载 schema 而失败或参数语义不明", "派工约束表面冲突（'不建新定时' vs '设置每天定时任务'），不知如何裁决"]
source_sessions: [ses_e4880e4d1ffevLSssStvdntXQC]
project: Date
severity: medium
quality_score: 84
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: A
related_experiences: ["2026-11-06-codeartsdoer-event-trigger-channel-inventory", "2026-11-06-event-driven-mechanism-liveness-single-fact-source"]
---

# 平台系统级定时任务配置法：cronList 先核实防重复建，cronCreate 承接禁自建定时的外部事件合规路径

## Scenario

派工单要求把某项周期性维护（如 CodebaseWiki 每日同步）配置成"每天定时任务（每日 1 次）"，同时规则层红线明确"Agent 禁自建定时/禁轮询，走外部事件"。Agent 不能在项目里写轮询循环、不能自造定时脚本，必须找到平台级的合规触发通道；而平台定时类工具（cronCreate/cronList）通常挂在 deferred 内置工具清单里，不经 tool_describe 加载 schema 无法直接调用，参数语义（cron 字段数、时区、持久化）也需先确认。

## Key Signals

- 派工单/规则出现"每日定时""每天 1 次""禁自建定时""禁轮询，走事件"等字样——同时给出周期化需求与实现方式红线；
- cronCreate/cronList 出现在平台的 deferred 内置工具清单（如 "Deferred built-in tools available" 提示段），未 describe 前无 schema；
- cronList 返回 "No scheduled tasks."——现状核实结果，也是"是否需要新建"的裁决依据；
- 约束文本表面冲突：红线写"本派工不建新定时"，任务又要求"设置为每天定时任务"。

## Essence

平台系统级定时任务就是"外部事件"机制的合规实现体：触发由平台调度器发起，Agent 侧零轮询、零自建循环，与"禁自建定时"红线不冲突。约束语义按此裁决："不建新定时"禁止的是 Agent 层自造定时/重复建设，而非禁止使用平台定时——是否属于"重复建"以 cronList 实查现状为准（实查为空则新建即合规）。每日类任务必须 durable=true 持久化，否则重启即丢；cron 表达式为 5 字段本地时间，非 6 字段。

## Approach

1. **加载 schema**：对 cronCreate/cronList 先 `tool_describe` 取参数契约（deferred 工具必须先加载再调用）；
2. **现状核实**：`cronList` 实查当前项目已有定时任务——一是防重复建设（红线"不建新定时"的核实式履行），二是确认参数风格；同一查询不要在同轮经 `tool_call` 与内置别名双通道重复调用（本次实战两通道各调一次返回相同结果，浪费轮次）；
3. **创建任务**：`cronCreate` 关键参数——`cron` 用 5 字段本地时间（如 `30 7 * * *` = 每日 07:30）、`recurring: true`（周期）、`durable: true`（跨重启存活，每日任务必开）；`prompt` 写无人值守执行契约：做什么（调哪个技能/工具）、失败降级路径、输出纪律（不落业务文件、结果简报）；
4. **返回核验**：检查返回 JSON 的 `taskId`/`status: active`/`schedule`/`recurring`/`durable` 字段齐全且符合预期；
5. **事实表登记**：把 taskId 与调度参数写入项目单一事实源（如"机制状态"节），后续检索/审计只认事实表，不靠记忆。

## Faster Next Time

- 一条固定链五步走完：tool_describe → cronList 核实 → cronCreate → 返回核验 → 事实表登记，全程约一轮工具调用即可交付"每日定时已配置"类任务；
- 遇"每日/定时/周期"类派工，先查平台有没有系统级定时工具（deferred 清单），再考虑其他方案；写循环轮询在任何红线环境下都不合规；
- 约束表面冲突时先实查现状再裁决语义：cronList 为空 → "不建新定时"=不重复建设，新建合规；cronList 已有同目标任务 → 复用或报告冲突，禁止再建；
- 无人值守 prompt 必须自包含：触发会话没有本次派工上下文，降级路径与输出纪律不写就会执行漂移。

## Applicability Boundaries

- 适用：平台提供 cron 类 deferred 工具（cronCreate/cronList 或等价物）的环境；规则层禁止自建定时/轮询的场景；每日/周期性同步、巡检类派工；
- 不适用：平台无 cron 类工具（降级为手动派工或外部 CI/OS 级计划任务，且须用户批准）；一次性延时任务（recurring=false 即可）；秒级/分钟级高频触发（系统定时粒度不足，且高频触发实质等同轮询，违背红线精神）；
- 平台限定：taskId/schedule 字段与 deferred 工具机制实测自 CodeArts Agent（码道）；其他平台需先确认等价工具与参数语义，判断逻辑（核实→创建→核验→登记）平台无关。

## Evidence or Examples

- 来源会话：ses_e4880e4d1ffevLSssStvdntXQC（2026-11-08，Date 项目，派工单 TASK-20261108-004 任务2）；
- 实测序列：tool_describe 取得 cronCreate schema（cron 5 字段本地时间/recurring/durable/taskId）→ cronList 返回 "No scheduled tasks."（此前无定时任务，新建不构成重复建）→ cronCreate 返回 `{"success":true,"taskId":"c122980a","status":"active","schedule":"30 7 * * *","recurring":true,"durable":true,"projectPath":"C:\\Users\\Administrator\\Desktop\\Date"}`；
- prompt 实例："优先调用 repo-wiki-update-execution 技能同步 Wiki；不可用则按 Knowledge 工具流程核验刷新"，未落任何业务文件；
- 派工红线原文："禁轮询/自建定时：Wiki定时走外部事件，本派工不建新定时"——通过 cronList 空清单实查 + 公约第 4 条语义裁决（平台定时=外部事件）化解表面冲突；
- 事后同步：taskId c122980a 已登记入 `notes/项目事实表.md`（机制状态节）；本模式另沉淀为 generated-skills 技能 `cron-scheduled-task-config`（显式调用通道），本经验承载检索注入通道，二者互补。