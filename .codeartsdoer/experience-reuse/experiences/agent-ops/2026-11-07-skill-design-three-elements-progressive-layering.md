---
id: 2026-11-07-skill-design-three-elements-progressive-layering
title: 配套 skill 设计稿按官方三要素+渐进式三层评审，明细下沉 L3 资源实现 body 极简
category: agent-ops
nature: methodology
created_at: 2026-11-07T19:58:29
updated_at: 2026-11-07T20:05:46
tags: [skill-design, 三要素, 渐进式加载, 分层架构, 设计稿评审]
keywords: [name命名, description触发, instructions剧本, 渐进式三层, L1元数据, L2正文, L3资源, 自动化脚本, 参考文档, 输出模板, body极简]
problem_patterns: ["为规矩设计配套 skill 时缺少结构标准，name 模糊、description 只写功能不写触发边界、指令写成抽象原则", "要求 body 极简时直接删减执行细节，导致 skill 激活后执行不稳定", "资源类（脚本/参考/模板）不知何时该用哪类，全部塞进正文造成上下文浪费"]
source_sessions: [ses_e4a308c09ffePvUITm7PSWOiWX]
project: Date
severity: medium
quality_score: 92
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
utility_score: 95
tier: S
related_experiences: [2026-11-06-codeartsdoer-rule-vs-skill, 2026-11-06-skill-trigger-batch-audit-checklist, 2026-11-07-reference-style-requires-full-directory-inventory]
---

# 配套 skill 设计稿按官方三要素+渐进式三层评审，明细下沉 L3 资源实现 body 极简

## Scenario

为既有规矩/流程设计配套 skill 的**设计稿阶段**（尚未落 SKILL.md）：需要给出 skill 的结构定义供评审，且用户明确要求"最简单/极简 body"。设计稿若只写"触发+动作"两要素或把所有执行细节塞进正文，会在落地后出现触发失准或执行漂移。

## Key Signals

- 设计稿对 skill 的描述缺要素：无明确 name 命名规则、description 未区分适用与不适用场景、instructions 写成抽象原则而非分步剧本。
- "极简"要求被理解为删减执行细节——正文越删越薄，执行稳定性同步下降。
- 附带资源（固定操作、背景知识、输出格式）没有分层去处，全部挤在 SKILL.md 正文里。

## Essence

skill 设计稿的验收标准是官方最佳实践（bp0010）的三要素+渐进式三层：**三要素**——name 用动词+名词表达做什么（review-code/generate-prd 式，禁 helper/tool1 类模糊名）；description 是激活判断的**唯一依据**，必须写清适用场景+不适用场景（写得模糊=白写）；instructions 是分步执行剧本，越具体执行越稳定。**三层加载**——L1 元数据（name+description）常驻参与路由；L2 SKILL.md 正文激活后才载入；L3 捆绑资源按需加载。"极简 body"的正确实现是**分层下沉**（明细移入 L3），不是删减要素——正文只留路由与主干剧本，稳定性由具体剧本保住，上下文占用由分层保住。

## Approach

1. **name 定名**：动词+名词或动宾式小写连字符（如 check-done、guard-original）；拒绝 helper/tool1/assistant 类模糊名。
2. **description 双段写法**：适用场景（何时触发，含触发词）+"不适用"排除边界（与相邻 skill 互斥防串台）；两段齐备才允许进入设计稿评审。
3. **instructions 分步剧本**：祈使句步骤序列+失败分支，写"智能体默认不会做的事"，不写常识。
4. **三层归位**：L1 只留 name+description；L2 正文控制在一屏可读（主干触发+核心动作+指向 L3 清单）；L3 按**资源选型**分三类归位——固定机械操作→自动化脚本，背景知识长文→参考文档（加目录索引），严格格式场景→输出模板。
5. **触发可靠性诚实标注**：设计稿须声明 skill 触发非 100%，强制类约束由规矩/规则条兜底，skill 只做流程配套（规矩为主、skill 为辅的载体裁定见关联经验）。

## Faster Next Time

- 设计稿评审清单四问：name 是否动宾可读？description 有没有"不适用"句？instructions 是否分步可执行？明细是否已下沉 L3？四问全过才放行。
- "要极简"= 下沉不删减：先问"这段明细该住哪层"，而不是"能不能删掉"。
- 资源选型口诀：机械重复上脚本，长背景进参考，格式严进出模板；三者都不沾才留在正文。

## Applicability Boundaries

- 适用：为规矩/流程配套设计 skill 的设计稿评审阶段；对既有 skill 做"为什么执行不稳"的结构归因；用户要求 body 极简的场景。
- 不适用：决定知识该沉淀成规则还是 skill（形态选择，见 2026-11-06-codeartsdoer-rule-vs-skill）；SKILL.md 落盘后的编写合规细节（字段长度、目录命名等以该条合规清单为准）。
- 平台边界：三要素与三层架构来自码道官方最佳实践（bp0010）；"description 决定激活"原则对多数按需加载的 Agent 技能体系通用，字段名与层数可能不同。
- 验证状态边界：本条证据止于设计稿评审通过（v4 失败→v5 采纳）；SKILL.md 落盘后的实际触发率与执行稳定性尚未运行验证，复用时按"设计稿阶段方法"对待，不等同落盘验证结论。

## Evidence or Examples

- 来源会话：ses_e4a308c09ffePvUITm7PSWOiWX（2026-11-07，Date 项目 optimization_plan v5 规格修订）。
- 失败背景：v4 规格的配套 skill 设计因未参照 bp0010 官方标准被用户标记失败；v5 全部按三要素+渐进式三层重写（§5.10：check-done/DoD 判定器、guard-original/单一文件维护器，各含三要素完整定义，body 一屏可读）。
- 官方要点实证（bp0010 实读）：name 好例 review-code/analyze-competitor/generate-prd、坏例 helper/tool1；description 为激活唯一判断依据；渐进式三层 L1 元数据→L2 正文→L3 捆绑资源；资源三型=自动化脚本/参考文档/输出模板。
- 与规矩的协同实证：v5 设计中强制类 DoD 判定收编为公约第 8 条（一句话极简），skill 仅做配套判定器；明细（判定流程五步、收编映射表）外置知识库，正文保持极简。