---
id: 2026-11-08-subagent-patch-field-drift-silent-content-loss
title: LLM subagent 结构化输出的字段名/字符形态漂移：消费端脚本严格按字段名读取，漂移即静默丢失——合并前必须做字段归一校验
category: agent-ops
nature: pitfall
created_at: 2026-11-08T03:26:16
updated_at: 2026-11-08T03:33:09
tags: [subagent交付, 字段漂移, 静默失败, 结构化输出, 合并校验]
keywords: [content vs new_content, 字段名漂移, 弯引号, 直引号, merge_section_patch, 静默降级, line_number_only, patch JSON, 字段归一, merged_sections 核对]
problem_patterns:
  - 并行派工多个 subagent 各自返回结构化 JSON，部分 subagent 用近义字段名（content）替代契约字段名（new_content），消费端脚本读不到正文却不报错
  - merge 类脚本对缺失字段的降级是静默的（replace_content 退化为 line_number_only），输出仍 success，修订正文无声丢失且无人察觉
  - subagent 产出的正文中直引号被漂移为弯引号（"→""），含路径/代码语境的文本被污染，人工逐字校验成本高
source_sessions: [ses_e488e3ea4ffeibxmS5KxTmxPRl]
project: Date
severity: medium
quality_score: 93
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-08-wiki-update-script-behavior-contract-blindspots, 2026-11-08-wiki-section-revision-patch-json-mode, 2026-11-07-subagent-delivery-spot-check-acceptance]
---

# LLM subagent 结构化输出的字段名/字符形态漂移：合并前必须做字段归一校验

## Scenario

编排者并行派 4 个修订 subagent，各自返回小节级 patch JSON（契约字段：`section_title` / `action` / `new_content` / `code_refs`），随后用确定性脚本 merge_section_patch.py 统一合并回 Wiki 文档。4 个 subagent 独立会话、同一段 prompt 契约，产出由脚本严格按字段名消费。

## Key Signals

- 4 个 subagent 中 **2 个**返回的 patch 对象用 `content` 字段承载正文，而非契约要求的 `new_content`——同一 prompt 下字段名仍发生漂移，契约遵守率仅 50%。
- 消费端脚本源码只认 `new_content`（`if action == "replace_content" and p.get("new_content")` 才做正文替换）：字段缺失时 **不报错**，该小节按 line_number_only 处理，merge 输出仍是 success——修订正文无声丢失。
- 另一处漂移：patch 正文中直引号被写成弯引号（`"..."` → `"..."`），原文语境（引用源码/路径措辞）被污染。
- 决定性证据链：merge 的 success + `merged_sections` 列表 ≠ 内容已替换，必须对照预期 action 清单核对 replace 数量。

## Essence

LLM subagent 的结构化输出存在两类系统性漂移：**字段名漂移**（近义命名替代契约命名）与**字符形态漂移**（直引号→弯引号等）。确定性消费脚本按严格字段名/字符语义读取，漂移等价于字段缺失，而脚本的容错路径是静默降级而非报错——"LLM 产出 + 脚本消费"链路的最大风险不是执行失败，而是**成功回执下的内容丢失**。编排者必须在合并前做一次字段归一校验，不能信任 subagent 对 prompt 契约的自觉遵守。

## Approach

1. **合并前逐 patch 校验字段集**：核对每个 patch 对象具备 `section_title`/`action`/`new_content`/`code_refs` 四要素；`action=replace_content` 而 `new_content` 缺失/为 null → 判定漂移。
2. **字段名归一**：`content` → `new_content` 统一改写后再落盘；归一动作由编排者用写文件工具完成（保存为 UTF-8 无 BOM 的 patch 文件），不要求 subagent 返工。
3. **字符形态归一**：扫描正文中的弯引号（""''）、全角标点，凡处于源码/路径/键名语境的一律恢复直引号半角。
4. **落盘后喂脚本**：修正后的 patch 写入固定临时目录，合并脚本从文件读取；不把 subagent 返回消息直接粘给脚本（防长 JSON 截断与二次漂移）。
5. **merge 后数量核对**：对照预期 action 清单核对输出 `merged_sections` 中 replace 类小节数量——replace 数 < 预期数即为漂移残留信号，回头查字段名。

## Faster Next Time

- 判定表：merge success 但 replace 小节数 < 预期 → 先查字段名漂移（content vs new_content）；merge success 但某小节内容未变 → 查该 patch 的 action/new_content 组合；正文出现非预期弯引号 → 全文扫描字符形态漂移。
- 快捷校验：一条 grep/读文件即可完成——检索 patch 文件中 `"content"` 与 `"new_content"` 的出现次数差，即漂移数量。
- ROI：归一校验约 1 轮工具调用；漏检的代价是修订正文静默丢失且在下游校验（validate/lint 均不查内容替换）中不可见，直到人工比对文档才发现，返工成本高一个数量级。
- 反模式：把 subagent 返回原文直接传给合并脚本；只看 merge 的 status=success 不核对 merged_sections 构成；假定"同一 prompt 下所有 subagent 输出契约一致"。

## Applicability Boundaries

- 适用：一切"LLM 产出结构化 JSON + 确定性脚本消费"的编排链路（patch 合并、流水线产物、批量配置生成）；并行派工多 subagent 时校验必要性随数量上升。
- 不适用：单 Agent 直读直改场景（无结构化契约可漂移）；subagent 产物仅供人读、无脚本消费的场景（漂移降级为质量问题而非静默丢失）。
- 平台边界：实证于 CodeArts Agent 的 Task 工具派工 + system skill 脚本链；漂移倾向是 LLM 输出的通用行为，字段归一校验对任意平台同构适用。

## Evidence or Examples

- 源会话 ses_e488e3ea4ffeibxmS5KxTmxPRl（docgen-apply fork #1，Date 项目 Wiki 增量更新，4 个修订 subagent 并行）。
- 漂移实证：collaboration_conventions 与 business_glossary 两个 subagent 的 patch 用 `"content"` 字段（规范为 `"new_content"`），官方文档与协作规范的 subagent 输出中"技能使用—技能编写—团队协作"处直引号被写成弯引号。
- 脚本契约实证：merge_section_patch.py 第 188-189 行 `if action == "replace_content" and p.get("new_content"): content = p["new_content"]`——字段缺失即跳过正文替换，无告警。
- 归一实证：编排者保存 4 份修正后 patch 文件（统一字段名、恢复直引号）后执行合并，4 篇文档 `merged_sections` 全部符合预期且 hash 刷新，下游 validate/lint 全绿。