---
id: 2026-11-11-bridgedb-bridge-line-channel-deadend-human-handoff
title: 网桥行获取通道死路图谱与 AI/人工分工交接协议：递归悖论判定 + 可达性先行实测 + 待命闭环
category: debugging
nature: methodology
created_at: 2026-11-11T12:14:30
updated_at: 2026-11-11T12:14:30
tags: [debugging, 网桥, 受限网络, 人机分工, 通道可达性]
keywords: [bridges@torproject.org, get transport obfs4, moat 直连超时, Gmail 悖论, Riseup, IP 层阻断, 本机出口代理, 手机蜂窝数据, torrc 恢复出厂, 待命闭环]
problem_patterns:
  - "tor 网桥调试到最后一环：PT 框架已通但拿不到有效网桥行，参数试尽仍不通，不知道卡在配置还是通道"
  - "想用本地加速代理辅助访问境外受信服务（BridgeDB/moat/Gmail）拿凭证，实测发现全部不可达，误以为是代理配置问题反复折腾"
  - "判定为'必须人工操作'后直接甩给用户，没有清场、没有具体交接协议，用户不知道做什么、AI 收到输入后做什么"
source_sessions: [ses_e3a9c97a3ffeCp9OO263dGGrPC]
project: Date
severity: medium
quality_score: 84
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: A
related_experiences: ["debugging/2026-11-11-tor-censored-network-bridge-debug-chain", "build-env/2026-11-11-tor-browser-full-package-acquire-official-config-integration", "debugging/2026-11-11-local-proxy-mitm-scope-egress-verification"]
---

# 网桥行获取通道死路图谱与 AI/人工分工交接协议：递归悖论判定 + 可达性先行实测 + 待命闭环

## Scenario

受限网络下 tor 网桥调试链的最后一环：PT 插件框架已验证可工作（bootstrap 到 `conn_done_pt`），出口连通只差**一条有效 obfs4 网桥行**。约束：纯命令行、非提权、仅有"本机出口型加速代理"（不翻墙）可用辅助通道、无浏览器 GUI。目标是在纯 AI 侧拿网桥行的通道全部穷尽后，正确判定结构性死路并设计 AI/人工分工交接，而不是无限重试或放弃。

## Key Signals

- **参数级穷尽的标志**：官方内置 PT 参数逐一失败且形态各异——snowflake broker 卡 2%（PT 连接成功但下一跳超时）、meek 旧参 `Key digest wrong length`（字段错位）、meek 新参 TLS 握手无响应卡 10%。三种不同失败形态意味着**不是某个参数写错，而是通道被墙**，继续调参属于同症状重复尝试。
- **moat 直连超时**：`moat.torproject.org` 动态网桥 API 直连 20s 超时——动态获取路也被 IP 阻断切断。
- **本机加速代理对境外受信服务"全 000"**：`mail.google.com`、`bridges.torproject.org`、`www.google.com` 经代理 `-I` 实测全部 000（不可达）。与"200 但出口=真实 IP"（可达但无隐匿）是**两种不同信号**：000 = IP 层阻断，出口型代理无解。
- **BridgeDB 邮箱通道前置规则**：`bridges@torproject.org` 只回复 **Gmail/Riseup 域发件人**（正文 `get transport obfs4`），QQ 邮箱等被拒（先例）——而 Gmail 本身需要翻墙，构成递归死路。
- **代理白名单不可编程配置**：DevSidecar 的白名单字段不存在于 `setting.json`（GUI 侧管理），命令行侧无法通过改配置让代理"翻墙"——该代理架构上就是本机出口，出口=真实 IP。

## Essence

**递归悖论是结构性死路的判定标志**：拿网桥行需要 Gmail → Gmail 需要翻墙 → 翻墙需要网桥行。当满足三个条件——①官方参数级尝试穷尽且失败形态各异；②动态获取域直连超时；③本机辅助代理对目标服务全 000——即可判定"纯命令行/AI 侧结构性不可行"，这不是能力不足而是**物理脱离被墙网络**的需求，唯一解是人工环节（手机蜂窝数据）。此时 AI 的正确动作不是放弃也不是硬试，而是切换为**交接协议**：AI 完成清场（恢复出厂配置，防 GUI 首连被残留配置干扰）+ 明确交接单（人工侧只做仅有它能做的动作）+ 待命闭环承诺（收到输入后分钟级完成配置与验证，判据前置声明）。

