---
id: 2026-11-14-docker-desktop-datafolder-vhdx-move-boundary
title: Docker Desktop 数据盘位置不受 wsl --manage --move 管辖：settings-store.json 的 DataFolder 字段控制，改字段等启动自搬
category: build-env
nature: technique
created_at: 2026-11-14T10:30:21
updated_at: 2026-11-14T10:30:21
tags: [Docker Desktop, 数据盘迁移, vhdx, WSL边界, settings-store]
keywords: [docker_data.vhdx, wsl --manage docker-desktop --move, main ext4.vhdx, DataFolder, settings-store.json, Disk image location, EngineTypeWindows wsl2, 数据盘落点, 手动搬vhdx禁忌, JSON反斜杠转义]
problem_patterns: [用wsl --manage --move迁移docker-desktop后docker_data.vhdx纹丝不动只移走main盘, 误以为Docker数据盘是独立WSL发行版或可直接手动搬vhdx, C盘腾空间时找不到Docker数据盘的官方迁移入口]
source_sessions: [ses_e2b6e8159ffe6f3G6R6H54eHt7]
project: Date
severity: low
quality_score: 82
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: A
related_experiences: [2026-11-12-docker-desktop-winget-install-registry-mirror-credential-path, 2026-11-14-c-drive-space-inventory-cache-migration-object-routing, 2026-11-13-kali-wsl-distro-form-recognition-nat-segment-registration]
---

# Docker Desktop 数据盘位置不受 wsl --manage --move 管辖：settings-store.json 的 DataFolder 字段控制，改字段等启动自搬

## Scenario

C 盘腾空间时想迁移 Docker Desktop 的数据盘 `docker_data.vhdx`（本例 1.91GB，位于 `AppData\Local\Docker\wsl\disk\`）。直觉路径是把它当成 WSL 发行版盘用 `wsl --manage docker-desktop --move` 迁走，结果只移走了 0.09GB 的 main 盘，数据盘纹丝不动。

## Key Signals

1. `wsl --manage docker-desktop --move <目标>` 执行成功（exitcode=0），但检查发现只有 `wsl\main\ext4.vhdx`（0.09GB）被移动，`wsl\disk\docker_data.vhdx`（1.91GB）仍留在原位——"命令成功但大头没动"即命中本边界。
2. `%APPDATA%\Docker\settings-store.json` 实测内容：`"EngineTypeWindows": "wsl2"`、`"SettingsVersion": 48`，初始**没有** `DataFolder` 字段——数据盘位置默认跟随安装盘，字段缺失说明从未自定义过。
3. Docker Desktop 未运行（Stopped）时改配置无进程竞争。

## Essence

`docker-desktop` 发行版的 **main 盘 ≠ docker_data.vhdx 数据盘**：`wsl --manage --move` 只管辖发行版注册的 main 盘；数据盘（镜像/容器/卷的实际存储）落点由 Docker Desktop 自己的配置文件 `%APPDATA%\Docker\settings-store.json` 的 **`DataFolder` 字段**控制。因此数据盘迁移的正确入口是改该字段，而不是 WSL 命令；且**改字段后不要手动搬 vhdx**——Docker Desktop 下次启动会按新 DataFolder 自动搬迁数据，手动搬动与内部迁移逻辑冲突。

## Approach

1. 读 `%APPDATA%\Docker\settings-store.json`，确认 `EngineTypeWindows` 为 `wsl2` 且当前无 `DataFolder` 字段（或记录旧值以便回滚）。
2. 建目标目录（如 `D:\WSL\docker-desktop`）。
3. 向 settings-store.json 写入 `"DataFolder": "D:\\WSL\\docker-desktop"`——注意 JSON 中反斜杠必须转义为 `\\`；与既有字段合并写入，不要覆盖整个文件丢掉其他设置。
4. **不手动搬 vhdx**：下次 Docker Desktop 启动时自动把数据盘迁到新 DataFolder。
5. 兜底路径：若启动后未生效，GUI 里 Settings → Resources → Disk image location 改一次等效。
6. main 盘（0.09GB 级别）不值得单独 `--move`，留给 Docker Desktop 自行处理，避免与 DataFolder 迁移逻辑互相踩。

## Faster Next Time

- 看到 Docker 相关 vhdx 先分清两类：`wsl\main\ext4.vhdx`=发行版注册盘（`wsl --manage --move` 可管）、`wsl\disk\docker_data.vhdx`=数据盘（只认 settings-store.json 的 DataFolder）。
- 执行 `wsl --manage docker-desktop --move` 前先查 settings-store.json——若目标就是数据盘，直接跳过 WSL 命令改字段，省一次无效操作。
- "命令 exitcode=0 但目标文件没动"的通用排查：查目标对象是否归另一个配置体系管（这里 WSL 管 main 盘、Docker 自己管数据盘），而不是怀疑命令没执行。

## Applicability Boundaries

- 适用：Docker Desktop WSL2 引擎（`EngineTypeWindows=wsl2`）在 Windows 上的数据盘跨盘迁移；SettingsVersion 48 实测。
- 不适用：Hyper-V 引擎（数据盘落点机制不同）；Linux 原生 Docker（daemon.json data-root，另属一套）；WSL 发行版本身的 main 盘迁移（走 `wsl --manage --move`，与本经验互补）。
- 边界：`DataFolder` 生效时机依赖 Docker Desktop 下次启动自动搬迁，本次会话只能写入字段无法即时验证搬迁完成，属"待观察项"；GUI 兜底路径的菜单位置随版本可能变化。

## Evidence or Examples

- 实录（ses_e2b6e8159ffe6f3G6R6H54eHt7，2026-11-13）：`wsl --manage docker-desktop --move` 后实测仅 `main\ext4.vhdx` 0.09GB 到位、`docker_data.vhdx` 1.91GB 原位未动。
- 写入实录：settings-store.json 修改后读回验证含 `"DataFolder": "D:\\WSL\\docker-desktop"`，其余字段（AutoStart/DisplayedOnboarding/EngineTypeWindows/SettingsVersion=48 等）完整保留。
- 收尾口径：主任务汇报中标注"Docker 数据盘下次启动自动搬迁；若未生效，GUI Settings → Resources → Disk image location 改一次即可"，作为唯一待观察项留档。