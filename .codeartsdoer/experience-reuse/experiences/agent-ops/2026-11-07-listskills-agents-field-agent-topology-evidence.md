---
id: 2026-11-07-listskills-agents-field-agent-topology-evidence
title: listSkills 的 agents 字段是平台主/子智能体拓扑的一手实证入口
category: agent-ops
nature: technique
created_at: 2026-11-07T06:27:00
updated_at: 2026-11-07T06:27:00
tags: [平台实证, 主子智能体, listSkills, AgentTeam, 能力盘点]
keywords: [listSkills, agents字段, 主智能体, 子智能体, 两级形态, scope分层, system/project, cloud_enterprise, AgentTeam, 配置载体, 空目录枚举]
problem_patterns: [调研平台智能体体系时不知主/子智能体真实形态与配置载体在哪, 需要实证"平台有哪些主/子智能体及其关联"却没有显式的智能体清单API, 凭设置面板截图或二手信息写平台能力结论无法溯源]
source_sessions: [ses_e4d11ce50ffesKQFm6qpmDfFP0]
project: Date
severity: medium
quality_score: 86
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-06-codeartsdoer-skill-market-registry, 2026-11-06-glob-empty-result-read-verify, 2026-11-06-tool-language-filter-false-empty-result]
---

# listSkills 的 agents 字段是平台主/子智能体拓扑的一手实证入口

## Scenario

接到"调研平台智能体体系"类任务（如主/子智能体方案设计、AgentTeam 对标、前后端创建能力边界分析）时，平台通常不提供显式的"智能体清单 API"，本地配置目录（agent-team/、agents/）的语义也不明。此时容易凭用户截图、面板印象或推断写平台能力结论，无法溯源也无法验证。

## Key Signals

- 手头只有二手信息：设置面板截图、用户口述、"系统内置有 N 个主智能体"之类描述。
- 本地存在疑似配置载体目录但为空，语义未知。
- 派工单要求"能力边界实证"，而平台文档检索暂无结果或不可达。

## Essence

`listSkills` 返回的每条技能记录里的 `agents` 字段直接暴露"技能 ↔ 智能体"的关联关系：被同一组子智能体共同关联的主智能体（或按 agents 聚类）可还原出平台的主/子智能体两级拓扑；`scope` 字段给出三层归属（system/project/cloud_enterprise），对应平台智能体层级语义。配合本地配置目录的实存性检查，可在不动平台配置的前提下拼出实证拓扑。

## Approach

1. 用 `tool_describe` 加载 listSkills 的 schema 后立即调用（schema 已在手则勿重复 describe），拉取全量清单，记录 `totalCount` 防截断误判。
2. 按 `skills[].agents` 字段聚合：把共享同一 agents 集合的技能归簇，得到"主智能体→子智能体"映射；单独出现的系统技能不计入拓扑。
3. 记录 `scope` 的实际取值分布（如 system/project/cloud_enterprise），与平台层级语义对齐。
4. 目录枚举平台本地配置区（如 `.codeartsdoer/`），对疑似载体目录（agent-team/、agents/）用 glob 查文件非空性；注意 glob 不返回空目录本身，空目录要靠目录枚举单独下结论。
5. 把结论分两列写："已实证"（工具返回、目录实存）与"推断"（字段语义解读），推断项标证据等级，重大决策前二次验证。

## Faster Next Time

- 先 listSkills 后查文档：一次调用即可拿到拓扑骨架，省去文档空手翻。
- agents 字段聚合替代配置猜解：不需要逆向配置文件格式。
- 空目录结论必须来自目录枚举而非 glob 空结果，避免"不存在"误判。
- 三层 scope 值是层级映射的现成判据，可直接用于四层级语义对齐。

## Applicability Boundaries

- 适用于提供 listSkills（或等价技能/智能体清单工具）且返回体含 agents 关联字段的 Agent 平台（实证于码道 CodeArts Agent）。
- 单次实证只能确认被验证案例的映射；其余主/子关联属推断，需逐例验证后才可写入正式结论。
- 不适用于：平台无技能清单工具的场景（应转为配置文件逆向或文档检索）；agents 字段语义的官方口径与实证不符时以官方口径为准。

## Evidence or Examples

- 本会话（ses_e4d11ce50ffesKQFm6qpmDfFP0）实证：listSkills 返回 50 条技能（totalCount=50，truncated=false）；「鸿蒙开发」主智能体关联 harmonyos-ascf、harmonyos-plugin 两个子智能体，呈两级形态；scope 实际取值含 system/project/cloud_enterprise 三层。
- 本地实查：`.codeartsdoer/agent-team/` 与 `agents/` 两目录实存但为空（与派工单 files=0 交叉印证）；skills/.codeartsdoer/skills/<id>/SKILL.md 落盘后 ProjectSkillStatus.txt 自动出现注册状态（旁证"落盘即注册"机制）。
- agents 字段语义解读属推断（单例验证），非官方文档口径，已在结论中标注。