---
id: 2026-11-12-docker-desktop-winget-install-registry-mirror-credential-path
title: Windows 冷启动 Docker Desktop 全链：虚拟化预检→winget 后台装→registry-mirrors 被墙适配→credential helper PATH 刷新→金丝雀验证
category: build-env
nature: technique
created_at: 2026-11-12T22:43:28
updated_at: 2026-11-13T00:09:37
tags: [Docker, Windows, 镜像加速, 部署链, 被墙适配]
keywords: [Docker Desktop winget 安装, HypervisorPresent 预检, registry-mirrors daemon.json, docker.m.daocloud.io, docker-credential-desktop PATH, 金丝雀镜像验证, vhdx 拉取进度信号, compose 后台静默, 401 registry 标准响应, 后台任务相对路径]
problem_patterns: [本机无 Docker 命令且容器化框架部署被阻，不知虚拟化前提是否满足, Docker Hub 直连超时镜像拉取挂起，公共加速源可达性无法快速判断, 新装 Docker 后 compose/pull 静默无输出，分不清是在下载还是根本没执行]
source_sessions: [ses_e311cd36dffe130cnixzTDBFDC]
project: Date
severity: medium
quality_score: 87
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-11-blocked-official-channel-ecosystem-bundle-discovery, 2026-11-13-image-pull-retry-cap-human-handoff-discipline]
---

# Windows 冷启动 Docker Desktop 全链：虚拟化预检→winget 后台装→registry-mirrors 被墙适配→credential helper PATH 刷新→金丝雀验证

## Scenario

本机从未安装 Docker（`docker` 命令不存在），但目标框架的官方部署形态是 docker-compose 栈，部署链被整体阻断。同时 Docker Hub 直连被墙，镜像拉取需要在装好引擎后立刻配置镜像加速。整条链必须在不违反"不动框架官方形态"约束的前提下一次跑通：装引擎→配加速→验证拉取→起 compose。

## Key Signals

- `docker version` 报 `CommandNotFoundException` = 引擎本体缺失；先探测虚拟化前提再安装，避免装完发现起不来。
- 虚拟化前提全绿的判定输出：`HypervisorPresent: True`、`wsl -l -v` 显示已有 WSL2 发行版（默认版本 2）——此时无需启用任何 Windows 特性，安装即可用。
- `winget show Docker.DockerDesktop` 的 `安装程序 URL` 指向 `desktop.docker.com`——先确认下载源可达再启动安装。
- Docker Hub 直连预检：`curl -o NUL -w "%{http_code}" -m 15 https://registry-1.docker.io/v2/` → `000`（15s 超时）= 被墙，拉取会无限挂起。
- 候选 mirror 源探测返回 `401`：**这是 registry 标准未认证响应，代表通路可达**，不要把 401 误判为"不可用"。
- 金丝雀 pull 报 `error getting credentials - err: exec: "docker-credential-desktop": executable file not found in %PATH%` = 会话 PATH 陈旧（Docker 刚装入，旧会话未刷新），此时 pull/compose 会静默挂起而非明确失败。
- compose 后台执行零输出 ≠ 还在下载：后台任务 workdir 漂移时 `> temp\xxx.log` 相对路径 Out-File 直接 `DirectoryNotFoundException`，compose 根本没执行。

## Essence

容器部署链上有四类**互相独立**的阻塞点：①引擎不存在；②registry 网络被墙；③安装后既有会话 PATH 陈旧导致 credential helper 找不到；④后台执行时 workdir 与相对路径假设漂移。任何一步的失败信号都可能被下一层掩盖（compose 无 TTY 天然静默），必须按序逐一验证，并用引擎状态、mirror 生效标志、vhdx 字节增长等**硬信号**代替"等它跑完"的假设。

## Approach

