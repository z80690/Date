---
id: 2026-11-08-examiner-precheck-evidence-parallel-audit
title: 子智能体SOP前置自检证据化：门禁语义直读+旧轮事件链核对+材料实读，一轮并行实查
category: agent-ops
nature: methodology
created_at: 2026-11-08T02:01:55
updated_at: 2026-11-08T02:20:00
tags: [SOP自检, 子智能体, 证据清单, 考核出题, 并行实查]
keywords: [前置自检, 门禁放行, 结论语义, 事件链完整, 旧轮闭环, 材料实读, 素材范围锁定, 证据清单, 并行读取, 存在性语义分层, 执行方, 派工声称态]
problem_patterns: ["SOP 含前置自检步骤时若只凭派工单声称或只做文件存在性检查即动笔，可能带着未验证前置执行", "子智能体隔离会话无法访问主智能体会话状态，前置状态必须用磁盘证据自行重建", "门禁文件存在但结论为驳回/中间态时，存在性检查被误判为前置已满足"]
source_sessions: [ses_e492b172cffeS0u6qRrZ50JFT6]
project: Date
severity: medium
quality_score: 90
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [workflow/2026-11-07-exam-question-authoring-contract.md, workflow/2026-11-08-exam-event-ledger-structure-ordering-discipline.md, workflow/2026-11-06-design-stage-self-serve-evidence-decisions.md, workflow/2026-11-07-stage1-evidence-baseline-and-halt-reporting.md, agent-ops/2026-11-07-worker-grader-exam-gate-pattern.md, agent-ops/2026-11-08-examinee-key-contact-disclosure-independence.md]
---

# 子智能体SOP前置自检证据化：门禁语义直读+旧轮事件链核对+材料实读，一轮并行实查

## Scenario

多角色考核链路（主智能体→出题官→批改官）中，执行方子智能体的 SOP 含"自检前置"步骤（如出题官六步 SOP 的步骤②：确认上游门禁放行在档、无未闭环旧轮次、学习材料已三查）。子智能体运行在隔离会话中，看不到主智能体会话状态；派工单中的前置项都是"声称态"（"已三查""已放行""旧轮已闭环"），若只凭声称或只做文件存在性检查就动笔，可能带着未验证的前置执行整轮产出。

## Key Signals

- 派工单前置项均为声称态，无已验证的磁盘证据指针（或给了指针但只确认"文件在"）。
- 门禁证据文件存在≠结论为放行——存在性检查会漏掉"结论为驳回/中间态"的情况。
- 旧轮目录存在≠旧轮闭环——需事件链完整性核对才能证明上一轮已走完。
- "材料已三查"是派工方声明；执行方的产出素材范围锁定必须以自己实读到的内容为准，而非仅凭指针存在。

## Essence

子智能体无法访问主智能体会话状态，前置状态只能用磁盘证据自行重建。关键约束：**存在性检查（文件在）与语义检查（结论正确/链路完整/内容可作素材）是两层，缺一层即前置未证**。执行法是把 SOP 自检项转为三类证据的检查单（门禁放行语义 / 旧轮事件链完整性 / 材料实存+实读），一轮并行读取完成，全部通过才进入产出步骤。

## Approach

1. 动笔前把 SOP 自检项逐条转为磁盘证据清单（复用通用"派工单证据项转证据清单并行实查"模式，见 related）。
2. 门禁证据双层查：确认门禁文件存在 + 直读其"放行结论"节，确认结论语义为放行（而非驳回/中间态）。
3. 旧轮闭环查：逐轮读该轮事件流水，核对事件链完整且发布方正确（链路完整性速查见 related 事件流水条）；本轮目录此时应只含派工留痕行。
4. 材料实读锁范围：材料指针逐一实读内容（非仅确认存在），产出素材范围锁定为实读过的已核验材料，禁出自未读材料。
5. 一轮并行调用完成全部实查（禁逐条串行核对）；自检结论显式分条留痕（逐项 a/b/c），供完成事件行与返回摘要直接引用。
6. 失败分支：任一证据项未过→终止产出并上报，不带病动笔。

## Faster Next Time

- 三类前置证据检查单（门禁语义 / 旧轮事件链 / 材料实读）可直接复用于任何含前置自检步骤的执行方 SOP。
- "存在≠语义"一句话自查：每项前置先问"文件在吗"，再问"结论/链路/内容对吗"。
- 并行一轮读齐既省时又防漏；自检结论分条留痕可直接粘贴进完成事件与摘要，免二次整理。

## Applicability Boundaries

- 适用：子智能体执行含前置自检步骤的 SOP（考核出题/批改/验收类派工等）；任何"派工单声称的前置需磁盘证实"的执行方场景。
- 不适用：主智能体自身（其即门禁判定义务人，判定与执行一体）；无门禁、无前置的轻量派工（自检开销大于价值）。
- 边界：自检只证前置成立，不保证产出质量（产出质量由产物自检与下游验收环节保证）；执行方前置证据重建不替代门禁判定——门禁结论仍由判定义务方落盘。
- 平台：实证于 CodeArts（码道）平台主子智能体 Task 派工机制（子代理隔离会话）；模式为通用 Agent 模式，可迁移。
- 相邻经验分工：出题派工契约格式（派工方视角五要素）见 workflow/2026-11-07-exam-question-authoring-contract；事件链完整性速查与流水纪律见 workflow/2026-11-08-exam-event-ledger-structure-ordering-discipline；证据清单并行实查的通用模式见 workflow/2026-11-06-design-stage-self-serve-evidence-decisions——本条是其出题场景实例化，独有点是三分类前置检查单与"存在性/语义"分层判定；考教分离下作答方接触评分 key 的自披露与独立性处置见 agent-ops/2026-11-08-examinee-key-contact-disclosure-independence，其与本条角色边界互补：执行方实读已三查学习材料属职责内无需披露，作答方接触评分 key 内容须走披露路径。

## Evidence or Examples

- 来源会话：ses_e492b172cffeS0u6qRrZ50JFT6（2026-11-08，Date 项目 sdd_agent_refactor 特性 V1 考核出题轮，examiner 子智能体执行，trigger=RUNTIME_VERIFY、新版 v2 配置首跑实测）。
- 自检实测：三类证据一轮并行实查全过——门禁文件直读"④放行结论"节=放行（三项全过无中间态）；R1 轮 events.md 四事件链 E1→E4 完整（grade.complete 在案）；V1 目录仅含派工行；四份已三查学习材料全部实读成功。
- 产出闭环证据：50 题落盘 questions.md（8587B）+ key.md（20438B）；正则计数 50/50；三级覆盖记忆15/理解23/应用12；首尾抽验（题1–5、41–50）与 key 逐题对应正确；E2 完成事件由出题官自行追加至本轮 events.md。
- 自检结论分条留痕实例："a. M1 已放行（结论'放行'三项全过）✅ / b. 无未闭环旧轮次（R1 轮 E4 在案，V1 目录仅含派工行）✅ / c. 四份已三查材料实读成功 ✅"。