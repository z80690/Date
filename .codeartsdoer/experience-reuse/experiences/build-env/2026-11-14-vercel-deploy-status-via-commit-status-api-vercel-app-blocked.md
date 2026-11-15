---
id: 2026-11-14-vercel-deploy-status-via-commit-status-api-vercel-app-blocked
title: Vercel 部署状态以 GitHub commit status API 为权威验证，vercel.app 域名国内直连 HTTP=000 是访问墙不是部署失败
category: build-env
nature: technique
created_at: 2026-11-14T18:44:44
updated_at: 2026-11-14T18:44:44
tags: [vercel, 部署验证, commit-status, vercel-app, 域名被墙]
keywords: [commit status API, Vercel 部署状态权威验证, vercel.app 被墙 HTTP 000, DNS 污染, target_url 部署控制台, context Vercel, 部署与访问分型, state success, webfetch socket closed, 自定义域名 CNAME]
problem_patterns:
  - 部署推送后无法确认成功与否，试图用生产域名 curl 验证，HTTP=000 被误判为部署失败而反复重部署
  - 本机代理类工具均未运行，curl 直连与平台 webfetch 双双不通，以为验证无路可走
  - 猜测 *.vercel.app 域名去访问，实际项目分配的域名/别名从未被核实
source_sessions: [ses_e2663e19effewWyExkRIOfefi6]
project: Date
severity: medium
quality_score: 85
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [build-env/2026-11-14-vercel-python-zero-dep-wsgi-entry-pattern, build-env/2026-11-14-deploy-repo-mismatch-commit-sha-identity-vercelignore, debugging/2026-11-13-port-protocol-form-confirm-before-000-misdiagnosis]
---

# Vercel 部署状态以 GitHub commit status API 为权威验证，vercel.app 域名国内直连 HTTP=000 是访问墙不是部署失败

## Scenario

向 GitHub 仓库推送修复后等待 Vercel 自动部署，需要确认部署是否成功并验证服务响应。手头没有 Vercel CLI/登录态，且生产域名访问全部失败。

## Key Signals

- 部署结果不反映在 git push 回执上——推送成功 ≠ 部署成功，两者证据源不同。
- 生产域名（`*.vercel.app`）curl 返回 **HTTP=000**（连接层失败，无 HTTP 响应）；平台 webfetch 对同一域名报 socket closed。
- 本机代理通道（DevSidecar 类加速代理、tor SOCKS5）均未运行——本机出口不存在任何可用替代通道。
- GitHub commit status 查询返回 `state: success` + `context: Vercel`——与 HTTP=000 并存，构成"部署成功但访问不通"的完整分型。

## Essence

Vercel 与 GitHub 集成部署时，会把每次部署结果**回写为 commit status**：`GET /repos/{owner}/{repo}/commits/{sha}/status` 返回 state（success/failure/error）与 context，target_url 即部署控制台页。这是免登录、免猜域名的权威验证通道。而 `vercel.app` 域名在国内网络环境全域被 DNS 污染，直连 HTTP=000——**部署状态**与**访问可达性**是两条独立判定链，HTTP=000 只能证明访问通道不通，不能反推部署失败；反之类推，域名可达也不等于部署成功。

## Approach

1. 拿到部署对应的 commit sha（推送回执或远端 `ls-remote` HEAD）；
2. 查 commit status（凭据用本机凭据管理器，token 不落盘）：`GET https://api.github.com/repos/{owner}/{repo}/commits/{sha}/status`，读 `state` 与 `context: Vercel`，从 `target_url` 取部署控制台地址；
3. `state: success` 即部署成功，不再依赖域名可达性判断；
4. 访问验证与部署验证**分型处理**：HTTP=000 先判访问通道（本机代理是否运行、目标域名是否属被墙域），确认是访问墙后**不动部署**；
5. vercel.app 直连不通的替代路径：启动本机代理通道后浏览器访问，或为项目绑定自定义域名（CNAME 解析后国内可直连）；
6. 平台 webfetch 对被墙域同样受限（socket closed），其失败不构成"服务确实挂了"的反证。

## Faster Next Time

- 一查一判分离："部署成没成"查 commit status API；"能不能访问"另判通道与域名归属——两条链的证据永不互推；
- 无需猜域名：部署别名/控制台 URL 都在 status 的 target_url 里；
- 复用前先确认本机凭据可用（credential fill 一次即知），无凭据时该验证通道降级为"等用户在控制台确认"。

## Applicability Boundaries

- 适用：GitHub 集成的 Vercel 项目部署验证；同理可平移到其他把 CI/CD 状态回写 commit status 的平台（同为 status API 消费）；
- 不适用：未集成 Git 仓库的手动上传部署（无 commit 对应关系）；commit status API 需要认证凭据与 API 配额；
- "vercel.app 国内被墙"为 2026-11-14 实测结论（HTTP=000 三通道一致），网络策略可能变化，复用前快速重测一次 HTTP 码再定性。

## Evidence or Examples

- 来源会话：ses_e2663e19effewWyExkRIOfefi6（2026-11-14）。
- 权威验证实证：`GET /repos/z80690/my-date/commits/f34fe22825.../status` 返回 `state: success | context: Vercel | target_url: https://vercel.com/z80691/my-date/6FA1UmuZ95ZGz1P3eq5QJFrY6P7X`。
- 访问墙实证：`https://my-date.vercel.app/` 直连 HTTP=000；本机 tor SOCKS5 未运行（False）；平台 webfetch 报 "The socket connection was closed unexpectedly"——三路访问证据一致，但部署 status 确证 success。
- check-runs 对照：`GET .../check-runs` 返回空——Vercel 走 classic status 回写而非 check runs，验证时勿查错端点。