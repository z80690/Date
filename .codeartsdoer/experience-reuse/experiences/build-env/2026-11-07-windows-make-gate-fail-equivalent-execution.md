---
id: 2026-11-07-windows-make-gate-fail-equivalent-execution
title: Windows 下 make 门禁目标失败：读 recipe 取实质断言，宿主 shell 等价执行，不改第三方源码
category: build-env
nature: technique
created_at: 2026-11-07T04:37:00
updated_at: 2026-11-07T04:37:00
tags: [windows, gnu-make, build-verification, powershell, exe-suffix]
keywords: [make check-invariants, unexpected EOF, sh -c 引号解析, 等价执行, 架构不变量, .exe 后缀缺失, mingw make, Go 构建, PowerShell 5.1, LASTEXITCODE]
problem_patterns: [第三方仓库 make all 在 Windows 构建成功但门禁目标报 sh 解析错误, 构建出的二进制无 .exe 后缀导致 PowerShell 无法直接执行, 不能改第三方源码又不能跳过架构检查时的两难]
source_sessions: [ses_e4f5c5a83ffefUFnzHFvOEFJCW]
project: Date
severity: medium
quality_score: 86
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-07-maven-download-degradation-chain-sha512-verify, 2026-11-07-framework-capability-verify-official-test-suite, 2026-11-06-github-clone-timeout-intermittent-link]
---

# Windows 下 make 门禁目标失败：读 recipe 取实质断言，宿主 shell 等价执行，不改第三方源码

## Scenario

克隆第三方 Go 工程（参考仓库，只读约束）后在 Windows 上做"构建+自检"验收：`make all` 期望一条命令完成依赖下载 → build → verify（含架构不变量机器检查）。在 Linux/macOS 一条命令的构建链路，到 Windows 上门禁步骤与产物命名都可能失败，且失败点会被构建日志的输出顺序掩盖。

## Key Signals

1. `make all` 日志尾部：`make[1]: *** [Makefile:110: check-invariants] Error 2`，错误原文 `\: -c: line 2: unexpected EOF while looking for matching '"'`——但同一次运行里 `binaries built → bin/ (8 binaries)` 与 `go vet ./...` 均已成功。失败被限定在最后一个门禁目标，不是构建本身。
2. 直接运行产物：PowerShell `& .\cairn-mcp` 报 CommandNotFoundException——列目录确认 8 个二进制全部**无 .exe 后缀**（Makefile 固定输出名，未做 Windows 适配）。
3. PowerShell 5.1 不支持 `&&`（报 `标记"&&"不是此版本中的有效语句分隔符` 的 ParserError），多命令须用分号顺序执行。

## Essence

Windows 的 mingw make 用 `sh -c` 执行 recipe，多行且含引号/转义的 recipe 行会解析失败（unexpected EOF）；这类失败只证明"该 recipe 行与 Windows sh 不兼容"，**不证明被检查的架构性质不成立**。正确处置是把门禁目标还原为它实质断言的内容（例如 4 条 grep 架构不变量），在宿主 shell 中逐条等价执行，语义一一对应、结果留痕——既不跳过检查，也不为跑通而改第三方源码。二进制无 .exe 是产物命名层问题，复制副本即可修复，不影响二进制本身的有效性。

## Approach

1. 先分段判位：从 make 日志确认哪些目标成功（build、vet）、哪个目标失败（check-invariants）；失败目标不等于前序步骤失败，不要全部重来。
2. 读 Makefile 失败目标的 recipe，把每条命令翻译回它断言的语义（如 `grep -rn "X" ... | grep -q .` = "存在至少一处调用"；`! grep ...` = "必须零命中"）。
3. 在 PowerShell 中逐条等价执行（Select-String/Get-ChildItem 等原生等价物），保留 recipe 里的过滤条件（排除 `*_test.go`、剥离注释行等）；每条记录 True/False 与命中数。
4. 汇报格式："构建 N 二进制 ✓ + go vet ✓ + 架构不变量 N/N 等价执行 PASS（原 make 门禁因 Windows sh 解析缺陷无法运行，等价执行留痕）"——检查强度与通过事实分开陈述。
5. 产物后缀修复：`Copy-Item cairn-mcp cairn-mcp.exe`（只加副本不动原文件）；逐个探测 `& .\xxx.exe` 并查 `$LASTEXITCODE`。
6. 主备路线验证：服务入口（MCP/stdio）与 CLI 入口各测一次，exit 0 且语义输出正常即判可用；stdio 服务无帮助输出属协议正常，不要误判为失败。任一主备路线可用即可满足"接入可用"验收。

## Faster Next Time

- 一句话决策：Windows make 的门禁目标失败 → 读 recipe 取实质断言 → 宿主 shell 等价执行；禁改第三方源码、禁跳过检查。
- 警告信号：make 输出出现 `unexpected EOF while looking for matching '"'`，基本可断定是 recipe 与 sh 的解析冲突，不是代码缺陷。
- Go 工程在 Windows make 构建后先列 `bin/` 看后缀；无 .exe 先补副本再探测，省掉一次 CommandNotFoundException 试错。
- PowerShell 5.1 用 `;` 不用 `&&`；判断外部 exe 成败用 `$LASTEXITCODE` 而非 `$?`。

## Applicability Boundaries

- 适用：Windows + mingw/GNU make 4.x 执行含多行/引号 recipe 的 Makefile；第三方参考仓库只读约束；make 管理的 Go 等工程。
- 不适用：CI/CD Linux 环境（recipe 原生可跑）；失败源自代码/依赖本身（应修代码而非等价执行）；有权且应当修改 Makefile 的自有工程（拆行或修语法比等价执行更根治）。
- 等价执行的强前提：断言语义必须能无损翻译（正则/路径/过滤条件一一对应）；翻译有损时如实报告"无法等价验证"，禁止硬凑通过。

## Evidence or Examples

- 实录（2026-11-07，refs/Cairn，Go 1.26.5 + GNU Make 4.4.1 + Windows 10）：`make all` 产出 8 个二进制后 check-invariants 报 `unexpected EOF while looking for matching '"'`；PowerShell 等价执行 4 条不变量（ResolveLatest 调用存在 hits=2、查询端零 LLM import、零 embedding/向量库引用、查询端只读 raw-hits=0），扫描 75 个生产 Go 文件，4/4 PASS。
- `cairn-mcp.exe` / `cairn.exe` 副本探测 exit 0；`cairn` CLI 7 个子命令（find/impact/status/sentinel/why/timeline/show）help 输出正常，备用路线实证可用。