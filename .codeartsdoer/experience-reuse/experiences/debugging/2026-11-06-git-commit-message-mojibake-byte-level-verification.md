---
id: 2026-11-06-git-commit-message-mojibake-byte-level-verification
title: git 中文提交信息乱码：先分显示级还是数据级，用字节级直读 commit 对象做决定性验证
category: debugging
nature: pitfall
created_at: 2026-11-06T21:16:59
updated_at: 2026-11-06T21:59:51
tags: [git, encoding, mojibake, powershell, verification]
keywords: [提交信息乱码, git commit, GBK, UTF-8, 控制台代码页, amend, cat-file commit, 字节级验证, StandardOutputEncoding, Out-File 二次解码]
problem_patterns: [git commit 后中文提交信息显示为乱码疑似已损坏写入仓库, 反复 amend 换编码越改越乱无法确认真实存储状态, 途经 PowerShell 管道的验证输出本身被二次解码污染导致误判]
source_sessions: [ses_e4f5c5a83ffefUFnzHFvOEFJCW]
project: Date
severity: medium
quality_score: 91
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-06-config-mojibake-not-corruption]
---

# git 中文提交信息乱码：先分显示级还是数据级，用字节级直读 commit 对象做决定性验证

## Scenario

win32 + PowerShell 环境下执行 `git commit -m "中文信息"` 或 `git commit --amend -F <文件>`，回显与后续 `git log` 中中文均呈乱码，疑似中文提交信息已按错误编码写入仓库对象，需判断是否真实损坏并决定是否继续 amend。

## Key Signals

1. 同一控制台下更早的中文提交（f6ed489）回显正常——提示乱码可能是本次会话链路问题而非 git 全局配置问题。
2. 乱码形态呈 UTF-8↔GBK 错读规律形态，但"读文件按 UTF-8 写、按 GBK 解读"与"git 内部真存了 GBK 字节"两种假设的回显无法用肉眼区分。
3. 最大的误导源：用于验证的 `git log > 文件` 自身也经 PowerShell 管道（Out-File 按控制台代码页二次解码），验证工具输出的乱码不能证明数据损坏——出现了"验证手段与被测数据同链路"的循环污染。

## Essence

根因链：git 输出默认按 `logOutputEncoding`（此处 GBK）转码 → 控制台/重定向按代码页再次解码 → 所有途经 PowerShell 文本管道的中文都是"被显示链路改写过的副本"。因此**任何经 PowerShell 管道的 git 中文输出都不可作为存储状态的证据**；唯一的权威证据是绕开文本解码链、按原始字节直读 git 对象（`git cat-file commit HEAD` 的原始字节流）。判别的核心决策：输出乱码 ≠ 数据损坏，先建立字节级验证通道，再决定是否改写数据；盲目反复 amend 会在真实数据正确的情况下引入真正的损坏。

## Approach

1. 第一步先冻结数据：确认输出乱码后，**先不要 amend**，避免把显示层问题变成数据层问题。
2. 排除显示层：用 .NET Process 直读 commit 对象原始字节——`ProcessStartInfo` 设 `FileName='git'`、`Arguments='cat-file commit HEAD'`、`RedirectStandardOutput=true`、`StandardOutputEncoding=[Text.Encoding]::UTF8`、`UseShellExecute=false`，把 `StandardOutput.ReadToEnd()` 结果用 UTF-8 写入文件再读取。此通道不经控制台代码页，输出即 git 真实存储。
3. 判定分支：字节级读出的中文正常 → 数据未损坏，乱码纯属显示链路，收工不改数据；字节级读出乱码 → 才是数据级损坏，此时用 `-F <UTF-8 文件>` amend 修复，修完回到第 2 步复验。
4. 落盘验证脚本（ASCII 文件名与内容，仅路径与编码设置涉及非 ASCII）保存到临时目录执行，避免多语句长命令被工具层拒绝；验证后删除临时文件。

## Faster Next Time

- 首次看到 git 中文乱码，直接跑字节级直读（第 2 步），跳过所有"用 log/echo/Out-File 再看一遍"的循环——那些输出全在同一污染链路上，结论必然打架。
- 记住污染链清单：`git log` 回显、`git log > file`、`Out-File` 中转文件、`Select-String` 过滤输出，全部途经控制台代码页，均不可信；只有 .NET Process 显式编码 / 绕开 shell 的读取可信。
- 警告信号：同一数据两次"验证"给出不同乱码形态（UTF-8 错读 vs 更深的乱码）→ 说明是解码链不同层级在污染，不是数据在变。

## Applicability Boundaries

- 适用：Windows + PowerShell/GBK 代码页控制台下操作含中文的 git 提交信息；以及任何"验证输出自身经同一文本管道"的场景。
- 不适用：Linux/macOS 默认 UTF-8 终端（无二次解码链）；提交信息为纯 ASCII（无编码歧义）；已确认 git 配置 `i18n.commitEncoding/logOutputEncoding` 显式统一为 UTF-8 且控制台为 UTF-8 的环境。
- 平台限制观察：部分 Agent 工具层对多语句超长 PowerShell 命令直接拒绝解析，验证逻辑须落盘为脚本执行。

## Evidence or Examples

- 失败链（同一会话）：`-m` 提交回显乱码 → `amend -F` UTF-8 文件仍乱码 → 转 GBK 文件再 amend 后乱码形态更深 → `git log` 重定向文件读出仍是乱码——四轮均无法判定。
- 决定性验证：.NET Process 按 UTF-8 直读 `git cat-file commit HEAD`，输出 `知识库与技能治理入库：三库分工机制落地…` 完全正确，证明前四轮乱码全部来自显示层（logOutputEncoding=GBK + 控制台 CP936），数据从未损坏。
- 第二次提交复用同法：commit 4b6662c 字节级直读验证通过，parent 链 e7ad025 正确，全流程 2 次工具调用内闭环（此前同类判定耗费 4 轮以上无效 amend/重定向）。