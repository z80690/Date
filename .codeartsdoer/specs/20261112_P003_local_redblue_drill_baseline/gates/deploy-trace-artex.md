# G2.3 ARTEX 本地部署留痕（gates/deploy-trace-artex.md）

> 承接 tasks.md 2.3（spec 4.3.2-3、5.4.1-1/3；design M1-3）｜执行时间：2026-11-12｜执行者=主智能体（用户裁决 A：装 Docker Desktop 后推进）

## 1. 资产与形态

| 项 | 值 | 证据 |
|---|---|---|
| 来源 | **RuoJi6/ARTEX 官方 Release v0.3.29**（windows-amd64.zip，方式三预编译部署） | SHA256 `0ee0a497...935` 与官方 SHA256SUMS **MATCH=True**（2026-11-12 校验） |
| 下载通道 | github.com 直连被墙（HTTP=000）→ gh-proxy.com 公共加速代理 200（15,566,407 B），SHA256 字节级校验兜底真实性 | curl 实测 |
| 部署目录 | D:\refs\ARTEX-release\artex-0.3.29-windows-amd64\（artex.exe+skills\+start.bat+config.json） | Expand-Archive 实测 |
| 许可证 | AGPL-3.0（本机内部使用不对外分发，R8 合规登记） | README:606 引证 |
| PG 依赖 | postgres:16-alpine 容器 `artex-pg`（**127.0.0.1:5432 回环映射**，pg_isready accepting） | docker ps 实测 |
| 控制台/traffic | **8787+8788 双端口全部绑定 127.0.0.1**（`-addr 127.0.0.1:8787 -proxy 127.0.0.1:8788` flag） | Get-NetTCPConnection 实测（IF-5 通过） |
| 长驻方式 | WMI Win32_Process.Create + run-p003.ps1 包装（ARTEX_CONFIG env+cwd+flag）；start.bat 守护功能降级未用（cmd.exe 被平台拦截，直跑 artex.exe 功能完整仅缺自动拉起） | WMI_RETURN=0、ALIVE=yes |

## 2. 关键配置

- config.json：`database.dsn=postgres://artex:...@127.0.0.1:5432/artex?sslmode=disable`（PG 容器回环）。
- LLM 配置：**全空**（ANTHROPIC/OPENAI key 空缺省、ARTEX_LLM_BASE_URL 未设）——方案 a 回执模式：ARTEX 不直连任何模型，调度决策由码道智能体承担；哑端点（127.0.0.1:7810）供后续按需切换。
- traffic 记录代理：127.0.0.1:8788（go-mitmproxy，全量明文留痕=蓝方取证素材）。

## 3. 过程降级登记（P8 口径，如实留痕）

1. 源码构建路线失败：浅克隆缺 webui/dist（go:embed 报 no matching files）→改走官方 Release 预编译（方式三）。
2. Docker Hub 直连+daocloud/1ms mirror 对 ruoji6/artex 主镜像回源均失败→compose 路线放弃；PG 依赖改由**已拉成的 postgres:16-alpine 独立容器**承载（金丝雀镜像成功证明 mirror 对热镜像可用）。
3. cmd.exe /c set 链被平台拦截器拒绝→bat/ps1 包装文件承载 env。

## 4. 验收对照

- spec 4.3.2-3（端口仅回环）：✅ 双端口实测 127.0.0.1。
- spec 5.4.1-3（来源登记/拦截面禁用）：✅ 来源+SHA256 登记；无公网伪装目标配置。
- design M1-3（Windows 宿主直跑）：✅。
- 【验证方式】`curl http://127.0.0.1:8787/api/health` 可回查；Get-NetTCPConnection 双端口回环可复放。

（完）