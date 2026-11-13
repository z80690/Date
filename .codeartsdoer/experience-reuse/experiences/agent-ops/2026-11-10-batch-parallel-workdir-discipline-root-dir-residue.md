---
id: 2026-11-10-batch-parallel-workdir-discipline-root-dir-residue
title: 批量并行操作逐条核对落点参数：忘传 workdir 产物落根目录与下游报错暴露模式
category: agent-ops
nature: pitfall
created_at: 2026-11-10T22:04:10
updated_at: 2026-11-10T22:08:06
tags: [批量操作, workdir参数, 产物落错, 并行调用, 下游报错信号]
keywords: [workdir忘传, 产物落根目录, 根目录残留, 下游No such file, Move-Item迁移, 并行命令参数核对, 落点参数, yt-dlp下载落错, 逐条独立契约]
problem_patterns:
  - "批量并行处理 N 个外部资源时，部分命令忘传 workdir/输出目录参数，产物落到工作区根目录而非各资源独立目录"
  - "落错位置由下游命令报 No such file or directory 才暴露，误判为文件丢失或下载失败而重新下载"
source_sessions: [ses_e3a448aefffeqBjZRM1XamKpG4]
project: Date
severity: low
quality_score: 85
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: ["workflow/2026-11-10-video-content-full-recovery-pipeline", "build-env/2026-11-10-ffmpeg-binary-via-imageio-ffmpeg-package", "agent-ops/2026-11-10-skill-evolution-review-dedupe-first-patch-existing"]
---

# 批量并行操作逐条核对落点参数：忘传 workdir 产物落根目录与下游报错暴露模式

## Scenario

批量并行处理多个外部资源（实例：双头条视频下载→抽音频→转写流水线，两视频约定各自独立目录 `temp/<平台>_<视频ID>/`）。每条 bash 调用需显式指定该资源的工作目录；第二条下载命令忘传 workdir，yt-dlp 产物（video.mp4 约 60MB、video.info.json、video.jpeg）落到工作区根目录而非目标子目录。错误未在上传配时暴露，而是延迟到下游 ffmpeg 抽音频时报"Error opening input file video.mp4 / No such file or directory"才被发现。

## Key Signals

1. **第一信号是下游报错而非落点异常**：下游命令在预期目录找不到输入文件——此时才回头检查上条命令的落点参数。文件名与预期完全一致、只是目录不对，是"落错"而非"丢失"的判别特征。
2. **根目录残留特征**：工作区根目录出现本不属于该层的批量产物文件（video.mp4 / video.info.json / video.jpeg）——批量任务收尾时根目录不应残留任何资源产物，出现即落错。
3. 并行/连续多命令场景的错觉：第一条参数写齐且成功，易形成"后续也齐了"的惯性——参数是逐条独立契约，不存在继承。

## Essence

批量并行文件操作的调用参数是**逐条独立契约**：workdir、输出路径、-o 目标目录等落点参数在每条并行调用里必须显式完整核对，上一条传了不等于这条会继承。落错位置的暴露点通常在下游命令（找不到输入文件）而非上传配本身，修复成本 = 定位 + 迁移 + 重跑下游；预防成本 = 每条命令构造时核对一遍目标目录参数。二者相差一个数量级——且大文件落错时 Move-Item 迁移是秒级，重新下载要重耗带宽与时间。

## Approach

1. 逐项独立目录约定：N 个外部资源各建 `temp/<资源标识>/` 独立目录，产物、中间物、脚本全落各自目录。
2. 每条命令发出前核对落点参数：workdir / 输出路径 / -o 与该资源目录一致——并行调用逐条核对，不复制上一条参数。
3. 发现落错（下游报错或根目录残留）：Move-Item 将产物迁入正确目录，避免重新下载；确认迁移后重跑下游命令。
4. 批量收尾核对：根目录不应残留批量产物文件，出现即迁移归位。
5. 批量收尾核对升级版：每个资源处理完成后立即 ls 该资源目录确认产物落位，不等下游报错。

## Faster Next Time

- 一句话规程：**批量并行 = 每条命令独立核对落点参数；逐条传 workdir，防产物落根目录。**
- 早检测：资源处理完成即 ls 该资源目录验证产物落位，把暴露点从"下游报错"提前到"落配完成时"。
- 警示信号：下游命令报 "No such file or directory" 且文件名与预期一致 → 第一怀疑对象是上条命令的落点参数错误，不是文件丢失；先查根目录与错误目录残留，勿直接重下。
- 迁移优于重下：数十 MB 级产物落错目录时 Move-Item 秒级修复；重下浪费带宽时间且可能因反爬/限速二次失败。

## Applicability Boundaries

- 适用：任何"逐项处理 N 个外部资源"的批量任务——视频/网页/文件批量下载、格式转换、批量分析，特别是并行工具调用场景；同样适用于 output、-o、目标路径等一切落点类参数。
- 不适用：单条命令任务（天然无漏传对象）；框架强制注入工作目录的场景（参数不可能缺失）。
- 平台标注：本实例为 CodeArts Agent bash 工具的 workdir 参数实测；模式本身泛化为所有带落点参数的命令行工具（yt-dlp -o、ffmpeg 输出路径、scp 目标等）。

## Evidence or Examples

- 来源会话：ses_e3a448aefffeqBjZRM1XamKpG4（2026-11-10，双头条视频维修资料入库流水线）。
- 实测数据：视频① 57.36MiB 下载（目标目录 toutiao_7688124510432428078，workdir 正确）；视频② 16.36MiB 下载时忘传 workdir，产物落根目录（video.mp4 60147999 字节、video.info.json 5164、video.jpeg 100871）；下游 ffmpeg 报 `Error opening input file video.mp4. No such file or directory`；Move-Item 迁移归位后双目录独立流水线跑通（音频 5'45"/1'31"，转写 TRANSCRIBE_OK）。
- 关联：视频流水线整体方法论见 workflow/2026-11-10-video-content-full-recovery-pipeline；ffmpeg 定位见 build-env/2026-11-10-ffmpeg-binary-via-imageio-ffmpeg-package；本踩坑后续被沉淀进 web-content-scraping 技能的"多视频并行处理要点"小节（见 agent-ops/2026-11-10-skill-evolution-review-dedupe-first-patch-existing）。