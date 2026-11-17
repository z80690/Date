---
id: 2026-11-15-edit-asymmetric-replacement-drops-json-closing-structure
title: Edit 工具替换范围结构不对称会静默漏删 JSON 闭合层：oldString/newString 层级配对对称 + 改完必 json.load 验证
category: debugging
nature: pitfall
created_at: 2026-11-15T20:19:23
updated_at: 2026-11-16T00:01:54
tags: [Edit工具, JSON结构损坏, 状态文件编辑, 静默失败, 结构对称性]
keywords: [JSONDecodeError, oldString, newString, 漏闭合, 闭合结构, progress.json, Edit 工具, 结构对称, json.load 验证, 状态文件编辑]
problem_patterns:
  - "对嵌套 JSON 状态文件做局部 edit：oldString 覆盖到外层闭合结构而 newString 只写到内层闭合，替换成功但结尾闭合层被静默删掉，下次解析才爆发 JSONDecodeError"
  - "Edit 返回 success 就认定 JSON 仍合法，未做结构校验，事故潜伏到流程后续阶段才暴露"
  - "报错提示 Expecting ',' delimiter 被误读为标点笔误，逐字符全文扫描找逗号，实际根因是结构层级缺失"
source_sessions: [ses_e20e3529dffeTnb2pIjC6FE8dB]
project: Date
severity: medium
quality_score: 91
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-11-programmatic-atomic-json-state-rewrite, 2026-11-14-wiki-update-plan-clear-vs-crossround-prior-note-token, 2026-11-14-edit-trailing-newline-false-success-byte-patch, 2026-11-15-wiki-interrupted-before-build-index-crossround-recovery]
---

# Edit 工具替换范围结构不对称会静默漏删 JSON 闭合层：oldString/newString 层级配对对称 + 改完必 json.load 验证

## Scenario

Agent 用 Edit/替换类工具对结构化状态文件（含 stages 嵌套对象的 progress.json 类文件）做多处局部更新（状态翻转、键值改写）。一次编辑把某 stage 块从 pending 改为 completed：oldString 的选取范围包到了该块的**外层闭合结构**（内部数组 `]` + 对象 `}`），而 newString 只写到了**内部数组闭合** `],` 就结束。Edit 本身成功返回——oldString 精确匹配且被完整替换——没有任何即时报错，结构损坏静默潜伏，直到下一次 json.load 验证时才爆发。

## Key Signals

- **最早可信信号**：`json.decoder.JSONDecodeError: Expecting ',' delimiter: line 211 column 2`，报错位置在文件尾部闭合结构应在的区域——第一结构断点通常在漏闭合处或其后的闭合收敛点。
- **误导线索**：报错字面提示"缺少分隔符"，容易误判为逗号笔误而逐字符扫描全文找标点；真正根因是**少了一层闭合结构**，与标点无关。行号列号是入口，不是病灶本身。
- **静默期特征**：Edit 工具的成功返回只保证"精确替换已发生"，不校验替换后文件的整体结构合法性；成功 ≠ 结构未损。

## Essence

完整因果链：oldString/newString 是**范围替换**而非"内容补丁"——newString 整体替换 oldString 覆盖的字节范围。当两者覆盖的结构层级不对称（oldString 包到外层闭合、newString 止于内层闭合），处于替换范围内但未在 newString 中重现的闭合结构就被删除，文件在字节层面依然合法（无悬空字符），但在结构层面缺了一层闭合，解析时以"期望分隔符"类错误爆发。根因在**编辑范围的选择**，不在 JSON 内容本身——所以修复手段是补结构，预防手段是约束范围选择。

## Approach

