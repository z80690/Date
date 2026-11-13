---
id: 2026-11-11-tor-browser-full-package-acquire-official-config-integration
title: 完整产品获取与官方配置对接链：可信镜像定位 + perUser 静默安装 + defaults/user_rc 两文件姿势
category: build-env
nature: technique
created_at: 2026-11-11T10:54:31
updated_at: 2026-11-11T10:54:31
tags: [build-env, 安装包获取, 镜像加速, tor-browser, 配置对接]
keywords: [第三方镜像仓库, DevSidecar 加速下载, NSIS /S "/D=", perUser 静默安装, torrc-defaults, user_rc, --defaults-torrc, moat 动态网桥, CurrentDirectory, PluggableTransports 相对路径, CookieAuthentication, control_auth_cookie]
problem_patterns:
  - "官方渠道被墙后只找到'生态捆绑组件'或源码构建配置，拿不到完整安装包本体，不知去哪找可信镜像"
  - "非提权会话里 perMachine 安装器静默安装全死路，误以为所有安装器都不能免提权装"
  - "拿到 Tor Browser 后想把浏览器成熟配置接到无头 tor 通道（9050/9051），不知官方姿势与 PT 相对路径如何解析"
source_sessions: [ses_e379dbf6effeKdDEkw7jGkm075]
project: Date
severity: medium
quality_score: 87
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: ["build-env/2026-11-11-blocked-official-channel-ecosystem-bundle-discovery", "build-env/2026-11-11-non-elevated-installer-payload-extraction-7z-msiexec", "debugging/2026-11-11-tor-censored-network-bridge-debug-chain", "workflow/2026-11-11-learn-first-tor-bridge-dispatch-review"]
---

# 完整产品获取与官方配置对接链：可信镜像定位 + perUser 静默安装 + defaults/user_rc 两文件姿势

## Scenario

受限网络（官方下载域全被墙）下需要获取某桌面软件的**完整安装包**（实例：Tor Browser 洋葱浏览器），并把它内置的成熟配置与组件（tor.exe、PT 插件、torrc-defaults）对接到本机无头通道（SOCKS5 9050/9051）。约束：非提权会话、纯命令行、只能用已通代理加速通道。前置教训：用官方生态捆绑组件（如 OnionShare 内置 tor.exe）或挖源码构建配置替代完整产品，均被用户否决（"扒半成品组件/偷工减料"）。

## Key Signals

- 用户授权语出现"**拉取完整 X**"字样时，配置级调研（源码仓库的构建配置文件）与组件捆绑提取**都不构成交付**——必须拿到安装包本体。
- winget manifest 的 `Scope: user` 字段 + `InstallerType` 是免提权静默安装的预判依据：perUser 安装器 `/S`（NSIS）或 winget 直装**无需提权即可成功**；perMachine 才是"静默参数不豁免提权"的死路（报"请求的操作需要提升"）。
- **Tor Browser 15 起的架构变更**：torrc-defaults（18 行）里**不再有静态 Bridge 行**（旧版内置 meek/snowflake 网桥行已移除），网桥改由 moat 动态获取——在 defaults 里找网桥行必然落空；受限网络下 `moat.torproject.org` 直连被墙（实测 20s 超时），网桥行获取成为出口连通的最后卡点。
- `ClientTransportPlugin ... exec TorBrowser\Tor\PluggableTransports\lyrebird.exe` 是**相对路径**：tor.exe 的工作目录必须在 `Browser` 目录下才能解析，否则 PT 拉不起来（表现为 bootstrap 停在 `no configured transport`）。
- `CookieAuthentication 1`（官方 defaults 默认开启）→ 控制端口认证必须读 data 目录下的 `control_auth_cookie`，空密码 `AUTHENTICATE ""` 会失败。

## Essence

"完整产品获取 → 官方配置对接"是一条四段链，每段都有独立判据：**①镜像定位**——GitHub 搜"专做官方二进制镜像"的仓库（描述含 mirror to download binaries 字样），枚举其 releases 资产拿安装包；**②加速下载**——借已通的本地加速代理拉大文件，完成判定走文件系统（文件字节数与 release 资产吻合）而非进程退出码；**③静默安装**——perUser 安装器 `/S "/D=<全 ASCII 路径>"` 免提权直装，仅 perMachine 才降级到 7z/msiexec /a 载荷提取；**④配置对接**——两文件姿势（官方 defaults 不可改 + 自写 user_rc）+ 工作目录对齐（PT 相对路径）+ cookie 认证探针。缺任何一段的判据，都会退回"半成品/瞎拼"死路。

## Approach

1. **镜像定位**：`api.github.com/search/repositories?q=<产品>+mirror` 找专做官方二进制镜像的仓库（自我描述含 "mirror ... download binaries/executables"）→ `api.github.com/repos/<owner>/<repo>/releases` 枚举资产，选资产名带显式平台词的（`windows-x86_64-portable`）。
2. **加速下载**（后台保活 + 文件系统判定）：
   ```powershell
   # 后台 shell 执行（大文件不占前台）
   curl.exe -x http://127.0.0.1:<加速代理端口> -L -o <产物.exe> <release资产URL>
   # 轮询判定：(Get-Item <产物.exe>).Length 与 release 资产字节数吻合即完成
   ```
