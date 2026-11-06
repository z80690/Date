---
id: 2026-11-06-skill-trigger-batch-audit-checklist
title: 多技能触发条件批量审查清单（边界互斥自证+资源实存核对）
category: agent-ops
nature: technique
created_at: 2026-11-06T20:20:20
updated_at: 2026-11-06T20:31:10
tags: [技能审查, 触发条件, frontmatter, 边界互斥, 技能治理]
keywords: [SKILL.md, description, 触发条件, 不适用边界, name 一致性, 边界互斥, 技能状态记录, 孤儿检测, 技能治理, 技能状态文件]
problem_patterns: [批量审查多个技能的触发条件是否冲突需调整, 派工单要求逐个技能给出保留或调整结论且禁止反问]
source_sessions: [ses_e4f472e57ffeK1eNXlpjLq4sys]
project: Date
severity: low
quality_score: 91
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-06-codeartsdoer-rule-vs-skill, 2026-11-06-verify-before-write-knowledge-docs]
---

# 多技能触发条件批量审查清单（边界互斥自证+资源实存核对）

## Scenario
派工要求逐个审查项目技能集（`<skills-root>/<name>/SKILL.md` 结构）的触发条件"有冲突就改，没冲突就维持，自己定"，禁反问。技能已全部实存，且配有独立状态记录文件（每技能一条布尔状态）。

## Key Signals
- 审查对象全部实存（本例 5 个 SKILL.md，514–813 字节），说明审查对象是存量资产而非新建。
- 官方最佳实践文档在项目库内可引用，可作为合规对照基准。

## Essence
触发条件审查的判定核心不是"写得好不好"，而是三个无冲突证明：① 标识一致性——name 与目录名一致；② 边界完备且互斥/互补——每个 description 含"当…时触发"的正面触发条件与"不适用于…"的排除边界，且任意两技能的触发域不重叠；③ 引用资源实存——description/body 中提到的工具、参考文档必须真实存在。三者都通过 ⇒ 维持不动，不制造无谓改动。

## Approach
1. 逐个核对 name 与目录名一致；description 同时含触发条件句式（"当…时触发"）与不适用边界句式（"不适用于…"）。
2. 两两比对触发域：互斥（如"模糊输入" vs "明确收敛"）或互补（如"规则初始化" vs "技能编写"）判合规；触发域重叠或边界含糊判调整。
3. 实存核对：技能中引用的工具/API、参考文档路径逐一确认存在。
4. 孤儿检测：状态记录文件条目与技能目录一一对应，多出或缺失都要上报。
5. 对照官方基准文档核对写法合规项（frontmatter 必备、description 长度上限等）；无冲突则结论"全部保留"并写明依据，不改文件。

## Faster Next Time
- 五步清单一轮并行读取即可完成多个技能的审查，逐条产出"保留/调整+具体改法"结论。
- 阴性结论（全部保留）同样要附依据句（边界两两互斥/互补、引用实存、无孤儿），否则审查不可信。
- 检测到触发域重叠时，改法优先收窄 description 的不适用边界，而不是重写技能正文。

## Applicability Boundaries
- 适用：Agent 项目技能集（SKILL.md 结构）的批量触发条件审查；几个到几十个技能的规模。
- 不适用：单个技能的深度编写评审（应走技能编写流程）；与内置技能的重叠度判断需先有内置技能清单作对照基准，无基准时该项标注"推断"而非断言。
- 与《码道知识沉淀的分工决策：规则 vs 技能，及 SKILL.md 合规清单》的分工：那条管沉淀形态决策与单技能编写阶段的合规（写），本条管存量技能集的批量触发条件审查与孤儿检测（审）；两者在"触发条件互斥防串台"的判定准则上同源，可互相引用，但不可互相替代。
- 反模式：只审查 description 措辞不核对引用资源实存；发现微小措辞瑕疵就要求返工（过度优化）。

## Evidence or Examples
- 项目 Date（2026-11-06 实查）：5 技能 find-skills/grill-me/lazy-exec/ruleinit/skill-writer，514–813 字节；grill-me（模糊输入）↔ lazy-exec（明确收敛）互斥、ruleinit（规则 .mdc）↔ skill-writer（技能 SKILL.md）互补；find-skills 引用的 listSkills 工具、skill-writer 引用的 docs/官方最佳实践-如何写好一个Skill-bp0010.md 均实存；ProjectSkillStatus.txt 5 条 =true 与 5 个目录一一对应无孤儿。
- 结论：5 技能全部保留、无冲突、无需修改；15 个内置热门技能与本地 5 技能零重叠，对照基准只能取官方最佳实践（bp0010）。