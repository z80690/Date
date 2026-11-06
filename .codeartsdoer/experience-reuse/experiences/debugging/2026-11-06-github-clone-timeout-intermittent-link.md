---
id: 2026-11-06-github-clone-timeout-intermittent-link
title: 间歇性可达链路下 git clone 超时：同源重试窗口与后台输出文件处置
category: debugging
nature: pitfall
created_at: 2026-11-06T22:51:59
updated_at: 2026-11-06T22:56:51
tags: [git-clone, timeout, intermittent-network, background-task, stderr]
keywords: [Connection timed out, 300028, ls-remote 探针, 间歇性可达, 同源重试, 换源禁止, 后台任务, 输出文件, NativeCommandError, 工作树检出]
problem_patterns: [ls-remote 成功但 clone 超时不知能否重试, git clone 超时被移后台后不知如何取结果, stderr 重定向吞掉克隆错误输出]
source_sessions: [ses_e4ec5b313ffeKGWXQnKRNCYKDi]
project: Date
severity: medium
quality_score: 90
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-06-network-direct-connect-diagnosis, 2026-11-06-shell-session-state-not-persistent]
---

# 间歇性可达链路下 git clone 超时：同源重试窗口与后台输出文件处置

## Scenario
受限网络环境下对 GitHub 执行 `git clone`。此前 `git ls-remote` 探针成功（链路当时可达），随后克隆却挂起 300 秒后超时失败——链路是间歇性的，不是源不可达也不是本地配置问题。需要判断"能否重试、怎么重试、结果怎么取"，同时不违反"失败报原文、禁盲目重试换源"的纪律。

## Key Signals
- 错误原文形态是分类器（新增 timeout 条目）：`fatal: unable to access 'https://github.com/...': Connection timed out after 300028 milliseconds` = 链路通但慢/间歇（区别于 `Connection was reset` = 立即重置、`Could not connect` = 端口不通、`403 rate limit` = 限额须停止）。
- 决定性对照：**同一 URL 的 ls-remote 刚成功过** → 存在"同源重试窗口"，单次超时不代表源不可达。
- 误导线索：PowerShell 下 stderr 被重定向吞错，克隆输出显示为 `NativeCommandError` 且看不到真实结果——不能据此判成败。
- 命令超时被移入后台后，终端只给了一个输出文件路径和任务 id，没有结果。

## Essence
间歇性链路的因果链：链路时通时断 → 轻量探针（ls-remote 只握手不下载数据）命中"通"的窗口 → 完整克隆（数据量大、暴露时间长）撞上"断"的窗口。因此**探针成功是重试合法性的证据**：同源同命令重试是在收窄暴露窗口，不是盲目重试；换源/自造 HTTP 才是禁止项。超时转后台后，唯一可信的结果源是输出文件与磁盘状态，不是被吞的 stderr。

## Approach
1. 超时第一步：完整记录错误原文（含毫秒数），不立即动作。
2. 查重试合法性：本次会话中同一目标的轻量探测（ls-remote）是否成功过？成功过 → 存在同源重试窗口，执行第 3 步；从未成功过 → 转入分层诊断（配置层→出口链路），不适用本篇。
3. 同源同命令重试 1 次；大仓库加 `--depth 1` 缩短暴露窗口。重试仍败 → 停止再报，等待授权。
4. 后台任务取结果：命令超时转后台时，读它给的输出文件路径拿完整输出（fatal 行在里面）；不依赖 stderr 显示。
5. 克隆进度用磁盘判定，不猜：目标目录只有 `.git` = 传输中/未检出；`.git` + 工作树文件 >0 = 已检出（数一下条目数）；目录不存在 = 已失败清理。
6. 成功后立即记录本地 commit 版本号（`git -C <dir> rev-parse --short HEAD` + 日期），供引用核对。

## Faster Next Time
- 顺序固定：ls-remote 探针 → clone（--depth 1）→ 超时则读后台输出文件 → 磁盘判进度 → 同源重试 1 次 → 仍败停止。
- 判"能否重试"看两件事：错误形态（timeout≠reset≠rate limit）+ 探针是否近期成功过。
- 长命令预期可能超时，就主动放后台跑并轮询输出文件，别等前台超时被动转后台。

## Applicability Boundaries
- "同源重试窗口"仅适用于：探针近期成功 + 错误形态为 timeout 的间歇性链路。rate limit 类错误禁止重试（窗口不存在）。
- PowerShell 现象（stderr 吞错、NativeCommandError 显示）为 Windows 实证；后台转存+输出文件机制为平台行为，路径形态因平台而异。
- 修复权限归用户的原则不变：本篇只覆盖"重试与取结果"，不覆盖改配置/换源/配代理。

## Evidence or Examples
- 实证会话：2026-11-06 调研两开源仓库。Cairn 克隆一次成功（903 文件）；deepseek-super-agent 第一次克隆后台 300 秒超时（`Connection timed out after 300028 milliseconds`），第二次同源 `--depth 1` 克隆成功（工作树 18 条目）。
- 磁盘判进度实证：超时后查目录只见 `.git`（未检出），输出文件中读到 fatal 行确认失败；重试后 `git_exists + worktree_files=18` 确认检出。
- 版本登记实证：Cairn=2ae4eef(2026-10-29)、deepseek-super-agent=e705e87(2026-11-05)。