## Approach

通道排查决策树（按序执行，任一环失败即跳下一环，全败即触发交接）：

1. **版本前提检查**：Tor Browser 15+ 的 torrc-defaults 无静态 Bridge 行（moat 动态化），别在 defaults/omni.ja 归档里找网桥行，必然落空。
2. **参数级穷尽**：内置 PT 参数逐一试（每形态记录失败层级），失败形态各异（解析错/PT 卡/broker 卡/TLS 卡）= 通道级问题的证据。
3. **动态获取可达性**：直连 `moat.torproject.org` 设 20s 超时，超时即放弃此路。
4. **辅助代理可达性实测**：对目标服务域名逐个 `curl.exe -x http://127.0.0.1:<port> <url> -I`；**000 = IP 阻断代理无解**（停止折腾代理），200 = 可达（可继续走该通道）。
5. **邮箱通道前置校验**：先确认发件人域是否在 BridgeDB 白名单（Gmail/Riseup），再确认 Gmail 本身可达性——两项任一不可满足即跳过此路，不发无效请求。
6. **判定结构性死路 → 人工交接协议**（三件套）：
   - **AI 清场**：GUI 生成态 `torrc` 重命名为 `torrc_backup`（恢复出厂，`DisableNetwork 1` 原状），确保用户打开 Tor Browser GUI 时出现干净的"连接"界面，不被 AI 侧残留 user_rc/网桥行干扰。
   - **交接单具体化**：人工侧动作写到"一步一动作"粒度（实例：手机**蜂窝数据**勿连家庭 WiFi → 浏览器登录 Gmail → 写信 `bridges@torproject.org`、主题空、正文仅一行 `get transport obfs4` → 等 5-15 分钟收回信 → 提取 1-2 行完整 obfs4 网桥行交给 AI）。
   - **待命闭环承诺**：AI 侧声明收到网桥行后的固定动作序与判据（写入 user_rc → 重启 tor → `check.torproject.org` 含 Tor 标识 + `ipinfo.io` 出口 IP ≠ 真实 IP），让闭环验证可预期。

## Faster Next Time

- 网桥行卡点先二问："**参数坏了还是通道被墙？**"——失败形态各异 + 官方域直连超时 = 通道级，立即停止调参转通道调研，省掉全部无效重试。
- 辅助代理一行判语义：`-I` 返回 **000** = IP 阻断（代理无解，别改代理配置）；**200 但 IP 真实** = 可达但无隐匿（可用但不能隐匿）。两种信号对应完全不同的下一步。
- "仅人工能做"的判定成立后，AI 的增量价值在**清场 + 交接单 + 待命闭环**三件套，而不是继续在死路上产出"尝试报告"。
- 交接单里给用户的技术前提要显式（如"蜂窝数据"而非"换个网络"），因为用户默认环境正是被墙网络本身。
- 人工输入的验收判据在交接时就声明（出口 IP≠真实 IP 双判据），避免拿到输入后才知道怎么算"通"。

## Applicability Boundaries

- 适用：受限网络下任何"需要境外受信服务**颁发**凭证/密钥/配置行"的场景（网桥行、注册验证、签名材料）；判定"纯命令行侧结构性不可行"并设计 AI/人工交接。
- 不适用：网络可达环境（BridgeDB 网页/moat 直接可用，别绕人工环节）；本机已有其他翻墙通道（用它拿网桥行，无需人工）；纯参数级配置错误（走 tor-debug-chain 的分层定位，不涉及通道）。
- 边界：通道可用性随时漂移，本图谱的"000/超时"结论为 2026-11-11 实测快照，复用前须重测；"QQ 邮箱被拒"为用户转述先例非本轮实测，BridgeDB 域名白名单以官方文档为准；人工环节在本会话内尚未执行，闭环承诺待网桥行到位后兑现；若人工侧长期无法提供网桥行，主方案应显式降级登记待办而非无限等待。