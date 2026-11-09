---
id: 2026-11-09-cli-subprocess-utf8-ansi-decode-mojibake
title: 外部 CLI 子进程 UTF-8 中文输出被 PowerShell 按 ANSI 解码致留痕失真：OutputEncoding 修复 + 裁决复验
category: debugging
nature: pitfall
created_at: 2026-11-09T01:32:45
updated_at: 2026-11-09T01:32:45
tags: [编码失真, 子进程输出, UTF-8, ANSI 解码, OutputEncoding]
keywords: [子进程 stdout, UTF-8 乱码, ANSI 代码页, Console OutputEncoding, 中文诊断失真, 留痕可审计, 规则代码可读, 编码链验证, 修复复验, PowerShell 5.1]
problem_patterns: ["脚本捕获外部 CLI 诊断输出写入报告留痕，中文描述变乱码，误判为 CLI 输出异常或文件损坏而排查下游", "乱码只影响描述文本不影响规则代码（ASCII 完好），裁决结果看似正常，报告可审计性受损却无人察觉", "修复编码后不确定是否改变工具裁决语义，不敢直接收口"]
source_sessions: [ses_e43dfeddbffecZ9Y91Am1PbKju]
project: Date
severity: medium
quality_score: 86
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [build-env/2026-11-08-ps51-getcontent-selectstring-encoding-split, debugging/2026-11-06-config-mojibake-not-corruption]
---

# 外部 CLI 子进程 UTF-8 中文输出被 PowerShell 按 ANSI 解码致留痕失真：OutputEncoding 修复 + 裁决复验

## Scenario

门禁脚本捕获外部 CLI（如 Ruff）的诊断输出并整体写入审查报告留痕；CLI 在中文环境输出 UTF-8 中文诊断（如"系统找不到指定的文件"），落盘报告里同一句变乱码。

## Key Signals

- 报告原文区中文诊断显示为乱码（绯荤粺鎵句笉鍒版寚瀹氱殑鏂囦欢），但规则代码（E902/F401 等 ASCII）完整可读——裁决不受影响，容易被当"显示问题"放过。
- 易混淆陷阱：同时期有"Get-Content 读文件乱码 ≠ 文件损坏"的既有经验，容易套错结论——本次是捕获层污染，落盘文件内容**真的**被写坏，属于可审计性损失而非显示假象。

## Essence

根因链：外部进程按 UTF-8 写 stdout → PowerShell 5.1 管道/捕获按系统 ANSI 代码页解码 → 失真字节在进入字符串变量的那一刻就固化 → 落盘后不可逆。与"读文件乱码"是两条不同故障链：读文件乱码是**解码显示层**问题（文件本体可能正常），子进程捕获乱码是**编码转换层**问题（内容已污染）。
修复点在捕获发生之前：脚本开头设 `[Console]::OutputEncoding=UTF8`（try/catch 包裹，防旧版本无此属性崩溃）。修复纪律：编码修复不得改变工具裁决语义——修复后必须复验受影响场景，确认乱码消除且 exit/verdict 不变。

## Approach

1. 判链定位：乱码发生在"子进程输出 → 脚本变量"环节还是"文件 → 控制台显示"环节——前者修 OutputEncoding，后者按读取层经验处理（文件本体另行验证）。
2. 脚本开头加 `[Console]::OutputEncoding=UTF8`（try/catch 包裹），置于一切引擎调用之前。
3. 复验受影响场景：乱码样例重跑，逐项核对 ①中文原文可读 ②规则代码不变 ③exit 与 verdict_tag 不变 ④计数（finding_count）不变。
4. 报告审计口径：凡留痕含非 ASCII 诊断原文，验收先抽验编码链，再验内容。

## Faster Next Time

- 判别口诀："CLI 中文进报告就乱码 → 先修 OutputEncoding 再谈内容；读文件乱码 → 先验文件本体再定性"。
- 指纹特征：规则代码可读而描述文本乱码 = 捕获层解码失真（ASCII 完好、非 ASCII 损毁）。
- 新门禁/留痕脚本上线前的编码冒烟：构造一条会产生中文诊断的调用，确认报告原文区可读。

## Applicability Boundaries

- 适用：Windows + PowerShell 5.1 下以管道/变量捕获外部 CLI 输出并落盘留痕的场景（门禁报告、日志归档、批改记录）。
- 不适用：纯控制台显示场景（走终端设置）；PowerShell 7+（外部进程编码默认行为不同）；CLI 本身输出非 UTF-8 编码的场景（先确认 CLI 端编码再定修复方向）。
- 边界：OutputEncoding 在持久会话中有副作用（设置一次持续生效），后续乱码判断要考虑此因素。

## Evidence or Examples

- 来源会话：ses_e43dfeddbffecZ9Y91Am1PbKju（2026-11-09，ruff-review.ps1 编码修复）。
- 实测：Ruff E902 中文描述"系统找不到指定的文件。 (os error 2)"初版报告显示为"绯荤粺鎵句笉鍒版寚瀹氱殑鏂囦欢"；修复后复验 T1/T5/D7 三场景，中文可读且裁决 4/4/0 保持不变。
- 与 build-env/2026-11-08-ps51-getcontent-selectstring-encoding-split 的分工：那条管"读文件"层（Get-Content vs Select-String 解码不一致，文件本体可能正常）；本条管"子进程捕获"层（内容真被污染），两条合起来覆盖 PS 5.1 中文乱码的两条故障链。