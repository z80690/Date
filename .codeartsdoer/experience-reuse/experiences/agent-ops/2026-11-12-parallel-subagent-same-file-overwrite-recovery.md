---
id: 2026-11-12-parallel-subagent-same-file-overwrite-recovery
title: 并行子代理产物路径重叠静默覆盖——复验指纹识别与 task_id 会话恢复协议
category: agent-ops
nature: pitfall
created_at: 2026-11-12T18:39:44
updated_at: 2026-11-12T19:30:39
tags: [agent-ops, 并行子代理, 写覆盖, 恢复协议, 落盘复验]
keywords: [并行子代理同文件覆盖, 字节数骤降, LastWriteTime 时序矛盾, task_id 恢复会话, 产物路径切分, 后写覆盖先写, 静默丢失实测证据, 子代理上下文隔离, 避免重跑实测, 复验指纹]
problem_patterns: ["为省时间并行派发两个子代理（文档结构修订 + 实测数据填充），产物路径指向同一文件，后写者静默覆盖先写者", "子代理各自声称落盘成功但复验发现字节数远小于自述值、LastWriteTime 与自述完成时序矛盾", "覆盖事故后直接重跑全部实测任务造成实测成本翻倍"]
source_sessions: [ses_e311cd36dffe130cnixzTDBFDC]
project: Date
severity: high
quality_score: 92
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-12-subagent-delivery-claim-verification, 2026-11-08-subagent-patch-field-drift-silent-content-loss, 2026-11-12-supplemental-ruling-additive-revision-exception-registration]
---

# 并行子代理产物路径重叠静默覆盖——复验指纹识别与 task_id 会话恢复协议

## Scenario

主代理为缩短周期，把"基线文档增量修订"与"外部框架拉取实测+实测数据填充"两类任务并行派发给两个子代理，两者均声明产出同一份核验报告文件。两个子代理在各自隔离上下文中独立完成并自述"已落盘"，但实际发生先写者产物被后写者整体覆盖。适用于主代理/子代理（Task 工具）协作、多个子代理并行且可能产出文件型交付物的全部场景。

## Key Signals

- 复验时字节数远小于子代理自述值（实测版自述 21601 字节，磁盘实际仅 4494 字节）——骤降幅度大且无解释；
- LastWriteTime 显示"自述更早完成的产物版本"反而更晚写入磁盘（框架版 17:19:51 晚于实测版写盘时点）——写入时序与自述完成顺序倒挂；
- 两个并行子代理的交付物声明中出现同一路径（回顾派发指令即可发现，无需读文件）。

## Essence

并行子代理持有互相隔离的上下文与文件视图：后写者以自己的完整版本整体覆盖先写者产物，双方均无感知、均如实自述成功，实测证据（命令+输出摘录）随覆盖静默丢失。**产物路径互斥是主代理派发前的职责**，不是子代理运行时的自我保护——"声明唯一落盘路径"必须成为并行派发的前置检查项，而不是事故后的复盘结论。

## Approach

1. **派发前路径切分**：列并行子代理各自声明的产物路径清单，查重叠；有重叠则改为串行派发、合并为单一子代理、或明确拆分到不同文件/目录。这是唯一可靠的预防手段。
2. **复验指纹识别**：并行交付后逐文件 `Get-Item <path> | Select-Object Name,Length,LastWriteTime`，与各子代理自述值交叉比对；字节数骤降或时间戳倒挂即判覆盖事故。
3. **恢复优先续跑会话而非重跑任务**：确认覆盖后，用 Task 工具携带原 task_id 恢复被覆盖证据的子代理会话，指令"将最终版重新落盘"——子代理上下文仍持有全部实测证据，续跑只补写盘，实测成本近乎零。
4. **恢复后二次复验**：重新落盘后再跑一遍字节数+头部内容+关键章节核对（本例 20000 字节/168 行、门禁编号与裁决登记章节齐全），确认恢复完整后才向用户呈报。

## Faster Next Time

- 并行派发前的产物路径清单查重是一次性低成本检查，能把整条恢复链路的成本降为零——排在所有并行派发 checklist 的第一位。
- 覆盖事故指纹口诀：**字节数骤降 + 时间戳倒挂 = 后写覆盖先写**，两个信号出现任一即复查，不要先怀疑子代理幻觉。
- 恢复决策口诀：**证据在子代理上下文里，重跑是浪费，恢复续跑才是修复**；仅当平台不支持 task_id 续跑时才退化为把双方产物人工合并重写。

## Applicability Boundaries

- 适用：Task 型子代理平台通用模式，文档/报告/配置等一切文件型交付物；实证平台为 CodeArts Agent 类主/子代理架构（支持 task_id 会话恢复）。
- 不适用：子代理只返回分析结论不落盘的场景（无覆盖载体）；主代理自己串行写文件的场景（Edit 工具 mtime 冲突走另条经验的"重读重应用"路径，机制不同）。
- 局限：恢复协议依赖平台支持按 task_id 续跑子代理会话；不支持续跑的平台只能人工合并，成本上升但检测指纹（步骤 2）不受影响。
- 相邻经验边界：2026-11-12-subagent-delivery-claim-verification 处理"单子代理自述 vs 磁盘实态"的存在级复验（防幻觉交付），本条处理"多子代理并行写同一文件"的冲突检测与恢复——前者复验一次交付，本条复验一组并行交付并裁决覆盖归属；2026-11-12-supplemental-ruling-additive-revision-exception-registration 记录了被覆盖文件（评估框架版）的修订纪律本体，本条只管覆盖事故的检测与恢复，不重复修订纪律。

## Evidence or Examples

- 实证会话 ses_e311cd36dffe130cnixzTDBFDC（2026-11-12，P003 前置门禁核验报告 pre_check.md）：主代理并行派发 spec-requirement-agent（落 v0.1 评估框架版）与 general 代理（实测拉取可行性并填充落盘），两者产物路径均为 `.codeartsdoer/specs/20261112_P003_local_redblue_drill_baseline/pre_check.md`。
- 覆盖实证：general 代理实测版 21601 字节落盘后被 spec-requirement-agent 的框架版 4494 字节整体覆盖（17:19:51 写入）；主代理复验 `Get-Item` 发现 Length=4494 与实测版自述 21601 严重不符，判定覆盖。
- 恢复实证：主代理以 task_id（ses_e310141edffekOHV8ZYYxcDfRv）恢复 general 代理会话，指令重新落盘；恢复后复验 168 行/20000 字节，G-PC1/G-PC2/G-PC3 门禁编号、裁决输入登记章节完整保留，"待实测"占位全部以实测证据填充——未重跑任何实测动作。
- 教训留痕：主代理当时自评"两个代理并行写同一文件存在覆盖风险"，复验动作恰好命中——复验清单中"字节数+时间戳"两项是指纹识别的决定性证据。