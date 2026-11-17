---
id: 2026-11-15-subagent-dual-patch-line-anchor-divergence-resolution
title: 并行 subagent 双 patch 对同一文件行号锚点分歧：分歧≠错误，合并前实测消解并保留各自有效锚点
category: workflow
nature: technique
created_at: 2026-11-15T20:27:53
updated_at: 2026-11-15T20:27:53
tags: [subagent派工, patch合并, code-refs, 行号锚点, 分歧消解]
keywords: [行号分歧, 双 patch, 语义锚点, line_number_only, 合并前验证, 并行派工, 实测优先, 有效锚点并存, 误判重派, 引用面收窄]
problem_patterns:
  - "并行派工两个 subagent 修订不同文档、各自对同一变更文件补 code_refs，合并时发现同一引用行号不一致（:11 vs :12），直觉判'必有一方错误'，引发不必要的怀疑与重派冲动"
  - "把行号分歧误当字段漂移或幻觉处理，强行'统一'成单一行号，静默丢弃另一端的有效语义锚点，引用面无谓收窄"
source_sessions: [ses_e20f0f623ffeRnF5320fpM4rXv]
project: Date
severity: low
quality_score: 83
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: A
related_experiences: [2026-11-13-code-refs-range-line-number-validation-reject, 2026-11-13-merge-code-refs-replace-semantics-union-guard, 2026-11-08-subagent-patch-field-drift-silent-content-loss, 2026-11-11-wiki-verbatim-consistency-line-number-only]
---

# 并行 subagent 双 patch 对同一文件行号锚点分歧：分歧≠错误，合并前实测消解并保留各自有效锚点

## Scenario

Wiki 增量更新流水线并行派工两个 subagent（Stage 3 模块文档 + Stage 4 规范文档，正交修订不同 .md），两者均以 line_number_only 动作给小节补 code_refs，且各自引用了同一个变更文件（配置文件）。合并前核对 patch JSON 时发现：同一文件、同一用途（部署路由 rewrite 声明）的引用，patch A 写 `:12`、patch B 写 `:11`——两个数字不相等。编排者须在合并前决定：相信哪一方，还是另作处理。

## Key Signals

- 分歧指纹：两份 patch 的 code_refs 指向同一文件（vercel.json），行号仅差 1 且集中于同一段声明（rewrites 块）；其余引用（如另一文件 api/index.py 的 `:15/18/33`）完全一致。
- 触发直觉的诱因：行号不一致通常被当作"幻觉/字段漂移"信号（相邻经验中的 drift 形态），此处外观相似但性质不同。
- 判别关键：源文件该声明块是**多字段结构**（`source` 在行 11、`destination` 在行 12），两个行号各自锚定同一段落的相邻字段，均为真实相关内容。

## Essence

行号锚点的唯一性假设不成立：同一条声明内的不同字段行都是该声明的合法锚点，两个 subagent 各自抓了不同字段行，产生"分歧"但不产生"错误"。分歧的正确消解方式是**实测优先于仲裁**——读源文件验证每个行号指向的内容是否与文档断言相关；全部有效则各自保留（行号归属各 patch 所在小节，合并时互不覆盖），仅当某行号指向无关内容才判错修正。校验器（validate_code_links）只验证文件存在与行号在界内，不验证语义相关性，因此语义层正确性只能靠合并前的实测把关。

## Approach

1. **收集分歧项**：合并前对两份 patch 的 code_refs 做交集比对，列出同文件不同行号的项（不必全文比对，只看新增引用）。
2. **逐项实测**：对每个分歧行号读源文件对应行，确认内容与文档断言的关联性（本例：行 11=`source` 路由、行 12=`destination` 转发目标，均指向 rewrite 声明）。
3. **分流处置**：全部有效 → 双双保留，不做跨 patch 统一；某行号无效 → 仅修正该 patch 的该项（本地 edit patch JSON），不升级重派。
4. **合并后复验**：merge 后 validate_code_links 确认通过（本例 2/2），并在修订报告中注明行号分歧消解依据，留痕供复盘。

## Faster Next Time

- 一行判据：同一文件**行号差在声明块字段间距内**（±1~3 行）→ 优先怀疑"多字段锚点"而非幻觉，直接实测；差得多（>5 行或跨块）→ 才按错误处理。
- ROI：实测消解 1 分钟内完成，避免两条歧路——怀疑错误走重派（一轮派工+等待）或强行统一（丢弃有效锚点、引用面收窄且留下"谁对谁错"的假问题）。
- 反模式：见行号不一致即判一方幻觉并要求重派；不读源文件就"取平均/取多数"统一行号；把本形态与 patch 字段漂移（content≠new_content 类，见相邻经验）混为一谈——漂移是结构事故需防丢内容，本形态只是锚点多元性。

## Applicability Boundaries

- 适用：并行派工多个 subagent 各自产出 line_number_only 型 patch（仅补 code_refs、正文不动）、且引用面存在交集的合并场景；一般化到任何"多来源对同一目标各自标注行号锚点后合并"的流程。
- 不适用：replace_content 型 patch（行号错位会连带正文上下文核对，需更严格处理）；单 subagent 单 patch（无分歧面）；行号由脚本机械生成且契约统一锚定字段（无多元性空间）的场景。
- 与相邻经验分工：2026-11-13-code-refs-range-line-number-validation-reject 管校验器格式契约与失败分流（validate 侧），本条管合并前的语义分歧消解（merge 前侧）；2026-11-13-merge-code-refs-replace-semantics-union-guard 管 merge 的并集保护语义（合并行为），本条管合并前对分歧项的判定输入；2026-11-08-subagent-patch-field-drift-silent-content-loss 管字段漂移结构事故（防丢内容），与本条的锚点多元性（非事故）根因不同、处置不同。

## Evidence or Examples

- 源会话 ses_e20f0f623ffeRnF5320fpM4rXv（docgen-apply，Date 项目 wiki 增量更新 version_token 36 轮）。
- 分歧实录：patch A（codebase-knowledge/P003演练适配器.md/配置与命令）code_refs 含 `vercel.json:5` 与 `vercel.json:12`；patch B（project-knowledge/build_system/build_system.md 两小节）含 `vercel.json:5` 与 `vercel.json:11`；`api/index.py:15/18/33` 两 patch 完全一致。
- 实测消解实录：read vercel.json（15 行）确认行 5=`src` 声明（两 patch 一致）、行 11=`source`、行 12=`destination`——均为 rewrites 路由声明的有效字段锚点，判定两行号并存正确，合并时各自保留。
- 闭环佐证：merge 后 validate_code_links 2/2 passed；build_index 后索引中 vercel.json 共 6 处引用落地（P003 文档 2 处 + build_system 4 处，行号 11 与 12 均在索引中存活）；uniq_paths 增量=2 与 R=2 对账一致。
- 证据等级：单次成功闭环；"±1~3 行怀疑多字段锚点"的行差阈值是本例归纳的启发式，待复用检验。