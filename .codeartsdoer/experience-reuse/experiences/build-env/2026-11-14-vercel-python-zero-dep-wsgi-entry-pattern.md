---
id: 2026-11-14-vercel-python-zero-dep-wsgi-entry-pattern
title: Vercel Python 部署须"约定入口+显式配置"双要素：stdlib WSGI 单文件入口 + vercel.json builds/rewrites 显式声明
category: build-env
nature: technique
created_at: 2026-11-14T12:15:23
updated_at: 2026-11-14T12:26:15
tags: [vercel, python, wsgi, 部署入口, vercel-json]
keywords: [vercel, api/index.py, wsgi app, vercel.json builds, rewrites, @vercel/python, 零依赖入口, python entry not found, 冒烟测试, serverless]
problem_patterns:
  - Vercel 部署 Python 仓库报"找不到 Python 入口"，根目录无 api/ 目录且无 vercel.json，误当成依赖或构建命令问题去排查
  - 为"跑通部署"顺手引入 Web 框架，把部署问题与依赖安装问题耦合，失败面扩大
source_sessions: [ses_e27c4dc39ffekQ77OksGO0tXru]
project: Date
severity: medium
quality_score: 85
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [workflow/2026-11-14-git-changeset-gate-newfile-false-negative-skip, debugging/2026-11-14-edit-trailing-newline-false-success-byte-patch]
---

# Vercel Python 部署须"约定入口+显式配置"双要素：stdlib WSGI 单文件入口 + vercel.json builds/rewrites 显式声明

## Scenario

Vercel 自动部署 Python 仓库时构建失败，报"找不到 Python 入口"。仓库主体是一个纯 Python 业务包（位于子目录），根目录既无 `api/` 目录也无 `vercel.json`——Vercel Python runtime 找不到入口文件，部署必然失败。任务目标是在不破坏原业务结构的前提下跑通部署。

## Key Signals

- 部署报错直接指向入口缺失（Python entry not found）。
- 根目录结构探测：无 `api/`、无 `vercel.json`；原业务是子目录 Python 包（`pyproject.toml` 声明包名）——确认失败根因是"入口文件与入口配置双缺失"，不是依赖安装或构建命令问题。

## Essence

Vercel 对 Python 项目按约定优先发现入口：`api/` 目录下的 `.py` 文件即 serverless 函数入口，且要求入口暴露 WSGI/ASGI 应用变量。修复的最小闭环是"双要素"：① 按约定新建唯一入口文件；② 用 `vercel.json` 显式声明入口与路由，不再依赖隐式发现。入口应用刻意选纯标准库 WSGI 类（零第三方依赖），避免为"跑通部署"引入框架依赖和 requirements 链路，把部署问题与依赖问题解耦。

## Approach

1. **新建唯一入口 `api/index.py`**：定义一个最小 WSGI 应用类并暴露 `app` 变量；所有路径返回 `200 OK` + JSON 状态体（仅固定字符串与请求路径，不放敏感数据，因为入口会被公网访问）。
2. **新建 `vercel.json` 显式指定入口**：`builds` 段把 `api/index.py` 交给 `@vercel/python` 构建；`rewrites` 段把所有路由转发到该入口（单入口承接全路由的部署形态）。
3. **原业务零改动**：入口是新增文件，不触碰原有包结构与配置，满足"跑通部署但保留原业务"约束。
4. **推送前本地冒烟**：用 `python -c` 内联构造 WSGI 环境对入口发起请求，断言响应 `200` 且 JSON 体正常——本地先证明入口可服务，再推送触发自动部署。
5. **提交推送 main 触发部署**：冒烟产物（`api/__pycache__/` 等）不加入暂存区，不入库。

## Faster Next Time

- 一句话自检："仓库里入口文件和入口配置两要素齐了吗？"缺任何一个都可能构建失败；双要素齐了再推送，避免把 Vercel 构建面板当测试器（每次失败都要等一轮云端构建）。
- "跑通部署优先"场景先选零依赖 stdlib WSGI，把"能不能部署"与"依赖能不能装"两个问题解耦；等部署通了再按需引入框架。
- 公网可达入口的响应体只放固定字符串与请求路径，禁放环境变量、密钥、内部路径等敏感数据。

## Applicability Boundaries

- 适用：Vercel Python runtime、无需第三方框架的"跑通部署"场景；也适用于"保留原业务、只加部署入口"的存量仓库改造。
- 不适用：需要 Flask/FastAPI 完整功能的场景（应引入框架并把入口指向其 app 对象）；Vercel 其他 runtime（Node/Go 等）入口约定不同，本模式不可平移。
- 推断标注：`vercel.json` 的字段结构与 WSGI 发现机制基于 Vercel 平台惯例（推断）；"api/ 目录即入口"为本次修复采用的约定形态。trace 截止于推送成功（`0b629a1..4247c03 main`），云端构建最终结果未回传，部署面板验证留待后续。

## Evidence or Examples

- 来源会话：ses_e27c4dc39ffekQ77OksGO0tXru（2026-11-14，Date 项目 Vercel 部署修复，23 条消息）。
- 冒烟输出：`200 OK` + `{"status": "ok", "service": "p003-drill-adapter", "path": "/"}`；修补文件尾换行后复测仍 `200 OK`。
- 变更落地：提交 `4247c03`（Add Vercel Python entrypoint and explicit build config，2 files changed, 48 insertions，新增 `api/index.py` + `vercel.json`），推送 `0b629a1..4247c03 main -> main` 到 `git@github.com:z80690/Date.git`，自动部署已触发。
- 附带事实：英文提交信息规避本机 git 中文乱码坑；`api/__pycache__/` 为冒烟产物未入暂存区。- 同源门禁支线：本条入口文件 `api/index.py` 的审查与修复链见 related_experiences——默认变更集对新文件 skip 假阴性须 -Files 显式补审，补审检出 W292 后 Edit 假成功改走字节级补写。