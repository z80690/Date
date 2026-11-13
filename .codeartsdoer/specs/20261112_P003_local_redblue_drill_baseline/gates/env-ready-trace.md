# G3 环境就绪留痕（gates/env-ready-trace.md）

> 承接 tasks.md 3.1/3.2/3.3/3.4（spec 1.4-9、6.1-3/5、5.5.1-3、5.7.1-1/2；design M1-4、M3-2、D1、D2）｜留痕时间：2026-11-12｜执行者=主智能体
> 用户指令基线（2026-11-12）：镜像拉取重试上限 5 次、多源各自单次直连、失败留日志人工接管、禁后台死磕——本文件第 2/4 节按此口径执行。

## 1. Kali 就绪与 W3 网段登记（3.1 ✅，A-3 裁决=复用现有）

- **形态修正**：本机 Kali 实为 **WSL2 发行版 kali-linux**（非 VMware VM；宿主无 VMnet 适配器，实测仅 WLAN/WSL/Hyper-V Default Switch 三网卡）——A-3"复用现有（已跑通攻防）"正主=WSL kali-linux。
- 系统版本：PRETTY_NAME="Kali GNU/Linux Rolling"；WSL2 默认 **NAT 模式**（非桥接）=隔离合规（spec 6.1-3）。
- **W3 登记值**：Kali WSL eth0=`192.168.25.128/20`，宿主侧 vEthernet (WSL)=`192.168.16.1/20`→**W3=192.168.16.0/20（WSL NAT 隔离段）**。
- systemd 在跑（ps -p 1=systemd）→journalctl 可用。
- 【验证方式】`wsl -d kali-linux -- ip addr show eth0` 回执可复放。

## 2. DVWA 官方镜像部署（3.2 ⏸ 按 5 次上限停手，人工接管）

- 官方来源：ghcr.io/digininja/dvwa:latest（DVWA 官方 README 推荐镜像）。
- 按新标准的拉取尝试日志（**3 次/上限 5，主动停手**）：
  1. `docker.m.daocloud.io/ghcr.io/...`：形式错误 invalid repository（daocloud ghcr 代理为独立域名非路径前缀）。
  2. `ghcr.m.daocloud.io/digininja/dvwa`：**白名单拦截**（镜像不在 daocloud 允许清单，官方提示 issues/2328）。
  3. `ghcr.io/digininja/dvwa` 官方直连：**ghcr.io 可达**（v2 端点 HTTP 401/2.2s 正常），层下载启动后停滞（vhdx 1.92GB 零增长 180s）。
- 处置：按用户指令**停止重试、释放进程（docker pull 已强杀）、留日志等待人工手动拉取**；余 2 次尝试额度未挥霍。
- **【用户裁决 2026-11-12】靶场方案变更**：①DVWA Docker 镜像拉取按 5 次上限停手（3/5 次留痕如上），人工接管确认；②**靶场正式换为 GitHub 官方源码方案**（digininja/DVWA 官方仓库源码，白客实验合规操作），**不跑本地 Docker 镜像、不另寻多源死磕**；③部署形态与 W5 地址在 3.2 续执行时确定（明日），W5 登记前靶场相关演练动作不启动。tasks.md 3.2 已同步注记。

## 3. 抓包链路（3.3，双通道）

- **主通道**：Wireshark/tshark——winget 包 ID 修正（实际=WiresharkFoundation.Wireshark，首次失败系 ID 记忆错误）→4.6.9 MSI 官方源下载中（dl.wireshark.org CDN 极慢，后台继续不等待）；Scoop 路线卡 buckets 更新（GitHub 墙）已停。
- **兜底通道**：Windows 内置 pktmon 实测**需管理员权限**（"无法与 PktMon 驱动程序通信"——非提权会话限制）；tshark 抓包同理依赖 Npcap 服务权限。**抓包执行环节需一次管理员会话协作**（G4 演练启动前用户侧确认），或 Npcap 安装时选"非管理员可抓"模式。
- ARTEX 健康实测：`curl http://127.0.0.1:8787/api/health` → **HTTP 200**（演练主链路服务健康，2026-11-12 实测）。
- 归档目录规约：`temp/p003_drill/round-XX/`（pcapng 落位，spec 6.4-1）——round-00-probe\ 已建（pktmon 试抓因提权未产出样本，tshark 就绪后补）。

## 4. 双侧审计通道（3.4 ✅）

- **Kali 侧 journalctl**：✅ 可用（WSL systemd 在跑；实测 `journalctl --no-pager -n 3` 正常输出审计记录：systemd target reached 等）。
- **宿主侧 Windows 事件日志**：✅ 可用（`Get-WinEvent -LogName System -MaxEvents 2` 实测返回 DCOM 10016 等真实记录）。
- 审计通道状态=双侧健康，J5 核验前提满足（spec 5.7.3-3 不触发）。
- 【验证方式】上述两条命令回执可复放。

## 5. 待办与人工接管清单

| 项 | 状态 | 接管人 |
|---|---|---|
| DVWA 镜像拉取 | 3/5 次停手 | 人工（网络通道就绪后 docker pull） |
| PentAGI 镜像拉取 | 四通道失败停手 | 人工（同上；拉通后 compose up -d pentagi） |
| Wireshark/tshark 安装 | Scoop 进行中 | 主智能体续（下一轮核验） |
| 3.5 适配层 Python 代码（IF-1~IF-10+Ruff 门禁） | 未开始 | 主智能体（G3.5 编码任务） |

## 6. 环境保活终态登记（2026-11-12 夜间收口，用户指令）

| 组件 | 保活状态 | 次日续用口径 |
|---|---|---|
| Kali WSL2（kali-linux） | **保持运行，禁重置** | A-3 复用资产，W3=192.168.16.0/20 已登记 |
| ARTEX（artex.exe+artex-pg 容器） | **保持长驻（WMI），禁停服务** | 8787/8788 双回环，/api/health=200 实测 |
| 哑端点（mock_llm_server.py） | **保持长驻（WMI）** | 127.0.0.1:7810 |
| Docker Desktop 引擎 | **保持运行**（registry-mirrors 已配） | PentAGI 人工拉镜像后即可 compose up |
| Wireshark winget 后台任务 | **不手动干预**——等自然超时/装完（用户指令：防自动重启，主循环不发新命令） | 装完核验 tshark（次日轮） |
| 审计通道（journalctl+Get-WinEvent） | **保持可用** | 双侧实测健康，J5 前提满足 |
| 抓包链路 | 按现状留底 | 管理员权限环节等用户点击（G4 前） |
| 明日任务 | 3.5 演练适配层 Python 实现（IF-1~IF-10+Ruff 门禁）→3.2 靶场 GitHub 源码方案落地→G4 |

（完）