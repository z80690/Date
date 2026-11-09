---
name: cron-scheduled-task-config
description: 平台系统级定时任务（cronList/cronCreate）的配置契约与合规定位：deferred 工具先 tool_describe 取 schema 再 tool_call、勿同轮双通道重复调用；cron 5 字段本地时间、recurring/durable 语义、prompt 无人值守执行契约写法；建前先 cronList 核实现状防重复建。凡涉及"每天定时/每日一次/周期任务/定时同步 Wiki"类派工、或项目公约要求定时走外部事件（禁自建定时/禁轮询）时使用。
---

# 平台系统级定时任务配置（外部事件合规路径）

## 合规定位（公约第 4/5 条）
- 公约"禁自建定时/禁轮询"指禁 Agent 自行实现轮询循环/后台 sleep 定时；平台 cronCreate 属系统级定时=外部事件机制，是公约认可的合规路径（派工单明确"利用现有技能或系统级定时"时即指此）。
- 建前先 cronList 核实现状：派工单带"不建新定时"红线时，既有任务即复用确认、零重复创建；无既有才新建，并把"已核实无重复"写进汇报。

## 调用协议（deferred 工具）
- cronCreate 等延迟加载工具：先 tool_describe 取 inputSchema（同会话一次即可，后续免重复 describe），再以 tool_call(id, args) 调用。
- 同轮勿再以原生工具名重复调用同一动作（实测双通道各调一次=同一任务仅建一份但输出冗余，白耗预算）。

## 参数契约（cronCreate，2026-11-08 实测）
- cron：5 字段本地时间表达式（分 时 日 月 周），如 `"30 7 * * *"` = 每日 07:30。
- recurring：`true`=周期任务（每日/每小时），缺省 false=一次性。
- durable：`true`=跨重启持久——**每日定时必须 true**，否则平台重启后任务丢失。
- prompt：每次触发时作为独立执行上下文跑，按"无人值守"标准写自足契约，四要素：①优先调用的现有技能名+不可用时降级路径 ②单次动作边界（同步一次+简要汇报结果）③公约约束（禁轮询、单次限时、写必落盘）④完成汇报要求。

## 建后留痕
- 返回 taskId（如 c122980a）+ schedule 记入项目事实表机制状态区（一行：任务 ID/表达式/频率/recurring+durable/触发方式），页面与文档引用该定时机制时以事实表为准，不抄死值双源。
- 后续调整/删除：先 cronList 核实再走 cronDelete/重建（cronDelete 未实测，按工具清单推断）；禁在不核实现状的情况下重复 create。