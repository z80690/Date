---
id: 2026-11-06-glob-empty-result-read-verify
title: glob 空结果不可单独定论，read 目录复核后再下"不存在"结论
category: agent-ops
nature: pitfall
created_at: 2026-11-06T19:48:43
updated_at: 2026-11-06T19:48:43
tags: [glob误报, 目录探测, 工具复核, 存在性判断, Agent工具]
keywords: [glob, No files found, 误报, 空结果, read目录, SKILL.md, 存在性判断, 工具差异, 证据等级, 复核]
problem_patterns: [glob 模式匹配返回空结果但目标文件实际存在，导致误判文件或目录不存在, 依据单次 glob 空结果跳过本应执行的任务或改写文档现状表述]
source_sessions: [ses_e4f58d3e0ffebDYA8xP43bw3qm]
project: Date
severity: medium
quality_score: 88
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-06-verify-claimed-prerequisites-before-research]
---

# glob 空结果不可单独定论，read 目录复核后再下"不存在"结论

## Scenario
Agent 用 glob 探测目录树中是否存在特定文件（如 `**/SKILL.md`），返回 "No files found"，随即可能得出"文件不存在"的结论，并影响后续动作：改写文档现状表述、跳过本应执行的审查、误判命名冲突或前提证伪。

## Key Signals
- glob 返回 No files found，但同轮或前轮 read 目录列表已显示目标文件所在子目录存在。
- 对同一位置用不同工具（read 目录 vs glob 模式）得到矛盾结果。
- 目标文件位于二级及以上嵌套子目录。

## Essence
glob 的空结果是"模式匹配无命中"，不等于"文件不存在"——它受模式写法、工具实现与路径解析影响，本例中确凿出现误报（5 个技能目录均含目标文件，glob 两次返回 No files found）。目录条目是文件系统实况，模式匹配是推导，因此存在性判断的证据等级为：read 目录命中 > glob 命中（命中可直接采信，不会无中生有）> glob 空结果（不可单独证伪，必须复核）。注意：误报触发条件未查明，此结论属观察级。

## Approach
1. glob 返回空且该结论将影响动作时，先 read 上一级目录，确认子目录是否存在。
2. 子目录存在则逐层 read 到目标层级，检查目录条目中是否有目标文件；有即判"存在"，确无才可判"不存在"。
3. 记录结论时标注证据来源："read 目录条目证实"或"glob+read 双重空结果证伪"；禁止以单次 glob 空结果作为唯一依据。
4. glob 命中场景无需复核，直接采信命中结果。

## Faster Next Time
- 记忆口诀：glob 命中可信，glob 空结果存疑，read 目录定案。
- 批量探测存在性时，先 read 根目录拿子目录清单，再决定是否值得 glob；目录层级浅时直接 read 各子目录一次到位，比 glob+复核更快。
- 将"glob 空结果 + read 目录有文件"的实例留证，供平台方排查工具实现。
- 反模式：把"空结果即证伪"当无边界规则使用；因一次 glob 空结果改写"已有 X"类现状表述。

## Applicability Boundaries
- 适用：任何以 glob 空结果作为"不存在"依据的 Agent 场景（本例观察于 CodeArts 码道平台 + Windows；其他平台是否复现未验证）。
- 不适用：glob 命中的场景（命中可直接采信）；目标目录本身 read 失败的情况（权限/路径问题属另一类故障）。
- 局限：误报触发条件（模式写法、嵌套深度、缓存等）未定位，遇到矛盾时始终以 read 目录复核兜底。

## Evidence or Examples
- 会话 ses_e4f58d3e0ffebDYA8xP43bw3qm（项目 Date）：read `.codeartsdoer/skills` 目录确认 6 个条目（find-skills、grill-me、lazy-exec、ruleinit、skill-writer 及 ProjectSkillStatus.txt）后，glob 查 SKILL.md 两次均返回 No files found；随后逐个 read 五个技能子目录，均显示各自含 SKILL.md。执行方据此改判"每个技能目录下确有 SKILL.md（glob 误报）"。
- 与《派工单声称"已核实"的结构性前提，动手前仍用特征检索秒级复核》的关系：该条提出"空结果即证伪"，本条为其补充可靠性边界——空结果证伪前必须经 read 目录复核，单次 glob 空结果证据力不足。