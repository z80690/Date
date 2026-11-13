---
id: 2026-11-09-subagent-patch-code-refs-baseline-fallback
title: line_number_only patch 的 code_refs 以检索基线为原值：subagent 越界扩充的未实读引用一律裁剪回退，扩充须逐一实读核实后才可保留
category: agent-ops
nature: pitfall
created_at: 2026-11-09T02:05:58
updated_at: 2026-11-09T02:16:06
tags: [subagent交付, code_refs, 基线回退, 过度覆盖, patch校验]
keywords: [code_refs 扩充, 未实读引用, wiki-index 原值, 基线回退, line_number_only, 最小修订, 引用集越界, 溯源链污染, patch JSON, 编排者校验, 过度覆盖倾向]
problem_patterns:
  - 只读修订 subagent 返回 line_number_only patch 时主动扩充 code_refs 引用集（原 2 条扩为 4 条），新增引用未经实读核实，编排者不知该接受还是回退
  - 把 subagent"引用做得更完整"当作增益直接采纳，未核实引用进入 code_refs 溯源链并被索引固化传播
  - 不清楚 line_number_only 场景下引用集的权威基线是什么，误以 subagent 返回值为准
source_sessions: [ses_e4405534affeu8pLGAbuG7Iwh9]
project: Date
severity: medium
quality_score: 88
hit_count: 5
last_hit_at: 2026-11-13T13:03:01
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-08-subagent-patch-field-drift-silent-content-loss, 2026-11-09-glossary-status-refresh-zero-revision-criterion, 2026-11-09-wiki-hash-shortcut-requires-merge-pass, 2026-11-08-wiki-section-revision-patch-json-mode]
---

# line_number_only patch 的 code_refs 以检索基线为原值：subagent 越界扩充的未实读引用一律裁剪回退，扩充须逐一实读核实后才可保留

## Scenario

编排者并行派只读修订 subagent 产出 Wiki 小节级 patch JSON（契约：`section_title`/`action`/`new_content`/`code_refs`）。某 subagent 对判定为 line_number_only 的小节，除按派工单核对既有引用行号外，还主动把 code_refs 从检索基线的原值集合扩充了 2 条（新增指向其他笔记文件的 `:3` 行引用），随后由主 Agent 校验后交合并脚本消费。

## Key Signals

- subagent 返回的概述小节 code_refs 为 4 条，而检索基线（wiki-index 现值）为更少的原值集合——扩充项是 subagent 自行添加的，派工单未要求引用集重构。
- line_number_only 的职责边界是"核对既有行号仍准确"，不含"补充新引用"；扩充项无实读证据支撑。
- 对照正例：同批次另一 replace_content 小节新增的 2 条引用（源文件的具体行号）经实读核实后保留，并在合并输出 `hashes_updated` 中出现——新增本身合规，缺的是实读核实这一步。

## Essence

LLM subagent 存在"把引用做完整"的**过度覆盖倾向**：在只要求行号核对的场景里主动扩充引用集。code_refs 是可溯源纪律的载体，其权威基线是检索基线的现值（wiki-index 原值），不是 subagent 的返回值。未实读的扩充引用一旦被接受，会污染该小节的溯源链、随合并进入索引并固化传播——错误引用比缺引用危害更大。判定规则：**line_number_only 场景以基线原值为基线，行号实读无误即维持原值；任何扩充项必须逐一实读核实，无实读证据一律裁剪回退**。这与字段名漂移（`content` vs `new_content`）同属"编排者不信任 subagent 自觉遵守契约"的校验主题，但漂移对象从字段形态扩展到了引用集内容。

## Approach

1. **逐条对照基线**：收到 patch 后把 code_refs 与检索基线（wiki-index 现值）逐条比对，多出的条目即扩充项。
2. **扩充项逐一实读核实**：对每条扩充引用实读源文件确认行号指向所述内容；有实读证据且语义正确的保留，无实读证据的裁剪。
3. **line_number_only 场景从严格**：即使扩充项行号看似合理（如 `:3` 导语行），未实读即回退——该场景的产出应当是"基线原值 + 核对确认"，最小修订。
4. **replace_content 场景新增引用必须伴随实读**：正文改写带来的新引用允许进入，但派工或校验时要求 subagent/编排者给出实读核实记录；合并输出 `hashes_updated` 可反查最终引用集合是否与预期一致。
5. **合并后反查**：merge 输出的 `hashes_updated` 只应覆盖预期引用的源文件；出现基线之外的文件即扩充项残留信号。

## Faster Next Time

- 判定口诀：line_number_only → 基线原值，扩充即裁；replace_content → 扩充可留，实读为证。
- 快捷校验：对比 patch 的 code_refs 条数与基线条数，条数差即需裁决的扩充项数量。
- ROI：一轮对照 + 至多一轮实读即可完成裁决；漏检代价是错误引用随索引固化传播，下游检索时才暴露，返工成本高一个数量级。
- 反模式：把 subagent 扩充引用当"更完整"直接采纳；只校验字段名和引号形态不校验引用集构成；假定 subagent 不会在 line_number_only 里做引用集重构。

## Applicability Boundaries

- 适用：一切"LLM 产出结构化 patch + 消费端按引用集消费"的编排链路（Wiki 小节修订、代码引用索引、溯源标注类任务）；subagent 返回值与权威基线并存的场景。
- 不适用：subagent 产物仅供人读、无溯源链消费的场景（扩充降级为质量问题而非污染）；基线本身缺失或已过期的场景（须先刷新基线再校验）。
- 与相邻经验分工：`2026-11-08-subagent-patch-field-drift-silent-content-loss` 管字段名/字符形态漂移的字段归一校验，本条管引用集越界扩充的基线回退——两者构成编排者 patch 校验的两个互补面；`2026-11-09-glossary-status-refresh-zero-revision-criterion` 管 line_number_only 的零修订判据（subagent 侧视角），本条是编排者侧对同场景产出的引用集校验视角。
- 证据等级：单次实战闭环（1 处扩充回退 + 1 处实读扩充保留的对照）；"过度覆盖倾向"的普遍性基于本批次与既往漂移经验的归纳，复用中可继续检验。

## Evidence or Examples

- 源会话 ses_e4405534affeu8pLGAbuG7Iwh9（docgen-apply fork #1，Date 项目 Wiki 增量更新）。
- 回退实证：概述小节 subagent 返回 4 条 code_refs（含 2 条未实读扩充），主 Agent 判定后回退为基线原值；合并输出 `hashes_updated` 中该小节仅含原值集合对应的源文件，无扩充项残留。
- 保留实证：架构设计小节（replace_content）新增 `notes/项目事实表.md:22`（事件钩子）与 `:24`（维护机制 §9）两条引用为实读核实行号，合并后进入 `hashes_updated`，溯源链完整。
- 判定留痕：主 Agent 在合并前显式记录两处修正（"回退为 wiki-index 原有引用"与"new_content 字符串 null 修正为 JSON null"），裁决依据可审计。