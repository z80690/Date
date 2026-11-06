---
id: 2026-11-07-single-command-batch-assertion-inventory
title: 环境盘点与守卫核查用单命令批量断言：一行一个 key:value，一次调用拿全结论
category: agent-ops
nature: technique
created_at: 2026-11-07T06:42:01
updated_at: 2026-11-07T06:42:01
tags: [盘点, 断言清单, Test-Path, 环境核查, 轮次优化]
keywords: [批量断言, 单命令盘点, Test-Path 组合, 迁移守卫, ST0 盘点, 存在性核查, 布尔命名消歧, 轮次压缩, 守卫核查, 断言失败语义]
problem_patterns: [盘点/守卫需核实十余个存在性事实逐条调用工具浪费轮次, 断言结果分散在多轮输出中难以对照复核, 批量断言的布尔语义不消歧导致 True/False 读反误判]
source_sessions: [ses_e4f5c5a83ffefUFnzHFvOEFJCW]
project: Date
severity: low
quality_score: 86
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-07-powershell-command-construction-limits-script-fallback, 2026-11-07-refresh-env-baseline-before-planning]
---

# 环境盘点与守卫核查用单命令批量断言：一行一个 key:value，一次调用拿全结论

## Scenario

阶段状态机的 ST0 盘点、ST→ST 迁移守卫、环境基线刷新等场景，需要核实一组存在性/状态性事实（目录在不在、.git 删没删、jar 产没产出、配置区建没建），动辄 8–10 项。逐项一次工具调用既慢又让结论散落在多轮输出里，难以一次性对照"准出检查单"复核。

## Key Signals

- 准出条件/盘点清单本身就是一组可程序化判定的布尔断言（存在性、版本号、计数阈值）。
- 发现自己在连续多轮里发的都是 `Test-Path` 式单点查询。

## Essence

把整张核查清单**编译成一条 shell 命令**：内联多个 Test-Path/条件表达式，以 `key: True/False`（或 `key: 值`）逐行输出。一次调用返回全部断言结果，与准出检查单逐行对照即可放行或拦截。断言的判定标准在写命令时就定死，避免"查到了但不知道算不算达标"。

## Approach

1. 先把核查单写成断言清单：每项一个语义化 key + 预期值（如 `p3c-git-gone: True` 表示 .git 已删 = 正常）。
2. 单条命令内联全部表达式，输出逐行 `key: 值`；需要的中间量（计数、大小）一并输出（如 `ref-contamination-hits: 0`）。
3. **布尔命名消歧**：key 名直接表达"满足预期"的语义（`git-gone=True`=已删除=正常；`dir-exists=True`=目录在=正常），防止读反。
4. 解析输出时逐 key 与预期对照，全绿才放行；任一 False 单独追查，不整批重跑。
5. 断言项过多或逻辑复杂时退回脚本文件模式（受工具层多语句长命令限制）；只读断言才适合批量合并，**含副作用的动作不要混进同一条命令**。

## Faster Next Time

- 模板一句话：**"准出检查单 → 一条命令 → 逐行断言 → 对照放行"**，替代 N 轮单点查询。
- key 命名带预期方向（-gone/-exists/-ready），半年后回看也不用猜布尔含义。
- 断言清单本身可直接落盘为准出检查单，命令与文档一一对应，迁移守卫复核成本趋近于零。

## Applicability Boundaries

- 适用：存在性/状态/计数类只读核查（盘点、守卫、基线刷新、验收前置检查）。
- 不适用：需要观察中间输出再决定下一步的探索性操作（那是串行决策，无法预编译成断言）；有副作用的安装/删除/构建动作。
- PowerShell 5.1 下注意命令长度与多语句限制（复杂逻辑写 .ps1 再执行）；bash 下用 `&&`/`;` 组合同样成立。

## Evidence or Examples

- 本会话实例（ST0 盘点，一次调用 9 项断言）：`p3c-dir: True / p3c-git-gone: True / cairn-dir: True / cairn-git-kept: True / dsa-dir: True / dsa-git-kept: True / p3c-jar: True / maven-home: True / facts-stage-section: False`——最后一项 False 即"阶段状态区未建"，正好指向任务 1.2 的待办，结论与准出检查单完全对齐。
- 同模式复用（架构不变量等价执行）：4 条 grep 断言一次输出 `check1-ResolveLatest-called: True (hits=2) / check2-zero-llm: True / check3-zero-embedding: True / check4-readonly: True (raw-hits=0)`，计数与布尔并载，证据密度更高。
- 嵌套核查实例：`no-submodules: True / tracked-files: 63 / refs-contamination-hits: 0` 一条命令完成三项验收。