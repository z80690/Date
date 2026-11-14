---
id: 2026-11-14-c-drive-space-inventory-cache-migration-object-routing
title: C 盘空间分层盘点与缓存迁移对象分流矩阵：改配置、官方 move、junction、禁动四路分流
category: build-env
nature: methodology
created_at: 2026-11-14T10:30:21
updated_at: 2026-11-14T10:30:21
tags: [磁盘盘点, 缓存迁移, 跨盘腾挪, 对象分流, 环境变量重定向, WSL迁移, junction兜底]
keywords: [PSDrive分层盘点, Get-ChildItem按大小过滤, pip config set global.cache-dir, npm config set cache, go env -w GOMODCACHE, HF_HOME, GRADLE_USER_HOME, PLAYWRIGHT_BROWSERS_PATH, wsl --manage --move, 平台运行数据禁动, junction, 工具链本体位置核查]
problem_patterns: [C盘接近满需要腾空间但担心破坏现有工具链与项目引用, 缓存目录散布在AppData/用户根/Roaming多层难以一次找全大头, 对所有目录一刀切搬运会弄坏正在被宿主进程使用的平台数据或与官方迁移机制冲突]
source_sessions: [ses_e2b6e8159ffe6f3G6R6H54eHt7]
project: Date
severity: medium
quality_score: 90
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-07-reference-assets-cross-drive-relocation-path-sync, 2026-11-13-kali-wsl-distro-form-recognition-nat-segment-registration, 2026-11-14-robocopy-symlink-dangling-infinite-retry-hf-hub, 2026-11-14-docker-desktop-datafolder-vhdx-move-boundary]
---

# C 盘空间分层盘点与缓存迁移对象分流矩阵：改配置、官方 move、junction、禁动四路分流

## Scenario

C 盘接近满（本例实测仅剩 12.7GB），需要把程序缓存/环境数据迁移到其他盘腾出空间，同时必须保证现有工具链与项目引用不受影响（如 `pip install -e .` 的本地项目、依赖 WSL 发行版的脚本、已配置的包管理器）。用户通常要求给出方案并拍板执行范围（缓存档/系统档/全量档），涉及 pagefile、休眠文件这类需重启项时要单独标注。

## Key Signals

1. `Get-PSDrive` 实测：C 盘 UsedGB/FreeGB 与其他盘可用空间——先确认"能腾多少、往哪腾"。
2. 大头分散在多层，单层扫描找不全：本例大头包括 `AppData\Local\wsl\...\ext4.vhdx`（15.7GB）、`pagefile.sys`（9.9GB）、`AppData\Local\Temp`（2.1GB）、pip/npm/Docker 缓存（~5GB）、用户根 `.workbuddy`（8.1GB）/`.cache\huggingface`（4GB）/`.gradle`（2.9GB）、`go` 模块缓存（2.3GB）、Roaming `Tencent`（6GB）、`Program Files` 各程序（合计 ~14GB）。
3. 系统文件混在盘根：`pagefile.sys`/`hiberfil.sys`/`swapfile.sys` 在盘根目录扫描时会被一并列出，属系统管理项，与用户缓存性质不同。

## Essence

两个关键判据：①**盘点按系统盘结构分层走**（盘根系统文件 → AppData\Local → 用户根 → Roaming → ProgramData → Program Files），每层只保留 ≥300MB 条目，才能找全大头且不被小文件噪声淹没；②**迁移动作不统一，按对象性质分流**——可再生的缓存改配置指向新盘、整体 vhdx 走官方 move、无配置机制的私有目录 junction 兜底、正在被宿主进程使用的平台数据禁动。执行前先核查工具链本体位置：本体不在 C 盘（如 Scoop 装在 D 盘）则缓存迁移对项目零风险，本体在 C 盘的目录先排除出迁移清单。

## Approach

1. **分层盘点序**（每层过滤 ≥300MB，按序执行）：
   ```powershell
   Get-PSDrive -PSProvider FileSystem | Select-Object Name, UsedGB, FreeGB   # 总览
   Get-ChildItem C:\ -Force | Where-Object Length -gt 300MB                    # 盘根系统文件（pagefile/hiberfil）
   # 依次对 AppData\Local、用户根、AppData\Roaming、C:\ProgramData、Program Files* 做子目录求和过滤
   ```
