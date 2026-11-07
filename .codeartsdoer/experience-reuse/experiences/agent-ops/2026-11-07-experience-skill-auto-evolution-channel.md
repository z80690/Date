---
id: 2026-11-07-experience-skill-auto-evolution-channel
title: 经验系统自动技能化产物的识别、核验与登记闭环
category: agent-ops
nature: technique
created_at: 2026-11-07T09:43:58
updated_at: 2026-11-07T09:49:33
tags: [experience-system, auto-skill-evolution, registration, agent-ops, codearts]
keywords: [ProjectSkillStatus, listSkills, generated-skills, background-evolve-skills, skill-evolution-workspace, 经验技能化, 自动注册, register-feature, 未创建技能目录, U编号登记]
problem_patterns: [项目技能目录出现执行方未创建的技能目录, 需判定平台自动产物与异常产物的定性并登记]
source_sessions: [ses_e4c659edfffeZ7DQtPEcp0LFr9]
project: Date
severity: medium
quality_score: 86
hit_count: 1
last_hit_at: 2026-11-08T01:26:23
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-07-listskills-agents-field-agent-topology-evidence, 2026-11-07-experience-system-auto-skill-evolution]
---

# 经验系统自动技能化产物的识别、核验与登记闭环

## Scenario

智能体平台启用了经验库（experience-reuse）与技能自动注册机制时，执行方完成一个长会话后发现项目技能目录（如 `.codeartsdoer/skills/`）下出现了**自己从未创建**的技能目录（git status 显示为未跟踪 `?? skills/<name>/`）。此时需要判定：这是平台自动产物还是异常/外来产物，以及是否可以引用与登记。

## Key Signals

三条信号齐备即可定性为"经验系统自动技能化产物"（内容指纹 + 注册实证双确认）：

1. **内容指纹命中本会话知识**：新目录的 SKILL.md 内容是对本次会话反复出现的实战经验的知识化提炼（如平台注册机制、流程契约、环境怪癖），而非凭空或外来内容。
2. **状态文件自动登记**：平台技能状态文件（如 ProjectSkillStatus.txt）自动追加了 `<skill-name>=true`，执行方未做任何写入。
3. **运行时权威源可见**：listSkills 返回该技能 `scope=project, status=enabled`，description 完整可读。

同时，经验演化工作区（用户级 `evolve/skill_evolution_workspace/generated-skills/`）存在同名 SKILL.md，会话后台存在技能演化审查器（background-evolve-skills 类机制）的执行痕迹。

## Essence

平台的经验演化系统会把会话中沉淀的高价值经验**自动转化为技能文件**（SKILL.md）并**落盘即注册**（与手工创建技能走同一注册通道）。产物合法、可信、可直接引用；但"磁盘存在+平台注册"不等于"治理层登记完成"——注册表/索引/授权流程仍需按新功能准入走完，否则会出现"能力在跑、台账无名"的治理缺口。

## Approach

1. **定性**：先读新目录 SKILL.md 的内容，比对是否为本会话/近期会话经验的知识化提炼；内容指纹命中 → 平台自动产物；无关内容 → 按异常处理并呈报。
2. **核验**：双源交叉确认注册状态——状态文件（自动登记项）+ listSkills（scope/status/agents 挂载关系）；两源一致才采信"已注册"。
3. **不擅自删除**：即使暂时不需要，也保留（禁物理删除），因为它是平台托管的注册源；禁用类操作走平台 frontmatter 的 `disable` 开关。
4. **授权后登记**：向用户呈报清单并请求登记授权；获批后按新功能准入流程（如 register-feature 五步准入精神）补登注册表条目与知识库索引，并用 U 编号登记未决项收口，最后版本提交留痕。

## Faster Next Time

- git status 中首次出现 `?? skills/<新目录>/` 时，**先读 SKILL.md 内容定性，再决定处置**，不要按"未知文件"一律警惕或一律接纳。
- 登记动作一次批量完成（注册表 N 行 + 索引 + U 收口 + 提交），避免多轮往返。
- 见到"未创建却已注册"的能力时，先怀疑经验演化通道，再怀疑外来注入——前者有状态文件与运行时双实证可自证。

## Applicability Boundaries

- 适用：启用经验库/技能自动注册机制的智能体平台（实证于 CodeArts 码道平台，Windows 环境）；同样适用于判定 MCP 配置、agents 定义等其他"落盘即注册"载体的意外产物。
- 不适用：无技能自动注册机制的环境——那里未创建的目录默认按外来产物处理，须人工审查来源。
- 平台将项目级 skills 目录与用户级演化工作区同步的细节机制为【推断】，未逐层实证；两处同名文件的一致性维护由平台托管，执行方只读引用。
- 与 related: 2026-11-07-experience-system-auto-skill-evolution 的分工：该经验覆盖后台演进代理自身的沉淀纪律（双载体查重、更新优先于新建）与双源边界；本经验聚焦执行代理侧的定性核验（三信号）与治理登记闭环（注册表/索引/U 编号）。

## Evidence or Examples

- 实例：某长会话结束后发现 3 个未创建技能目录（codearts-platform-registration / sdd-spec-pipeline / windows-git-powershell-quirks），SKILL.md 内容分别是本次会话实证的平台注册机制、SDD 派工契约、Windows 环境怪癖的经验提炼；ProjectSkillStatus.txt 自动出现 3 条 `=true`；listSkills 显示 56 技能中 3 个新技能 `scope=project, status=enabled`。
- 登记结果：用户授权后注册表补 3 行（挂载项增至 19），索引技能层与 U 区同步收口，随提交 `d4e57a7` 入库。
- 佐证：技能演化工作区路径（用户级 `evolve/skill_evolution_workspace/generated-skills/`）与后台审查器的 skill_view/skill_manage 操作记录在案。