1. **虚拟化预检**：`Get-ComputerInfo` 的 `HypervisorPresent` + `wsl -l -v`（已有 WSL2 发行版即前提满足），无需启用任何 Windows 特性。全绿则直接安装。
2. **安装源预判**：`winget show <id>` 读 InstallerUrl，确认下载域可达（desktop.docker.com 本例可达）。
3. **后台安装**：`winget install` 重定向到**绝对路径**日志后台跑，防 20 分钟超时；轮询日志出现"已成功安装"且进程退出、`WINGET_EXIT=0` 判定成功（本例 UAC 自动通过）。
4. **引擎启动**：`Invoke-CimMethod Win32_Process.Create` 启动 Docker Desktop（长驻可靠），轮询 `docker version` 直到出现 `Server:` 版本号（本例 29.9.3）——Client 出现不代表引擎就绪。
5. **网络预检**：对 `registry-1.docker.io/v2/` 计时探测；000 超时即被墙，进入 mirror 配置。
6. **mirror 源探测与配置**：对候选源（docker.m.daocloud.io / docker.1ms.run / docker.xuanyuan.me）各发一次 `/v2/` 计时请求，401=可达；选两源写入 `%USERPROFILE%\.docker\daemon.json` 的 `registry-mirrors`，重启引擎后 `docker info` 确认 `Mirrors:` 列表生效。
7. **金丝雀验证**：先 pull 小镜像（如 `postgres:16-alpine`）验证 mirror 通路；若报 credential helper not found，则**每次调用前** `$env:PATH += ";C:\Program Files\Docker\Docker\resources\bin"` 刷新（新会话才会自动带上）。
8. **进度信号**：compose 拉取无 TTY 静默，用 Docker 数据盘 `DockerDesktopWSL\data\docker_data.vhdx` 字节增长判断是否真在下载；间隔采样两次零增长=拉取停滞，转去查后台任务日志找真因。
9. **后台任务纪律**：compose 日志一律绝对路径落盘；后台命令显式 `cd` 到 compose 文件所在目录或用 `-f` 绝对路径指定 compose 文件，防 workdir 漂移。

## Faster Next Time

- 装完 Docker 第一件事刷 PATH，再谈网络——credential helper 报错会以"静默挂起"形态吞掉后续所有命令。
- registry 探测 401 = 可达，000/超时 = 被墙；不要对 401 做无谓重试。
- 金丝雀小镜像先行，主镜像大拉取放在金丝雀通过之后；金丝雀成功不代表冷门大镜像层也能通（mirror 对冷门层可能回源失败），停滞判定以 vhdx 增长为准。
- compose 零输出时先查后台日志文件是否创建，再怀疑网络——Out-File 相对路径失败是零输出最常见的静默原因。

## Applicability Boundaries

- 适用：Windows 10/11 + WSL2 后端的 Docker Desktop 冷启动/重装；被墙网络环境下的 registry-mirrors 适配；平台化 agent 环境（命令超时转后台、workdir 漂移）。
- 不适用：Linux 原生 docker 引擎（无 Docker Desktop/credential-desktop 链路）；PATH 与 mirror 已就绪的既有环境（只需从金丝雀步进入）；企业内已有 Harbor/Nexus 私仓的场景（直接配 insecure-registries，不走公共 mirror）。

## Evidence or Examples

- 安装实测：`winget` 找到 Docker.DockerDesktop 版本 4.99.0，InstallerUrl `https://desktop.docker.com/win/main/amd64/245822/Docker%20Desktop%20Installer.exe`；后台安装日志"已成功安装"+"安装程序将请求以管理员身份运行。期待提示"（UAC 通过），`WINGET_EXIT=0`。
- 引擎就绪实测：WMI 启动 `WMI_RETURN=0 PID=14292`，轮询输出 `29.9.3`（Server）+ 空容器列表。
- 被墙与 mirror 实测：直连 `REGISTRY_HTTP=000 TIME=15.01s`；三源探测 `daocloud=401 1.49s / 1ms=401 2.49s / xuanyuan=401 4.11s`；daemon.json 更新后 `MIRRORS=[https://docker.m.daocloud.io/ https://docker.1ms.run/] SERVER=29.9.3`。
- credential helper 实测：金丝雀 pull 报 `error getting credentials - err: exec: "docker-credential-desktop": executable file not found in %PATH%, out: ```；PATH 刷新后同一命令成功，`Digest: sha256:aa6cb33cf4c19c765cefcf48d96176258800870a9a1e930ad126200f9d825139`，`postgres:16-alpine 420MB`。
- 进度信号实测：vhdx `1.83GB → 1.86GB`（真实下载中）与 120s 采样 `1.83GB→1.83GB`（停滞）两种形态都出现过；停滞真因=后台任务 `temp\artex_compose.log` 相对路径 `DirectoryNotFoundException`（workdir 在 D:\refs\ARTEX 而该目录无 temp\），compose 从未执行。
- 来源会话：ses_e311cd36dffe130cnixzTDBFDC（2026-11-12，P003 本地攻防演练框架部署，Docker Desktop 全链首次搭建）。