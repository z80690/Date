---
id: 2026-11-12-local-dummy-llm-endpoint-egress-governance
title: 本地哑端点承接框架 LLM 调用面：OpenAI 兼容占位服务绑回环 + .env 外连面清单化治理（WMI 启动解释器须全路径）
category: build-env
nature: technique
created_at: 2026-11-12T22:29:45
updated_at: 2026-11-12T22:39:19
tags: [哑端点, 回执模式, 外连面治理, WMI 启动, 回环绑定]
keywords: [LLM_SERVER_URL, OpenAI 兼容 /v1/chat/completions, 127.0.0.1 哑端点, 占位响应, SERVER_HOST, PROXY_URL 置空, 厂商 KEY 清空, TAVILY_API_KEY, WMI ReturnValue 9, Win32_Process.Create]
problem_patterns: [第三方智能体框架启动即调公网 LLM API，与禁公网外连红线直接冲突且平台无外部可调用模型端点, 框架 .env 散布多组厂商 KEY/搜索 KEY/代理项，只改 LLM 主项仍留隐蔽外连面, 用 WMI 启动 python 长驻服务返回 ReturnValue=9 无任何解释，误判为权限或语法问题]
source_sessions: [ses_e3024c46cffeogzf8wCK8buHaO]
project: Date
severity: medium
quality_score: 85
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-12-framework-llm-decoupling-config-first-endpoint-reality, 2026-11-06-third-party-framework-model-config-bypass, 2026-11-11-local-proxy-mitm-scope-egress-verification]
---

# 本地哑端点承接框架 LLM 调用面：OpenAI 兼容占位服务绑回环 + .env 外连面清单化治理（WMI 启动解释器须全路径）

## Scenario

回执模式（方案 a）下：智能体承担真实决策，第三方框架只保留调度与工具执行逻辑，其 LLM 调用面需要一个"不炸即可"的本地承接点；同时框架 `.env` 内除主 LLM 项外还散布搜索 API、厂商 KEY、代理等多处外连面，任何一处残留即违反禁公网外连红线。部署验证要求逐项实测而非口头声明。

## Key Signals

- 框架默认配置把 LLM 指向公网端点（如 PentAGI 默认 OpenAI 端点）；不治理则启动后首次推理即外连。
- `.env` 中成组出现的残留外连项：`OPEN_AI_KEY`/`ANTHROPIC_API_KEY`/`TAVILY_API_KEY` 等厂商 KEY、search 类（Tavily/DuckDuckGo 等多家）、`PROXY_URL`。
- WMI 启动返回 `ReturnValue=9` 且无 stderr 解释——路径未找到（相对名解析失败），非权限问题。

## Essence

哑端点 = 绑 127.0.0.1 的 OpenAI 兼容占位 HTTP 服务：`/v1/chat/completions` 返回确定性占位 JSON（合法响应结构、固定内容声明"决策由智能体回执承担"），`/health` 供存活探测。框架配置把 LLM 指向哑端点后，外连面治理须**清单化逐项清空**（主 LLM 项 + 全部厂商/搜索 KEY + 代理项 + 监听绑回环），并以 Select-String 逐项实测收口。长驻启动走 WMI `Win32_Process.Create` 时解释器与脚本一律全绝对路径。

## Approach

1. 哑端点实现（最小面）：Python HTTP 服务监听 `127.0.0.1:7810`；`/v1/chat/completions` 返回含 `id/object/created/model/choices/usage` 的占位响应；`/health` 返回 `{"status":"ok","mode":"placeholder"}`。无任何出站调用。
2. 长驻启动：WMI `Win32_Process.Create`——`CommandLine` 写解释器全路径（如 `D:\soft\scoop\apps\python311\current\python.exe`）+ 脚本全路径；相对名 `python` 实测 ReturnValue=9。成功返回 0 + 进程 PID，随即 curl 打 `/health` 与 `/v1/chat/completions` 双断言占位响应。
3. PentAGI `.env` 治理清单（逐项落值）：
   - `LLM_SERVER_URL=http://127.0.0.1:7810/v1`（主调用面指向哑端点）；
   - `SERVER_HOST=127.0.0.1`（服务绑定回环，禁 0.0.0.0）；
   - `PROXY_URL=`（置空兜底）；
   - 厂商 KEY 全清空：`OPEN_AI_KEY=` / `ANTHROPIC_API_KEY=` 等；
   - search 类 KEY 全清空（八家逐一置空，防 search/scraper 子栈外连）。
4. 验证收口：`Select-String -Path .env -Pattern "KEY|PROXY|SERVER_HOST|LLM_SERVER_URL"` 逐项输出实测值留痕；哑端点进程存活 + 双端点响应断言。

## Faster Next Time

- 治理用**清单模板**（主 LLM/服务绑定/代理/厂商 KEY/搜索 KEY 五组），不要只改 LLM 主项——search 与 scraper 子栈的 KEY 是高频漏项。
- WMI 返回 9 先查 CommandLine 路径解析（解释器是否全路径），再谈其他；Start-Process -ArgumentList 传参会吞参数，长驻服务一律 WMI。
- 哑端点响应体保持 OpenAI 结构合法（choices/usage 齐全），避免框架侧解析器比"返回 200"更早炸掉造成误判。
- 部署留痕把 `.env` 关键项实测输出直接贴入 trace 文件，验收时免重跑。

## Applicability Boundaries

- 适用：Windows 本机部署；框架配置面为 OpenAI 兼容端点；回执/占位模式下框架 LLM 层接受哑响应；禁公网外连类红线场景。
- 不适用：框架模型层强耦合无法重定向（须走适配层改造）；需要真实 LLM 推理跑在框架进程内的场景（此时哑端点不成立，应换决策方承担方式）；生产环境（哑端点仅限本地演练/开发）。

## Evidence or Examples

- 实测启动：`WMI_RETURN=0 PID=15176`（解释器全路径）；`WMI_RETURN=9`（相对名 python，修正前）。
- 哑端点实测响应：`/health` → `{"status": "ok", "mode": "placeholder"}`；`/v1/chat/completions` → `{"id":"chatcmpl-placeholder",...,"content":"[placeholder] deterministic response; decisions are made by the CodeArts agent (plan-a receipt mode)."...}`。
- PentAGI .env 实测核验输出：`OPEN_AI_KEY=` / `ANTHROPIC_API_KEY=` / `LLM_SERVER_URL=http://127.0.0.1:7810/v1` / `PROXY_URL=` / `SERVER_PORT=8443` / `SERVER_HOST=127.0.0.1` / `TAVILY_API_KEY=` 全部符合治理清单。
- 环境：win32 / PowerShell 5.1 / Python 3.11.9（Scoop）。