1. **报错行即入口**：JSONDecodeError 的行号+列号直接指向第一个结构断点附近，read 该区域前后约 20 行，不要全文扫描。
2. **数闭合层级**：对照报错行附近的闭合符号（`}`/`]`）与该位置的应有嵌套层级，找出"少一层"的位置（本例：stage_4 数组闭合后直接跟下一个 stage 块，缺一层 `}`）。
3. **最小块补编辑**：只针对缺失的闭合做一次最小 edit（在数组闭合后补上 `}`），不重写整块、不动相邻键。
4. **改完必验证**：每次结构编辑后立即 `python -c "import json; json.load(open(<file>, encoding='utf-8'))"` 验证；多编辑批次流程中每个批次收尾都要验证一次，不攒到最后。
5. **预防规则（发出编辑前）**：oldString 与 newString 的起止结构层级必须**配对对称**——oldString 包含几层闭合，newString 就必须原样包含几层；拿不准时把范围缩小到"单键值对"层级，或在 oldString 显式包含结尾闭合并在 newString 中逐层保留。

## Faster Next Time

- 一行检查：发出 edit 前数一遍 oldString 尾部与 newString 尾部的闭合符号数，`}`/`]` 计数不相等即重写编辑范围再提交。
- 最短排查路径：报错行号 → read 附近区域 → 数闭合层级 → 一次最小补编辑 → json.load 验证，四步内解决；禁全文逐字符找逗号。
- 超长 JSON 块（如 update_plan 整体清空类改写）不走 edit，改用独立 Python 脚本原子完成（见 2026-11-11-programmatic-atomic-json-state-rewrite）。
- 反模式：Edit success 即认定 JSON 合法；见"缺分隔符"就逐字符找标点；对大块嵌套结构改写且改后不验证。

## Applicability Boundaries

- 适用：Edit/替换类工具对 JSON/YAML/TOML 等结构化文件的局部编辑；含嵌套 stages/数组的状态文件；"多次小粒度编辑"流水（本例 8+ 次编辑中一次失手即足以瘫痪流程）。
- 不适用：无结构的纯文本；整文件 write 全量重写（无范围替换概念，但须自行保证内容完整）；程序化改写（Python json.load→改→dump 天然免疫本形态）。
- 与相邻经验分工：2026-11-14-wiki-update-plan-clear-vs-crossround-prior-note-token 记录了第一形态（**跨 stage 块边界**编辑吞相邻键名）与"最小块逐键替换"的预防，并实证过 8 次小粒度 edit 零事故；本条记录第二形态——**单块内部范围不对称漏闭合**，小粒度不能免疫，须叠加"层级配对对称 + 改后 json.load 验证"纪律。两形态根因不同（跨界吞键 vs 范围不对称），预防规则互补。2026-11-11-programmatic-atomic-json-state-rewrite 是超长块的原子改写降级通道。2026-11-15-wiki-interrupted-before-build-index-crossround-recovery 是本事故所在同一会话的跨轮恢复链记录——本条事故正发生在该恢复轮的多处状态翻转编辑中，恢复轮的高频状态文件编辑构成叠加风险面。

## Evidence or Examples

- 源会话 ses_e20e3529dffeTnb2pIjC6FE8dB（docgen-apply fork #1，Date 项目 wiki 增量更新 version_token 36 轮，progress.json 多处状态翻转流程中）。
- 事故实录：stage_4 块 pending→completed 的编辑中，oldString 包含内部数组闭合与外层 `"status": "pending"` 及块级 `}` 的完整结尾，newString 止于数组闭合 `],`，漏掉外层闭合；同轮后续验证报 `JSONDecodeError: Expecting ',' delimiter: line 211 column 2 (char 9589)`。
- 定位与修复实录：read 193-211 行确认 stage_4 数组闭合后直接衔接 stage_5（缺一层 `}`）→ 一次最小 edit 补闭合 → json.load 通过（stage_3 9 篇 / stage_4 6 篇 / pending 全空）。
- 对照佐证：上一轮（token 557）8 次小粒度 edit 零事故（见相邻经验）——本轮证明小粒度非充分条件，对称性检查与改后验证才是可迁移的关键纪律。