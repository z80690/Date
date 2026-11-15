---
id: 2026-11-14-deploy-repo-mismatch-commit-sha-identity-vercelignore
title: 部署平台自动构建失败先核"修复落点=平台连接的仓库"：提交号比对定真身，构建日志 entrypoint 建议指向脚本不可照做
category: build-env
nature: pitfall
created_at: 2026-11-14T18:44:44
updated_at: 2026-11-14T18:44:44
tags: [vercel, 部署失败, 仓库错位, vercelignore, entrypoint]
keywords: [vercel 部署失败, 仓库错位, commit sha 比对, ls-remote 定真身, entrypoint 建议, .vercelignore, 扫描干扰, OCR 仓库名误读, 修复落点, 自动部署平台]
problem_patterns:
  - 对仓库 A 完成部署修复并推送成功，部署平台构建仍失败——未意识到平台实际连接的是另一个手动上传的快照仓库，修复推错了落点
  - 部署构建日志建议 entrypoint 指向仓库中某个临时/mock 脚本，照做会把演练 mock 端点部署成生产服务
  - 截图或日志中的仓库名经 OCR 误读，按误读名核对凭据与权限徒劳往返
source_sessions: [ses_e2663e19effewWyExkRIOfefi6]
project: Date
severity: high
quality_score: 88
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [build-env/2026-11-14-vercel-python-zero-dep-wsgi-entry-pattern, build-env/2026-11-14-vercel-deploy-status-via-commit-status-api-vercel-app-blocked, workflow/2026-11-10-github-metadata-eval-owner-numeric-trap]
---

# 部署平台自动构建失败先核"修复落点=平台连接的仓库"：提交号比对定真身，构建日志 entrypoint 建议指向脚本不可照做

## Scenario

Git 托管平台集成的自动部署（Vercel/Netlify/Cloudflare Pages 类）构建失败。此前已在"看起来对的"仓库完成入口修复并推送成功，但部署仍报同样的错误——修复动作与部署产物之间没有因果关系，怀疑方向却仍停留在入口代码与构建配置本身。

## Key Signals

- **决定性证据**：部署日志中的 commit sha 与"已修复仓库"的 HEAD 不一致——平台构建的是另一个提交历史。取部署日志 sha 与各候选仓库 `git ls-remote` 输出逐一比对，与日志 sha 吻合的仓库才是部署平台实际连接的真身。
- 构建日志给出的 entrypoint 建议指向仓库里的**非入口脚本**（临时 mock 服务、演练脚本等）——这是平台全仓扫描的产物，不是业务入口的证明。
- 真身仓库内容核查：无 `api/` 目录、无 `vercel.json`（修复只落在了另一个仓库，所以真身里根本没有这些文件）。
- 截图/日志中的仓库名与实测不符（OCR 误读形态），按误读名做权限核查会全部落空。

## Essence

自动部署平台绑定的是它**导入/连接时**锁定的那个仓库与分支，不随"我以为我修的是它"转移。根因链：同一账号下存在两个相似仓库（主仓 + 手动上传快照仓）→ 修复推到主仓 → 平台连接快照仓 → 快照里缺入口文件 → 平台全仓扫描把临时脚本误认为入口候选 → 构建日志给出误导性 entrypoint 建议。修复必须落到真身仓库；扫描干扰须用显式入口声明 + 部署忽略文件双重消除。

## Approach

1. 从部署失败日志中提取 commit sha；
2. 对所有候选仓库执行 `git ls-remote <url>`，与日志 sha 比对确定真身（HEAD 与日志 sha 吻合者）；
3. 核查真身仓库内容（partial clone 或 API 检查），确认修复所需文件的实际缺失面；
4. 向**真身仓库**推送修复集：约定入口文件 + 显式构建配置 + `.vercelignore`（屏蔽临时目录/演练目录/大文件目录，含凭据类文件必排）；
5. 构建日志建议的 entrypoint 与业务入口语义核对：指向 mock/演练/临时脚本的**一律不照做**——部署的是生产服务，mock 端点绑回环地址且无业务语义；
6. 修复推送后以部署平台的回写状态（见 commit status 经验）闭环验证，不以本地推送成功为完成判据。

## Faster Next Time

- 部署失败第一查固定为"修复落点 = 平台连接的仓库？"——sha 比对是秒级动作，先于一切入口/依赖排查；
- 构建日志的 entrypoint 建议当线索不当结论：先判断它指向的文件是否业务入口，指向 mock/演练脚本即触发"扫描干扰"判定，转入显式配置 + ignore 屏蔽路线；
- 截图/OCR 得到的仓库名一律以 `ls-remote` 实测为准，不据其做任何权限或凭据判断。

## Applicability Boundaries

- 适用：GitHub/GitLab 等仓库托管集成的自动部署平台，同账号下存在多仓相似名/快照仓的场景；
- 不适用：手动上传产物类部署（无 commit 对应关系，sha 比对法失效）；部署日志不显示 commit sha 的平台需改用构建日志中的文件清单比对；
- sha 比对依赖平台日志展示构建对应提交；若平台构建的不是分支 HEAD（如固定 tag），比对对象相应调整。

## Evidence or Examples

- 来源会话：ses_e2663e19effewWyExkRIOfefi6（2026-11-14，Vercel 部署失败修复）。
- 真身判定实测：部署日志 sha `645ef8a` 与 `git@github.com:z80690/my-date.git` 的 `ls-remote` HEAD 完全吻合；而修复所在的主仓 HEAD 为 `baddcd0`——"z2006900"为截图 OCR 误读，实测账号名 z80690。
- 修复落点实测：向 my-date 推入 `api/index.py`(955B) + `vercel.json`(254B) + 修复版 `.gitignore`(77B) + `.vercelignore`(108B，屏蔽 temp/、DVWA/ 等 11 项)，远端提交 `f34fe22825`；Vercel 回写 state: success。
- 构建日志误导建议实例：曾建议 `entrypoint = "temp.mock_llm_server: Handler"`——该文件是本机演练 mock 端点（绑 127.0.0.1:7810），照做即把回环 mock 部署为生产函数。