3. **perUser 静默安装**（目标路径必须全 ASCII）：`& <安装器>.exe /S "/D=C:\path\to\ascii_dir"`；`$LASTEXITCODE=0` 后**列产物目录确认结构**（实例产物为 `app\Browser\TorBrowser\Tor\tor.exe` + `app\Browser\TorBrowser\Data\Tor\torrc-defaults`）。若报"需要提升"或产物不出现（perMachine），转 7z 双层解包（见关联经验 non-elevated-installer-payload-extraction）。
4. **两文件姿势启动**：
   - 官方 defaults 原样不改：`tor.exe --defaults-torrc <Browser>\TorBrowser\Data\Tor\torrc-defaults -f <自写user_rc路径>`
   - 自定义项全部写 user_rc（DataDirectory/Log/SocksPort/ControlPort 等），路径全 ASCII。
   - **工作目录对齐**：用 WMI `Win32_Process.Create` 启动并把 `CurrentDirectory` 设为 `Browser` 目录，PT 的相对路径（`TorBrowser\Tor\PluggableTransports\*.exe`）才能解析——实测 PT 连接成功（bootstrap `2% (conn_done_pt)`）。
5. **控制端口认证探针**：读 defaults 所在 Data 目录对应实例的 `control_auth_cookie`（十六进制展开），`AUTHENTICATE <hex>` 后 `GETINFO status/bootstrap-phase` 直读实时进度，不依赖日志文件。
6. **出口连通卡点的正确去向**：Tor Browser 15 无静态网桥行，网桥须经 moat 动态获取或外部渠道拿 obfs4 网桥行写入 user_rc（`UseBridges 1` + `Bridge obfs4 ...`）；出口隐匿判据 = `curl.exe --socks5 127.0.0.1:9050 https://ipinfo.io` 出口 IP ≠ 真实 IP（见关联经验 tor-censored-network-bridge-debug-chain 的分层定位）。

## Faster Next Time

- 授权语解析口诀：用户说"拉取**完整** X"= 交付物是安装包本体；源码配置调研、组件捆绑提取都算偷工减料，第一轮就别走。
- 找镜像先于找构建配置：`<产品> mirror` 检索词 + 仓库描述三查（是否专做镜像、资产是否官方命名、release 是否多版本维护）。
- 免提权判据补全（修正"所有静默安装都死路"的过度概括）：**winget manifest `Scope: user` 或实测 `/S "/D="` 产物出现 = perUser 可静默直装**；仅 perMachine（报需要提升/msiexec 卡死）才走 7z/msiexec /a 提取路。
- 下载完成判定永远查文件字节数，不赌进程退出码（后台任务超时杀进程不影响已落盘产物）。
- tor.exe 接浏览器配置三板斧：`--defaults-torrc` 指官方 defaults、`-f` 指自写 user_rc、工作目录设 Browser 目录。
- 新版 Tor Browser（15+）要网桥行：别在 torrc-defaults 里找（已移除），直接走 moat 动态获取或外部 obfs4 网桥行。

## Applicability Boundaries

- 适用：官方渠道被墙但 GitHub（经加速代理）可达的环境获取官方桌面软件完整安装包；把 Tor Browser 成熟配置对接到无头 tor 通道；Windows 非提权会话判断安装器可否静默直装。
- 不适用：要求对二进制做官方签名逐字节验证的高合规场景（第三方镜像须向用户声明"官方再分发"信任级别）；网络可达环境（直接官方源，勿绕路）；需要浏览器 GUI 本体的日常使用（本链路目标是取其 tor 与配置做通道）。
- 边界：本经验为**部分闭环**——获取、安装、配置对接、PT 连接四段已实证成功，出口隐匿（moat 网桥行获取）在受限网络下未打通，最终判据待网桥行到位后复验；镜像版本滞后于官方最新（实例 15.0.4 vs 官方 16.0.1）；"PT 相对路径依赖工作目录"行为来自实测，跨版本需复核；moat 域可达性随网络环境漂移。

## Evidence or Examples

- 来源会话：ses_e379dbf6effeKdDEkw7jGkm075（2026-11-11，用户授权 B 路线"走 DevSidecar 加速拉取 Tor Browser"）。
- 实测链：镜像仓库 `hr0ark/tor-mirror`（描述 "Tor browser mirror to download binaries/executables"，release tag `tor-15.0.4`，资产 `tor-browser-windows-x86_64-portable-15.0.4.exe` 标称 108.3MB）→ `curl.exe -x http://127.0.0.1:31181 -L -o` 落盘 113,522,912 bytes → `& installer.exe /S "/D=C:\Users\Administrator\AppData\Local\tor_browser\app"` exit=0 → 产物 `app\Browser\TorBrowser\Tor\tor.exe`（10.4MB）+ `app\Browser\TorBrowser\Data\Tor\torrc-defaults`（18 行，含 `ClientTransportPlugin meek_lite,obfs2,obfs3,obfs4,scramblesuit,webtunnel exec TorBrowser\Tor\PluggableTransports\lyrebird.exe`、`CookieAuthentication 1`，**无 Bridge 行**）→ WMI CurrentDirectory=`app\Browser` 启动 → 9050/9051 双开、`Bootstrapped 2% (conn_done_pt)`（PT 连接成功）→ cookie 认证后 `250-status/bootstrap-phase=NOTICE BOOTSTRAP PROGRESS=2 TAG=conn_done_pt`。
- 反例留档（用户裁决实证）：①挖 `tor-actions/tor-browser-build` 源码仓库的 moat-settings/torrc-defaults 构建配置——被用户判"禁止偷工减料"（配置调研 ≠ 完整产品）；②以 OnionShare 捆绑 tor.exe 充当主方案——同轮被否（"不是让你扒 OnionShare 自带的半成品组件"，且该路径此前已出现 9050 出口仍真实 IP 的假通问题）。
- perUser/perMachine 对照实证：同会话内 perUser 安装器（Tor Browser NSIS `/S "/D="`、OnionShare wix、docmirror.dev-sidecar 经 winget）全部免提权成功；perMachine 安装器（直接 `&` 运行报"请求的操作需要提升"、`msiexec /qn` 卡 UAC）静默全死路。