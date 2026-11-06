---
id: 2026-11-06-network-direct-connect-diagnosis
title: 网络直连失败分层诊断：先证配置层干净，再判出口链路
category: debugging
nature: methodology
created_at: 2026-11-06T18:41:59
updated_at: 2026-11-06T18:45:59
tags: [network-diagnosis, proxy, git-config, direct-connect, error-triage]
keywords: [Connection was reset, Could not connect, rate limit, git proxy, 空proxy, 直连, 环境变量, NO_PROXY, hosts, ls-remote, 分层诊断]
problem_patterns: [git clone / webfetch 报 Connection was reset 疑似代理问题, 不确定卡在代理配置还是出口链路, 空 proxy 配置被误当垃圾清理]
source_sessions: [ses_e51adb269ffeqfVMdEGO1eP4xa]
project: Date
severity: medium
quality_score: 89
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-06-codeartsdoer-docs-retrieval]
---

# 网络直连失败分层诊断：先证配置层干净，再判出口链路

## Scenario
git clone、webfetch 等对外请求报 `Connection was reset` / `Could not connect`，需要判断卡点在本地代理配置还是出口网络链路，且用户约束为"失败贴原文停止、禁盲目重试换源"。

## Key Signals
- 错误原文即分类器：`Connection was reset` = 连接中途被重置；`Could not connect (port 443)` = 端口不通；`403 rate limit exceeded` = 已达限额，必须停止而非换路径。
- 曾误导判断的线索：`.gitconfig` 里 4 条 `http.https://github.com/.proxy=`（空值）看起来像残留垃圾——实际是有效的"强制直连"配置。
- 决定性对照信号：IDE 到自家云 API 全部 200 成功，而 GitHub 失败 → 本地配置层干净，卡点在出口链路。

## Essence
完整因果链：本地曾有代理插件注入劫持（历史注释可证）→ 配置空值 URL 专属 proxy 强制 git 直连绕过 → 插件关闭后链路恢复。卡点判定必须先证配置层干净（无代理注入、hosts 无劫持），再判出口链路稳定性；空 proxy 的 Git 语义是对该域名强制直连，不是配置残留。

## Approach
1. 失败第一步：完整贴错误原文，停止重试，等待授权（禁盲目重试、禁自作主张换源）。
2. 分层核查（每层区分"存在但空值"与"根本不存在"，不可混报）：
   - Git 配置：`git config --show-origin --list` 按来源分层看 proxy 字段；读 `.gitconfig` 原文，注释常揭示历史配置意图。
   - 环境变量：进程级 / 用户级 / 机器级三级分别查 `HTTP_PROXY`/`HTTPS_PROXY`/`ALL_PROXY`/`NO_PROXY`。
   - IDE 配置：配置目录中搜 proxy 字段 + 运行日志里的 proxy 诊断行（如 `final proxy: 空`、`ProxyEnable enabled=false`）。
   - hosts：查目标域（github.com 等）是否有劫持映射。
3. 对照验证定位层：IDE/本地服务到自家 API 若 200 正常，则卡点在出口链路，与本地配置无关。
4. 恢复验证用轻量探测：`git ls-remote <url> HEAD` 只握手不下载数据，成功即证明链路恢复。

## Faster Next Time
- 诊断顺序固定为：错误原文分类 → Git 配置 → 环境变量 → IDE 配置 → hosts → API 对照 → ls-remote 复测，避免乱序试错。
- `ls-remote` 是零成本测连探针，克隆失败后验证恢复用它，不要重复完整 clone。
- 判断"配置项存在但值为空"与"不存在"分开报告——语义完全不同（空 proxy=强制直连；无 proxy=跟随默认）。

## Applicability Boundaries
- 分层诊断法与"空 proxy=强制直连"语义跨平台通用；具体路径（`%USERPROFILE%\.gitconfig`、`C:\Windows\System32\drivers\etc\hosts`、IDE 配置目录）为 Windows 实证。
- `Connection was reset` 类错误也可能是防火墙/GFW 干扰，此时本地修复无效，需用户提供可用代理或镜像——诊断结论只定位层级，不擅自换源。
- 修复权限归用户：诊断全程只读，改动（关插件、配代理）由用户执行。

## Evidence or Examples
- 实测：`.gitconfig` 注释原文 `# 绕过 sandbox-cli 注入的本地代理对 GitHub 的劫持; 空 proxy 表示直连`（2026-09-18 配置）。
- 实测：内核日志 `final proxy: 空`、`windows ProxyEnable enabled=false`、IDE 到华为云 API 全部 200。
- 实测：`git ls-remote https://github.com/.../hyra-results.git HEAD` 返回 `0dcc533... HEAD`，证明用户关闭代理插件后链路恢复（尝试 1/3 即成功）。
- 实测：4 种读取 GitHub README 的途径全部失败且原因各异（raw 域 socket closed / git clone reset / 主域 Unable to connect / API 403 rate limit）——多途径失败原因不同时说明是出口链路问题而非单一配置错误。