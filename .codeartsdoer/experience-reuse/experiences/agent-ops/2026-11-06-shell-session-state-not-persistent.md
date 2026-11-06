---
id: 2026-11-06-shell-session-state-not-persistent
title: shell 工具跨调用不保留会话状态，长命令序列落盘为脚本执行
category: agent-ops
nature: pitfall
created_at: 2026-11-06T19:29:49
updated_at: 2026-11-06T19:45:16
tags: [shell状态, 脚本落盘, win32, powershell, Agent工具]
keywords: [持久会话, 变量丢失, No such file, ps1脚本, 临时脚本, 分节echo, 工作目录, bash工具, 静默失败, 清理]
problem_patterns: [前一调用设置的shell变量在下一调用引用时静默丢失, 引用变量后报文件不存在实为会话状态未保留, 多步长命令拆多次调用导致中间状态断裂]
source_sessions: [ses_e4f7ba4bdffe5nL8JFlcchwE9L]
project: Date
severity: medium
quality_score: 85
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-06-parallel-tool-call-doom-loop]
---

# shell 工具跨调用不保留会话状态，长命令序列落盘为脚本执行

## Scenario

Agent 在 win32 环境用 bash/PowerShell 工具连续执行多步长命令（python 脚本 + 多个长路径参数），尝试"第一次调用设变量、后续调用引用变量"的两段式用法。

## Key Signals

后一调用报 `can't open file 'C:\\slice_artifacts.py': [Errno 2] No such file or directory`——脚本实际不在该路径，说明变量已丢失、命令按字面参数在错误的工作目录解析。关键是前一调用"设置变量"没有任何报错，丢失是静默的，报错出现的位置远离根因。

## Essence

Agent 的 shell 工具每次调用通常是独立进程/独立会话：变量、别名、cd 状态不跨调用保留。跨调用的状态必须落盘为文件，不能依赖 shell 会话内存。

## Approach

1. 把多步长命令（含全部参数与路径）写成脚本文件：win32 用 `.ps1`，unix 用 `.sh`，放到项目 temp 目录。
2. 每次工具调用只执行该脚本一条命令，不依赖任何前次调用设置的变量。
3. 脚本内部对每步 echo 分节标记（如 `=== step name ===`），单次调用完成多步并保留全部输出，便于一次读全结果。
4. 流程收尾删除临时脚本，避免中间产物残留在仓库。

## Faster Next Time

- 需要复用路径/参数时直接写进脚本文件，不做"先设变量后引用"的两段式调用。
- 警告信号：引用上一调用设置的变量后出现"文件不存在/命令不存在"类报错，先怀疑会话状态丢失，再怀疑路径本身——报错位置与根因是分离的。

## Applicability Boundaries

- 适用：win32 + PowerShell/bash 工具分次调用的 Agent 环境（观察于码道 CodeArts Agent）；其他平台/工具组合需先自证会话是否持久。
- 不适用：已确认支持持久会话的工具（变量可用，但关键长命令仍建议落盘以便复跑）；单次调用内部的多条命令（单调用内状态正常保留）。

## Evidence or Examples

- 失败路径：调用 1 设置 `$py`、`$art` 等变量 → 调用 2 执行 `& $py C:\slice_artifacts.py ...` → `can't open file 'C:\\slice_artifacts.py': [Errno 2] No such file or directory`（变量丢失 + 工作目录错误）。
- 成功路径：写 `_wiki_cmd.ps1`（含 slice_artifacts 与 extract_symbols 两模块的完整命令与分节 echo）→ 单次执行全部成功；收尾 deleteFile 删除该临时脚本。
- 复用验证：同一方式随后用于 code-links 校验、build_index、存在性检查脚本，均一次成功。