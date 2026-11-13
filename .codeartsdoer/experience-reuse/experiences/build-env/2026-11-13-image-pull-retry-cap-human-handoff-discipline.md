---
id: 2026-11-13-image-pull-retry-cap-human-handoff-discipline
title: 外部资源拉取重试上限与人工接管纪律：多源单次直连、停滞即止损、失败留痕移交
category: build-env
nature: decision
created_at: 2026-11-13T00:04:45
updated_at: 2026-11-13T00:09:37
tags: [镜像拉取, 重试纪律, 受限网络, 止损协议, 人工接管]
keywords: [docker pull 重试上限 5 次, 间隔 10-15s 分层缓存, 多源单次直连, daocloud ghcr 独立域名, allowlist 白名单拦截, invalid repository 前缀拼接, vhdx 停滞判定, Stop-Process 清理僵尸, 人工接管命令留痕, 金丝雀不背书冷门大镜像]
problem_patterns: [镜像或安装包拉取被墙，反复后台重试占用资源却零进展, 分不清该继续重试还是立即止损移交人工, 多个加速源形态差异导致试错而非有序排查]
source_sessions: [ses_e2f87ec5fffeUJ1dG59OmShG5q]
project: Date
severity: medium
quality_score: 91
hit_count: 1
last_hit_at: 2026-11-13T10:09:44
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-12-docker-desktop-winget-install-registry-mirror-credential-path, 2026-11-11-bridgedb-bridge-line-channel-deadend-human-handoff, 2026-11-11-user-interrupt-loop-rollback-rechannel-protocol]
---

# 外部资源拉取重试上限与人工接管纪律：多源单次直连、停滞即止损、失败留痕移交

## Scenario

受限网络环境下拉取容器镜像或官方安装包：mirror 源通路探测可达，金丝雀小镜像（如 postgres:16-alpine）拉取成功，但目标冷门大镜像（如 AI 渗透框架镜像）层下载停滞。此时极易滑入"换着花样反复后台重试"的循环——拉起 compose/pull 死磕、不监控进度、不设上限，占用后台资源且零进展。该行为被用户定性为"摆烂式重试，严重违规"，随之确立的硬性止损标准构成本篇核心。

## Key Signals

- mirror 源 `/v2/` 探测返回 `401` = 通路可达（registry 标准未认证响应）；`000`/超时 = 被墙。但**金丝雀小镜像成功 ≠ 冷门大镜像层能通**——mirror 对冷门层可能回源失败。
- `docker pull docker.m.daocloud.io/ghcr.io/<owner>/<repo>` 报 `invalid repository: "ghcr.io/digininja/dvwa", source: "docker.io"`——daocloud 的 ghcr 代理是**独立域名形式**（`ghcr.m.daocloud.io/<owner>/<repo>`），前缀拼接形式无效。
- `ghcr.m.daocloud.io/<owner>/<repo>` 报 `this image is not in the allowlist`——daocloud 白名单拦截冷门镜像，该源对该镜像**永久不可用**，重试无意义。
- 官方 ghcr.io 直连 `/v2/` 返回 401 可达，pull 进程存活但 Docker 数据盘 vhdx 两次采样零增长 = **层下载挂死**，等待无意义。
- winget 官方 CDN 下载（如 Wireshark MSI）11 分钟未完成——慢源不等待，转兜底方案。

## Essence

拉取失败必须区分两类形态并分别处置：①**明确失败**（通路 000、invalid repository 形式错误、allowlist 拦截）——立即换源或放弃该源，不重试；②**无限停滞**（进程存活、字节零增长）——立即杀进程，不等待。两者的正确动作都不是"再试一次"。重试本身要有硬性契约：上限 5 次（含换源）、间隔 10-15 秒（利用分层缓存）、每次必须换源或换形态；超限后终止全部残留进程释放资源、失败日志留痕、把可直接执行的接管命令写进留痕文件转人工，随即继续推进不依赖该资源的主线。Agent 的职责边界止于"有序尝试+留痕移交"，不在"替用户死磕"。

## Approach

