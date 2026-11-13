---
id: 2026-11-13-reuse-verdict-asset-form-verify-first
title: 复用类裁决执行前先实测资产形态：网卡清单反推虚拟化形态与网段登记
category: agent-ops
nature: technique
created_at: 2026-11-13T00:04:45
updated_at: 2026-11-13T00:41:17
tags: [资产核验, 虚拟化形态, WSL2, 网段登记, 复用裁决]
keywords: [复用现有先实测形态, Get-NetAdapter 反推虚拟化, Get-NetIPAddress 网段, ipconfig 乱码原生命令替代, WSL2 天然 NAT 隔离, kali-linux WSL 发行版, vEthernet (WSL), 网段登记以实测为准]
problem_patterns: [派工单或裁决描述的资产形态与真实形态不符，按描述规划导致选错配置对象, 中文 Windows 下 ipconfig 输出乱码难以解析, 虚拟机网段未知不知如何登记白名单]
source_sessions: [ses_e2f87ec5fffeUJ1dG59OmShG5q]
project: Date
severity: low
quality_score: 86
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-13-kali-wsl-distro-form-recognition-nat-segment-registration, 2026-11-12-same-name-repo-identity-verification-chain, 2026-11-12-docker-desktop-winget-install-registry-mirror-credential-path]
---

> **[已归档 2026-11-13]** 本经验与 `build-env/2026-11-13-kali-wsl-distro-form-recognition-nat-segment-registration` 为同一实测链（Get-NetAdapter 无 VMnet → wsl -l kali-linux → 客侧 192.168.25.128/20 + 宿主 vEthernet(WSL) 192.168.16.1/20 → W3=192.168.16.0/20）的重复总结，属同题冗余，已合并入该主文件。本文档独有增量（"描述是二手信息"与同名仓库陷阱同源类比、NAT 隔离约束映射登记口径、"派工单已附实测数据且抽样核验一致时直接采信"豁免）均已并入主文件；保留本文仅作来源追溯。

# 复用类裁决执行前先实测资产形态：网卡清单反推虚拟化形态与网段登记

## Scenario

派工单或用户裁决要求"复用现有 X 虚拟机（NAT/隔离）"类就绪任务时，描述中的形态（如 VMware 虚拟机）可能与本机真实资产不符。若按描述直接规划网络配置与探测路径，会选错对象。就绪动作的第一步应是实测资产真实形态——用宿主网卡清单反推虚拟化形态，用两侧 IP 实测登记网段，而非信描述。

## Key Signals

- 宿主 `ipconfig` 输出中文乱码（外部 CLI 子进程 UTF-8 输出被 ANSI 解码）——不要折腾编码修复，直接换 `Get-NetAdapter` / `Get-NetIPAddress` 原生对象输出。
- 适配器清单只有 `WLAN` + `vEthernet (Default Switch)` + `vEthernet (WSL)`（Hyper-V Virtual Ethernet Adapter），**无任何 VMnet\* 网卡**——VMware 形态不成立。
- `wsl -l -v` 列出 `kali-linux` 发行版且版本为 2——所谓"Kali 虚拟机"实为 WSL2 发行版。
- WSL 内 `ip addr` 显示 `eth0: 192.168.25.128/20`，宿主 `vEthernet (WSL)` = `192.168.16.1/20`——两侧 prefix 对齐即同一 NAT 段，网段登记以实测为准（本例 W3=192.168.16.0/20）。
- WSL2 默认 NAT 模式天然与外网隔离，"NAT/隔离、禁桥接公网"约束无需额外配置即满足。

## Essence

"复用现有 X"类指令的隐含前提是 X 的真实形态与描述一致——这个前提必须实测验证而非默认成立（同名仓库有身份陷阱，物理/虚拟资产有形态陷阱，两者同源：描述是二手信息）。形态判定用结构化原生命令的对象输出（PowerShell Cmdlet），外部 CLI 文本输出在中文 Windows 上易乱码且难解析。网段、地址、版本等一切登记值以实测输出为准，描述值仅作预期对照；不符时如实登记修正并在留痕中注明，不硬套描述规划。

## Approach

1. **列宿主网卡清单**：`Get-NetAdapter | Select-Object Name, InterfaceDescription`——按特征网卡反推虚拟化形态：`VMnet*`=VMware、`vEthernet (WSL)`（Hyper-V Virtual Ethernet Adapter）=WSL2、`vEthernet (Default Switch)`=Hyper-V 可用、无任何虚拟网卡=纯物理环境。
2. **形态不符时查实根**：`wsl -l -v` 列发行版与 WSL 版本；进入发行版执行 `cat /etc/os-release` 确认发行版身份（本例 "Kali GNU/Linux Rolling"）。
3. **网段双侧实测**：宿主 `Get-NetIPAddress -AddressFamily IPv4` 取各 vEthernet 地址；客户机内 `ip addr` 取 eth0；两侧 prefix 对齐即同一 NAT 段，登记宿主侧网段（稳定）而非客户机具体 IP。
4. **约束映射**：NAT/隔离类网络约束在 WSL2 默认 NAT 模式下天然满足，登记"形态=WSL2 发行版（天然 NAT 隔离）"替代"虚拟机 NAT 配置"口径。
5. **登记与留痕**：实测值（形态/网段/IP/约束映射）写进任务配置与事实表替代派工单描述值；描述与实测不符时在就绪留痕中注明差异，供后续追溯。

## Faster Next Time

- "复用现有"类就绪任务的**第一条动作永远是形态实测**，不是按描述配置——先花 2 条命令核形态，再省掉后续可能的整条错误配置路径。
- `ipconfig` 乱码零停留切换 `Get-NetAdapter` / `Get-NetIPAddress`，不要尝试编码修复。
- 适配器清单反推形态最快：VMnet\*=VMware、vEthernet (WSL)=WSL2、Default Switch=Hyper-V 就绪。
- WSL2 客户机 IP 重启后可能漂移——网段白名单登记宿主 vEthernet 网段（稳定），客户机 IP 只作当次实测对照。
- 顺带核验可复用能力：WSL2 systemd 在跑时 journalctl 可用（Linux 侧审计），宿主 Get-WinEvent 可读（Windows 侧审计）——双侧审计前提一次测齐。

## Applicability Boundaries

- 适用：Windows 宿主 + WSL2/Hyper-V/VMware 虚拟化环境的资产形态核验、"复用现有"类环境就绪、网段白名单登记。
- 不适用：Linux 宿主与云主机场景（网卡命名与虚拟化体系不同）；派工单已附实测数据且抽样核验一致的场景（此时直接采信）。

## Evidence or Examples

- 本例实测链：`Get-NetAdapter` 三网卡（WLAN / vEthernet (Default Switch) / vEthernet (WSL)）→ `wsl -l -v` kali-linux 版本 2 → `/etc/os-release` "Kali GNU/Linux Rolling" → 宿主 192.168.16.1/20 + 客户机 eth0 192.168.25.128/20。
- 派工单原文口径为"本地 Kali 虚拟机（NAT/隔离）"，实测形态=WSL2 发行版；NAT 隔离约束天然满足，网段登记 W3=192.168.16.0/20 以实测为准。
- 同场顺带核验：WSL systemd 活跃（journalctl 可读）、宿主 Get-WinEvent 可读——蓝方双侧日志审计前提满足，无需额外安装。