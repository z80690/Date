---
id: 2026-11-11-local-proxy-mitm-scope-egress-verification
title: 本地 MITM 类加速代理的解密范围与出口真实性判定法：出口 IP 双通道对照 + CA 装卸差分 + 供应链调研
category: debugging
nature: technique
created_at: 2026-11-11T10:39:30
updated_at: 2026-11-11T10:39:30
tags: [debugging, 本地代理, MITM, 出口验证, 供应链风险]
keywords: [选择性 mitm, 出口 IP 对照, 卸根证书差分, TLS 握手被拒, TCP 直转, 名单外直连, ipinfo.io, certutil, issues 检索, 远程配置注入]
problem_patterns:
  - "拿一个本地'加速代理'当隐匿工具用，不知道它到底解密哪些域名、出口流量是否暴露真实 IP"
  - "代理装了根证书后一切正常，无法判断解密范围只凭配置名单还是有越界拦截"
  - "评估第三方代理工具安全性，只会看 star 数和 README，不会查实证争议"
source_sessions: [ses_e3a9c97a3ffeCp9OO263dGGrPC]
project: Date
severity: medium
quality_score: 88
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: ["workflow/2026-11-11-learn-first-tor-bridge-dispatch-review", "build-env/2026-11-11-blocked-official-channel-ecosystem-bundle-discovery", "debugging/2026-11-06-network-direct-connect-diagnosis"]
---

# 本地 MITM 类加速代理的解密范围与出口真实性判定法：出口 IP 双通道对照 + CA 装卸差分 + 供应链调研

## Scenario

需要在受限网络下评估一个本地加速代理（MITM 中间人类工具）能否承担两类不同职责：加速（可达性）与隐匿（出口不暴露真实 IP）。必须用实测回答三问：它解密哪些域名的流量？出口 IP 是不是真实 IP？信任它有什么风险？实例为 DevSidecar（docmirror，Electron 本地代理，实测端口 31181）。

## Key Signals

- **出口 IP 与直连完全相同**：经代理访问 `ipinfo.io` 返回的 IP 与不带代理直连完全一致——该代理对目标域名做了 TCP 直转（未接管），出口无任何隐匿。这是"仅加速不隐匿"的定性证据，不是故障。
- **卸载根证书后名单内域名 HTTPS 仍能响应/或 TLS 握手被拒**：说明该域名在 mitm 拦截名单内（代理在本地终结 TLS）；名单外域名无此行为。CA 装卸差分是解密范围的实测判据。
- **GitHub issues 里的供应链信号**：远程配置可向页面注入脚本、明文 HTTP 被转成 SSL 波及名单外域名、静默失效类缺陷（配置写了但实际不生效）——这些是 MITM 类工具的共性风险面。

## Essence

判定一个本地 MITM 代理的"能力-风险"画像是一个三步实测链，结论必须是三分口径（加速能力 / 隐匿能力 / 信任风险），不允许笼统的"能用/不能用"：

1. **出口真实性**：出口 IP 是否等于真实 IP 决定"隐匿"定性——MITM 加速代理默认不做出口替换，隐匿判定一票否决。
2. **解密范围**：解密范围由其拦截名单决定且可变（远程配置可下发），"现在只解密 A 域名"不构成安全承诺；CA 一旦安装，名单扩大即全量解密。
3. **信任风险**：这类工具的架构本质是本地中间人，风险不在"是否有后门实锤"（往往查不到），而在**能力面**——远程配置可注入页面脚本、拦截范围可越名单扩张、静默失效导致用户误判防护在生效。

## Approach

1. **出口真实性一行对照**：
   `curl.exe -x http://127.0.0.1:<proxy_port> https://ipinfo.io` 与 `curl.exe https://ipinfo.io` 各跑一次比对 IP。相同 → 该通道无隐匿，结论"仅加速"。
2. **解密范围 CA 装卸差分**：装根证书前后对名单内/外域名各测一次 HTTPS；卸载后（`certutil -delstore Root <CN关键字>`，卸完 `certutil -store Root | findstr <CN关键字>` 校验残留为 0）名单内域名 TLS 握手被拒/行为变化 = mitm 拦截实证。**敏感用途环境永不安装其根证书**，评估用差分做完立即卸载。
3. **供应链调研（只用已通网络，命令行）**：对该工具 GitHub 仓库 issues 按关键词组检索（隐私/偷数据/后门/内存异常/安全漏洞/证书），逐条读正文只记事实不臆测；重点核"远程配置内容"（是否含脚本注入、拦截名单下发）。
4. **输出三分结论**：加速能力（哪些域名可达/提速）、隐匿能力（出口 IP 实测值）、信任风险（能力面清单 + issues 链接），并给出隔离纪律——与真正的隐匿通道（如 Tor）物理隔离，互不接管流量。

## Faster Next Time

- 先跑出口 IP 对照再谈一切：这一行命令直接决定工具能不能进"隐匿"赛道，省掉全部后续争论。
- 看到工具要求"信任根证书"立刻触发差分评估流程，而不是照装了事；装过的一定留卸载与残留校验记录。
- "远程配置可注入脚本"是 MITM 类工具必查项——它意味着今天的安全结论明天可被远程配置推翻，信任声明必须绑定"永不装 CA + 永不启用远程配置自动更新"。
- issues 检索零命中"后门"不等于安全：改查"能力面"（能做什么）而非"动机面"（想干什么）。

## Applicability Boundaries

- 适用：本地 HTTP/SOCKS MITM 类加速代理（DevSidecar、Whistle、Fiddler 类）的能力与风险评估；任何"代理装 CA 才能用"的工具准入决策。
- 不适用：VPN/透明代理/正向隧道类工具（出口 IP 会变、无本地 CA，判定语义完全不同，本法的 CA 差分步骤无意义）；对端可信内网代理（无 mitm 架构）。
- 边界：解密名单随远程配置变化，结论有时效性，复用本判定法重测而非引用旧结论；出口 IP 对照需排除 CDN 就近返回干扰（选无 CDN 的回显服务）；本方法只判行为不判动机，"未发现恶意行为"与"安全"不是同义语。