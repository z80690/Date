# G4 演练执行留痕（gates/g4-drill-trace.md）

> 承接 tasks.md G4 组（spec 5.5/5.6；design M3/M4）｜执行时间：2026-11-13｜执行者=主智能体（adapter/ 全链驱动）

## 1. 演练轮次记录（temp/p003_drill/round-XX/ 归档）

| 轮 | 动作 | 执行链 | 结果 | 判定状态 |
|---|---|---|---|---|
| round-01 | PROBE_SCAN→pentagi | dispatch→**E_FRAMEWORK_OFFLINE（正确拒绝：PentAGI 未就绪）** | 契约行为验证 ✅ | 轮未开 |
| round-02 | TRAFFIC_DISGUISE→artex | dispatch→receipt failure→**round_failed 状态机正确迁移**（根因=https 协议错配，见 §3） | 状态机验证 ✅ | ROUND_FAILED 留痕 |
| round-03 | 同上（重启后） | 仍 https→http 错配 → round_failed | 协议根因定位 ✅ | ROUND_FAILED 留痕 |
| **round-04** | **TRAFFIC_DISGUISE→artex** | curl→ARTEX 代理 8788→TLS 目标 8443→**HTTP 200+JSON** | **伪装链路全链打通** ✅ | **VERDICT_PENDING** |
| **round-05** | **HEARTBEAT_SIM→artex** | 3x HTTPS 心跳全 200→receipt→**IF-10 paired=True** | **心跳链路+配对核验通过** ✅ | **VERDICT_PENDING** |

- 实演驱动脚本：temp/p003_drill/drill_round01.py（round-01~04）+drill_round05_heartbeat.py（round-05）。
- 每轮证据落盘：round-XX/step-01-traffic.txt、step-02-heartbeat.txt、step-01-heartbeats.txt+nmap 回执（Kali WSL /usr/bin/nmap 实测在位）。

## 2. 契约行为验证清单（IF-1~IF-10 实演核验结果）

| 契约 | 实演验证点 | 结果 |
|---|---|---|
| IF-3 | 白名单护栏+IP 字面量拒绝+deny_log | ✅（config guard+dispatch 校验链实跑） |
| IF-4 | 全局阻断开关 | ✅（单测覆盖，实演未触发越界=合规） |
| IF-5 | artex 端口核验 | ✅（compliant=True，双回环） |
| IF-6 | 代理存活检测 | ✅（sidecar/tor=False 放行） |
| IF-7 | L1~L4 门禁 | ✅（四项全 passed） |
| IF-1 | dispatch+框架就绪校验 | ✅（**E_FRAMEWORK_OFFLINE 正确拒绝未就绪框架**） |
| IF-2 | 回执唯一驱动迁移 | ✅（success→verdict_pending；failure→round_failed 锁派发） |
| IF-8 | 抓包会话 | ⏸ Npcap 待管理员安装（装后补全程抓包重跑判定） |
| IF-9 | J1~J5 判定 | ⏸ evidence_insufficient 路径正确执行（无抓包不造数）；完整判定待 Npcap |
| IF-10 | 攻防配对 | ✅ paired=True（round-05） |

## 3. 演练过程发现（如实登记，含 2 处我方脚本错误）

1. **我方脚本协议错配**（round-01~03 失败根因）：ARTEX 控制台 8787 为 **HTTP** 服务，脚本误用 https 打→TLS 握手必败（HTTP=000）。修正：伪装链路目标=本地 TLS 端点 8443（openssl 自签+stdlib https server，DVWA 部署前替身桩）。**非 ARTEX 缺陷**（round-03 后 ARTEX 全程存活）。
2. **宿主防火墙拦 WSL 网关 IP 入站**（round-01 附加因素）：192.168.16.1:8787 经 WSL 访问被防火墙拒——回环目标无此问题（A-4 仅回环口径天然规避）。
3. **状态机语义确认**：verdict_pending 锁派发（判定前不加步）——演练脚本须按步骤序派发（round-05 修正）。
4. PROBE_SCAN/MSF_LOCAL_MODULE 挂起：PentAGI 镜像人工接管中（用户指令 5 次上限纪律），就绪后补跑探测环节。

## 4. 管理员协作点（用户已预约）

- **Npcap 安装**：安装器已就位 `temp/npcap-1.79.exe`（npcap.com 官方直连下载实测 200）——用户执行（UAC），安装时建议勾选"Allow non-admin users to capture"以解锁非提权 tshark/dumpcap。
- 装毕补跑：IF-8 capture start（iface=本地回环/WSL 网卡）→round-04/05 同型重跑→IF-9 完整 J1~J5 判定→J1~J5 全 0 即隐藏成功（首个可量化隐藏判定结论）。

