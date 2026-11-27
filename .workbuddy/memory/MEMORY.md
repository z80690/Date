# Date 项目 · 长期约定

## Git 提交约定（2026-11-15 用户明令，本项目专用，覆盖用户级通用规则）

- **单分支 main**：不建 feature 分支、不切分支。当前只有 `main` + `origin/main`。
- **全量提交**：用户要"所有东西都提交、不留暂存区"。本项目提交用 `git add -A` 全量暂存（覆盖用户级"精确 git add、禁止 -A"的通用规则——仅限本项目）。
- **推送同步**：每次提交后 `git push origin main`。远程 `git@github.com:z80690/Date.git`，SSH 已认证，推送会同步更新关联的服务器。
- 提交前仍须核查无敏感文件（.env/密钥）和大文件，此条不覆盖。

## 功能隔离（2026-11-15 用户明令）

- WorkBuddy 与码道 CodeArts 严格隔离，不许混。
- WorkBuddy 配置/规则/技能/子智能体只在 `.workbuddy/`，运行时只读这里。
- `.codeartsdoer/` 是码道的，WorkBuddy 不读、不写、不依赖，仅作出处标注。

## 临时测试服务：用完即关（2026-11-18 用户明令 · 原则）

- 临时测试/演练起的服务（Nginx、后端、各类 daemon）**一律不设后台常驻、不开机自启**。
- 活干完、验证结束，**必须把起过的服务全部关掉**，恢复干净状态。保留现场可以，但进程不许留。
- 目的是不污染环境、不占资源、不留隐患。下次要用再按命令重启即可。
- 例外：用户明确要求长期运行的（真部署场景），另说。

## WSL Kali 网络实情（2026-11-18 实测）

- 本机 Windows 10 build 19045，`.wslconfig` 虽配了 `networkingMode=mirrored` + `dnsTunneling=true`，但**镜像模式要 Win11 22H2/build 22621+**，本机版本不认 → 回退 NAT，DNS 隧道失效（Kali 内 DNS 解析全断、出站 ping 100% 丢包）。
- 结论：**Kali 无法与 Windows 用同一张网卡 IP**（版本天花板，非配置错）。升级 Win11 22H2+ 才可能。
- 可用通道：Windows → Kali 的 SSH 用 `kali@127.0.0.1`（localhost 转发通、免密、sudo 免密）；虚拟 IP `192.168.17.238` 从 Windows 不可达。
- Kali 装包：DNS 断导致 apt 不可用 → Windows 下 deb（源站可达）→ `/mnt/c/...` 进 Kali `dpkg -i` 离线装。
- **禁止擅自调网络配置（2026-11-18 用户明令）**：不升级 Win11、不改 `.wslconfig`/DNS/路由/IP。理由=网络分层多，调断后找病根像家电维修/医生看病，耗时且未必看得准，得不偿失。当前 NAT + DNS 断是可接受的已知限制，绕过去即可，不修。

## 攻防案例库（2026-11-25 用户明令）

- 案例存 `.workbuddy/memory/攻防案例库.md`。平常不用，**只在攻防/黑白盒测试任务时先读它**找对应案例。
- 用户要的是"记住案例，用时才调"，不是天天注入。

## 规则权威源（WorkBuddy 侧）

- `.workbuddy/rules/项目协作公约.md`（六条）+ `项目工作规则.md`（八条）为 WorkBuddy 侧唯一权威全文。
- 来源（`.codeartsdoer/rule/*.mdc`、项目根 `AGENTS`/`CLAUDE`）仅标注、非运行时依赖。
