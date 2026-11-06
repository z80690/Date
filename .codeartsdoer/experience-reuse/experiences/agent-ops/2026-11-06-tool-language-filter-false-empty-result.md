---
id: 2026-11-06-tool-language-filter-false-empty-result
title: 工具可选过滤参数返回假空：去参数重调一次再下"不存在"结论
category: agent-ops
nature: pitfall
created_at: 2026-11-06T21:16:59
updated_at: 2026-11-06T21:59:51
tags: [tool-usage, false-empty, filter-parameter, verification]
keywords: [listSkills, language过滤, 假空结果, totalCount, 空结果验证, 去参数重调, 工具行为, 过滤器语义, 技能清单, 不存在误判]
problem_patterns: [带可选过滤参数调用工具得到空结果后误判目标资源不存在, 工具返回的空列表与其元数据总数自相矛盾未被察觉, 因过滤维度字段缺失导致过滤语义失效]
source_sessions: [ses_e4f5c5a83ffefUFnzHFvOEFJCW]
project: Date
severity: low
quality_score: 85
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-06-parallel-tool-call-doom-loop]
---

# 工具可选过滤参数返回假空：去参数重调一次再下"不存在"结论

## Scenario

Agent 调用 `listSkills(language="chinese")` 期望获取中文技能清单，返回 `count=0` 但 `totalCount=49`——过滤后列表为空，疑似"没有中文技能"，而下一步动作（技能测试的运行时核对）依赖这份清单的真实性。

## Key Signals

1. 返回结构自相矛盾：`count: 0, truncated: false` 但 `totalCount: 49`——"截断"已排除，说明确实是过滤把 49 条全部滤掉了。
2. 已知磁盘上存在 5 个 project 级技能且描述为中文，与"无中文技能"结论冲突。
3. 过滤参数的语义不可靠：清单条目的语言字段可能根本未标注（工具按未标注字段过滤，任何值都匹配不到），参数合法但结果必空。

## Essence

带可选过滤参数的空结果 ≠ 资源不存在，它可能是**过滤维度失效导致的假空**。判别依据藏在返回元数据里：`totalCount > 0` 而 `count = 0` 且无截断，即过滤条件本身可疑。此时唯一可靠动作是去掉过滤参数重调一次取全集，再在本地按需筛选；不能基于假空结果向下传"不存在"结论——错误结论会在下游门禁（如技能测试）里被当真，造成整条验证链失真。

## Approach

1. 收到带参调用返回空列表时，先查返回元数据：`totalCount`、`truncated` 字段。`totalCount>0 且 count=0 且 truncated=false` → 判为过滤假空信号。
2. 与已知磁盘事实交叉核对（如技能目录确实存在）→ 矛盾即坐实假空。
3. 去掉可选过滤参数重调一次，取全集结果。
4. 需要维度筛选时在本地完成（按返回条目的实际字段自行匹配），不依赖工具的过滤参数。
5. 全流程注意频控：同一验证工具单轮只调一次、有结果即止，避免触发循环保护。

## Faster Next Time

- 任何 `xxx(list, filter=...)` 返回空，第一反应看 `totalCount` 与 `truncated`：两者矛盾即假空，去参重调，跳过所有"换个关键词再过滤"的尝试。
- 把"空结果 + 总数非零"写进工具调用的通用检查项，与其他工具行为陷阱（如并行重复触发保护）同级记忆。
- 对"资源不存在"类结论设置双证据要求：过滤结果为空 + 去参重调也为空，才允许下结论。

## Applicability Boundaries

- 适用：任何返回列表且带可选过滤参数的工具调用（观察于 CodeArts Agent 的 listSkills；该工具 totalCount=49 而按 language 过滤返回空，说明其条目语言字段未标注、过滤维度失效）。
- 不适用：`totalCount=0` 的真空（此时资源确实不存在）；强制必填过滤参数的工具；返回无元数据的纯列表（此时直接去参重调验证，成本同样只有一次调用）。
- 过滤参数语义随工具版本可能修复，使用前可用一次全集调用抽查条目是否带语言字段。

## Evidence or Examples

- 实录：`listSkills(language="chinese")` 两次调用均返回 `{"count":0,"totalCount":49,"truncated":false,"skills":[]}`，output 为 "No skills found for language: chinese"。
- 实录：去掉参数后 `listSkills()` 返回 49 个技能，其中 project 级恰好 5 个且 enabled，description 与磁盘 SKILL.md 逐字一致——假空坐实，全集可用。
- 该全集清单随后成为技能测试报告的运行时核对证据层。