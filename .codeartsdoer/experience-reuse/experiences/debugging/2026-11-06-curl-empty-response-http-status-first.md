---
id: 2026-11-06-curl-empty-response-http-status-first
title: curl 拉取空响应先查 HTTP 状态码：301 重定向不跟随致 0 字节
category: debugging
nature: pitfall
created_at: 2026-11-06T23:37:00
updated_at: 2026-11-06T23:37:00
tags: [curl, http-301, empty-response, diagnosis-first, redirect]
keywords: [HTTP 301, no element found, ParseError, size_download, http_code, 重定向不跟随, 空响应, 端点协议, -L, 状态码分类]
problem_patterns: [curl 拉取 API 得到 0 字节文件下游解析报空不知卡在哪层, XML/JSON 解析报 no element found 误判为接口故障, 重试同命令两次结果相同不产生新信息]
source_sessions: [ses_e4e8cc3d7ffenMVCgsUzGkzfrb]
project: Date
severity: medium
quality_score: 87
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-06-network-direct-connect-diagnosis, 2026-11-06-powershell-inline-json-escaping-python-fallback]
---

# curl 拉取空响应先查 HTTP 状态码：301 重定向不跟随致 0 字节

## Scenario
curl 拉取公开学术 API（http 端点）保存到本地文件，下游 XML 解析连续 2 次报 `xml.etree.ElementTree.ParseError: no element found: line 1, column 0`。表象是"接口没返回数据"，易误判为接口故障或网络问题而反复重试同一命令。

## Key Signals
- 误导表象：解析器报"空输入"——故障像是发生在解析层，但重试同命令两次结果完全相同，重试不产生新信息。
- 诊断动作的回报：重发请求带状态码输出 `-w '%{http_code}'`，得到 `HTTP:301 SIZE:0`——HTTP 层并非无响应，而是 301 重定向且响应体 0 字节。
- 确定性因果：端点写的是 http 协议，官方已做 http→https 永久重定向；curl 默认不跟随重定向（无 `-L`），拿到 301 的空响应体直接落盘——文件必然为空。

## Essence
解析层报"空输入"时，故障大概率在解析层上游（HTTP 层），因果链：端点协议过时（http）→ 服务端 301 → curl 默认不跟随 → 0 字节落盘 → 解析器报 no element found。表象在解析层、根因在请求参数层。先量化 HTTP 状态码与响应尺寸一次，即可把"网络故障/接口故障/参数错误"三类假设收敛为确定结论，再用确定性修复（换官方 https 端点）一次成功。

## Approach
1. 空文件/解析空输入第一步：重发请求带 `curl -s -o out.file -w '%{http_code} %{size_download}'`，先拿状态码与字节数，不看解析器报错做决策。
2. 按状态码分支处置：
   - `301/302` → 端点协议或路径变更：优先换官方 https 端点（显式正确协议），次选加 `-L` 跟随跳转；数据拉取场景推荐显式 https，减少中间跳转不确定性。
   - `200` 但 `SIZE:0` → 查请求参数/请求头（如 User-Agent 被服务端拒绝、查询条件无命中）。
   - `4xx` → 按码分类：403 rate limit 类立即停手，404 查端点拼写。
   - `5xx` / 超时 → 服务端或链路问题，按网络诊断路径处理，不归本篇。
3. 诊断一次成型后再改命令重试；禁止在无状态码信息时原样重试（第二次同错无信息量）。

## Faster Next Time
- 写 curl 命令时默认带上 `-w '%{http_code} %{size_download}'`，把诊断信息内建到第一次请求里，省掉专门的诊断轮。
- 遇到知名站点先确认官方端点协议（https 为默认），http 端点可能是历史写法。
- 判定顺序口诀：空响应 → 状态码 + 尺寸 → 301 换 https / 200 空查参数 / 429 停手。

## Applicability Boundaries
- 适用：curl/类 curl 的 HTTP 拉取在"拿到文件但内容为空/下游解析报空输入"的场景；Windows PowerShell 环境实测（PowerShell 下 curl 为 Invoke-WebRequest 别名时行为不同，需用 `curl.exe`）。
- 不适用：响应非空但内容畸形（解析报错非 no element found）；未落盘直接管道传递的场景（SIZE 信息需改用管道后统计）。
- `-L` 跟随跳转适用于允许跳转的场景；对需鉴权或跨域跳转的端点，跟随可能丢头，显式换正确端点更稳。

## Evidence or Examples
- 实证会话：arXiv API http 端点连续 2 次空文件 + `ParseError: no element found`；诊断输出 `HTTP:301 SIZE:0`；换官方 https 端点一次成功，返回 12 篇近 1 年代码审查智能体论文（含 OpenCodeReview、Ericsson 工业案例、ALIBI 对抗攻击、CRJudgeBench）。
- 时间成本对照：带状态码诊断 1 次请求即定位，修复 1 次即成；若继续盲目重试 http 端点则永远 0 字节。