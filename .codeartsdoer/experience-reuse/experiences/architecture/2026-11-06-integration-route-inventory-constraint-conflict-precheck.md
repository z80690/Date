---
id: 2026-11-06-integration-route-inventory-constraint-conflict-precheck
title: 外部编排器接入方式清单化选型：逐项预检本地约束后再定主路线
category: architecture
nature: decision
created_at: 2026-11-06T23:22:11
updated_at: 2026-11-06T23:22:11
tags: [integration-route, external-orchestrator, constraint-precheck, primary-vs-reserve, cairn]
keywords: [接入方式, MCP, CLI, REST, 库直调, 常驻守护进程, 轮询, 禁定时任务, 主路线, 储备方案, 适用场景, 冲突预检]
problem_patterns: [默认外部工具只有一种官方接入方式错失更轻量的入口, 选了功能最强的接入方式后才发现与本地硬约束冲突返工, 接入方式调研只看文档不看源码漏掉隐蔽入口]
source_sessions: [ses_e4ea45cd3ffeUDYx5ChB6gH84o]
project: Date
severity: medium
quality_score: 85
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-06-oss-reference-pattern-scan-method, 2026-11-06-process-control-state-machine-over-gate-chain]
---

# 外部编排器接入方式清单化选型：逐项预检本地约束后再定主路线

## Scenario

引入外部编排器/知识服务（如知识图谱构建+查询系统）时，"它只有一种进入方式吗"是选型必答题。官方主推的默认入口未必是唯一入口，也未必是符合本地约束的入口；若只按 README 一句话接线，容易漏掉更轻量的入口，或选了最重的入口后才发现与本地硬约束（禁定时任务、禁网络等）冲突。

## Key Signals

- 架构设计里只写了外部工具的**单一**接入路径。
- 接入方式的来源是 README 主推描述，而非源码核实。
- 选型理由没有对照本地硬约束逐项预检——"功能最强"被默认当成"最优"。

## Essence

接入方式必须**清单化**：读源码列全部入口并标注适用场景，再逐项与本地硬约束预检，冲突者弃用；最后按"主路线 + 储备方案"分层固化，避免单点依赖。核心张力在于：功能最强的入口（如常驻守护进程持续构建）往往也是最重、最容易与轻量化约束冲突的入口——预检必须先于心动。

## Approach

1. **入口类型学排查**（逐类查源码确认存在性与成熟度）：传输协议入口（MCP 多传输/REST/gRPC）、CLI 入口、构建流水线入口、可视化入口、库直调（SDK/core 包）入口、常驻进程入口（守护进程/轮询）。
2. **逐类标注适用场景与代价**：部署成本、实时性、隔离性、运维负担。
3. **约束预检先于选型**：逐项对照本地硬约束（例：禁定时任务 → 常驻轮询守护进程类入口直接弃），预检不后补。
4. **定主路线 + 储备清单**写入架构文档：主路线注明选择理由，储备方案标明启用条件（如主路线不可用时降级到哪个入口）。

## Faster Next Time

- 拿到外部工具先问"有几种进入方式"而不是"怎么接"——前者是清单题，后者容易收窄成单点。
- README 主推 ≠ 唯一入口 ≠ 最适入口；"库直调/CLI"类轻量入口常埋在源码目录结构里，只读文档会漏。
- 警告信号：候选入口的工作模式是"常驻/轮询/持续"字样，而本地约束含"禁定时任务"——先预检再心动。
- ROI：本例一次清单化调研同时回答了"是否只有一种接入"（否，7 类）与"哪个可用"（cairnd 弃用、MCP 主路线），避免了选错主路线后的架构返工。

## Applicability Boundaries

- 适用于引入带多入口的外部服务/编排器/工具链的选型阶段。
- 不适用于：工具只有单一入口时（退化为常规集成设计）；纯内部模块间的调用设计（无"接入"语义）。
- 重新评估条件：本地约束修订（如解禁定时任务）、工具新增入口、或主路线在运行中暴露稳定性问题需切换储备方案。

## Evidence or Examples

- 实证会话：2026-11-06 kb_arch_foundation spec v3 修订（ses_e4ea45cd3ffeUDYx5ChB6gH84o），用户问"Cairn 编排器只有 worker→注册表一种进入方式吗"。
- Cairn 实查（本地浅克隆，HEAD=2ae4eef，903 文件）确认 **7 类接入途径**：① MCP（多传输，README 主推）；② cairn CLI 查询；③ build 流水线（cairn-ingest/cairn-incremental）；④ REST 查询端点；⑤ graph-viewer 前端；⑥ core 库直调（Go 包 import）；⑦ cairnd 常驻轮询守护进程（持续构建）。
- 约束预检结果：cairnd 为轮询型常驻进程，与项目"禁自建定时任务、一切触发走事件"硬约束冲突，**弃用**；MCP 链路定为主路线，其余列为储备方案并标注适用场景（spec v3 固化）。
- 调研路径本身（ls-remote 探链、隔离浅克隆、结构扫描）沿用 2026-11-06-oss-reference-pattern-scan-method，本条只覆盖其后的接入途径选型环节。