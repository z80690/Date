---
id: 2026-11-11-tor-censored-network-bridge-debug-chain
title: Tor 受限网络网桥调试链：bootstrap 百分比分层定位 + torrc 三坑 + 控制端口实时探针
category: debugging
nature: methodology
created_at: 2026-11-11T10:39:30
updated_at: 2026-11-11T10:39:30
tags: [debugging, tor, 网桥, 受限网络, bootstrap]
keywords: [bootstrap 卡 5%, conn_pt, snowflake, obfs4, meek_lite, Key digest wrong length, no configured transport, 反斜杠转义, PROTOCOLINFO, GETINFO status/bootstrap-phase]
problem_patterns:
  - "Tor 启动后 bootstrap 长期卡在某个百分比（如 5% conn），反复 relay 连接超时，不知道卡在网络哪一层"
  - "torrc 配置看起来完全正确，tor 却报 no configured transport / Key digest wrong length 后退出"
  - "tor 进程秒退且日志文件没生成，无从下手定位"
source_sessions: [ses_e3a9c97a3ffeCp9OO263dGGrPC]
project: Date
severity: medium
quality_score: 86
hit_count: 1
last_hit_at: 2026-11-11T11:44:05
low_quality_hit_count: 0
tier: S
related_experiences: ["workflow/2026-11-11-learn-first-tor-bridge-dispatch-review", "build-env/2026-11-11-blocked-official-channel-ecosystem-bundle-discovery", "debugging/2026-11-11-electron-portable-platform-trap-crash-deadend-map"]
---

# Tor 受限网络网桥调试链：bootstrap 百分比分层定位 + torrc 三坑 + 控制端口实时探针

## Scenario

受限网络（直连 Tor 中继被墙）下手动调通 Tor SOCKS5 隐匿通道：启动捆绑 tor.exe（来源见渠道发现经验）、写 torrc、配置可插拔传输（PT：snowflake/obfs4/meek）、验证 9050/9051 与连通性。多轮卡点分布在配置解析、PT 插件、网桥行、出口建连四个不同层，各层故障特征与修法完全不同。

## Key Signals

- **bootstrap 卡 5% (conn) 且反复出现 relay 连接超时**（`WSAETIMEDOUT; count 递增; host <fingerprint> at <ip>:<port>`）——直连中继层被墙，配置再对也没用，必须上 `UseBridges 1`。
- **`Can't use bridge ... there is no configured transport called "snowflake"`**——`ClientTransportPlugin` 的可执行路径没被 tor 接受。根因：torrc 引号字符串里的**反斜杠被 tor 当转义符**，Windows 路径损坏 → PT 拉不起来。改正斜杠即解。
- **`Key digest for Bridge is wrong length` / `Bridge line did not parse`**——某行 Bridge 行字段损坏。多行网桥时逐行二分（注释掉一半重跑）定位坏行。
- **bootstrap 卡 1-2% (conn_pt / conn_done_pt)**——PT 插件已成功启动并连接，卡点在 broker/网桥层（snowflake 的 broker 建连受阻属此层），重试 snowflake 无意义，换 obfs4 真实网桥行。
- **进程秒退且日志文件没生成**——不猜，前台直跑读 stderr，或用控制端口实时探针。

## Essence

**bootstrap 百分比是分层定位器**：`0% starting` = 配置解析通过；`5% conn` = 直连中继层被墙（需网桥）；`1-2% conn_pt / conn_done_pt` = PT 插件层已通、下一跳（broker/网桥）受阻。调试必须按层推进，逐层确认后再看下一层，跳层排查全部是无效功。调试链：端口监听 → SOCKS5 握手 → 控制端口协议 → bootstrap 分级 → torrc 行级修正。torrc 有三个 Windows 特有坑（ASCII 路径 / PT 路径正斜杠 / 网桥行逐行验证），任何一个都会让 tor 静默退出或拒绝配置。

## Approach

1. **端口层**：`netstat` 确认 9050/9051 LISTENING；`TcpClient` 握手 9050 期待回包 `5x0`（SOCKS5），9051 发 `PROTOCOLINFO` 期待 `250-`。
2. **bootstrap 分层**：读日志（或探针）中的 `Bootstrapped N%` 行，按上述语义定位卡点层；每次只修当前层的配置。
3. **torrc 三坑修正**：①所有路径（DataDirectory/Log/PT）用**全 ASCII 绝对路径**（中文路径在 tor 的 ANSI 处理下乱码，DataDirectory 创建失败即退）；②`ClientTransportPlugin` 路径用**正斜杠**；③`Bridge` 行逐行验证（来源可靠、字段完整），坏行二分。
4. **PT 插件来源**：用官方生态捆绑件（如 OnionShare 安装目录内置 meek-client/obfs4proxy/snowflake-client），不手搓下载。
5. **控制端口实时探针**（日志不落盘/秒退时的替代）：`AUTHENTICATE ""` → `GETINFO status/bootstrap-phase` 直读实时 bootstrap，不依赖日志文件。
6. **进程常驻**：用 WMI `Win32_Process.Create` 传完整命令行启动（`Start-Process -ArgumentList` 的数组与单字符串两种形式传参都会被吞，tor 会静默改用默认配置）；配置先前台跑一次读 stderr 确认无解析错误，再转常驻。

## Faster Next Time

- bootstrap% 语义速查：5%+relay 超时=换网桥；1-2% conn_pt=换网桥行（不要重试同一 PT）；连 0% 都不到=配置解析失败，先修 torrc。
- "no configured transport called X" 十有八九是 PT 路径反斜杠转义——直接改正斜杠，别查别的。
- 中文 Windows 环境给任何第三方 CLI 工具写配置/数据路径，一律 ASCII，一次到位。
- snowflake 卡 2% 是 broker 层受阻，解法是向 BridgeDB 取 obfs4 真实网桥行替换，不是调参重试——重试属于同症状重复尝试。
- 验通判据固定三件：9050 握手 5x0、9051 PROTOCOLINFO 250、`curl -x socks5h://127.0.0.1:9050 https://ipinfo.io` 出口 IP ≠ 真实 IP（前两件只证明"通道就绪"，第三件才证明"隐匿通"）。

## Applicability Boundaries

- 适用：直连被墙环境下的 tor 手动网桥调试、任何基于 tor 的 SOCKS5 通道搭建；bootstrap 卡点的分层判读可推广到 tor 衍生工具。
- 不适用：tor 可直连的网络（无需网桥，别过度配置）；以 Tor Browser 图形界面为主的使用（应提取浏览器成熟配置，禁手搓瞎拼——手拼 torrc 已被实证为低级错来源）。
- 边界：本经验为部分闭环——通道层（握手/控制端口）已实证调通，出口层（snowflake broker 受阻 → 需 obfs4 网桥行）在本网络环境下未最终打通，"隐匿通"判据待网桥行到位后复验；PT 生态与网桥可用性随网络环境漂移，卡点层语义不变但具体受阻原因需重测。