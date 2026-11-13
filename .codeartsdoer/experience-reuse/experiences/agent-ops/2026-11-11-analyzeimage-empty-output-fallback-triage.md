---
id: 2026-11-11-analyzeimage-empty-output-fallback-triage
title: analyzeImage 间歇空输出（EMPTY_OUTPUT_FALLBACK）的换帧探测与两次止损纪律
category: agent-ops
nature: technique
created_at: 2026-11-11T00:24:41
updated_at: 2026-11-11T00:30:54
tags: [analyzeImage, 空输出, 图像分析, 止损纪律, 平台工具]
keywords: [analyzeImage, EMPTY_OUTPUT_FALLBACK, 空输出回退, 同输入重试无效, 换帧探测, 单帧错位, 止损上限, 批量图像分析, 关键帧提取, 信息足够即收]
problem_patterns: [analyzeImage 批量分析多帧时间歇报 EMPTY_OUTPUT_FALLBACK 无任何内容返回，同输入重试仍失败浪费时间, 连续多轮图像分析调用接连失败，不知道是输入问题还是服务端容量问题, 视觉信息只是补充验证手段时不知道何时该放弃视觉通道止损]
source_sessions: [ses_e3a9c97a3ffeCp9OO263dGGrPC]
project: Date
severity: low
quality_score: 84
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: A
related_experiences: [2026-11-07-desktop-js-shell-mobile-domain-degradation, 2026-11-10-analyzeimage-batch-threshold-unstable-reduce-retry]
---

# analyzeImage 间歇空输出（EMPTY_OUTPUT_FALLBACK）的换帧探测与两次止损纪律

## Scenario

视频关键帧批量视觉分析（每批 1-4 帧传 imagePath）中，analyzeImage 间歇返回 `Error calling tool "analyzeImage": EMPTY_OUTPUT_FALLBACK:kimi-k3.1-pro`，无任何分析内容。同批次输入重试仍失败；但换一批不同帧或换单帧往往成功。典型场景：转写文本已拿到主线信息，抽帧仅用于补充目录结构/界面演示等视觉证据。

## Key Signals

- 错误特征：`EMPTY_OUTPUT_FALLBACK:<模型名>`——回退到空输出的字面含义，说明上游模型对该输入未产出内容，非本地参数错误。
- 判别信号：同输入重试一次仍空 → 大概率不是瞬时抖动；换输入（不同帧）成功 → 服务在特定内容/负载上不稳定，与本地调用方式无关。

## Essence

图像分析服务对部分输入会稳定地产出空结果（内容或负载原因），同输入重试不产生新信息；而"换一个输入"（错位取帧、单帧探测）是能产生新信息的唯一低成本变量。因此处置原则是：**变量从重试次数换成输入本身，同输入连败两次即止损**——尤其当文本通道（字幕/转写）已覆盖主线信息时，视觉通道是锦上添花，不值得为它阻塞主任务。

## Approach

1. 批量失败后第一次换法：从批中挑 1 帧单独探测（单帧请求小，最可能成功），确认服务是否可用。
2. 单帧成功 → 服务可用，改用小批量（1-2 帧）+ 挑选与已失败批次错位的帧继续。
3. 单帧也失败或同输入第二次空输出 → 停止视觉通道：已有转写/OCR 文本足够支撑结论时直接收，不足时在汇报中如实标注"视觉补充未取得"。
4. 全程不做第三次同输入重试——两次空输出已证伪"瞬时抖动"假设。

## Faster Next Time

- 优先顺序：先文本通道（转写/字幕）后视觉通道；视觉只补文本覆盖不到的信息（目录树、界面布局），文本够就少抽帧。
- 帧错位技巧：批量失败的那几帧换相邻帧号（±2）重试，画面常连续，信息等价。
- 把"同输入 2 次止损"写进批量图像任务的自查项，避免在报告收尾前被连环空输出拖住。

## Applicability Boundaries

- 适用于 analyzeImage（或同类多模态图像分析工具）报 EMPTY_OUTPUT_FALLBACK 类空回退错误；不适用于明确参数错误（路径不存在、格式不支持）——那是修输入的问题。
- 与 2026-11-10-analyzeimage-batch-threshold-unstable-reduce-retry 的分工：那篇覆盖批量参数策略（≤5 张/批起步、失败减半重试）；本篇承接"减批量、拆批之后仍连环失败"的后续决策——换帧错位探测与两次止损。决策链：减批量 → 换输入错位 → 同输入两次止损。
- "两次止损"阈值适用于视觉为辅助通道的场景；若视觉是唯一信息源（纯图片任务），止损阈值可放宽到 3 次且要换更大粒度的输入重切。
- 证据来自单会话多轮实测（失败 8+ 次、换帧/单帧成功 4 次），服务端行为可能随版本变化。

## Evidence or Examples

- 本会话欧工视频 105 帧分析中：4 帧批 ×2 成功后，后续批次连环 `EMPTY_OUTPUT_FALLBACK:kimi-k3.1-pro`；换 f_050/f_058/f_066/f_074 错位批成功，单帧 bf_040、bf_044 成功（抓到学员群实证截图）。
- 止损决策：头条主视频 100-148s 段确认纯口播（文本通道已全覆盖）后，放弃该段视觉复核，直接转入下一任务，未损失结论完整性。