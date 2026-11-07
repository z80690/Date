---
id: 2026-11-07-long-design-doc-chunked-write-structure-verify
title: 长设计文档分块落盘与完工结构自检（write首块+edit追加+章节grep核验）
category: workflow
nature: technique
created_at: 2026-11-07T09:26:58
updated_at: 2026-11-07T09:31:32
tags: [sdd, design-stage, chunked-write, self-check, document-production]
keywords: [design.md, 分块写入, edit追加, 结构核验, 章节grep, 行数核验, 单次输出限制, 长文档, 完工自检, SDD流水线]
problem_patterns: ["数百行设计文档超出单次输出预算，一次性write被截断或被迫压缩内容", "分块写完后凭感觉交差，章节缺失或锚点断裂无人发现"]
source_sessions: [ses_e4cb3b6f5ffeItlrKDOwdybcjW]
project: Date
severity: medium
quality_score: 86
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-07-design-inferred-value-writeback-loop, 2026-11-06-design-stage-self-serve-evidence-decisions, 2026-11-07-sdd-spec-to-tasks-coverage-mapping]
---

# 长设计文档分块落盘与完工结构自检（write首块+edit追加+章节grep核验）

## Scenario

SDD 流水线 design 阶段：派工单要求产出覆盖 7 项实施模块的设计文档（预期 500+ 行，含需求对比分析/增量设计/验收标准三大章），执行方为隔离会话的子智能体（spec-design-agent）。单次输出预算无法承载全文一次性 write，而内容完整性优先于篇幅（用户已明令废除压缩上限），必须既写满又不截断。

## Key Signals

- 文档规模预估超过单次 write 安全预算（数百行级）——信号是派工单要求的章节清单展开后行数明显超限。
- 平台环境提示明确"先写完所有文件再运行验证、单轮批量写 3-5 个文件"——输出受限是环境常态而非偶发。
- 早期采用"逐块写→逐块读回验证"的试探路径；后续识别出 edit 失败自带报错，读回验证是冗余动作，改为"全部落盘后一次性结构核验"。

## Essence

长文档产出要把**内容生成**与**完整性验证**解耦：写入阶段按章节分块（write 建骨架+首章，后续 edit 以文末锚点逐块追加），每块控制在安全输出预算内且不在中途验证；全部落盘后用一次 bash 结构核验（行数+章节标题 grep 对照规划清单）把"感觉写完了"变成"结构可证明"，缺章即补。逐块读回验证是浪费——edit 工具在目标文本未命中时本身会报错，失败信号已内置。

## Approach

1. **写前分块规划**：列出章节清单（一/1.1/1.2/二/2.1/2.2/2.3/三…），按 1-2 章一块切分，估算每块行数确保低于输出预算；首块=文档骨架（标题+章目录）+第一章。
2. **write 建首块**：首块一次 write 落盘，文末预留清晰锚点（下一章标题行或结尾段）供 edit 定位。
3. **edit 逐块追加**：以文末锚点为 oldString 尾部，newString=锚点+新章节；每轮 edit 追加 1-2 章，失败会即时报错无需读回。
4. **完工统一自检**：一次 bash 执行两条命令——行数统计（wc -l）+ 章节标题 grep（输出全部章节锚点行号）；对照写前规划清单逐项核对，缺章/断链立即补 edit。
5. **呈报附结构预览**：交付摘要附核验输出的章节表（章节名+行号），让评审者第一眼确认结构完整，无需自行打开文档核对。

## Faster Next Time

- 写前先列章节清单并直接转成分块计划，边写边规划必超预算。
- 核验命令一条搞定：`wc -l <file>` + `grep -n "^#" <file>`，输出即结构证据，禁凭记忆断言"已写完"。
- 警惕信号：某章内容明显比规划薄、或 edit 连续命中同一锚点失败——先停下核验结构再继续追加。
- 单文件长文档用"write+edit 追加"；多文件模块才用并行 write 批量落盘，两者勿混用。

## Applicability Boundaries

- 适用：SDD design/tasks 等数百行级单文档产出；单次输出受限的平台环境；内容完整性优先的交付场景。
- 不适用：短文档（一次 write 内完成，分块徒增操作）；多文件批量创建（应并行 write）；需频繁在文档中段插章的结构（文末锚点追加模式不适配，应预留占位段）。
- 反模式：逐块写完逐块读回（edit 失败已自带报错，读回是双倍 token 成本）；为凑单次输出压缩内容完整性（违反文档完整性优先原则）；写完不核验直接呈报。

## Evidence or Examples

- 来源会话：ses_e4cb3b6f5ffeItlrKDOwdybcjW（2026-11-07，Date 项目 subagent-team-design 特性 design 阶段，spec-design-agent 子智能体执行，11 条消息）。
- 实际执行序列：write 第一章（需求与存量功能关系分析）→ edit 追加 2.1 → edit 追加 2.2/2.3/第三章 → bash 核验输出 443 行 + 8 个章节锚点（`1: 标题 / 7: 一 / 20: 1.1 / 69: 1.2 / 106: 二 / 108: 2.1 / 360: 2.2 / 472: 2.3 / 543: 三`），结构无缺章。
- 产物：`.codeartsdoer/specs/subagent-team-design/design.md` 落盘并经核验；该特性 tasks 阶段消费的版本后续修订至 604 行，分块落盘未产生结构缺陷。
- ROI：全程未发生内容截断返工；完工核验一次通过；逐块读回验证被裁剪掉，落盘轮次从"写一块验一块"压缩为"3 次写入+1 次核验"。