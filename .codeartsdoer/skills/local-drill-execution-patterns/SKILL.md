---
name: local-drill-execution-patterns
description: >-
  本地授权攻防演练（P003 类）适配层实现与演练执行的实证模式：契约驱动实现
  （design IF 签名→错误码 StrEnum→dataclass 载荷→纯判定函数与证据采集分离）、
  JSONL 证据流留痕（temp/p003_drill/audit/ 流=IF-9 判定与 IF-10 配对的数据源）、
  白名单配置化与用户拍板锁（仅 IP 字面量纪律，主机名会触发 DNS 外发直接拒绝）、
  框架就绪单点（FRAMEWORK_READY 与 deploy-selfcheck 同源，未就绪 E_FRAMEWORK_OFFLINE
  如实拒绝）、越界即停全局开关（reset 仅限用户裁决）、演练轮次状态机（receipt 唯一
  驱动迁移；round_failed 留痕允许重跑；verdict_pending 锁派发判定前不加步）、
  降级链与替身桩（PentAGI 缺席→ARTEX 就绪链路先行；DVWA 部署前用本地 TLS stand-in
  端点；evidence_insufficient 不造数）、纯 stdlib 零第三方依赖与 Windows 官方命令
  子进程核验（netstat/tasklist/docker ps）。凡涉及演练适配层/回执协议实现、白名单
  校验器、端口绑定核验、代理存活检测、演练轮次 dispatch/receipt、隐藏判定 J1~J5、
  攻防配对检查、演练降级链/替身桩、dumpcap 抓包会话管理时使用。
---

# 本地攻防演练适配层与执行模式（2026-11-13 P003 实证）

## 契约驱动实现五要素

1. **错误码先行**：design.md 各接口的异常映射逐条落成 `ErrorCode(StrEnum)`（如 E_TARGET_DENIED/E_FRAMEWORK_OFFLINE/E_EMPTY_CONCLUSION），AdapterException(code, message, detail) 统一携带 detail 供留痕。
2. **载荷 dataclass 化**：IF 签名的伪类型（Str/Enum/Dict）直译为 frozen dataclass+StrEnum——dispatch 返回 TaskHandle、receipt 返回 ReceiptAck，签名与 design 逐字对齐，禁自创字段。
3. **纯判定函数与证据采集分离**（IF-9 关键设计）：`verdict_from_counts(round_no, counts)` 只吃结构化计数出结论（hidden_success/hidden_failure/evidence_insufficient 三态），单测直接喂计数；证据采集（tshark 子进程解析 pcap）独立成 `collect_evidence`，工具缺失映射 E_EVIDENCE_MISSING→判定走 insufficient——**证据不齐不造数**。
4. **留痕即证据**：全部接口操作落 JSONL 流（dispatches/receipts/deny_log/boundary/captures/verdicts/pairings/gate/portaudit/proxycheck），目录=演练产物区（.gitignore 排除的 temp/ 下）——IF-9/IF-10 的核验直接读这些流，回查可复放。函数签名带 `evidence_dir` 参数（测试用 tmp_path 隔离，不污染真实审计流）。
5. **纯 stdlib 零第三方**：端口/进程核验走 Windows 官方命令子进程（`netstat -ano -p tcp` 正则解析 LISTENING 行、`tasklist /FI` CSV、`docker ps --format` 端口映射），代理存活检测同理——无依赖风险，Ruff 最简。

## 安全校验链（dispatch 前置顺序）

round 存在且 running → 越界阻断开关未触发 → trigger 二值（user_command/receipt_event 之外即 E_TRIGGER_ILLEGAL）→ IF-3 白名单 → action 框架映射（ACTION_FRAMEWORK 字典）→ 框架就绪单点（FRAMEWORK_READY 字典与 deploy-selfcheck 同源，未就绪如实 E_FRAMEWORK_OFFLINE 拒绝，禁伪造就绪）。

