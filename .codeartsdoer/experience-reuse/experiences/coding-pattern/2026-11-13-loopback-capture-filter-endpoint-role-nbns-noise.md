---
id: 2026-11-13-loopback-capture-filter-endpoint-role-nbns-noise
title: "回环抓包判定过滤器按端点角色收窄：接口名义覆盖面须实测核对，系统级广播是真实泄漏特征非误报"
category: coding-pattern
nature: methodology
created_at: 2026-11-13T12:33:44
updated_at: 2026-11-13T12:33:44
tags: [tshark, display-filter, 回环抓包, 判定口径, 流量审计]
keywords: [tshark display filter J1~J5, NPF_Loopback 实际覆盖面, 按端点角色收窄过滤器, 代理协议头不计明文, NBNS 广播泄漏主机名, LLMNR mDNS 系统噪音, 隐藏判定 hidden_failure, 非演练流量混入, SNI 摘录证据, 整改口径用户裁决]
problem_patterns: [判定过滤器用"非 TLS 即明文命中"的全局否定式，把回环代理协议段等不出机的流量也计入，命中数虚高, 回环抓包接口名义上是 loopback，实际捕获面包含宿主全部回环与邻近广播流量，与本演练无关的进程流量混入判定集, 判定器抓到系统级广播（NBNS/LLMNR）泄漏主机名时当作误报丢弃，丢失真实检测价值]
source_sessions: [ses_e2d1b45edffeiZTF0xjq1cyv7a]
project: Date
severity: medium
quality_score: 85
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-13-restricted-agent-adapter-literal-ip-jsonl-verdict, 2026-11-12-local-dummy-llm-endpoint-egress-governance]
---

# 回环抓包判定过滤器按端点角色收窄：接口名义覆盖面须实测核对，系统级广播是真实泄漏特征非误报

## Scenario

流量判定器（tshark display filter 驱动）对演练 pcapng 做五项判定：明文命中/白名单外 IP/异常外连/伪装有效/日志干净。初版过滤器用全局否定式（"tcp and not tls and not (ip.addr in 白名单)"）定义"明文命中"，且假设 loopback 抓包接口只含本演练回环流量。实跑判定暴露两类口径问题：过滤器语义过宽（代理链路的协议明文段被计入"目标明文"），以及抓包面混入大量与本演练无关的宿主流量——其中系统级 NBNS 广播恰好构成真实泄漏证据。

## Key Signals

- **过滤器语义过宽的信号**："明文命中"的判定意图是"目标端点收到非加密交互"，但"not tls"这类全局否定式把链路上任何非 TLS 段都算上——语义应绑定**端点角色**（谁发给谁的什么端口），而非流量形态全局否定。
- **接口覆盖面与名义不符的信号**：回环抓包的 pcap 里出现局域网物理网段地址（NBNS 广播 192.168.0.103→192.168.0.255）与无关进程的回环 TLS（SNI 指向云服务域名）——名义 loopback ≠ 实际只抓演练流量。
- **真实发现的信号**：判定器报出的"白名单外命中"若能溯源到具体协议与内容（NBNS Name query 泄漏主机名），它不是噪音误报，而是判定器抓到的**真实检测点**——哪怕该流量并非演练动作产生。

## Essence

流量判定过滤器的设计规则有两条：**①按端点角色收窄**——每项判定绑定"通信双方角色+端口"（如 J1=目标端口上的非 TLS 明文），代理/工具自身的协议头属本机回环不出机，不计入"目标明文"；**②抓包面先实测后判定**——接口名义名称（loopback）不等于实际捕获面，首跑前用判定过滤器本身试抓核对，确认混入流量的构成。系统级广播（NBNS/LLMNR/mDNS，Windows 默认开启）向局域网泄漏主机名是**蓝队真实检测点**：判定器抓到它应产出 hidden_failure + 整改口径（禁用广播协议/豁免口径/维持原判）交用户裁决，而非当误报抹掉——"非演练动作产生"改变的是整改责任归属，不是泄漏事实本身。

## Approach

1. **过滤器按端点角色改写**：把"not tls 全局否定"改为绑定目标端口与方向的精准式，例：明文判定 = `tcp.port == <目标端口> and not tls`；伪装有效性判定绑定 TLS handshake 类型并摘录 SNI 作证据。
2. **首跑核对抓包面**：判定前先跑一次 `tshark -r pcapng -q -z conv,tcp`（会话统计）或抽 3 条原始包，确认 pcap 构成——演练流量占比、混入流量类型（其他进程回环/局域网广播）。覆盖面不符则换接口或加 BPF 收窄采集端。
3. **命中溯源后再定性**：任何非零命中先取摘录（`-T fields` 取 src/dst/协议/内容首行）溯源：演练动作产生 → 判 failure；系统级广播 → 判 failure + 整改口径三选一（禁用协议/豁免登记/维持原判）交用户裁决，禁静默豁免。
4. **判定与整改分离**：判定函数只输出事实（命中数+证据摘录），整改口径由 spec 条款+用户裁决决定——判定器不改规则。

## Faster Next Time

- 写流量判定过滤器时的三问：①语义绑定的是端点角色还是流量形态全局否定？②抓包接口的实际覆盖面实测过吗？③非零命中的溯源动作 defined 吗？
- Windows 局域网检测基线：NBNS（UDP 137）/LLMNR（UDP 5355）/mDNS（UDP 5353）广播默认泄漏主机名——真实环境蓝队加固第一条即禁用之；判定器遇到它们是**抓到了东西**，不是过滤器坏了。
- 证据摘录模板：每项命中留 `src→dst 协议 长度 内容首行` 一行，报告可回放。

## Applicability Boundaries

- 适用：pcap/tshark 驱动的流量合规判定、演练隐藏效果验证、局域网泄漏审计；任何"抓包面含非受控流量"的判定场景。
- 不适用：内核级精确采集（BPF 在采集端已按五元组收窄，判定端无需再过滤）；纯指标统计（不做逐包判定时过滤器语义要求可放宽）。
- 边界：Npcap 的 loopback adapter 实际捕获面以实测为准（不同版本/绑定方式覆盖面不同）；NBNS 判定命中后"禁用广播协议"是系统配置变更（需管理员），豁免口径属 spec 级裁决——两条路都超出判定器职责，须留痕交用户。

## Evidence or Examples

- 实证会话（P003 round-08 判定，Npcap loopback 接口）：J1 明文=0（过滤器按目标端口 8443 精准化后）/J2 白名单外 IP=3（NBNS 广播 192.168.0.103→192.168.0.255，Name query 泄漏主机名 SKY-20260623PHL）/J3 异常外连=0/J4 伪装有效=True（TLSv1.2 ClientHello 摘录含 SNI）/J5 日志干净=0 → 结论 hidden_failure，failing=['j2_public_ip_hits']。
- 混入流量实证：同 pcap 内出现与本演练无关进程的回环 TLS（SNI=snap-access.cn-north-4.myhuaweicloud.com）——证实"名义 loopback ≠ 只抓演练流量"。
- 修复位置：adapter/verdict.py 过滤器按端点角色重写 + 子进程 UTF-8 解码修正（GBK 噪音崩溃另条目覆盖）；判定结论与整改口径（禁用 NBNS/豁免登记/维持原判）按 spec 5.7.1-4 留用户裁决，未整改禁开下一轮。