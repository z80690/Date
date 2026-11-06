---
id: 2026-11-07-powershell-stderr-native-command-error-false-failure
title: PowerShell 下原生命令 stderr 被包装为 NativeCommandError，成功易被误判为失败
category: debugging
nature: pitfall
created_at: 2026-11-07T06:42:01
updated_at: 2026-11-07T06:42:01
tags: [PowerShell, NativeCommandError, stderr, 误判, 原生命令]
keywords: [NativeCommandError, RemoteException, stderr 包装, git clone 成功误判, Picked up JAVA_TOOL_OPTIONS, 2>&1 重定向, LASTEXITCODE, 产物验证, 失败判定, 进度信息]
problem_patterns: [原生命令输出带 NativeCommandError/RemoteException 包装疑似执行失败, git clone 或版本查询报红色错误但不确定是否真的失败, 以"有无报错文本"判断命令成败导致误重试或误报失败]
source_sessions: [ses_e4f5c5a83ffefUFnzHFvOEFJCW]
project: Date
severity: high
quality_score: 91
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-06-github-clone-timeout-intermittent-link, 2026-11-06-config-mojibake-not-corruption, 2026-11-06-git-commit-message-mojibake-byte-level-verification]
---

# PowerShell 下原生命令 stderr 被包装为 NativeCommandError，成功易被误判为失败

## Scenario

Windows + PowerShell 5.1 环境下，Agent 经 bash 工具调用原生命令（git clone / java -version / mvn 构建 / go build 等）。这类命令习惯把**进度信息、版本信息等非致命内容写到 stderr**；当命令经 `2>&1` 重定向或工具层捕获输出时，PowerShell 把每行 stderr 包装为 `NativeCommandError`/`RemoteException` 错误记录并渲染为报错样式。Agent 若以"输出里有没有 error 字样"判断成败，会把成功操作误判为失败，触发不必要的重试、降级甚至向用户谎报失败。

## Key Signals

- 报错样式为 `所在位置 行:1 字符:1 + <原命令> + ~~~~~~ CategoryInfo: NotSpecified: (...:String) [], RemoteException + FullyQualifiedErrorId: NativeCommandError`——注意**被包装的正文其实就是命令自己的输出**。
- 高频误导内容：`Cloning into 'xxx'...`（git clone 的进度输出就在 stderr）；`Picked up JAVA_TOOL_OPTIONS: ...`（JVM 环境变量提示，java/mvn 每次都会打印）；go/make 的中文日志在 GBK 控制台的乱码行。
- 同一命令的后续产物验证却显示一切正常。

## Essence

根因链：原生命令按 Unix 惯例把进度写 stderr → PowerShell `2>&1` 将 stderr 行转成 ErrorRecord → 工具层把 ErrorRecord 渲染成 error 样式 → "有报错"与"失败"被错误画上等号。**stderr 出现 ≠ 命令失败**；判据必须从"输出观感"切换到"退出码 + 实际产物"。

## Approach

1. 见到 NativeCommandError 包装时**先读被包装的正文**：是 `Cloning into...`、`Picked up...` 这类进度/提示（无害），还是 `Connection was reset`、`fatal:` 这类真实错误（需处置）。
2. 以 `$LASTEXITCODE` 为第一判据（0 = 成功）；工具层不便取退出码时直接做产物验证。
3. 产物验证按操作类型选择：clone → 目录存在 + 文件清单 + 关键文件大小；安装 → 可执行文件版本输出；构建 → 目标产物（jar/二进制）存在 + BUILD SUCCESS 行。
4. 三判据（正文性质、退出码、产物）结论冲突时以产物为准，并如实留痕"输出有包装但验证通过"。

## Faster Next Time

- 判定模板一句话：**先看正文是不是进度信息，再验产物，报错样式本身不构成失败证据**。
- 对 git/java/mvn/go 这类高频原生命令，预期内 stderr 输出（clone 进度、JVM 提示）可直接忽略，无需逐次排查。
- 反向警示：真实错误也走 stderr，所以不能因为"stderr 常是假警报"就整体忽略——逐行读正文是唯一可靠分流手段。
- 该误判的代价不止重试：会把"成功"当"失败"上报，违反"失败先报原文错误"类协作纪律的前提（报错的前提是真的失败了）。

## Applicability Boundaries

- 适用：Windows + PowerShell 5.1（包装最明显）；bash 下 stderr 不包装，但 `2>&1` 混流后同样适用"读正文分流"判读法。
- 不适用：命令确实非零退出且产物缺失——那是真失败，走重试/降级流程而非本经验。
- 包装行为与工具层实现相关（有的工具层会把 ErrorRecord 平铺），换平台/换 shell 后需重新观察一次包装形态。

## Evidence or Examples

- p3c 克隆：输出显示 `git : Cloning into 'C:\...\refs\p3c'... NativeCommandError` 样式，验证 `Test-Path refs\p3c` = True 且目录含 p3c-pmd 等完整结构 → 第 1 次克隆即成功，未做任何重试。
- `java -version` 输出 `Picked up JAVA_TOOL_OPTIONS: -Dfile.encoding=UTF-8...` 被包装为 error，但紧随其后的版本行 `openjdk version "17.0.20.1"` 正常——JDK 17 就绪结论成立。
- Maven 全程每条命令都带 `Picked up...` 包装，最终 `BUILD SUCCESS` 与产物 jar 均正常，构建结论不受包装影响。