---
id: 2026-11-10-video-content-full-recovery-pipeline
title: 视频链接内容完整还原流水线：yt-dlp 下载 + 抽帧 OCR + 转写双源交叉修正
category: workflow
nature: technique
created_at: 2026-11-10T19:47:03
updated_at: 2026-11-10T19:47:03
tags: [workflow, 视频还原, yt-dlp, 转写, 多源交叉验证]
keywords: [视频链接, 看视频内容, 头条视频, yt-dlp下载, ffmpeg抽帧, faster-whisper转写, 帧字幕OCR, 同音字修正, 双源交叉验证, hf-mirror, imageio-ffmpeg]
problem_patterns: ["用户贴视频链接要求看内容且不接受'看不了'的答复", "需要还原视频完整口播内容与画面细节但只有链接", "语音转写同音字误写需要正字源仲裁"]
source_sessions: [ses_e3abe9d50ffe6h0jefPpuZafdL]
project: Date
severity: medium
quality_score: 88
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: ["agent-ops/2026-11-10-video-link-content-verify-screenshot-vlm", "debugging/2026-11-07-desktop-js-shell-mobile-domain-degradation", "agent-ops/2026-11-10-analyzeimage-batch-threshold-unstable-reduce-retry", "debugging/2026-11-10-python-print-redirect-gbk-mojibake-write-file-directly"]
---

# 视频链接内容完整还原流水线：yt-dlp 下载 + 抽帧 OCR + 转写双源交叉修正

## Scenario

用户贴出视频平台链接（实例：头条/今日头条）并明确要求 AI"看视频内容"，且不接受"无法播放视频"的边界声明式答复（用户批评："你可以做个切片嘛……你自己想办法"）。此前只有截图 VLM 核对的降级方案（见关联经验），本条提供完整还原视频内容的自主链路。规模：单条短视频（约 1 分钟），个人 Agent 会话。

## Key Signals

- webfetch 抓视频页面静默无输出（头条反爬，见关联经验 2026-11-07-desktop-js-shell-mobile-domain-degradation）——此时不要在网页抓取路径上纠缠，视频内容有独立的文件级获取路径。
- 用户明确批评"只声明看不了"的回答，暗示可自行安装工具（"安装个 mcp""自己找个方案"）——这是启动自主工具链方案的信号。
- 此前会话遗留"截图地址栏长数字与 URL 不一致"的疑云——视频 ID 是流水线的天然输入，可一并闭环。

## Essence

Agent 无法在线播放视频 ≠ 无法获取视频内容：视频是可下载文件，走"下载→抽帧→转写→OCR"四段流水线即可完整还原。真正起作用的方法有两个决策点：

1. **工具链一次装齐**：`pip install yt-dlp you-get imageio-ffmpeg` —— ffmpeg 可执行文件由 imageio-ffmpeg 附带（`imageio_ffmpeg.get_ffmpeg_exe()`），免 scoop/系统级安装；yt-dlp 对头条有**原生提取器**（`[toutiao] Fetching ttwid` 自动完成，无需手写 cookie/接口）。
2. **双源交叉仲裁**：faster-whisper 转写有同音字误写（实测"平权→评选""传话筒→手画筒""小智→小质"），**帧字幕 OCR 为正字源**；转写提供时间轴与连续语流，帧 OCR 提供画面细节（板子参数、烧录日志、界面文字）。两者互相印证后合并为可信稿。

## Approach

1. 装工具链：`pip install -q yt-dlp you-get imageio-ffmpeg -i <镜像源>`；验证 `yt-dlp --version` 与 `python -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"`。
2. 探测格式：`yt-dlp -F <url>`（头条自动取 ttwid），列出 480p/720p 档位与体积，选合适档。
3. 下载本体+元数据+封面：`yt-dlp -f 720p --write-info-json --write-thumbnail -o "<dir>/video.%(ext)s" <url>`。
4. ffmpeg 探时长（`-i` 读 Duration）→ 定抽帧步长（实例：51.94s × 每 3 秒 = 17 帧）→ 抽帧 `ffmpeg -i video.mp4 -vf fps=1/3 frames/frame_%02d.jpg` + 抽音频 `ffmpeg -i video.mp4 -ar 16000 audio.wav`。
5. 转写：pip 装 faster-whisper，脚本内设 `os.environ["HF_ENDPOINT"]="https://hf-mirror.com"` 走镜像拉模型（small 级够用），分段输出带时间戳文本。
6. 帧字幕 OCR：analyzeImage 按 ≤5 张/批串行分析帧（见关联经验批量策略），提取逐帧字幕原文与画面文字。
7. 双源合并：转写分段为骨架，同音字/误写字以帧 OCR 为准修正；画面细节（日志、参数贴片、界面文字）单独归档；产物统一落盘留档（video.mp4 / audio.wav / frames/ / transcript_utf8.json / 封面）。

## Faster Next Time

- 见"视频链接 + 看内容"直接跳过 webfetch/浏览器探测，从第 1 步工具链开始——网页抓取路径对该类站点大概率白耗一轮。
- 转写脚本的中文结果**脚本内直接写 UTF-8 文件**，不要经 stdout 重定向（见关联经验 mojibake 条目）；模型已缓存时重跑是秒级的，修脚本重跑优于逆向解乱码。
- 警告信号：转写文本出现"读得通但用词怪"的中文（评选/手画筒/小质）→ 立即查同时间段帧字幕 OCR 仲裁，勿直接采信转写。
- 遗留疑云闭环模式：先前的"长数字双源不一致"疑云，下载流水线天然复验——本实例下载到的真实视频 ID 与用户 URL 完全一致，确认为截图 OCR 误差。

## Applicability Boundaries

- 适用：用户给短视频链接要求看内容/核对信息，平台在 yt-dlp 支持列表内（头条/抖音/B站等主流站点实测覆盖面广）；需要完整口播稿或画面细节还原的场景。
- 不适用：直播流/需登录会员的内容（提取器拿不到直链）；超长视频（全量抽帧+转写成本高，应先看 info.json 时长再定抽样密度）；仅需页面文字信息的场景（走网页抓取降级链即可，不必下载本体）。
- 边界：本条在头条单视频实测闭环；其他平台的 yt-dlp 提取器支持为推断，首次使用先 `-F` 探测确认再批量。

## Evidence or Examples

- 来源会话：ses_e3abe9d50ffe6h0jefPpuZafdL（头条视频内容查看与信息核对 fork #1，2026-11-10）。
- 实测数据：头条视频 `7704227854556332607`，720p 档 21.19MiB（3421kbps, 1280x720@59.94fps）5 秒下完；总长 51.94s；抽 17 帧 + 16kHz 音频；faster-whisper small 输出 11 段带时间戳转写；帧 OCR 抓出完整字幕链与画面细节（烧录日志 `ESP32-S3 (QFN56, rev v0.2), 16MB Flash + 8MB PSRAM`、烧录 8,949,612 字节校验通过）。
- 修正实例：转写"AI 的评选时代"→ 帧 OCR 确认为"平权时代"；"当手画筒"→"当传话筒"；"开源的小质"→"小智"（xiaozhi-esp32，推断标注）。
- 产物留档：`temp/toutiao_7704227854556332607/`（video.mp4、audio.wav、frames/frame_01~17.jpg、transcript_utf8.json、video.jpeg）。
- 关联经验：2026-11-10-video-link-content-verify-screenshot-vlm 是其前置降级方案（无下载能力时的截图核对模式），本条将其"无法播放外部视频"的边界实质扩展为"可下载还原"；analyzeImage 批量策略与 print 重定向 mojibake 见关联条目。