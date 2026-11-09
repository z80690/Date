---
id: 2026-11-08-edit-cross-block-boundary-swallows-json-key
title: edit 跨 JSON 块边界的 oldString 会吞相邻键名行：newString 必须显式重建边界行，改后 json.load 验证兜底
category: agent-ops
nature: pitfall
created_at: 2026-11-08T03:26:16
updated_at: 2026-11-08T03:33:09
tags: [edit陷阱, JSON结构, 状态文件, 边界吞噬, 改后验证]
keywords: [oldString 跨块, stage_4 键名, JSON 损坏, 纯文本替换, progress.json, json.load 验证, 整体 write, 小步推进, 边界行重建, 无回执告警]
problem_patterns:
  - 对多块 JSON 状态文件（stages.stage_2...stage_N 相邻块）做小步 edit 推进，oldString 从上一块尾部跨到下一块首行，newString 重建时漏掉 `"stage_X": {` 键名行
  - edit 回执 success 无任何异常，结构损坏在后续读取/解析时才暴露，错误定位成本随时间推移倍增
  - 不知该用小步 edit 还是整体 write 维护状态文件，跨块改写时凭感觉拼 oldString/newString
source_sessions: [ses_e488e3ea4ffeibxmS5KxTmxPRl]
project: Date
severity: medium
quality_score: 91
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-06-edit-conflict-reread-then-reapply, 2026-11-07-edit-read-prerequisite-grep-not-counted]
---

# edit 跨 JSON 块边界的 oldString 会吞相邻键名行：newString 必须显式重建边界行

## Scenario

多阶段流程状态文件 progress.json（`stages` 下 stage_1...stage_7 多个相邻 JSON 对象块）按流程小步推进：每完成一个阶段就用 edit 把对应块的 status 改为 completed、追加阶段结论字段。一处 edit 的 oldString 从 stage_3 块尾部起、跨过 stage_4 块的首行 `"stage_4": {`，newString 重建该段时漏掉了这个键名行。

## Key Signals

- edit 回执 success，无任何告警——工具按纯文本做精确替换，不理解 JSON 语法边界，"吞掉一个键名"不构成执行层错误。
- 后续读取发现 JSON 结构损坏：某行位置只剩 `"stage_4": {` 应在的缩进内容而键名行消失，解析器（json.load）将报结构错误。
- 损坏特征高度特定：恰在 oldString 起止边界处缺一行，块内其余内容完好——与"手误删除大段"形态可区分。

## Essence

edit 是文本级替换：oldString 的起止边界若跨 JSON 对象/数组块（从一块的尾部延续到相邻块的键名行），newString 必须**逐字重建边界行**，漏一个 `"key": {` 行即结构损坏且零告警。状态文件高频小步修订时，"每轮改后 JSON 语法验证"是零成本的兜底防线；错误回执不会替你发现语义层损坏。

## Approach

1. **收缩 oldString 至单块内部**：oldString 尽量只覆盖一个 JSON 块（或一个完整键值对），不跨相邻键块边界；确需跨块时，newString 显式保留两块的边界行（含 `"stage_X": {` 键名行原样复制）。
2. **大范围改写优先整体 write**：批量推进多个 stage、清空大字段（如 update_plan）时，优先读全文件后整体 write 重建，保留 module_tree 等大结构原样——一次性重建比 N 次跨块 edit 更不易吞边界。
3. **每轮改后立即验证**：edit/write 落盘后立刻跑一次 `python -c "import json; json.load(open('<文件>', encoding='utf-8'))"`（或等价 JSON 解析），回执 success ≠ 结构无损。
4. **损坏后的修复闭环**：读回文件定位缺失的键名行 → edit 补回该行（oldString 取损坏处上下文）→ 再次 json.load 验证 → 再推进后续编辑。

## Faster Next Time

- 判定表：edit 回执 success 但后续 parse 报错 → 先查 oldString 起止边界处是否有行被吞；连续多轮 edit 后统一验证 → 错误定位成本倍增，改为每轮即验。
- 快捷信号：多块状态文件（stages/checkpoints/phases 命名族）+ 跨块 oldString = 高危组合，动笔前先确认边界行归属。
- ROI：每轮 1 条验证命令（秒级）；漏检的代价是状态文件不可解析、流程后续阶段全部建立在损坏基线上，修复需回溯多轮 diff。
- 反模式：凭 edit success 回执断定 JSON 完好；为图省事把 oldString 写成跨块大段再手工重拼；损坏后不验证直接继续下一轮 edit（错误叠加）。

## Applicability Boundaries

- 适用：JSON/YAML 等结构化状态文件的小步 edit 维护（progress/state/ledger 类）；任何"文本替换工具 + 语法敏感格式"组合。
- 不适用：纯 Markdown 正文编辑（无语法边界，吞行最多丢一句，损失可见）；已有整体 write 基建的批量重建场景（直接走 write，无跨块风险）。
- 与相邻经验分工：2026-11-06-edit-conflict-reread-then-reapply 处理「mtime 冲突后重读重放」，2026-11-07-edit-read-prerequisite-grep-not-counted 处理「已读基线判定」——两者都是**执行被拒**场景；本条是**执行成功但语义损坏**场景，三者互不覆盖。

## Evidence or Examples

- 源会话 ses_e488e3ea4ffeibxmS5KxTmxPRl（docgen-apply fork #1，Date 项目 progress.json 阶段推进）。
- 损坏实证：一处标记 stage_3/stage_4 状态的 edit 后，读回文件发现第 41 行缺 `"stage_4": {` 键名行（oldString 跨块导致），执行代理自述"刚才的 edit 误删了该行，会破坏 JSON 结构"。
- 修复实证：edit 补回 `"stage_4": {` 并顺带补齐 stage_2_5/stage_5 状态后，`python -c "json.load"` 验证输出 `progress.json JSON valid`；后续阶段 6 build_index 在合法基线上执行成功。