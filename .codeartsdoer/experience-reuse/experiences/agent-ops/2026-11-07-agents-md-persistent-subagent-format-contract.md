---
id: 2026-11-07-agents-md-persistent-subagent-format-contract
title: 持久化子智能体格式契约实测：最小实例提取字段集 + listSkills 回读验证注册
category: agent-ops
nature: technique
created_at: 2026-11-07T07:07:01
updated_at: 2026-11-08T01:39:57
tags: [平台实证, 子智能体, 格式契约, 自动注册, 批量生成]
keywords: [agents目录, YAML frontmatter, 子智能体持久化注册, 最小实例反推, listSkills回读, tools白名单, permission.skill, 落盘即注册, 批量生成路径, mode字段]
problem_patterns: ["拿到最小实例后不知哪些字段构成必要契约、哪些可省略", "配置文件落盘后不确定是否真正注册生效，凭文件存在推断", "需要批量生成同类配置实体时凭猜测写字段导致注册失败"]
source_sessions: [ses_e4f5c5a83ffefUFnzHFvOEFJCW]
project: Date
severity: medium
quality_score: 91
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-07-minimal-instance-format-probing, 2026-11-07-listskills-agents-field-agent-topology-evidence, agent-ops/2026-11-08-listskills-enum-excludes-persistent-agents]
---

# 持久化子智能体格式契约实测：最小实例提取字段集 + listSkills 回读验证注册

## Scenario

沿用"最小实例反推格式法"（姊妹方法论经验）确认了"格式待反推"缺口后，用户已在平台前端手工创建 1 个最小测试子智能体。此时任务转为：把真实实例转化为可复用的**格式契约**（字段集与语义），并验证"文件落盘是否真的注册生效"——验证通过后，后端即可程序化批量生成同类配置实体，不再依赖前端逐个手工创建。

## Key Signals

- 前端创建动作完成后，磁盘随即出现实例文件（如 `agents/<name>.md`，约 1KB）——这是"持久化载体 + 落盘即注册"机制存在的直接信号。
- 实例文件 = YAML frontmatter（声明字段）+ 正文提示词（角色指令），与已验证的技能文件（SKILL.md）结构同构。
- 用 listSkills 复查时，既有技能条目的 `agents` 字段里**新增了实例名**——注册生效的权威回读信号，强于"文件存在"这一表象。

## Essence

格式契约的最短获取路径是"读最小实例 → 提取必要字段集 → 回读验证注册"。核心判据：**注册生效与否必须以清单工具的关联字段回读为准**（本平台为 listSkills 的 `agents` 字段），文件落盘只是必要条件而非充分证据；只有当运行时清单中出现该实体名，"落盘即注册"才从先例类比升级为实测结论。批量生成的本质 = 复制字段骨架 + 替换身份字段 + 按需收窄授权字段。

## Approach

1. **读实例文件提取字段契约**：逐字段记录 frontmatter 的字段名、取值形态与语义（身份字段如 description/scope/avatar；能力字段如 mode、tools 白名单布尔表；授权字段如 permission.skill 的通配 deny + 逐名 allow；开关字段如 disable）。
2. **listSkills 回读验证注册**：加载 schema 后调用一次清单工具，检索关联字段是否包含实例名；调用一次即可（同轮重复调用同一验证工具易触发循环保护，有结果即止）。
3. **对照姊妹资产确认同构性**：与已验证注册机制的同类文件（SKILL.md）逐字段对照，确认"frontmatter + 正文"双段结构通用，批量生成时可复用同一骨架。
4. **批量生成按契约执行**：复制字段骨架 → 换名（文件名即实体 ID）→ 改 description 与正文提示词 → 按需收窄 tools/permission（最小授权原则）→ 落盘 → 回读验证注册。
5. **实验品处置权归创建者**：用户手工创建的最小实例保留不动，是否转为正式资产由用户裁决，后端不擅自删除或改名。

## Faster Next Time

- 一句话规程：**批量生成配置实体 = 读最小实例 → 提字段契约 → 清单工具回读验证 → 复制骨架批量落盘**；禁止凭猜测写字段、禁止凭文件存在判注册。
- 警告信号：实例文件已落盘但清单工具关联字段无该名 → 注册未生效（检查 disable 开关、字段拼写、scope 归属），而非文件没写对位置。**前提限定**：本判据仅适用于有技能挂载的智能体；permission.skill 全 deny 且无技能挂载的智能体，关联字段必然无其名（枚举边界外），属正常现象而非注册失败，注册验证应转运行时派工实证，见 agent-ops/2026-11-08-listskills-enum-excludes-persistent-agents。
- 字段契约里优先关注授权字段（如 permission.skill 的 deny 通配 + allow 逐名模式）：它决定子智能体能力边界，批量生成时按"每个子智能体只授权其职责所需"收窄，避免全量放权。

## Applicability Boundaries

- 适用于：提供"配置文件落盘即注册"机制的 Agent 平台（实证于码道 CodeArts Agent 的 agents/*.md 子智能体注册）；已按最小实例反推法拿到 1 个真实实例的场景。
- 不适用于：注册需显式命令或平台审核的场景（此时文件落盘不等于注册）；无最小实例可参照时（应先走最小实例反推法，禁猜测格式）。
- 平台相关性：方法通用（最小实例 → 契约 → 回读验证），字段集与目录结构为码道平台实测细节，不可跨平台照搬；字段语义基于单例验证，批量生成前对非身份字段语义存疑时逐字段小步验证。

## Evidence or Examples

- 实录（2026-11-07，主会话 ses_e4f5c5a83ffefUFnzHFvOEFJCW）：用户前端创建最小测试子智能体后，`.codeartsdoer/agents/test_mini.md` 落盘（31 行）。frontmatter 实测字段集：`description`（一句话职责）、`mode: all`、`tools`（write/read/edit/bash/glob/grep/webfetch/CodeSemanticSearch/ComprehensiveSearch/GetFeatureTree/GetRemoteCallChain/deleteFile/browser 逐个布尔白名单）、`permission.skill`（`'*': deny` + ruleinit/skill-writer/lazy-exec/find-skills/grill-me 逐个 allow）、`disable: false`、`scope: project`、`avatar: avatar1`；正文为一段角色提示词（"最小测试子智能体，仅响应派工，用阅读/编辑工具，不关联技能，完成即退"）。
- 注册验证实录：listSkills 复查返回 50 条技能，find-skills/grill-me/lazy-exec/ruleinit/skill-writer 5 个 project 技能的 `agents` 字段均含 `test_mini`——文件落盘即注册实测成立。
- 姊妹方法论：三态可行性拆分与最小实例反推法见 2026-11-07-minimal-instance-format-probing（该篇写于实验前，明确标注"无实例可参照格式"；本篇为其闭环验证篇）；关联字段回读入口见 2026-11-07-listskills-agents-field-agent-topology-evidence。