1. **拉取前测通路**：`curl.exe -s -o NUL -w "%{http_code}" -m 15 https://<registry>/v2/`——000=被墙换源，401=可达继续。
2. **多源清单各试一次**（同源不重复）：①daocloud 独立域名形式 `ghcr.m.daocloud.io/<owner>/<repo>`；②`docker.1ms.run/<owner>/<repo>`；③`docker.xuanyuan.me/<owner>/<repo>`；④官方直连。前缀拼接形式（`docker.m.daocloud.io/ghcr.io/...`）对 daocloud 无效。
3. **白名单拦截即放弃该源**：报 "not in the allowlist" 说明该源对该镜像不可用，记入留痕后不再尝试。
4. **每次拉取后验真进度**：对 Docker 数据盘 vhdx（或下载目录）间隔采样两次字节增长；零增长 = 停滞，杀进程。不用"感觉等很久"做判断。
5. **硬上限 5 次**：每次间隔 10-15s；超限立即 `Stop-Process` 清理全部残留 docker/docker-compose 进程（含僵尸），并验证未伤及在跑容器（`docker ps` 确认既有容器 Up）。
6. **失败留痕与移交**：留痕文件记录尝试清单（源×结果×错误原文）+ 人工接管命令原文（如 `docker pull ghcr.io/digininja/dvwa:latest`），人工可直接复制执行；随即继续推进不依赖该资源的主线任务。
7. **慢源不等待**：官方 CDN/大文件下载挂后台不轮询死等，先启用兜底方案推进验证链路（本例 Windows 内置 pktmon 先行验证抓包链路，tshark 慢装不阻塞）。

## Faster Next Time

- **第一次失败就定重试计划**（上限/间隔/源清单），把"再试一次"升级为"第 N/5 次，换源 X"——有台账的死磕才是合规死磕。
- 信号速查：401=可达；000=被墙；`invalid repository`=前缀拼接形式错误，换独立域名形式；`not in the allowlist`=该源放弃；进程存活+字节零增长=停滞即杀。
- 金丝雀只验证 mirror 通路，不背书冷门大镜像层——主镜像拉取仍按上限纪律走。
- 移交人工时命令必须写进留痕文件（可直接复制），不要让用户从对话记录里翻。
- 停滞判定只认字节增长硬信号，拒绝"再等等"。
- 分工边界：引擎安装与 registry-mirrors 初始配置链（虚拟化预检→winget 装机→PATH 刷新→金丝雀首拉）见 2026-11-12-docker-desktop-winget-install 经验；本条只管"装好之后"的拉取纪律与止损移交。

## Applicability Boundaries

- 适用：容器镜像、安装包、依赖包等外部资源在受限网络下的拉取；Agent 后台执行与多源加速场景。
- 不适用：本地代码编译/测试重试（确定性高，可另行约定重试策略）；用户明示"继续尝试/死磕"的场景（用户指令优先于默认纪律）；源本身可达且字节持续增长的有效下载（此时按进度等待是正确动作）。

## Evidence or Examples

- 本例四源实测记录：daocloud 前缀拼接 → `invalid repository`；`ghcr.m.daocloud.io` → allowlist 拦截；docker.io 直连 → 000（15s 超时）；ghcr.io 直连 → 401 可达但 vhdx 停滞（postgres:16-alpine 金丝雀经 mirror 成功，vxcontrol/pentagi 与 digininja/dvwa 全通道失败）。
- 用户质询定性原文要点："遇到镜像墙后仅浅尝辄止配了少量源，随后直接启动无限循环（RESTART-PULL）后台死磕，属于摆烂式重试……未做多源容灾，未做有效探测，拉起循环就不管，严重违规。"
- 硬性标准原文要点：最大重试 5 次，每次间隔 10-15 秒（利用分层缓存）；超过 5 次必须停止并报错退出，释放后台资源；失败后保留日志等待人工接管。
- 终止验证：docker.exe ×5 + docker-compose.exe ×3 残留进程强杀后，在跑容器 artex-pg 未受影响（Up 持续），引擎正常。