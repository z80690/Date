---
id: 2026-11-08-skill-manage-edit-vs-patch
title: 技能库局部增改应选 patch 而非 edit：edit 是整文件替换且强制校验 frontmatter
category: agent-ops
nature: pitfall
created_at: 2026-11-08T10:46:13
updated_at: 2026-11-08T10:49:52
tags: [skill-management, edit-tool, patch, frontmatter, tool-behavior]
keywords: [skill_manage, action=edit, action=patch, 整文件替换, frontmatter 校验, SKILL.md, 局部追加, 报错降级]
problem_patterns:
  - 向已有技能 SKILL.md 追加内容时被 frontmatter 校验拒绝
  - 需要局部修改技能正文段落而非整篇重写
source_sessions: [ses_e4959da14ffejCAE7aMOLXLF5c]
project: Date
severity: medium
quality_score: 86
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-07-skill-manage-patch-for-partial-edit]
---

> **[ARCHIVED 2026-11-08 refine]** 已并入主文件《skill_manage 局部替换必须用 patch 动作：edit 的 frontmatter 校验报错是动作误用的误导性信号》（agent-ops/2026-11-07-skill-manage-patch-for-partial-edit.md）。归档原因：与主文件同问题模式、同方法与同证据链（skill_manage edit 报 frontmatter 校验错误 → 改走 patch），核心结论重复，加权相似度约 0.83，属冗余条目。本文件独有增量（误用 edit 后的重定向路径、Read/Edit 工具语义区分、新建技能用 create、评审→沉淀高发场景提示）已并入主文件 Approach / Applicability Boundaries / Scenario 对应节；本文件仅作历史证据与溯源存档，检索命中时以主文件为准。

# 技能库局部增改应选 patch 而非 edit：edit 是整文件替换且强制校验 frontmatter

## Scenario

技能评审/沉淀场景：会话结束后向一个**已存在**的技能（generated-skills 目录下的 SKILL.md）追加一个新章节或修正局部段落。操作者容易按普通文件编辑的直觉选用 `skill_manage` 的 `action=edit` 并只提供增量内容，导致失败。

## Key Signals

- 调用 `skill_manage action=edit`、只传新增段落内容（不带完整原文件+frontmatter）时，返回 `ok: false, error: "SKILL.md must have name and description in frontmatter"`。
- 该报错看似"frontmatter 缺失"，实际含义是：edit 要求 content 是**完整的替换后全文**（含 name/description 的 frontmatter），而不是本次要追加的增量。

## Essence

`skill_manage` 的两个写操作语义完全不同：

- `edit`（及 `create`/`write_file`）：整文件替换语义，content 必须是含合法 frontmatter（name、description 必填）的完整 SKILL.md。
- `patch`：真正的局部替换语义，用 old_string/new_string 做片段级修改，不需要动 frontmatter。

向已有技能追加内容时，拿到的往往是"增量"，用 edit 就会撞上 frontmatter 校验。

## Approach

1. 判定操作类型：局部追加/局部修正 → 直接用 `action=patch`（old_string 取目标段落原文，new_string 为替换后文本）。
2. 仅当需要整篇重写、迁移结构或重建 frontmatter 时才用 `action=edit`，且 content 必须含完整原内容+完整 frontmatter。
3. 若已误用 edit 并收到 frontmatter 报错，不要试图只补 name/description 两行——那是整文件替换的校验，直接改走 patch 成本最低。
4. patch 成功的返回是 `ok: true`，无需读回文件验证（工具语义保证替换成功）。

## Faster Next Time

- 默认动作记忆：**已有技能改内容=patch；新建/重写技能=edit/create**。
- 见到 "must have name and description in frontmatter" 报错，第一反应应是"我用了整文件替换语义但只给了增量"，而不是去补 frontmatter 字段。
- 评审类后台任务（评审会话→沉淀技能）几乎全是局部追加，可跳过尝试 edit 直接 patch，省一次失败往返。

## Applicability Boundaries

- 适用：generated-skills 技能管理通道的 `skill_manage` 工具（CodeArts 码道平台）。
- 不适用：普通文件的 Read/Edit 工具（其 edit 本身就是局部替换语义，行为不同）；技能目录之外的文件管理。
- 未验证：edit 是否对其他附属文件（如 skill 内 reference 文件）同样强制 frontmatter——本经验仅基于 SKILL.md 的实测。

## Evidence or Examples

- 实测序列（2026-11-08 会话）：`skill_manage action=edit`（只传新增章节）→ `ok:false, error "SKILL.md must have name and description in frontmatter"`；改用 `action=patch`（old_string/new_string 局部替换）→ `ok:true`。
- 本经验由该次评审会话的技能沉淀动作直接取证，属于工具行为发现而非文档推断。