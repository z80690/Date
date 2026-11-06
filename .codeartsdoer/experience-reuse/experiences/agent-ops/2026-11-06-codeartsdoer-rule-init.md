---
id: 2026-11-06-codeartsdoer-rule-init
title: 码道项目级规则初始化：界面创建路径与生效验证
category: agent-ops
nature: pitfall
created_at: 2026-11-06T18:41:59
updated_at: 2026-11-06T18:41:59
tags: [codeartsdoer, rule-init, platform-behavior, ide-configuration]
keywords: [码道, CodeArts Agent, 规则初始化, 规则不生效, 裸md文件, .mdc, metadata.properties, projectExpert, 自动应用, 生效验证]
problem_patterns: [手动写入规则目录的文件不被平台加载, 手改 metadata.properties 触犯平台托管约束, 无法确认规则是否真实生效]
source_sessions: [ses_e51adb269ffeqfVMdEGO1eP4xa]
project: Date
severity: medium
quality_score: 94
hit_count: 2
last_hit_at: 2026-11-06T19:43:20
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-06-codeartsdoer-rule-vs-skill, 2026-11-06-codeartsdoer-docs-retrieval]
---

# 码道项目级规则初始化：界面创建路径与生效验证

## Scenario
需要让智能体遵守项目协作约定（行为约束、门禁、纪律），为项目初始化码道（华为云 CodeArts Agent）项目级规则时。平台对 rule 目录的托管方式与直觉相悖，走错路径会导致"写了文件但规则不生效"。

## Key Signals
- 往 `.codeartsdoer/rule/` 手动扔裸 `.md`/`.mdc` 文件：平台不加载，规则不生效；且违反复确认的门禁（G1）。
- 直接编辑 `metadata.properties` 里的 `projectExpert=[]`：该文件由平台托管，手改属违规（G6），且可能被平台覆写导致"生效不可证"。
- 误判信号：目录里文件存在 ≠ 规则生效；判断生效必须看上下文注入与元数据双向印证。

## Essence
rule 目录文件（`.mdc` 正文 + `metadata.properties` 元数据）全部由平台托管生成，Agent/用户手写文件不进入加载链。规则在对话开始时由平台注入上下文（triggerType=always 的规则全量注入），这才是生效的物理证据。

## Approach
1. 走 IDE 界面创建：设置 → 技能与规则 → 项目级 → 新建规则；填三项：名称、适用范围选"自动应用"、内容。
2. 内容只写原则与动词（"禁止/必须"句式），不写路径、命令参数、临时步骤；单条控制在数行内。
3. 创建后平台自动生成 `rule/<规则名>.mdc` 并把 `projectExpert` 从 `[]` 更新为含 name/triggerType/source/absolutePath 的条目——不手改，只读核对。
4. 生效验证（无需重启会话）：① 目录齐套核对（`.mdc` + `metadata.properties`，无裸文件）；② `metadata.properties` 中 projectExpert 非空且 triggerType=always；③ 让智能体复述规则全文，与写入内容逐字比对——会话上下文已注入即为生效直接证据。

## Faster Next Time
- 同名规则优先级（官方口径）：云端企业级 > 云端团队级 > 本地项目级 > 本地个人级 > 云端个人级；无云端规则时冲突以本地项目级为准。
- always 规则每次会话全量注入、持续占上下文——数量保持克制（单条约数百字以内健康）。
- 遇到"规则要不要手改文件"类请求，先停下提示改走界面创建，再做齐套核对。

## Applicability Boundaries
- 适用于华为云码道 CodeArts Agent（IDE 客户端本地规则机制）；个人级规则路径同理（`%USERPROFILE%/.codeartsdoer/rule`）。
- 不适用于其他 Agent 平台（如 Cursor 的 .cursorrules 可手写，机制不同）。

## Evidence or Examples
- 实测：界面创建后平台生成 `rule/协作原则.mdc`（600B）并更新 `metadata.properties`，projectExpert 由 `[]` 变为含 `"triggerType":"always","source":"project"` 的条目（平台写入，916B）。
- 实测：新会话中规则内容出现在 session-rules 注入块，智能体逐字复述成功，与 metadata.content 完全一致。
- 平台自带 `.codeartsdoer/.gitignore`（内容 `*`）会把整个 rule 目录排除出 git——版本管理策略需另行考虑。