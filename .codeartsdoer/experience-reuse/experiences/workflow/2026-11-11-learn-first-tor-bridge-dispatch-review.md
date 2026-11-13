---
name: 先学后干失败复盘与 Tor/DevSidecar 标准动作
description: G4 整改派工复盘（20/100）：未查包管器先手搓、证书摇摆、Tor snowflake 卡 2%；含双工具调通标准动作与网桥待办
type: feedback
---

# 先学后干失败复盘（2026-11-11 派工，评分 20/100）

**Why**：用户强令问责——①未先学后干（没查包管器就手搓下载/解包/静默装，事后 winget search 一条命令就发现 docmirror.dev-sidecar 官方包）②代理异常仍折腾（DevSidecar 出口 IP=直连 IP 属名单外直连的设计行为，把它当故障反复折腾）③洋葱未通（snowflake 卡 2% 后进程退出）④证书摇摆（装了又卸，违反"绝不碰证书"红线）。

**How to apply**：
1. 装软件第一步永远 `winget search` / `scoop search`；包管没有才官方 release；release 没有才手搓。
2. 同症状连续失败 2 次立即换实现路径，禁止在同一入口反复试探。
3. 诊断/验证禁止落盘脚本文件——用内联命令/内置工具（netstat/TcpClient/Test-NetConnection）。
4. DevSidecar 定性=仅 GitHub 加速（名单外直连、出口 IP 不变是设计行为），永不装 CA，永不用于隐匿。
5. Tor 隐秘判据=出口 IP≠真实 IP（snowflake 当前受阻，需 obfs4 真实网桥行替换；meek_lite 行 digest 解析失败待修）。

# 双工具标准动作（已实证）

- **DevSidecar（31181 加速）**：`curl.exe -x http://127.0.0.1:31181 https://github.com -I` 期望 200；`https://ipinfo.io` 返回直连 IP=事实记录（仅加速不隐秘）。
- **Tor（9050 隐匿）**：torrc 全 ASCII 路径+PT 路径正斜杠（引号内反斜杠会被 tor 转义）+ `UseBridges 1`；启动用 WMI `Win32_Process.Create`（Start-Process 两种传参形式皆被吞）；验证=`TcpClient` 握手 9050（5x0）+ 9051（PROTOCOLINFO 250）+ `GETINFO status/bootstrap-phase`；通网判据=check.torproject.org 含 Tor 标识+ipinfo 出口 IP 非真实。
- **隔离纪律**：DevSidecar 不接管 Tor 流量；敏感流量只走 Tor。