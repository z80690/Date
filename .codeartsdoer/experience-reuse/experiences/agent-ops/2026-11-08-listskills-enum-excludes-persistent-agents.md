---
id: 2026-11-08-listskills-enum-excludes-persistent-agents
title: listSkills 枚举不单列持久化子智能体，"查不到"≠"未注册"，派工实行为权威验证
category: agent-ops
nature: technique
created_at: 2026-11-08T01:22:36
updated_at: 2026-11-08T01:39:57
tags: [注册验证, 子智能体, listSkills边界, 行为指纹, 运行时实证]
keywords: [listSkills, 枚举边界, 持久化子智能体, agents/*.md, 全deny权限, 注册生效, 行为指纹比对, 派工实证, 会话边界, 验收记录]
problem_patterns: ["改造 agents/*.md 子智能体配置后查 listSkills 找不到该智能体，误判为未注册而重复注册或误报失败", "子智能体权限全 deny 时清单与挂载字段均无痕迹，无法用静态清单确认注册状态", "验收记录写'listSkills 核对通过'但清单根本不覆盖该类实体，验证方法本身无效"]
source_sessions: [ses_e4901eb75ffel23pcFPtONtVPN]
project: Date
severity: medium
quality_score: 85
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-07-listskills-agents-field-agent-topology-evidence, 2026-11-07-agents-md-persistent-subagent-format-contract, 2026-11-07-subagent-delivery-spot-check-acceptance]
---

# listSkills 枚举不单列持久化子智能体，"查不到"≠"未注册"，派工实行为权威验证

## Scenario

改造 `agents/*.md` 持久化子智能体配置（如 SOP 收窄、触发条件改写）后，需要验证"注册是否生效、新配置是否在实际运行"。直觉动作是查 listSkills，但清单主列表中查不到该智能体名——此时不能直接判"未注册"或重复注册。

## Key Signals

- listSkills 返回 N 项，逐项核对全部为 `skills/*/SKILL.md` 技能条目，无任何 `agents/*.md` 智能体条目。
- 该智能体 `permission.skill` 为全 deny（`'*': deny` 且无 allow 白名单）时，连任何技能记录的 agents 挂载字段都不会出现它的名字——静态清单完全无痕迹。
- 但按其派工后实际运行成功，且执行行为逐项对齐现行配置文件（步骤数、自检项、产物结构一致）。

## Essence

listSkills 的枚举边界是**技能清单**，不是智能体注册表——持久化子智能体不出现在枚举主列表中，全 deny 权限的智能体更无挂载痕迹。"枚举查不到"有三种互斥可能：未注册 / 枚举边界外 / 权限无挂载痕迹，单凭清单缺失不能判"未注册"。注册生效的权威验证是**运行时派工实证**：从配置文件提取可观测行为指纹（SOP 步骤数、必做自检项、产物结构约定），派工后逐项比对返回摘要与产物——行为指纹对齐现行配置即证明新版配置在跑。

## Approach

1. 分层验证序列：①磁盘实存（`agents/<id>.md` 存在且非空）→ ②listSkills 交叉（仅当该智能体有技能挂载时有迹可循）→ ③Task 派工实际运行（权威级）。
2. 行为指纹比对：派工前从配置文件提取可观测指纹清单（SOP 步骤编号、必报自检结论、产物文件结构），运行后逐项比对子代理返回摘要与落盘产物，一致即"新版配置已生效"。
3. 枚举缺席时先归因三选一（未注册 / 枚举边界外 / 权限无挂载痕迹）再决定是否处置——边界外属正常现象，无需修复。
4. 会话边界问题按预案登记：若怀疑注册状态受会话加载时机影响，登记现象后换新会话复验，不以单会话清单下定论。
5. 验收记录写"运行时派工实证 + 行为指纹比对通过"，不写"listSkills 核对通过"（后者对持久化子智能体是无效验证方法）。

## Faster Next Time

- 判断顺序口诀：**"磁盘文件 → 派工实跑 → 行为对指纹；清单缺席不算数。"**
- 配置改造类验收在设计期就把"可观测行为指纹"写进配置（固定步骤编号、必报自检结论、固定产物结构），运行后才有可比对项。
- 成本对比：静态清单核查是零成本但无效；派工实证一次派工的成本换来的是"新版配置确实在跑"的强证据。

## Applicability Boundaries

- 适用：`agents/*.md` 式持久化子智能体的注册/改造验收，特别是权限全 deny、无技能挂载痕迹的智能体。
- 不适用：普通 SKILL.md 技能（listSkills 直接可见，无需运行时实证）；临时 Task Worker（本就无持久化注册概念）；disable=true 的智能体（属主动退出，不是验证问题）。
- 平台：实证于 CodeArts 码道平台；"清单 ≠ 注册表"的原理在其他 Agent 平台同样成立，但枚举具体形态以各平台实测为准。
- 与相邻经验分工：用 listSkills 的 agents 字段还原平台智能体拓扑见 2026-11-07-listskills-agents-field-agent-topology-evidence（顶层调研用途）；agents/*.md 配置格式契约见 2026-11-07-agents-md-persistent-subagent-format-contract——本条聚焦"注册/改造验收的验证方法与枚举边界陷阱"。
- 前提差异决策规则（对 format-contract "清单回读为准"结论的适用前提收窄）：智能体**有技能挂载**（permission.skill 含 allow）→ 清单关联字段回读有效，"关联字段无该名 → 注册未生效"判据成立；智能体**全 deny 无挂载**（如出题官/批改官）→ 关联字段必然无其名，属枚举边界外的正常现象而非注册失败，注册验证必须转运行时派工实证（本条方法）。两条经验按"有无技能挂载"分治，不冲突。

## Evidence or Examples

- 实测：listSkills 返回 58 项（totalCount=58，truncated=false），全部为技能条目，无一为 agents/*.md 智能体；出题官/批改官两智能体权限均为全 deny，任何技能记录的 agents 字段均无其名。
- 运行时实证：R1（正式考核）、V1（可运行验证）、OLD（对比测试）三轮派工均成功运行；V1 轮出题官返回摘要含六步 SOP 逐步结论（与新版 v2 配置的六步结构一一对应），批改官报告结构与新版配置约定一致——行为指纹比对通过，新版配置确在运行。
- 结论留痕方式：M3 改造门验收按本方法写"派工实证+行为指纹对齐"，并将枚举缺席现象登记为会话边界可见性问题（预案：新会话复验）。