---
id: 2026-11-06-spec-to-tasks-decomposition-pipeline
title: 规格到任务清单的拆解流水线（预检固化→覆盖映射→门禁排序→确认冻结）
category: workflow
nature: methodology
created_at: 2026-11-06T20:16:59
updated_at: 2026-11-07T01:26:24
tags: [task-decomposition, sdd, workflow, gating]
keywords: [任务拆解, tasks.md, spec转任务, 裁决固化, 覆盖映射, 依赖主线, 门禁前置, 确认冻结, 预检]
problem_patterns: ["拆解任务时回潮用户已否决的方案", "任务清单未覆盖规格全部能力条目"]
source_sessions: [ses_e4f3dbe70ffeQ2k0pNEQHUQilW]
project: Date
severity: low
quality_score: 82
hit_count: 3
last_hit_at: 2026-11-07T08:22:30
low_quality_hit_count: 0
tier: A
related_experiences: ["2026-11-06-dispatch-order-conflict-gating", "2026-11-06-verify-claimed-prerequisites-before-research", "2026-11-06-terminal-gates-in-task-dependency-graph", "2026-11-07-sdd-spec-to-tasks-coverage-mapping"]
---

# 规格到任务清单的拆解流水线（预检固化→覆盖映射→门禁排序→确认冻结）

## Scenario
规格驱动开发（spec → design → tasks）中从上游 spec.md 与 design.md 生成任务清单的任务规划阶段。适用于规模较大的拆解：多任务组、数十个子任务、含归档/提交等收尾动作。

## Key Signals
- 上游文档经历过用户裁决修订（部分方案被否决、部分事项列为未决）；
- 规格含编号化的能力条目列表，拆解要求逐条覆盖；
- 存在顺序敏感的收尾动作（测试→归档→提交），顺序错排会产生返工或违规提交。

## Essence
拆解阶段最大的风险不是"拆得不够细"，而是两条：① 回潮——把用户已否决的方案重新写进任务；② 顺序错排——把不可逆收尾动作排在依赖链中段。先预检固化情况再动笔、以依赖图编排顺序，一次通过确认的概率最高。

## Approach
1. 完整读取全部上游文档（spec 与 design 全文），不凭派工单转述拆解；
2. 预检核对用户裁决固化情况：逐条检查已否决方案是否未回潮、未决事项是否已编号列明，输出"未发现新增冲突"结论后再动笔；
3. 任务逐条映射规格能力编号，形成覆盖对照（每条能力至少落到一个任务），防遗漏；
4. 每个任务写明独立验收条件与显式依赖标注；顺序敏感约束（如"归档必须在测试通过后""提交必须最后且门禁前置"）转为依赖图硬边，而非留在约束文字里；
5. 产出"概览表（任务组×能力覆盖×关键约束）+ 依赖主线"做结论前置汇报，等待用户确认后冻结文档，才进入执行阶段。

## Faster Next Time
- 拆解前先列"裁决固化核对清单"（否决项/未决项/边界约束各一行），几分钟即可防回潮；
- 依赖主线用紧凑记法（如 1→2→(3,4)∥(5,6)→7→8→9→10）一眼看出串行门禁与并行编组；
- 汇报用表格而非段落并限字数，减少确认往返。

## Applicability Boundaries
- 适用：规格/设计文档齐备且经历过人工裁决的多任务拆解；含不可逆收尾动作的流水线；
- 不适用：单步可完成的一次性小任务；上游文档缺失或未经用户确认时（应先补齐上游而非强行拆解）。

## Evidence or Examples
- 来源会话：ses_e4f3dbe70ffeQ2k0pNEQHUQilW（2026-11-06，Date 项目 kb_maintenance 特性任务规划阶段）；
- 实际执行：完整读取 spec.md（582 行）与 design.md（549 行）→ 预检确认用户两项裁决（80 行上限废除、缺失 4 篇文档不补造）已固化于 spec 4.1.2/5.2.1.1 与 design 2.4-U1 → 生成 tasks.md：10 个主任务组、28 个子任务，覆盖规格能力 5.1–5.9；
- ROI：预检未发现新增冲突，任务清单一次生成即进入确认环节，避免了拆解后因裁决回潮导致的重写返工。