2. **工具链本体位置核查**：`Get-Command node,go,python,pip | Select-Object Source`——确认语言工具链本体落点；本体不在 C 盘 → 缓存随便迁；本体在 C 盘 → 该目录进"排除清单"。
3. **对象分流决策矩阵**（对齐对象性质选动作）：
   | 对象 | 动作 | 要点 |
   |---|---|---|
   | 包管理器缓存（pip/npm/go/gradle/HF/playwright） | 先改配置指向新盘，再迁旧缓存 | `pip config set global.cache-dir <新路径>`、`npm config set cache <新路径>`、`go env -w GOMODCACHE=... GOCACHE=...`、环境变量 `HF_HOME`/`GRADLE_USER_HOME`/`PLAYWRIGHT_BROWSERS_PATH` |
   | WSL 发行版 vhdx | `wsl --manage <distro> --move <目标目录>` | WSL 3.0+ 官方命令；发行版须 Stopped；迁移后命令名不变，依赖方无感 |
   | 无配置机制的私有工具目录 | robocopy /MOVE + junction 指回 | junction 保持旧路径透明可达，工具无感 |
   | 正在被宿主进程使用的平台数据 | 禁动 | 迁移平台自身运行数据有自断风险，宁可跳过 |
   | `pagefile.sys`/`hiberfil.sys` | 系统设置改盘 / `powercfg /h off` | 需重启、失去休眠功能，默认单列待用户拍板 |
4. **执行序**：建目标目录（顺带确认目标盘介质 SSD，拷贝时长可控）→ 先写配置 → 再 robocopy 迁数据 → 删除源侧空壳 → （并行大拷贝转后台后继续跑小项，定期查后台进度）。
5. **验证三件套**：配置回读（`pip config list`/`go env`/`npm config get`）+ 功能实测（`wsl -d <distro>` 实跑一条命令）+ 前后空间核验（UsedGB/FreeGB 对照盘点基线）。
6. **生效边界交代**：新写入的环境变量/配置对已开着的终端与应用不生效，重开即读到——收尾时明确告知。

## Faster Next Time

- 一句话判据：**缓存→改配置，vhdx→官方 move，私有目录→junction，平台运行数据→禁动，系统文件→重启类单独拍板**；先查工具链本体落点再定迁移清单。
- 盘点第一层就查 `wsl -l -v` + vhdx 文件大小——单个发行版 vhdx 往往就是最大单项，且官方 move 命令零风险收益最高。
- 环境变量配置类迁移"先写配置再迁数据"，顺序反了会导致迁移期间的请求写回旧路径。
- 并行 IO 竞争会让大拷贝超时转后台——大目录拷贝直接放后台跑，主线继续清小项，定期读输出文件查进度。
- 迁移含 symlink 的缓存目录前必读 [2026-11-14-robocopy-symlink-dangling-infinite-retry-hf-hub]。

## Applicability Boundaries

- 适用：Windows 本机 C 盘腾挪；缓存/环境数据跨盘迁移；PowerShell 5.1 环境；WSL 3.0+（支持 `wsl --manage --move`）。
- 不适用：Linux/macOS 路径与符号链接语义不同；WSL 低于 3.0 无 `--manage --move`，需 export/import 重建路线；目标盘空间不足以容纳迁移项；正在运行的服务数据目录（应走应用自带迁移功能，如微信"存储迁移"）。
- 边界：环境变量方案生效范围是"新开进程"，常驻服务需重启才读到新值；Roaming 应用数据（聊天工具类）含自迁移机制的优先用应用自带功能，不硬移。

## Evidence or Examples

- 实录（ses_e2b6e8159ffe6f3G6R6H54eHt7，2026-11-13）：C 盘 126.5GB 已用/12.7GB 可用 → 分层盘点锁定 13 项 → 按"缓存+WSL ≈32GB"档执行（pagefile/hiberfil 经用户拍板跳过、.workbuddy 8.1GB 平台数据禁动）→ 最终 94.2GB 已用/45GB 可用，回收 32.3GB。
- 工具链核查实录：node/go/python/pip `Source` 全部指向 `D:\soft\scoop`，Date 项目（src/adapter，pip install -e）不受迁移影响；WSL Kali 迁移后 `wsl -d kali-linux -- echo KALI_OK` 实测通过。
- 配置回读实录：`pip config list` 得 `global.cache-dir='D:\soft\cache\pip'`、`go env` 得 GOMODCACHE/GOCACHE 指向 `D:\soft\go`、`npm config get cache` 得 `D:\soft\cache\npm-cache`。
- 明细对账：WSL Kali 15.71GB（`wsl --manage kali-linux --move D:\WSL\kali`）+ HF 4.0GB（HF_HOME）+ go 2.92GB + .gradle 2.89GB（GRADLE_USER_HOME）+ laya-models 2.21GB（junction）+ Temp 1.78GB + pip 1.54GB + npm 1.19GB + ms-playwright 0.68GB（PLAYWRIGHT_BROWSERS_PATH）；Docker 1.9GB 走 DataFolder（另见 2026-11-14-docker-desktop-datafolder-vhdx-move-boundary）。