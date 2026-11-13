---
id: 2026-11-11-patch-new-content-section-title-stripping
title: patch JSON 的 new_content 混入小节标题行须合并前剥离：合并器以原标题行重建标题、正文区不含标题
category: workflow
nature: pitfall
created_at: 2026-11-11T11:31:19
updated_at: 2026-11-11T11:31:19
tags: [patch契约, subagent交付校验, 标题行漂移, 小节合并, 交付前验证]
keywords: [replace_content, new_content, section_title, 标题行, category注释, merge, subagent patch, 漂移校验, 契约确认, 重复标题]
problem_patterns:
  - subagent 交付的 patch 中 new_content 自带 "## 标题 <!-- category:... -->" 行，合并后小节出现重复标题行
  - 主 Agent 直接采信 subagent 输出格式，未核对合并器对 new_content 的真实契约（替换标题行之后的正文区）即执行合并
  - 交付内容格式漂移无前置校验环节，错误要到合并产物或 lint 阶段才暴露，返工成本后置
source_sessions: [ses_e37c7267cffewyCyg5XHZYfAwm]
project: Date
severity: medium
quality_score: 90
hit_count: 7
last_hit_at: 2026-11-13T13:03:01
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-08-wiki-section-revision-patch-json-mode, 2026-11-11-replace-content-merge-integrity, 2026-11-11-wiki-verbatim-consistency-line-number-only]
---

# patch JSON 的 new_content 混入小节标题行须合并前剥离

## Scenario

主 Agent 并行派发多个 subagent 产出小节级 patch JSON（action=replace_content），由主 Agent 调用确定性合并脚本统一合并回 wiki 文档。合并器的隐含契约是：`section_title` 定位小节，`new_content` 只承载标题行之后的正文；文档重组时用解析原文保留的标题行（含 category 注释）重建标题。本例 3 个 subagent 中 2 个在 new_content 开头带上了 `## 架构设计 <!-- category:architecture_design -->` 标题行——若直接合并将产生重复标题。

## Key Signals

- 漂移信号：subagent 返回的 new_content 以 `## <小节标题> <!-- category:... -->` 开头，与 section_title 字段内容重复。
- 契约确认方法：在合并前用 grep/实读查看合并脚本源码，确认三点——①小节解析按 `^## ` 切分并从标题行提取 category 注释；②`new_content` 写回位置是标题行**之后**的正文区；③重组用 title_raw（原标题行）重建标题，不使用 new_content 内的任何标题文本。
- 出现率信号：同批次多个 subagent 独立产出时，格式漂移可复现（本例 3 个中 2 个）——不能假设"其中一个格式正确则全部正确"，须逐个校验。

## Essence

结构化交付物的字段语义以**消费方（合并脚本）的实现为准**，不以生产方（subagent）的输出惯性为准。new_content 的真实语义是"标题行之后的正文区"，标题行由 section_title 对应的原文重建——因此生产方混入标题行属于格式漂移，必须在合并前统一剥离。正确的工序是：合并前先读消费方源码确认契约 → 逐 patch 校验并剥离漂移 → 落盘修正后的 patch → 执行合并 → 以合并器输出（merged_sections/preserved_sections）验证。

## Approach

1. **合并前读消费方契约**：对将要执行合并的脚本，grep 关键实现（小节切分正则、new_content 写回位置、标题重建逻辑），把"new_content 是否应含标题行"的答案从源码确认，不靠猜测。
2. **逐 patch 格式校验**：检查每个 patch 的 new_content 开头是否混入 `##` 标题行（含 category 注释变体）；发现即把标题行从 new_content 中剥离，保留其后正文。
3. **落盘修正后统一合并**：把修正后的 patch JSON 写入临时文件，按 wiki 文档逐个执行合并；line_number_only 型 patch 的 new_content 保持 JSON null（非 "null" 字符串）。
4. **合并输出验证**：检查合并器返回的 merged_sections 是否覆盖预期小节、preserved_sections 是否符合预期（未派工修订的小节应保持 preserved），零异常即通过。
5. **临时产物清理**：patch 中间文件在合并验证通过后删除，仅保留文档与索引产物。

## Faster Next Time

- 一个前置检查点：拿到 subagent patch 先扫一眼 new_content 首行——以 `##` 开头即漂移，30 秒内完成全批校验。
- ROI：合并前剥离把返工点前移（合并产物错误需回滚文档并重合并，剥离只需改 patch 文件）；本例 2/3 patch 被前置修正，合并一次通过 5/5 小节。
- 反模式：直接合并 subagent 原始输出（赌其格式正确）；只校验 JSON 可解析不校验字段语义；发现重复标题后改合并脚本迁就漂移（消费方契约不应被生产方惯性带偏）。

## Applicability Boundaries

- 适用：任何"subagent 产出结构化 patch → 确定性脚本合并"的文档修订流水线；一般化到一切"生产方-消费方分离的结构化交付物"场景——字段语义必须以消费方实现为准。
- 不适用：subagent 被授权直接写文档（无 patch 合并环节）；new_content 契约明确要求含完整小节（含标题行）的合并器（以其实际契约为准，仍须源码确认）。
- 与相邻经验分工：wiki-section-revision-patch-json-mode 条管 patch 载体契约与口径逐字比对（写什么内容）；replace-content-merge-integrity 条管整节替换时原文保全的脚本提取与断言（内容完整性）；本条管 patch 结构本身的格式漂移校验（标题行剥离）——三者分别管内容口径、内容保全、结构格式。

## Evidence or Examples

- 源会话 ses_e37c7267cffewyCyg5XHZYfAwm（docgen-apply fork #1，Date 项目）：3 个 subagent 中 2 个（工作流底座、tooling_and_environment）的 new_content 混入标题行，1 个（business_glossary，line_number_only 型）格式正确。
- 契约确认实证：grep 合并脚本源码确认 `new_content` 直接替换标题行之后的正文、重组时 title_raw 重建标题行（注释明言 title_raw 是"去掉 category 注释后的标题行原文"），据此判定混入即重复。
- 修正实证：2 个 patch 剥离标题行后落盘执行合并，输出 merged_sections 覆盖全部派工小节（架构设计/配置与命令/关键文件与位置等 5/5）、preserved_sections 符合预期；后续 validate_code_links 3/3 passed、lint 0 error。