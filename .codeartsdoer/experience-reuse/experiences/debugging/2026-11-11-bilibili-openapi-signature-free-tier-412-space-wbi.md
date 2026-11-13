---
id: 2026-11-11-bilibili-openapi-signature-free-tier-412-space-wbi
title: B 站公开 API 免签可用性分层：搜索与视频详情直调可用，UP 空间列表 wbi 风控 412 需绕行
category: debugging
nature: technique
created_at: 2026-11-11T00:24:41
updated_at: 2026-11-11T00:50:39
tags: [bilibili, wbi 签名, 412 风控, API 分层, 外部调研]
keywords: [api.bilibili.com, x/web-interface/search/type, x/web-interface/view, wbi 签名, 412 Request blocked, yt-dlp flat-playlist, UP 空间枚举, bvid, mid, 免登录接口]
problem_patterns: [调研 B 站 UP 主视频列表时直调空间接口返回非 JSON 或 412 被风控，误判为整个 B 站 API 不可用而放弃, 不知道哪些 B 站接口免登录免签名可用、哪些必须 wbi 签名，逐个试错浪费时间, yt-dlp 下载单个 B 站视频成功但 --flat-playlist 枚举 UP 空间被 412 拦截，误判为下载通道坏了]
source_sessions: [ses_e3a9c97a3ffeCp9OO263dGGrPC]
project: Date
severity: low
quality_score: 88
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-06-github-api-vs-git-protocol-channel-split, 2026-11-10-toutiao-jsvm-wall-playinfo-token-direct-bypass]
---

# B 站公开 API 免签可用性分层：搜索与视频详情直调可用，UP 空间列表 wbi 风控 412 需绕行

## Scenario

外部调研任务：确认某 UP 主（B 站同名账号）的真实公开资料（视频列表、账号信息）。直接请求 UP 空间相关接口拿回非 JSON/报错，yt-dlp 枚举空间列表报 `Request is blocked by server (412)`；但下载单个视频、搜索接口调用均正常。需要一套"哪些通道能用、哪些必须绕"的分层口径。

## Key Signals

- 可用信号：`https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword=...` 与 `https://api.bilibili.com/x/web-interface/view?bvid=...` 带常规 UA 直调，返回 `{"code":0,"data":...}` JSON，免登录免签名。
- 受阻信号：空间视频列表类接口直调返回非 JSON（风控页），yt-dlp 对 `space.bilibili.com/<mid>` 的 `--flat-playlist` 报 412——wbi 签名缺失是根因（列表接口 2023 起强制 wbi）。

## Essence

B 站公开 API 不是"整体可用/不可用"，而是按接口分层：**读单个对象（视频详情 view、搜索 search）免签直调，枚举集合（UP 空间列表、动态）强制 wbi 签名**。wbi 是对 query 参数加时间相关签名的机制，逆向成本不低且随版本变化；调研场景的正确策略是绕开枚举接口，用"搜索接口（keyword 含 UP 名）+ view 详情（从搜索结果取 bvid/mid）"拼出等价信息，单视频下载交给 yt-dlp（它对单视频走另一条免签链路）。

## Approach

1. 先调搜索接口 `search/type?search_type=video&keyword=<UP名或主题>`：拿到 `bvid/title/author/mid/play` 等字段，确认账号身份。
2. 用 `view?bvid=<BV号>` 拿单视频详情：标题、简介（desc）、时长、pubdate、UP 主 mid——简介字段常含关键说明。
3. 需要 UP 全部视频时：勿直调空间列表接口；改用多关键词搜索（UP 名 + 主题词变体）迭代枚举，或接受"搜索可见子集"并在报告中如实标注覆盖边界。
4. 单视频取证：yt-dlp 直接下 BV 号（可用），m4a 音频流可直接喂 faster-whisper 转写（无需先转 wav）。
5. 抽帧用 imageio-ffmpeg 定位的二进制，analyzeImage 批量读关键帧。

## Faster Next Time

- 检查顺序：B 站调研先打 `view`（最小验证，确认 API 通道活着）→ 再 `search`（枚举）→ 空间列表永远放最后且预期要 wbi。
- 看到 412 或非 JSON 返回，先归因"wbi 风控"而不是重试——重试不产生新信息。
- 报告口径：搜索枚举的覆盖边界（"关键词可见子集"）要写明，勿冒充全量列表。

## Applicability Boundaries

- 实测时点 2026-11：接口路径与免签分层可能随 B 站风控策略变化，使用前先各调一次验证。
- 免登录调用受频率约束，批量搜索需加间隔；带登录 cookie 可提升配额但引入账号风险，调研场景不建议。
- 仅适用于公开数据调研；不适用于需要登录态的（收藏夹、私密视频）——那条路需要 cookie 且有合规边界。

## Evidence or Examples

- 本会话实测：`search/type?keyword=AI 单片机 工作流` 直接命中目标 UP 的专题视频 `BV1jd4g6fECp`；`view?bvid=BV1jd4g6fECp` 拿到 mid=3706962065754292、简介（"从项目资料归档、硬件接口到代码开发…"）与 115s 时长。
- 受阻实录：yt-dlp `--flat-playlist https://space.bilibili.com/3706962065754292/video` → `ERROR: Request is blocked by server (412)`；自写脚本调空间列表接口 → JSONDecodeError（返回非 JSON 风控页）。
- 转写链路：yt-dlp 分流产物 `*.f30280.m4a` 直接作为 faster-whisper 输入，12 段中文转写成功，无需 ffmpeg 预转 wav。