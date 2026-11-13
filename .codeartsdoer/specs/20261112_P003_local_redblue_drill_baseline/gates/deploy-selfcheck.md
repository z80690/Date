# G2.6 部署就绪自检（gates/deploy-selfcheck.md）

> 承接 tasks.md 2.6（spec 5.4.1-2/3/4/6；design M1、IF-5、T3）｜自检时间：2026-11-12｜执行者=主智能体

## 就绪自检结果表

| 组件 | 来源/版本 | 监听核验（IF-5） | 角色声明 | 就绪状态 |
|---|---|---|---|---|
| Cairn（xcosmosbox） | D:\refs\Cairn-build（HEAD=2ae4eef+SQLite 修复+modernc v1.34.4），cairn-mcp.exe | **stdio 零端口**（未启用 HTTP 模式） | 知识图谱与状态记录资产经 MCP 服务智能体调用 | ✅ 就绪（MCP 注册完成，运行时可见性待新会话重载） |
| ARTEX | RuoJi6/ARTEX **v0.3.29 官方 Release**（SHA256 MATCH）+artex-pg 容器 | 8787/8788 **双端口 127.0.0.1** 实测 | 指挥所伪装模拟：traffic 记录代理（全量明文留痕）+探索图/审批门参照 | ✅ 就绪（长驻 WMI PID 实测 ALIVE=yes） |
| PostgreSQL | postgres:16-alpine 容器 artex-pg | **127.0.0.1:5432** 映射实测 | ARTEX 数据库 | ✅ 就绪（pg_isready accepting） |
| 哑端点（MockEP） | temp\mock_llm_server.py（Python 3.11 标准库） | **127.0.0.1:7810**（硬编码） | OpenAI 兼容占位响应；误调用落回环而非云端（R4） | ✅ 就绪（WMI 长驻，/health 实测） |
| PentAGI | vxcontrol/pentagi（官方仓库，镜像拉取受阻） | —（栈未起） | 沙箱执行层 | ⛔ **暂缓**：Docker Hub 直连被墙+daocloud/1ms mirror 对该大镜像回源失败（四通道实测）；`.env` 配置已就位（回环+外连面清空）；镜像拉通后 `docker compose up -d pentagi` 即可续 |
| Kali | 用户现有虚拟机（A-3 裁决复用） | NAT 隔离 | 目标机 | ✅ 既有资产（G3 登记网段） |

## IF-5 端口绑定核验明细（T3 口径）

- Get-NetTCPConnection 实测：8787=127.0.0.1、8788=127.0.0.1、5432=127.0.0.1、7810=127.0.0.1（绑定值）；**0.0.0.0 命中=0**。
- cairn-mcp stdio 模式无 TCP 端口（stdin/stdout）。
- Docker Desktop 引擎自身管理端口（named pipe/WSL 内部）不计入演练暴露面。

## 未过项处置

- PentAGI 未就绪→对应演练任务（G4 中 PentAGI 沙箱执行环节）暂缓启动（spec 5.4.1-6）；演练可先行覆盖 ARTEX traffic 留痕+Kali 工具链+哑端点回执链路，PentAGI 就绪后补跑该环节。
- 已拉取项不重复拉取、缺失项仅官方渠道补全并留痕（spec 5.4.1-2）：✅（ARTEX=官方 Release+SHA256；postgres=官方镜像；无第三方改包）。

（完）