---
id: 2026-11-06-codeartsdoer-rule-vs-skill
title: 码道知识沉淀的分工决策：规则 vs 技能，及 SKILL.md 合规清单
category: agent-ops
nature: decision
created_at: 2026-11-06T18:41:59
updated_at: 2026-11-06T18:41:59
tags: [codeartsdoer, rule-vs-skill, skill-authoring, knowledge-distillation]
keywords: [码道, 规则, 技能, SKILL.md, frontmatter, description, 触发条件, 串台, 按需加载, 上下文占用, 官方规范]
problem_patterns: [不知道该把知识写成规则还是技能, 技能描述只写功能导致激活判断失准, 相邻技能触发条件重叠互相串台]
source_sessions: [ses_e51adb269ffeqfVMdEGO1eP4xa]
project: Date
severity: low
quality_score: 85
hit_count: 3
last_hit_at: 2026-11-06T20:08:03
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-06-codeartsdoer-rule-init, 2026-11-06-codeartsdoer-docs-retrieval]
---

# 码道知识沉淀的分工决策：规则 vs 技能，及 SKILL.md 合规清单

## Scenario
在码道项目中积累了约束或流程知识，需要决定沉淀形态；或编写/评审 SKILL.md 时要保证触发精准、合规。

## Key Signals
- 错配症状：把操作流程塞进规则 → 每次会话全量注入浪费上下文；把行为约束写成技能 → 智能体不会主动激活，约束失效。
- 串台症状：两个技能描述场景词重叠（如"配置文件编写"），模糊请求下同时命中。
- 激活失准症状：description 只写"做什么"不写"什么时候用"，智能体该触发时不触发。

## Essence
官方机制（ug_0019/ug_0024）：规则在对话开始时全量加载、持续参与推理，控制"应该怎么做"（行为边界）；技能按需加载减少上下文占用，解决"如何完成任务"（流程指导）。判断准则：约束/边界/纪律 → 规则；操作步骤/方法论/经验 → 技能。

## Approach
1. 分工判断：行为约束与团队约定 → 规则（保持数量克制，always 规则全量占上下文）；流程知识 → 技能。
2. SKILL.md 编写合规清单（逐项核对）：
   - YAML frontmatter 必填。
   - name 与技能目录名一致（小写连字符）。
   - description ≤1024 字符，且必须含"当…时触发"的触发条件——智能体仅凭 description 决定是否激活。
   - description 补"不适用于…"边界句，与相邻技能互斥防串台。
   - 指令写智能体默认不会做的事，勿写常识；确定性操作可配 `scripts/`，按需加载的知识放 `references/`，不进上下文的模板放 `assets/`。
3. 参照官方最佳实践组织指令：分步骤、祈使句、给出"不适用边界"与核对清单。

## Faster Next Time
- 描述三要素口诀：场景触发词 + 功能概括 + 排除边界——三者齐备激活判断才准。
- 评审技能时先看 description 的触发词与相邻技能是否互斥，再看指令可执行性，最后看目录结构。
- "单条不超 8 行""≤1024 字符"等数值约束直接写入核对清单，勿凭印象。

## Applicability Boundaries
- 适用于码道 CodeArts Agent 的规则/技能双机制；"描述决定激活"原则对多数按需加载的 Agent 技能体系（如 Claude Skills）通用，字段名不同。
- 官方未给出"项目级规则最适配几条"的硬性数值——数量判断属推断级，依据是 always 全量注入机制。

## Evidence or Examples
- 实测：项目两个技能（ruleinit/skill-writer）初始描述无边界句，模糊请求下存在同时命中风险；各补一句"不适用于…"后边界互斥，终审通过。
- 实测：官方《规则》文档明示加载方式对比（规则=对话开始加载持续推理；技能=按需加载）。
- 实测：官方最佳实践（bp0010）强调 description 是智能体决定激活的唯一依据。