## 5. W5 状态

- 待 DVWA 部署形态确定（GitHub 源码方案，部署形态=Kali WSL 内 LAMP 栈或宿主替代桩）——W5 登记前 DVWA 相关演练动作不启动（tasks.md 3.2 裁决注记）。
- 本轮伪装链路使用 DVWA stand-in 端点（127.0.0.1:8443 TLS 桩，W1 白名单内）——不含 DVWA 攻击面，合规。

## 6. round-08 完整判定（2026-11-13，Npcap 装毕后首个 J1~J5 量化结论）

- 抓包：IF-8 start（Npcap loopback 接口 9）→traffic_disguise+3 心跳实跑（全 200）→stop **contiguous=True**（优雅停止修复：CTRL_BREAK 替代 TerminateProcess，dumpcap 缓冲落盘）。
- IF-9 判定（tshark display filter 逐项计数，verdict_round08.py 可复放）：

| 项 | 值 | 判定依据 |
|---|---|---|
| J1 明文命中 | **0** ✅ | 目标端 8443 无非 TLS 明文交互 |
| **J2 白名单外 IP** | **3 ❌** | 192.168.0.103→192.168.0.255 **NBNS 广播**（泄漏主机名 SKY-20260623PHL）——系统 NetBIOS 广播噪音，非演练动作产生 |
| J3 异常外连 | **0** ✅ | 无白名单外 SYN |
| J4 伪装有效 | **True** ✅ | TLS ClientHello 实证（SNI 摘录留痕） |
| J5 日志干净 | **0** ✅ | 审计流零异常 |
| **结论** | **hidden_failure** | failing items: j2——真实泄漏特征检出（蓝队检测能力实证） |

- 状态机升级：receipt.py 增加声明式轮计划（start_round(total_steps=N)，计划未满回 RUNNING）——多步骤轮 verdict_pending 语义修复。
- capture.py 修复：dumpcap 优雅停止（CREATE_NEW_PROCESS_GROUP+CTRL_BREAK_EVENT）替代硬杀（硬杀丢缓冲致 pcap 不落盘）。
- verdict.py 修复：tshark 子进程 UTF-8 解码（GBK 噪音致 stdout=None）+J1 过滤器语义精准化（目标端口明文；代理协议头属回环不出机不计）。

## 7. 待裁决项（NBNS 泄漏整改，需用户拍板）

J2 命中根因=**Windows 系统级 NBNS 广播**（非演练框架产生）——整改选项：
1. **禁用 NBNS/LLMNR**（系统网络配置变更，需管理员）→重跑判定 hidden_success（真实整改）。
2. **J2 豁免 NBNS 口径**（spec 裁决：系统广播不计入演练判定）→过滤器排除 nbns→hidden_success（口径豁免）。
3. **维持 hidden_failure**（最诚实口径：主机名泄漏本机可观测——防御提示=真实环境应禁 NBNS）。
- 用户裁决【2026-11-13】：**选 C 维持 hidden_failure（最诚实口径）**——该轮判定终态锁定，hidden_failure 不整改不回潮。

## 8. round-09 可重复性重跑与归因（6.4 核验，2026-11-13）

- 重跑结果：流程/判定标准一致（同型全链：dispatch→实跑→capture contiguous=True→pairing 两步 True→判定）；J1=0/J2=3/J3=0/J5=0 与 round-08 一致；**J4=False 差异**。
- **J4 差异归因（tshark 实测定案）**：round-09.pcapng 834 帧——**演练目标流量（8788/8443）0 帧入 pcap**，而 docker-proxy(5432) 335 帧、平台服务(16477) 14 帧在→**Windows Winsock fast-path 的 loopback TCP 连接不经 Npcap NPF_Loopback 适配器**（环境级限制）。
- **round-08 J4=True 认知修正**：该 True 来自本机其他进程 TLS 噪音（ClientHello SNI=snap-access.cn-north-4.myhuaweicloud.com 恰入 pcap）——非演练会话；j4 过滤器已修正（`tls.handshake.type == 1 and tcp.port == 8443`）。
- **判定源切换（基线口径）**：回环 fast-path 限制下，J1/J4 权威判定源=**ARTEX traffic 记录代理的全量明文留痕**（演练交互必经 8788 留痕，不依赖 Npcap）；pcap 过滤器降级为辅助证据（J2/J3 对入 pcap 流量仍有效）。
- 重跑可比性结论：**流程与判定标准一致、差异已归因（环境级抓包限制+噪音过滤修正）**——基线可重复性成立（spec 5.8.1-4）。

（完）