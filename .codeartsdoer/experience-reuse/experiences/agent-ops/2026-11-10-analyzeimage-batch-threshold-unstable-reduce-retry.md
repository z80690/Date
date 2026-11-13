---
id: 2026-11-10-analyzeimage-batch-threshold-unstable-reduce-retry
title: analyzeImage 多图批量阈值不稳定：≤5 张/批起步、EMPTY_OUTPUT_FALLBACK 减半重试
category: agent-ops
nature: technique
created_at: 2026-11-10T19:47:03
updated_at: 2026-11-11T00:30:54
tags: [agent-ops, analyzeImage, 批量分析, 失败重试, 视觉模型]
keywords: [analyzeImage, 多图批量, EMPTY_OUTPUT_FALLBACK, 空输出回退, 批量阈值, 减批量重试, 视频帧OCR, 分批串行, 原样重发禁忌, vision模型]
problem_patterns: ["analyzeImage 一次传多张图片报 EMPTY_OUTPUT_FALLBACK 空输出", "批量图片分析失败后不确定是图片问题还是批量大小问题", "多帧/图集/批量截图分析需要定批量策略"]
source_sessions: [ses_e3abe9d50ffe6h0jefPpuZafdL]
project: Date
severity: low
quality_score: 84
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: A
related_experiences: ["workflow/2026-11-10-video-content-full-recovery-pipeline", "2026-11-11-analyzeimage-empty-output-fallback-triage"]
---

# analyzeImage 多图批量阈值不稳定：≤5 张/批起步、EMPTY_OUTPUT_FALLBACK 减半重试

## Scenario

一次调用 analyzeImage 分析多张本地图片（实例：视频流水线抽出的 17 帧做字幕 OCR 批量分析）。同类场景：图集批量识别、多页截图汇总、逐帧画面核对。平台：本机 CodeArts Agent 内置 analyzeImage 工具（底层 vision 模型）。

## Key Signals

- 失败响应为 `EMPTY_OUTPUT_FALLBACK:deepseek-v4.1-flash-1017`——工具调用本身 status=error，返回空输出回退错误，**不是**图片内容或路径问题。
- 同一会话内批量大小行为不一致：9 张/次成功（系统自动分 2 批、每批 5 张串行），8 张/次失败，减至 4 张/次成功——说明无稳定的安全阈值，批量大小本身是风险变量。
- 成功时系统提示"本次请求包含 N 张图片，将分 X 批串行处理，每批 5 张"——平台内部已有分批机制，但外部请求的图片总数仍影响稳定性。

## Essence

Agent 运行时与人工逐张看图的差异：analyzeImage 单次调用批量越大，vision 服务返回空输出（EMPTY_OUTPUT_FALLBACK）的概率越高，且阈值不稳定（同会话 9 成 8 败）。失败与图片内容无关，与批量大小强相关。关键纪律：**失败后必须改参数重试（减批量），禁原样重发**——原样重发大概率复现同样的空输出，白耗一轮调用。

## Approach

1. 批量起步 ≤5 张/次：降低首次失败概率；成功时响应更完整（实测 5 张/批的逐帧描述质量优于大批次）。
2. 遇 `EMPTY_OUTPUT_FALLBACK`：判定为服务侧批量失败，立即将批量减半（8→4）重试，不检查图片文件本身、不原样重发。
3. 减半后仍失败：继续减半（4→2→1）或拆批串行；单张仍失败才考虑图片本身问题（损坏/过大）。
4. 大批次成功后不回切大批量：即使某次 9 张成功，也维持小批量策略（阈值不稳定意味着下一次同样大小可能失败）。

## Faster Next Time

- 多图分析任务规划时直接按 ≤5 张/批分批，避免一次全量投喂后失败重试的往返。
- 见 EMPTY_OUTPUT_FALLBACK 关键词直接进"减批量重试"分支——该错误码本身就是"批量过大"的强信号，与图片内容无关。
- 批量任务的 prompt 中明确逐帧输出格式（如"每帧给出字幕原文/物品/场景"），小批量时输出结构更稳定。

## Applicability Boundaries

- 适用：本机 CodeArts Agent 的 analyzeImage 工具批量分析场景（imagePath/imageId/imageBase64 三种传参方式的批量行为一致）。
- 与 2026-11-11-analyzeimage-empty-output-fallback-triage 的分工：本篇覆盖批量参数策略（≤5 张/批起步、减半重试）；减半+拆批后仍连环失败时，转入那篇的换帧错位探测与"同输入两次止损"决策，勿继续在参数维度打转。
- 不适用：单张图片分析（无批量风险）；其他平台的 vision API（阈值与错误码不同，需另行实测）。
- 边界：实测底层模型为 deepseek-v4.1-flash-1017，平台更换 vision 模型后阈值可能变化，但"失败减批量重试、禁原样重发"的纪律不变。

## Evidence or Examples

- 来源会话：ses_e3abe9d50ffe6h0jefPpuZafdL（头条视频帧 OCR，2026-11-10）。
- 实测三点数据：9 张/次（自动分 2 批每批 5 张）成功返回 frame_01~09 逐帧分析；8 张/次（frame_10~17）报 `EMPTY_OUTPUT_FALLBACK:deepseek-v4.1-flash-1017`；减至 4 张/次（frame_10~13）成功，再 4 张（frame_14~17）成功。
- 关联经验：2026-11-10-video-content-full-recovery-pipeline（该流水线的第 6 步即依赖本批量策略）。