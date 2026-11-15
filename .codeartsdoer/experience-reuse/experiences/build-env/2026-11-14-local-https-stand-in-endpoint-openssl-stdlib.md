---
id: 2026-11-14-local-https-stand-in-endpoint-openssl-stdlib
title: 本地 HTTPS 替身桩：openssl 自签证书 + stdlib TLS 服务承接被测链路目标端缺席
category: build-env
nature: technique
created_at: 2026-11-14T12:42:53
updated_at: 2026-11-14T12:42:53
tags: [替身桩, openssl 自签, stdlib TLS, 本地回环, 联调降级]
keywords: [openssl -x509 -newkey -nodes -subj, http.server ssl wrap_socket, curl -k 自签校验, 127.0.0.1 替身端点, WMI 长驻 python 全路径, 目标端缺席, 伪装链路联调, 占位响应标注 stand-in, 白名单回环登记, git 自带 openssl 免安装]
problem_patterns: [被测链路要求 HTTPS/TLS 握手语义参与判定，但真实目标服务（靶场/应用）部署被网络或依赖阻断无法就位, 误把"链路打不通"归因于上游服务缺陷，实际是手头根本没有可用的 HTTPS 目标端, 临时找一个本地 HTTP 端点硬充 HTTPS 目标，三连 000 后误判为代理或防火墙问题]
source_sessions: [ses_e2d47079affeCxFw04N761RrMo]
project: Date
severity: medium
quality_score: 86
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-12-local-dummy-llm-endpoint-egress-governance, 2026-11-13-port-protocol-form-confirm-before-000-misdiagnosis, 2026-11-13-image-pull-retry-cap-human-handoff-discipline]
---

# 本地 HTTPS 替身桩：openssl 自签证书 + stdlib TLS 服务承接被测链路目标端缺席

## Scenario

演练/联调链路对目标端的要求是"HTTPS 且 TLS 握手真实发生 + 回环可达 + 响应内容可控"，而官方靶场或真实应用因镜像拉取被墙（重试上限内停手、人工接管）无法就位。此时链路验证整体被阻，但被测语义其实不依赖真实应用逻辑——只需要一个满足握手真实性的本地 HTTPS 端点充当替身。

## Key Signals

- 上游代理/伪装服务就绪（如流量录制代理已监听 127.0.0.1:8788），但没有可打的 HTTPS 目标。
- 对本地 HTTP 服务误用 `curl https://` 请求三连 000——先按"目标协议形态先行确认"排查，确认本机确实不存在 HTTPS 端点，而非协议错配。
- 真实靶场 `docker pull` 层下载停滞（vhdx 零增长），按重试上限纪律停手移交人工。

## Essence

被测链路需要的是 TLS 层语义（真实握手、证书存在、加密信道），不是应用层语义。自签证书 + Python 标准库 TLS 服务约 30 行即可满足全部被测需求；本机 git for windows/scoop 通常自带 openssl.exe，免安装。替身桩必须在响应体中显式标注 stand-in 占位语义，并在留痕中与真实靶场分开登记，防止判定证据的语义混同。

## Approach

1. **定位 openssl（免安装）**：`Get-Command openssl`；Windows 常见落点为 git for windows 捆绑的 `D:\soft\scoop\apps\git\current\usr\bin\openssl.exe`（scoop 安装路径按实际调整）。
2. **一行式自签证书**（`-nodes` 免口令、`-subj` 免交互、`-days` 短寿命降暴露面）：
   ```powershell
   & "D:\soft\scoop\apps\git\current\usr\bin\openssl.exe" req -x509 -newkey rsa:2048 -nodes -keyout key.pem -out cert.pem -days 1 -subj "/CN=127.0.0.1"
   ```
3. **stdlib TLS 服务**（无第三方依赖）：`http.server.HTTPServer` + `ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)`，`context.wrap_socket(server.socket)` 加载 cert/key，绑定 `127.0.0.1:8443`，GET 返回 JSON 占位体并标注 `"note": "stand-in"`。
4. **长驻启动**：WMI `Win32_Process.Create`，python 解释器必须写全路径（短名 `python` 返回 ReturnValue=9 且无任何解释）；确认进程存活与端口监听。
5. **客户端验证**（自签证书必须 `-k` 跳过校验）：
   ```powershell
   curl.exe -k --proxy http://127.0.0.1:8788 https://127.0.0.1:8443/ -w "%{http_code}"
   ```
   预期 200 + JSON 占位响应。
6. **白名单衔接**：替身地址落在 127.0.0.0/8 回环段内则天然合规；使用其他本地地址须先登记白名单再发起请求。

## Faster Next Time

- 三个核对项一次过：TLS 握手真实（非 HTTP 硬充）、绑定 127.0.0.1、响应体标注替身语义。
- curl 自签场景 `-k` 必带，否则报证书校验失败浪费一轮排查；经代理打 HTTPS 用 `--proxy` 显式指定，防 no_proxy 环境变量静默吞代理。
- 先跑 `Get-Command openssl` 再考虑装任何 TLS 工具包——git/scoop 环境大概率已在位。
- 留痕中替身桩与真实靶场分列登记（来源/地址/性质三字段），判定结论不得把替身桩证据写成真实靶场证据。

## Applicability Boundaries

- 适用：本地演练/联调/测试需要 HTTPS 目标端且真实服务缺席或部署被阻；TLS 握手真实性参与验证；Windows + PowerShell 5.1（bash + git 自带 openssl 同样适用）；回环白名单纪律下的链路打通。
- 不适用：需要真实应用漏洞面或业务语义的验证（替身桩无 DVWA 类内容）；任何对外/公网服务（自签证书 + 占位响应仅限回环）；需要受信证书链的场景（须改用本地 CA 签发并显式信任，仍限本机）。

## Evidence or Examples

- 实测环境：Windows 11 + PowerShell 5.1，openssl 取自 `D:\soft\scoop\apps\git\current\usr\bin\openssl.exe`（git for windows 捆绑），零新增安装。
- 产物：`cert.pem`（1115 B）/`key.pem`（1704 B），CN=127.0.0.1，-days 1；TLS 服务脚本落盘项目 `temp/` 目录（stdlib 约 40 行）。
- 链路回执：curl -k --proxy（ARTEX traffic 代理 8788）→ https://127.0.0.1:8443 → HTTP 200 + `{"status":"ok","service":"p003-https-target","note":"DVWA stand-in"}`。
- 上游闭环：同链路后续心跳模拟 3×200、攻防配对检查通过（paired=True）；替身桩支撑的轮次在留痕中标注"DVWA 替身"性质，真实靶场（GitHub 源码方案）另行登记。
- 姊妹模式：HTTP 哑端点承接 LLM 调用面（见 related_experiences）与本条构成"回环替身资产"两类——哑端点解决框架外连治理，本条解决目标端缺席。