---
id: 2026-11-08-wiki-section-same-layer-action-criteria
title: Wiki 小节修订的逐节 action 判据：同层面改写正文、不同层面仅刷 code_refs
category: workflow
nature: decision
created_at: 2026-11-08T03:11:17
updated_at: 2026-11-08T10:49:52
tags: [文档修订, 同层面判断, patch决策, 口径联动, 知识库]
keywords: [replace_content, line_number_only, section_title, code_refs, 同层面, 受影响小节, 格式描述失真, 元层面小节, 联动判定, wiki-patches]
problem_patterns:
  - 大改版后逐节修订 Wiki 文档，不知哪些小节需 replace_content 改写正文、哪些只需 line_number_only 刷新引用，误判会产生无关噪声或残留旧口径
  - 派工单只点名部分受影响小节，小节正文中隐性的格式描述失真（序号风格、附条有无、条目命名）仅靠派工单清单会漏改
source_sessions: [ses_e48bee51affeThxvdxYI2D1zuM]
project: Date
severity: low
quality_score: 84
hit_count: 1
last_hit_at: 2026-11-09T13:40:08
low_quality_hit_count: 0
tier: A
related_experiences: [2026-11-08-wiki-section-tiered-revision-judgment-contract, 2026-11-08-wiki-section-revision-patch-json-mode, 2026-11-08-module-inflation-capability-grouping-granularity, 2026-11-07-secondhand-summary-insufficient-verify-primary-source, 2026-11-06-verify-before-write-knowledge-docs]
---

# Wiki 小节修订的逐节 action 判据：同层面改写正文、不同层面仅刷 code_refs

## Scenario

规范文档大改版（条数/结构/口径变更，本例协作公约 7 条 → 6 条）后的 Wiki 文档小节级修订派工：修订者以 patch JSON 交付，action 支持 `replace_content`（改写正文）与 `line_number_only`（正文不动仅刷 code_refs）两种。本例 5 个小节（概述/架构设计/技术栈/编码规范/关系），修订者独立执行无法中途确认。逐节 action 决策直接影响合并后质量：误 replace 会向元层面小节写入无关内容，误 line_number_only 会在正文留下旧口径残句。

## Key Signals

- 小节正文直接描述变更对象的内容特征（条数、条目主题、编号风格、成条方式、附条有无）→ 该节与变更同层面。
- 小节正文只描述载体形态、依赖关系、协作角色等元层面信息（如"技术栈列载体""关系列依赖方向"）→ 通常不受内容条数变化影响。
- 隐性信号：派工单只点名"描述公约的部分"，但格式性失真只有实读实文才暴露——本例编码规范小节原文写"协作公约以中文序号（一、二、…）单行成条，末条附同名规则优先级"，实文实为阿拉伯数字 6 行、无优先级附条。

## Essence

逐节 action 的判据是"变更与小节已有关注点是否同层面"：小节正文对变更对象做了内容级描述（条数/条目/格式）即同层面，必须 `replace_content` 按实文重述且不留残句；小节只从元层面提及变更对象（如"公约约束每次派工执行"的角色描述）则不同层面，`line_number_only` 保留正文、仅把 code_refs 刷到实文新行号。判据的输入是"小节原文 × 变更实文"的逐字比对，不是派工单的受影响清单——清单只是起点，实读才能暴露清单外的格式失真。

## Approach

1. 先实读变更源文件实文（本例公约 6 行），掌握新口径的条数、编号风格、有无附条——这是所有同层面比对的基准。
2. 逐节读小节原文，圈出其中直接描述变更对象的句子（条数、条目名、格式描述）。
3. 逐句与实文比对：句子所述特征已过时（如"7 条团队行为约束"、中文序号、优先级附条）→ 该节 `replace_content`，按实文口径重述。
4. 小节正文无过时内容特征、只有元层面角色/依赖描述 → `line_number_only`，`new_content` 置 null，code_refs 指向实文新行号。
5. 每节决策留一句话理由（如"技术栈：描述载体与托管形态，不受公约条数变化影响"），写入交付摘要供上游复核。

## Faster Next Time

- ROI：实文一轮 + 小节原文一轮共两轮读取即可完成全部 action 决策，避免"全部 replace"的过度改写或"只改点名小节"的残句遗漏。
- 快捷判据：小节正文出现数字条数/条目名/格式词（序号、附条、成条方式）→ 候选 replace；只出现角色/依赖/载体词 → 候选 line_number_only。
- 反模式：把派工单的受影响清单当完整决策依据（本例编码规范的格式失真靠实读才确认）；对元层面小节强行改写正文引入噪声；line_number_only 时漏刷 code_refs。

## Applicability Boundaries

- 适用：patch JSON 小节级修订流程（见 wiki-section-revision-patch-json-mode）内逐节选择 action；规范文档大改版后的口径联动判定。
- 不适用：全新文档生成（无既有小节可比）；授权直改的普通文档编辑（无 action 选项）。
- 与相邻经验分工：patch-json-mode 条管 patch 产出/落盘/合并与口径核实（其"受影响小节全部联动换口径"针对全 replace 场景），本条管混合 action 下的逐节判据，是其后置细化；`wiki-section-tiered-revision-judgment-contract` 与本条判据同源（同层面分流），其独有价值在只读 subagent 场景的执行契约：判定预判式派工（上游预判+下游验证）、纯文档行号锚点（"第 N 条 = 行 N"）解决符号骨架空时的 code_refs 定位、code_refs 保守原则（引用集合不变动除非有行级依据）——同一小节在不同轮次变更下 action 结论可不同（编码规范小节在 7→6 大改版轮判 replace、在条目合并轮判 line_number_only），以当轮变更实文逐句比对为准。
- 证据等级：单次实战闭环（5 小节决策 + patch 落盘成功）；判据框架源自派工单规范、实战验证其可执行性，跨文档复用稳定性待同类任务检验。

## Evidence or Examples

- 源会话 ses_e48bee51affeThxvdxYI2D1zuM（Date 项目，docs 模块 codebase-knowledge/官方文档与协作规范.md 修订）。
- 决策实证：概述/架构设计/编码规范 → replace_content（三者正文直接描述公约条数与格式）；技术栈/关系 → line_number_only（载体与依赖描述不受 7→6 影响）。
- 实读失真实证：编码规范小节"中文序号（一、二、…）+ 末条附同名规则优先级"描述与实文不符——`docs/项目协作公约-最终稿.md` 实为阿拉伯数字 1-6 行、无优先级附条。
- patch 落盘：`.codeartsdoer/temp/wiki-patches/docs_module.json`（UTF-8 无 BOM），code_refs 形如 `docs/项目协作公约-最终稿.md:1`。