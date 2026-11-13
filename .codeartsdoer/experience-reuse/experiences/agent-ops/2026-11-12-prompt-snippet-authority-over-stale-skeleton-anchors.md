---
id: 2026-11-12-prompt-snippet-authority-over-stale-skeleton-anchors
title: 派工修订 code_refs 行号权威源裁决：骨架锚点对本轮变更文件失真时以内嵌源码片段为准
category: agent-ops
nature: decision
created_at: 2026-11-12T07:23:11
updated_at: 2026-11-12T07:23:11
tags: [code_refs, 符号骨架, 行号权威, 内嵌片段, 派工契约]
keywords: [骨架行号失真, 内嵌源码片段, 行号权威源优先级, code_refs 取证, 新增文件锚点缺失, 派工单声明, patch JSON, wiki修订, 骨架滞后, 预判式派工]
problem_patterns:
  - 扫描生成的符号骨架对本轮新增/变更文件的行号锚点缺失或过期，subagent 误把骨架当行号权威导致 code_refs 引用错位并随合并固化
  - 骨架行号与派工单内嵌源码片段直接冲突（片段声明 102 行文件在骨架中出现 400+ 行号锚点）时不知采信哪一方，反复 grep 交叉求证浪费轮次
  - 派工方未显式声明行号权威源时，下游在骨架与片段之间摇摆或直接弃用其一造成漏引/错引
source_sessions: [ses_e37ceb8ddffelsPgmc3sRydf5P]
project: Date
severity: medium
quality_score: 87
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-11-code-refs-evidence-line-over-default-line, 2026-11-08-wiki-section-tiered-revision-judgment-contract, 2026-11-09-subagent-patch-code-refs-baseline-fallback, 2026-11-11-subagent-wiki-patch-code-refs-read-verify, 2026-11-08-target-path-absent-inline-content-authority]
---

# 派工修订 code_refs 行号权威源裁决：骨架锚点对本轮变更文件失真时以内嵌源码片段为准

## Scenario

以只读 subagent 身份承接源码变更驱动的 Wiki 小节级修订派工（patch JSON 载体，修订者禁写文件）。变更源为本轮新增的 Python 源码文件（评估维度常量配置文件、验收驱动脚本），派工单提供：变更文件源码片段（含行号注释）、受影响小节当前内容、符号骨架文件路径（声明"由源码扫描生成"）、逐节判定指引与字数粒度约束。code_refs 行号存在两个候选权威源：扫描生成的骨架文件与派工单内嵌源码片段，两者对本轮新增文件并不一致。修订者独立执行、无法中途确认。

## Key Signals

- 失真信号：派工片段明确某文件全文 102 行，骨架文件中该文件名下的符号锚点却出现行号 400+（如 TestStore:400、TestGates:327）——骨架行号与真实文件规模直接矛盾，属骨架扫描滞后或锚点错位。
- 缺失信号：另一新增文件在多轮骨架 grep 结果中均查无符号锚点节——骨架根本未覆盖该文件。
- 契约信号：派工单显式声明"该骨架由源码扫描生成，XX 文件的行号以本 prompt 中给出的源码片段为准"——上游已预裁决权威源，下游只需验证并采纳。
- 片段自带行号注释（如 `EMBEDDED_DIMENSIONS = (...)  # 第 6 行`），行号可直接取证，无需再读源文件。

## Essence

符号骨架由扫描预生成、天然滞后于本轮变更，**对本轮新增/变更文件不可作为行号权威**。code_refs 行号的权威源优先级：**派工单内嵌源码片段（含行号注释）＞ 扫描骨架 ＞ 待修订文档旧引用**。骨架对既有未变更文件的锚点仍然有效——裁决是"按文件分源"而非全盘弃用骨架。派工方应在骨架不可靠时于派工单显式声明该裁决（预判式派工）；下游遇到骨架与片段冲突时以片段为准直接产出，不为求证骨架反复 grep，更不因矛盾中止任务。

## Approach

