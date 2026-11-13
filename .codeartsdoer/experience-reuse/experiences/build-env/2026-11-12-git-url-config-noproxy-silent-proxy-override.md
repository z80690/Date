---
id: 2026-11-12-git-url-config-noproxy-silent-proxy-override
title: git URL 级配置与 curl no_proxy 双重静默覆盖代理参数——报错连接目标分型与三层穿透修复
category: build-env
nature: pitfall
created_at: 2026-11-12T17:40:09
updated_at: 2026-11-12T17:56:49
tags: [git-proxy, no_proxy, config-override, github-pull, codeload]
keywords: [http.https://github.com/.proxy, URL 级配置优先级, -c 参数被覆盖, no_proxy 白名单, curl -x 失效, --noproxy 强制代理, codeload tarball 直连, Connection was reset, 三域独立探测, 浅克隆修复命令]
problem_patterns: [git clone 传了 -c http.proxy 参数仍报连 github.com:443 直连超时/reset，误以为代理写法不对反复换参数形式, curl 带 -x 代理访问 GitHub 域返回 000/超时，verbose 才发现 Uses proxy env variable no_proxy，代理被环境变量白名单静默吞掉, api.github.com 可用但 git 通道失败（或反向），误判为整体网络不可用而放弃拉取]
source_sessions: [ses_e30f55cabffejHKLEoEEoyDS5c]
project: Date
severity: high
quality_score: 91
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-06-network-direct-connect-diagnosis, 2026-11-06-github-api-vs-git-protocol-channel-split, 2026-11-12-github-pull-feasibility-abc-community-fork-first]
---

# git URL 级配置与 curl no_proxy 双重静默覆盖代理参数——报错连接目标分型与三层穿透修复

## Scenario
本机对 GitHub 仓库执行 `git clone --depth 1` 浅克隆：直连报 `Connection was reset`，随后显式传入代理参数 `-c http.proxy=http://127.0.0.1:31181` 重试仍失败；改用 curl 验证代理连通性同样得到 000 超时。任务卡在"代理参数明明传了却不生效"，需要在不改全局配置的前提下命令级修复。

## Key Signals
- 决定性分型信号——看报错里的**连接目标**：`Failed to connect to github.com port 443` = 代理参数根本没生效（仍走直连）；`Failed to connect to 127.0.0.1:31181` = 代理本体不可达。两类错误的处置方向完全不同。
- `git config --global --list` 同时存在 `http.proxy=http://127.0.0.1:31181` 与多条 `http.https://github.com/.proxy=`（URL 级空值键）——通用代理键与 URL 级强制直连键并存。
- curl verbose 输出 `Uses proxy env variable no_proxy == 'localhost,127.0.0.1,::1,github.com,.github.com,*.githubusercontent.com,...'`，`-x` 代理被环境变量白名单静默绕过。
- 代理本体存活性对照证据：强制绕过 no_proxy 后同代理 curl 实测 200——代理是活的，是参数被覆盖。

## Essence
两个工具的优先级规则导致代理参数"传了等于没传"：
1. **git**：URL 级专属键（`http.https://github.com/.proxy=`）优先级高于命令行 `-c http.proxy` 通用键；URL 级**空值**的语义是对该域强制直连（与既有经验一致），因此命令行通用代理被静默无视。修复必须**用 URL 级键覆盖 URL 级键**，而不是换通用键写法。
2. **curl**：环境变量 `no_proxy` 白名单优先级高于 `-x` 代理参数；GitHub 相关域全部在白名单内 → `-x` 被静默绕过，须用 `--noproxy` 显式清空或强制代理方式穿透。
3. **三域可达性相互独立**：api.github.com / codeload.github.com / github.com 主站各自可能通或不通，须逐域探测；codeload 的 tarball 直连是免代理的备份源码获取通道。

## Approach
1. 失败第一步先分型：读错误原文的连接目标（目标站 443 = 参数被覆盖 → 走第 2 步；代理地址 = 代理本体问题 → 查代理进程/端口）。
2. `git config --global --list` 检查目标域是否存在 URL 级 proxy 键（空值也算存在）。
3. git 命令级修复（不改全局配置）：`git clone --depth 1 -c "http.https://github.com/.proxy=http://127.0.0.1:31181" <url> <dir>`——用同名 URL 级键写入代理值，压过全局空值键。
4. curl 命令级修复：`curl.exe --noproxy " " -x http://127.0.0.1:31181 <url>`（或等效强制代理参数）穿透 no_proxy 白名单。
5. 备份通道：直连 `https://codeload.github.com/<owner>/<repo>/tar.gz/refs/heads/<branch>` 下载源码快照 tarball，绕开 git 协议通道。

## Faster Next Time
- 诊断顺序固化为：报错连接目标分型 → `git config --global --list` 查 URL 级键 → `no_proxy` 环境变量白名单 → codeload 直连探测，避免在"换代理参数写法"上空耗。
- 两条一次性探针预判通道：强制代理 curl 探针（验代理本体）+ codeload 直连探针（验备份通道），先探后克隆。
- 看到"传了代理仍报连目标站 443"直接怀疑**覆盖**而不是**参数写法**——URL 级键/no_proxy 两种覆盖机制都表现为这个症状。

## Applicability Boundaries
- 实证环境：win32 / PowerShell 5.1 / git for Windows；`no_proxy` 为进程环境变量注入形态（本例由执行平台注入，非用户手工设置）。覆盖优先级机理（URL 级键 > `-c` 通用键；no_proxy > `-x`）跨平台成立，具体键值与白名单内容随机器而异。
- codeload tarball 只给源码快照（无 .git 历史）；需要历史时仍走 URL 级键修复后的 clone。
- 仅覆盖"代理参数被本机配置/环境变量静默覆盖"场景；出口链路被墙（本地修复无效须换源/镜像）场景参见关联经验，不适用本条修复命令。
- 授权前提：本条命令级修复适用于任务已授权自主排障的场景（`-c` URL 级键与 `--noproxy` 探针均为一次性命令参数，不改全局配置）；若会话约束"诊断只读、修复权限归用户"（见 2026-11-06-network-direct-connect-diagnosis 适用边界），分层诊断按该条执行，本条修复命令降级为呈报给用户的修复选项。
- 相邻经验边界："拉哪个源"的 A/B/C 结论判据（先搜社区续维护版再下"不可得"结论）见 2026-11-12-github-pull-feasibility-abc-community-fork-first——本条管"拉取通道修复"，那条管"拉取来源裁决"。

## Evidence or Examples
- 实测：`git clone --depth 1 -c http.proxy=... https://github.com/RuoJi6/ARTEX.git` → `fatal: unable to access ... Recv failure: Connection was reset`（直连，参数未生效）。
- 实测：`curl.exe -x http://127.0.0.1:31181 https://github.com` → `proxy_http_code=000 time=21s`，verbose 显示 no_proxy 白名单含 `github.com,.github.com,*.githubusercontent.com`。
- 实测：强制绕过 no_proxy 后 `forced_proxy=200`（代理 31181 存活）。
- 实测：`git config --global --list` 输出含 `http.proxy=http://127.0.0.1:31181`、`http.https://github.com/.proxy=`（空值）、`http.https://codeload.github.com/.proxy=`（空值）等 4 条 URL 级键。
- 实测：URL 级键覆盖修复后两仓库浅克隆成功——RuoJi6/ARTEX HEAD=73d5437、vxcontrol/pentagi HEAD=cffed94；codeload 直连 tarball 同样成功（ARTEX 7781523 字节、PentAGI 52671580 字节），且 `codeload_direct=200` 与主站直连超时形成三域独立实证。