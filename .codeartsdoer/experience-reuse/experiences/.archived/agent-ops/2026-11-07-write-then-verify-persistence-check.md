---
id: 2026-11-07-write-then-verify-persistence-check
title: 写后必验：落盘类交付的两步验证法
category: agent-ops
nature: technique
created_at: 2026-11-07T18:46:54
updated_at: 2026-11-07T18:51:27
tags: [写后必验, 落盘验证, agent-ops, 文件操作, 交付纪律]
keywords: [write-then-verify, 落盘失败, 空文件, 字节数, 列目录, read 回读, 假落盘, 交付验证, 写入确认]
problem_patterns: ["声明已落盘但文件实际未写入或为空文件", "工具返回成功被当作落盘成功的唯一证据"]
source_sessions: [ses_e4a6ba8f9ffecyMav4uHrFi453]
project: Date
severity: medium
quality_score: 84
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
utility_score: 100
tier: D
related_experiences: [2026-11-07-write-receipt-not-proof-of-persistence]
---

> **[已归档 2026-11-07]** 本经验与主文件 `agent-ops/2026-11-07-write-receipt-not-proof-of-persistence.md` 经加权相似度判定约 0.92（问题场景、problem_patterns、两步验证方法高度重叠），已按 Merge 规范并入主文件。独有增量（子智能体自验边界、LastWriteTime 检查、"会话内一次失败则全任务强制两步验证"纪律）已合入主文件的 Applicability / Faster Next Time / Evidence 章节。后续检索请命中主文件，本文件仅保留溯源链路。

# 写后必验：落盘类交付的两步验证法

## Scenario
智能体（主智能体或子智能体）向磁盘写文档/产物并声明"已落盘"，随后进入下一阶段。用户后续实测发现目标目录存在但文件数为 0——即"假落盘"。适用于任何以文件落盘为交付物的任务（规格文档、计划文档、报告、配置）。

## Key Signals
- 写入工具返回"成功"但没有第二证据源佐证。
- 上游会话曾出现过"声称落盘、实测 0 文件"的实例，说明写入工具的成功回执不能作为唯一依据。
- 用户明确要求"写后必验"作为交付纪律的场合。

## Essence
写入工具的成功回执 ≠ 内容真实持久化。必须用独立证据源（目录元数据 + 回读）闭环确认。两个证据维度互补：目录列表的文件大小能一秒发现 0 字节空文件；回读能确认内容非空且头部元信息（版本/日期/编号）完整。

## Approach
1. 写文件完成后，**立即**执行目录列表命令（如 PowerShell `Get-ChildItem` / `ls -l`），确认：文件存在、Length/size > 0、LastWriteTime 是刚刚。
2. 用 read 工具回读文件头部（前 20~30 行），确认内容非空且关键元信息（标题、版本、日期、编号）齐全。
3. 两步都通过才在呈报中声明"落盘已验证"；任一步异常则重写并再次验证，不得带病交付。
4. 在交付呈报中注明验证方式与结果（字节数、行数），供用户复核。

## Faster Next Time
- 把"列目录看字节数 + 回读头部"固化成落盘后的固定动作，成本约 2 次工具调用，可 100% 拦截假落盘。
- 警示信号：只要会话中出现过一次落盘失败，本次任务的所有写入都必须走两步验证，不做豁免。

## Applicability Boundaries
- 适用：通用 Agent 模式（写入工具 + shell/列表工具 + 回读工具齐全的环境）；主智能体与子智能体均适用，子智能体落盘后尤其需要自验，因其结果只以总结形式返回主智能体，中间态无人复核。
- 不适用：内存态/临时文件操作、由外部框架统一校验落盘的场合（如框架自带写后校验回调）。

## Evidence or Examples
- 本项目实例（源会话 ses_e4a6ba8f9ffecyMav4uHrFi453）：v1 规格被打回，打回理由之一为"落盘失败（实测 `.codeartsdoer/specs/optimization_plan/` 目录存在但为 0 文件，v1 声称落盘实际未写入）"。
- v3 重构后按两步法验证：目录列表输出 `spec.md 52601 2026/11/7 18:40:14`；回读确认 630 行非空、头部版本/日期/派工单编号元信息完整，验证通过。