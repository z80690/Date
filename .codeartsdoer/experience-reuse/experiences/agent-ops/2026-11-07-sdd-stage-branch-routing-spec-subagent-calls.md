---
id: 2026-11-07-sdd-stage-branch-routing-spec-subagent-calls
title: SDD 多阶段会话的阶段分支路由与 spec-* 子代理调用契约（原始请求直填+禁question+确认后编码+上游衔接）
category: agent-ops
nature: technique
created_at: 2026-11-07T10:21:58
updated_at: 2026-11-07T10:21:58
tags: [sdd, 阶段路由, 子代理调用, 意图分类, 调用契约]
keywords: [spec-requirement-agent, spec-design-agent, Task工具, 阶段推进, 进入下一阶段, 意图分支路由, question工具禁用, 原始请求直填, 确认后才编码, 上游文档目录衔接]
problem_patterns: ["SDD 多阶段会话中收到阶段推进消息，不确定应调用哪个阶段的子代理还是反问用户", "调用 spec-* 子代理时改写用户原始请求导致意图丢失，或未经确认直接开始编码任务"]
source_sessions: [ses_e4c5b74edffe0IiEtF5QgP4dBs]
project: Date
severity: medium
quality_score: 80
hit_count: 1
last_hit_at: 2026-11-07T18:47:40
low_quality_hit_count: 0
tier: A
related_experiences: [2026-11-07-claimed-count-vs-fact-source-conflict, 2026-11-06-spec-to-tasks-decomposition-pipeline, 2026-11-07-full-authorization-self-gated-execution]
---

# SDD 多阶段会话的阶段分支路由与 spec-* 子代理调用契约（原始请求直填+禁question+确认后编码+上游衔接）

## Scenario

规范驱动开发（SDD）多阶段会话（需求规格→实现方案→编码任务→任务执行）中，各阶段由专门子代理（spec-requirement-agent / spec-design-agent / spec-task-agent）承接，主代理负责阶段推进与 Task 委派。平台在用户消息中内嵌了一套分支协议：用户每条阶段推进消息自带 4 分支判定规则（进入下一阶段 / 重试或修改意见 / 补充或新任务 / 非研发请求），并附硬约束清单。主代理须先做意图分类，再按契约调用子代理，而非自行决定推进节奏。

## Key Signals

- 用户消息显式含"进入下一阶段"等表述，且消息体附带编号分支清单（1. 进入下一阶段→调下一阶段 agent；2. 重试/修改意见→重调当前阶段 agent；3. 补充/新任务→调第一阶段 agent；4. 非研发请求→反问澄清）。
- 消息尾部出现硬约束短语："不要调用 question 工具""不要在没有回复用户是否需要修改文档的情况下就开始执行编码任务""prompt 参数尽量填写用户的原始请求，不要做过多的更改""禁止使用与 brainstorming 相关的 skills"。
- 会话中已有上一阶段产物落盘信号（如 spec.md、TASK.md 经 glob 确认存在），下一阶段调用必须衔接这些文档目录。
- 出现"除非请求中明确表达进入下一阶段，否则应谨慎选择进入下一阶段"——即平台明示推进权在用户。

## Essence

阶段路由的本质是**意图分类问题**（不是流程设计问题）：协议已把分支枚举穷尽，主代理的职责是准确归类后委派，而不是发明推进逻辑。三条调用硬约束各防一类跑偏：①原始请求直填 prompt——防主代理改写导致子代理丢失用户原始意图与措辞细节；②禁 question 工具、呈现摘要后必须回复"是否需要修改文档"——防越权交互与未确认即编码的越权开工；③携带上一阶段文档目录并要求先读上游——防子代理在无上游上下文的情况下凭空重构，造成阶段间断裂。

## Approach

1. **意图四分支归类**：用户明确"进入下一阶段"→调用下一阶段子代理；"重试"或对当前文档提修改意见→重新调用当前阶段子代理；提供补充任务或新任务→调用第一阶段子代理；非研发请求→不回答、以反问澄清用户想实现什么研发任务。
2. **谨慎门**：除非用户消息明确表达进入下一阶段，否则不主动推进阶段——宁可停在当前阶段等待，也不抢跑。
3. **prompt 契约**：调用 Task 工具时 prompt 尽量填入用户原始请求原文，不做改写、缩写或"优化"。
4. **交互禁区**：不调用 question 工具；不使用 brainstorming 类 skills；每阶段产物生成后先向用户呈现文档摘要，并显式回复"是否需要修改文档"，确认前不得进入编码类任务。
5. **上游衔接**：调用下一阶段子代理时，在其 prompt 中写入上一阶段产物目录，并显式要求"先读取上一阶段生成的文档"再动工。

## Faster Next Time

- 调用前四问：意图分支归对了吗？prompt 是原始请求吗？交互禁区三条守住了吗？上游文档目录传了吗？四问全过再发 Task 调用。
- 警示信号：用户消息内嵌编号分支协议时，说明平台已固化阶段状态机——照协议执行即可，不要用一般对话的判断方式自行发明阶段推进规则。
- ROI：一次正确路由直接命中正确子代理与正确上下文，避免整阶段产出方向性返工（重做一次 spec/design 通常以小时计）。

## Applicability Boundaries

- 适用：配备 spec-* 子代理编队、用户消息内嵌分支协议的 SDD 平台会话（实证于 CodeArts Agent）。
- 不适用：无子代理平台（主代理直接执行各阶段，不存在 Task 委派路由）；用户消息未内嵌分支协议的普通会话（此时按常规对话意图判断即可）。
- 平台相关性：意图分类与四条契约的方法通用；分支枚举、禁区清单、协议措辞为 CodeArts Agent SDD 流水线实测细节，跨平台采用前需确认存在等价协议。
- 证据边界：本条实证覆盖 requirement 阶段的完整调用闭环与 design 阶段的调用发起；协议中 tasks.md 读取失败时回退第三阶段重新生成等分支细节来自协议原文，尚未在本会话轨迹内实测验证。

## Evidence or Examples

- 来源会话：ses_e4c5b74edffe0IiEtF5QgP4dBs（2026-11-07，Date 项目，P001 派工单"SDD流程图可视化"，6 条消息）。
- 契约执行实证：主代理判定为代码研发任务后，按"prompt=派工单原文"调用 spec-requirement-agent，产出 spec.md（5 大能力域 EARS 格式）与 TASK.md 落盘 `.codeartsdoer/specs/20261107_P001_spec_workflow_visual/`，glob 验证两文件存在；随后主代理向用户呈现 5 项摘要并以"请确认：需求规格文档是否需要修改？"收尾，未调用 question 工具。
- 阶段衔接实证：进入实现方案阶段时，主代理在委派 prompt 中携带 spec 文档目录并要求 spec-design-agent 先读取上游 spec.md（该 Task 调用发起后轨迹结束，结果未在本 trace 内闭合）。
- 相邻经验边界：2026-11-07-claimed-count-vs-fact-source-conflict 同源于本会话的 spec 子任务（spec.md 中口径仲裁规则固化的内容级经验）；本条独有的是阶段路由与子代理调用的**操作级契约**，两者分别覆盖"产物内写什么"与"怎么委派调用"。