1. **派工方侧**：骨架生成先于变更落盘或未覆盖新增文件时，在派工单中显式声明"XX 文件行号以内嵌源码片段为准"，并在片段关键行附行号注释（`# 第 N 行`），让行号免实读即可取证。
2. **subagent 侧抽查**：动笔前对可疑文件做一次骨架-片段一致性比对——片段声明的文件行数与骨架锚点最大行号相矛盾（102 行 vs 400+）即判定骨架对该文件失真。
3. **分源取证**：本轮新增/变更文件的行号一律抄自片段行号注释；职责定位类条目取 `:1` 或片段声明的主旨行；既有未变更文件的符号定位沿用骨架/原索引锚点。
4. **冲突裁决**：派工单已声明权威源 → 验证后采纳，不再交叉求证；未声明且骨架与片段冲突 → 以片段（变更后实文）为准，并在交付消息注明裁决依据，禁止把矛盾留进 code_refs。
5. **产出核验**：code_refs 交付为"既有仍有效引用 + 新增引用"的合并完整列表，新增引用行号与片段注释一一对应可溯源。

## Faster Next Time

- 一行规则：本轮新增/变更文件的行号 → 内嵌片段；既有未变更文件的符号定位 → 骨架。
- 快捷检测：片段声明行数与骨架锚点最大行号矛盾 → 骨架对该文件失真，立即弃用其行号，不再 grep 求证。
- ROI：省去在两个来源间反复交叉 grep 的轮次；避免骨架过期行号进入 code_refs 后随合并固化到索引——错误引用比缺引用返工成本高一个数量级。
- 反模式：把骨架当恒权威、对新增文件照抄骨架行号；发现骨架矛盾后中止任务或上报阻塞（正确动作是切换权威源继续）；为"验证骨架"对同一文件发起多轮 grep。

## Applicability Boundaries

- 适用：源码变更驱动的 Wiki/知识库小节修订派工（patch JSON + code_refs 契约），骨架文件由源码扫描预生成、变更文件含新增/改写的场景；判定预判式派工（上游声明权威源）与未声明场景（下游按片段实读裁决）。
- 不适用：纯文档变更（无代码符号，走"第 N 条 = 行 N"锚点，见 tiered-revision-judgment-contract）；骨架与本轮变更同步重扫且抽查一致的场景（骨架可直接用）；清单型小节同一文件内取证行选择（见 evidence-line-over-default-line）；line_number_only 引用集基线回退（编排者侧，见 baseline-fallback）。
- 与相邻经验分工：tiered-revision 管"骨架为空时的纯文档行号锚点"，本条管"骨架存在但对本轮变更文件失真时的权威源切换"；evidence-line 管实读可得前提下同一文件内的取证行选择，本条管跨来源（骨架 vs 片段）的权威裁决；baseline-fallback 管消费端对引用集的回退校验，本条是生产端取证视角；target-path-absent 管"目标路径失配以内嵌内容为权威降级继续"，本条把同一降级思想落到行号维度。
- 证据等级：单次实战闭环（骨架 400+ 行号锚点与片段 102 行声明的矛盾被 trace 直接记录；subagent 采纳片段行号完成 patch，两节 replace_content + 合并 code_refs）——骨架失真实证充分；"上游未声明时下游自行裁决"分支为推断补全，待同类任务复用检验。

## Evidence or Examples

- 源会话 ses_e37ceb8ddffelsPgmc3sRydf5P（@general 修订 subagent，codebase-knowledge/工作流底座（workflow_base）.md 架构设计 + 配置与命令两小节，变更源为 eval_dims.py/verify_base.py 实质新增）。
- 失真实证：派工片段声明 `tests/verify_base.py` 全文 102 行；骨架文件 software_src.txt 中该文件名下锚点却为 TestReceipts:185、TestEnvironment:226、TestGates:327、TestStore:400 等——行号远超文件实际规模。
- 缺失实证：`adapters/eval_dims.py` 在两轮骨架 grep 结果中均无符号锚点节。
- 契约声明原文："本模块符号骨架……可自行读取；注意该骨架由源码扫描生成，eval_dims.py 与 verify_base.py 的行号以本 prompt 中给出的源码片段为准"。
- 采纳实证：patch 的 code_refs 采用片段行号（`workflow_base/adapters/eval_dims.py:1`、`tests/verify_base.py:1`），既有未变更文件引用保留原行号，code_refs 为合并完整列表；两小节均 replace_content 且遵守粒度约束（常量名列表未罗列、验收命令仅追加一条）。