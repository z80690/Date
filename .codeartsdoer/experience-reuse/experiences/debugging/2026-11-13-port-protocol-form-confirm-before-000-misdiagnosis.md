---
id: 2026-11-13-port-protocol-form-confirm-before-000-misdiagnosis
title: "HTTP=000 三连先查端口协议形态再归因：https 打 http 服务必败，勿误判防火墙或进程崩溃"
category: debugging
nature: pitfall
created_at: 2026-11-13T12:33:44
updated_at: 2026-11-13T12:33:44
tags: [curl, 协议错配, HTTP-000, 根因误判, 服务联调]
keywords: [HTTP=000, curl https 打 http 服务, TLS 握手打纯 HTTP 必败, Connection refused, 防火墙误判, 进程崩溃误判, 端口协议形态先行确认, 多端口服务, 控制台端口 vs 代理端口, 重启框架无效]
problem_patterns: [curl 用 https scheme 请求纯 HTTP 服务端口，连接层直接失败返回 000，被误归因为防火墙拦截或服务崩溃, 同一 000 症状连续重试并重启服务框架，每次修复动作都打在错误层，真因协议形态从未被检查, 多端口服务（控制台/代理/TLS 目标）各端口协议形态不同，按单一假设统一构造请求]
source_sessions: [ses_e2d1b45edffeiZTF0xjq1cyv7a]
project: Date
severity: medium
quality_score: 88
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-06-curl-empty-response-http-status-first, 2026-11-12-third-party-framework-windows-daemon-startup-failure-chain]
---

# HTTP=000 三连先查端口协议形态再归因：https 打 http 服务必败，勿误判防火墙或进程崩溃

## Scenario

本地服务联调：经本地代理端口转发 HTTPS 请求到目标服务。用 `curl -x http://127.0.0.1:<proxy> https://<target>...` 连续 3 轮得到 HTTP=000，期间依次怀疑并排查：宿主防火墙拦截、框架进程崩溃退出（还重启了框架）——每个修复动作都"成功执行"但 000 依旧。真因从未被检查：请求的 scheme 与目标端口的实际协议形态不匹配。

## Key Signals

- **000 的双重歧义**：`%{http_code}` 返回 000 既可能是"连不上"（Connection refused）也可能是"连上了但 TLS 握手失败"（对纯 HTTP 端口发 TLS ClientHello，对方无法解析）——两种根因的修复动作完全不同，000 本身不区分。
- **误判链特征**：每轮重试带上了新的"修复"（改目标地址→重启框架），但请求构造里的 scheme 从未变过——**修复变量没盖住真因变量**，失败必然复现。
- **确定性鉴别动作**：`curl -v` 打同一端口，输出 `Connection refused` = 端口没监听；输出 TLS handshake 报错/乱码响应 = 端口在监听但不是 TLS 服务（多半是纯 HTTP）。

## Essence

对多端口本地服务，**请求构造前必须逐一确认每个端口的协议形态**（控制台端口、代理端口、TLS 目标端口的形态可以各不相同）。因果链：目标端口是纯 HTTP 服务 → 客户端按 https 构造请求 → TLS ClientHello 落在 HTTP 解析器上握手必败 → curl 报 000 → 被误读为网络层/进程层故障 → 修复动作（防火墙/重启）全部打错层。协议形态是请求的最前置前提，先于一切网络诊断。

## Approach

1. **000 第一问：scheme 对吗？** 拿到 000 先 `curl -v` 看失败层次：`Connection refused`（无监听）vs TLS 报错（协议错配）vs 超时（网络），三种输出指向三个不同的下一步。
2. **确认端口形态的三个来源**（按可信度）：①服务 README/启动日志（常明示"控制台 http://...:8787 / 代理 :8788"）；②服务源码监听段（`listen` 地址与协议处理器）；③试探性 `curl http://<port>/api/health`（http 形态能通即证伪 TLS 假设）。
3. **多端口逐一定义**：把服务的每个端口写成"端口→形态→用途"三列表（如 8787=HTTP 控制台 / 8788=HTTP 代理 / 8443=TLS 目标），请求构造严格按表选 scheme。
4. **重启框架前先做第 1 步**：进程崩溃是 000 的可能根因之一，但必须先排除协议错配（一条 verbose curl 的成本）再动重启——重启是重操作，且会掩盖现场。

## Faster Next Time

- 联调命令模板默认带 `-v` 和 `-w '%{http_code}'`：000 时 verbose 输出里直接读失败层次，一次请求完成鉴别。
- 检查清单：000 → ①scheme/协议形态 ②端口监听（netstat）③防火墙 ④进程存活——**协议形态排在防火墙和进程之前**，因为它的验证成本最低且最易被忽略。
- 反思信号：如果连续两轮"修复成功但症状不变"，停止在原假设上加码，回到请求构造本身找未变的变量（scheme、路径、请求头）。

## Applicability Boundaries

- 适用：curl/HTTP 客户端对本地或远程多端口服务的联调，尤其服务同时含 HTTP 控制台、HTTP 代理、TLS 端点三种形态（代理框架/网关类服务常见）。
- 不适用：响应非空但内容异常（走内容层诊断）；301 重定向导致的空响应（已有独立条目：先查状态码得 301 换 https 端点）；纯网络不可达（直连被墙、DNS 失败，另有诊断矩阵条目）。
- 边界：TLS 端点用自签证书时还需 `-k`/CA 配置，那是握手后的证书校验问题，与"000 连接层失败"不同层，勿混淆。

## Evidence or Examples

- 实证会话（P003 round-01~04）：`curl -x http://127.0.0.1:8787 https://...` 三轮 HTTP=000；期间实测防火墙因素（WSL 网关 IP 入站被拒）、ARTEX 进程确曾崩溃退出一次并重启，但重启后 8787 仍 000；最终以 verbose 输出 `connect to 127.0.0.1 port 8787 failed` + 对照 ARTEX README（8787=前端+API 纯 HTTP）定位真因为 https 打 http 服务。
- 正确构造（round-04 实测 HTTP=200）：`curl -x http://127.0.0.1:8788 https://127.0.0.1:8443/...`——8788 作 HTTP 代理，8443 才是 TLS 目标。
- 成本对照：协议形态检查 1 条命令 vs 误判链 3 轮重试+1 次框架重启。