- **白名单仅接受 IP 字面量**：解析主机名会先发出 DNS 查询（本身可能外发）——非字面量直接拒绝+拦截日志（deny_log.jsonl，deny_log_id 可回查）。加载失败/损坏→E_WL_CONFIG_MISSING 阻断启动。
- **越界即停是全局开关**：一旦越界事件，dispatch 对一切目标拒绝（含白名单内），直到用户裁决 reset；已建立连接的越界→E_BLOCK_FAILED 升级呈报（适配层断不掉框架持有的连接）。
- **端口合规判定矩阵**：0.0.0.0/::/* 与公网地址=不合规；127.0.0.0/8、::1、登记的虚拟网卡段=合规。框架进程定位（tasklist PID 过滤 netstat）、compose 栈（docker ps 端口映射解析）、stdio 型（cairn-mcp 零 TCP 端口=天然合规）三类分别处理。

## 演练轮次状态机纪律

- **receipt 是唯一状态驱动**（spec 4.2-1）：success 且全部步骤 done→verdict_pending；任一 failure→round_failed。
- **声明式轮计划（2026-11-13 round-06 实演暴露的状态机缺口）**：`start_round(round_no, total_steps=N)` 显式声明步骤数——未声明时（None）单步 receipt 即转 verdict_pending 并**锁死后续派发**（多步骤轮跑不下去，E_FRAMEWORK_OFFLINE 报"round is verdict_pending"是症状非根因）；声明后每步 receipt 回 RUNNING 直到计划步数满足才转 verdict_pending。演练驱动脚本按"先 start_round(N, total_steps=2)→step1 dispatch→receipt→step2 dispatch→receipt"顺序写，禁"先 receipt 后补 dispatch"。
- **回环抓包的 J 过滤器语义（round-08 实证）**：loopback 接口捕获全为本机流量——J1=**目标端口上的非 TLS 明文**（`tcp.port==8443 and not tls`；代理协议头走 8788 属本机回环不出机，不计入 J1）；J2/J3=非回环目的地的计数（`not (ip.dst in {127.0.0.0/8, W3})`）；J4=目标端口 TLS ClientHello 存在且 J1=0。**J2 命中系统级 NBNS 广播（192.168.0.x→0.255 泄漏主机名）是真实发现而非误报**——系统广播即泄漏特征，整改口径（禁 NBNS/J2 豁免/维持失败）须用户裁决，禁自判豁免（round-08 用户裁决 C=维持 hidden_failure 最诚实口径，判定终态锁定）。
- **Winsock fast-path 回环连接不经 Npcap loopback 适配器（round-09 可重复性重跑归因，2026-11-13）**：dumpcap 在 NPF_Loopback 抓 834 帧，演练目标流量（8788/8443）**0 帧**入 pcap，而 docker-proxy(5432) 335 帧、平台服务(16477) 14 帧在——**回环 TCP 能否入 pcap 取决于连接建立路径**（fast-path 连接旁路 NPF）。后果与对策：①J4 过滤器必须锁目标端口（`tls.handshake.type==1 and tcp.port==8443`）——无锁版在 round-08 给出 J4=True **假阳性**（他进程 TLS 噪音恰入 pcap，SNI=外部域名）；②J1/J4 权威判定源=**应用层全量明文留痕**（ARTEX traffic 记录代理侧，演练交互必经、不依赖 Npcap），pcap 过滤器降级为辅助证据（J2/J3 对入 pcap 流量仍有效）；③可重复性重跑（G6.4）差异逐项归因登记（环境限制/噪音过滤修正）——流程一致+数值差异归因清楚=基线可重复性成立。
- **dumpcap 优雅停止**：terminate()=TerminateProcess 硬杀→写缓冲丢失→pcap 文件不落盘（E_CAPTURE_BROKEN 假象）。Popen 加 `creationflags=subprocess.CREATE_NEW_PROCESS_GROUP`，停止用 `send_signal(signal.CTRL_BREAK_EVENT)`+wait(15s) 超时兜底 terminate——CTRL_BREAK 让 dumpcap flush 后退出（详见 windows-git-powershell-quirks）。
- **隐藏判定三态**：capture_contiguous=False 或审计通道不可用→evidence_insufficient（不造数）；J1~J5 全 0+伪装有效→hidden_success；任一命中→hidden_failure 并在 reason 列失败项。抓包会话中断=整轮证据无效（E_CAPTURE_BROKEN）。
- **health_check 事件驱动**：抓包存续核验挂在"每步回执到达时顺带"执行，禁独立定时循环（spec 6.2-3 禁轮询）。

## 降级链与替身桩

- **框架缺席时的演练链路**：就绪框架的动作先行（如 ARTEX traffic_disguise/heartbeat_sim），未就绪框架的动作如实拒绝并登记，就绪后补跑——禁伪造就绪状态。
- **目标服务缺 https 时的替身桩**：openssl（Git 附属 usr/bin）自签证书+Python stdlib `ssl.PROTOCOL_TLS_SERVER` 包 HTTPServer（绑 127.0.0.1 回环）——伪装链路（明文目标不可伪装）的合法替身，curl `-k` 直连验证。
- **代理链路诊断顺序**：目标服务协议形态先行确认（curl -I http:// 先探；ARTEX 控制台 8787 为 HTTP，https 打必 000——三次失败教训）→服务进程/监听核验→再谈代理与防火墙（Windows 防火墙拦宿主侧网关 IP 入站，回环天然规避）。
- **receipt failure 不改判定**：执行失败如实回执（evidence_ref 指向失败输出落盘），round_failed 留痕；禁把失败包装成成功过判定。

## 测试与门禁

- pyproject 定 ruff（line-length 100+E/F/W/I/UP/B）与 pytest testpaths；**Ruff 全过+pytest 全 PASSED 才算实现完成**。
- 测试覆盖=各 IF 的异常映射路径（白名单外拒绝/空结论拒绝/未知句柄/触发非二值/越界停/配对三态/判定三态/端口合规矩阵）+正常路径各一——异常映射是契约主体，正常路径只是入口。
- pytest sessionfinish 的 PermissionError（tmp 清理）为 Windows 噪音，测试结果以 PASSED/FAILED 计数为准（详见 windows-git-powershell-quirks）。
