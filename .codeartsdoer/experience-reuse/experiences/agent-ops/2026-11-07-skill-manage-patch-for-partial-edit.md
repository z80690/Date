---
id: 2026-11-07-skill-manage-patch-for-partial-edit
title: skill_manage 局部替换必须用 patch 动作：edit 的 frontmatter 校验报错是动作误用的误导性信号
category: agent-ops
nature: pitfall
created_at: 2026-11-07T18:31:30
updated_at: 2026-11-09T02:11:35
tags: [skill_manage, 技能演进, 平台API, 局部替换, 错误诊断, edit-tool, patch, tool-behavior]
keywords: [skill_manage, patch 动作, edit 全量 content, frontmatter 校验错误, 局部替换, 局部追加, 技能更新, 错误信息误导, 报错降级, 后台技能演进, 参数组合诊断, SKILL.md, action=edit, action=patch, 整文件替换]
problem_patterns: [用 skill_manage 的 edit 动做局部替换，反复报"SKILL.md must have name and description in frontmatter"但 frontmatter 实际完好, 误把报错当文件内容问题去反复修 frontmatter，连续多轮失败卡住技能更新, 需要对现有技能做小段增补/局部追加却不知道哪个动作支持 old_string/new_string, 向已有技能 SKILL.md 追加内容时被 frontmatter 校验拒绝，误判为需要整篇重写]
source_sessions: [ses_e4a7f3b4fffeEnN4ZZDzeCjyLV, ses_e4959da14ffejCAE7aMOLXLF5c]
project: Date
severity: high
quality_score: 91
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
utility_score: 90
tier: S
related_experiences: [2026-11-07-experience-system-auto-skill-evolution, 2026-11-06-skill-doc-env-mismatch-fallback, 2026-11-07-write-receipt-not-proof-of-persistence, 2026-11-09-skill-manage-folded-frontmatter-channel-matrix]
---

# skill_manage 局部替换必须用 patch 动作：edit 的 frontmatter 校验报错是动作误用的误导性信号

## Scenario

后台技能演进流程（background-evolve-skills 等）需要对 generated-skills 下已存在的 SKILL.md 做局部增补/修改。调用 skill_manage 的 `edit` 动作：带增量 content 与不带 content 两种参数组合连续失败共 8 次，浪费两轮批量调用；换 `patch` 动作后 4 个补丁一轮全部成功。评审会话后的技能沉淀是同一高发场景：几乎全是向已有技能局部追加章节/修正段落，可直接跳过 edit 走 patch，省一次失败往返。

## Key Signals

- `action=edit`（带增量 content）→ `{"ok": false, "error": "SKILL.md must have name and description in frontmatter"}`
- 去掉 content 只传替换意图 → 同样报错（复现 4 次，参数形态已换仍失败）
- 目标文件 frontmatter 实际完好（name/description 均在），报错与文件真实状态矛盾
- `action=patch`（old_string + new_string）→ 4 个补丁全部 `{"ok": true}`

## Essence

报错文案把"动作选错"伪装成"内容不合规"：edit 按整文件覆盖语义校验 content（增量片段或缺失时 frontmatter 校验必然失败），于是表面上的 frontmatter 错误诱导 Agent 去修内容、换参数形态，形成无效重试循环。局部替换的正确入口是 patch。平台工具的报错要优先怀疑"动作语义/参数组合"，其次才是目标内容。

## Approach

1. 更新需求分型：整文件重写 → edit（content 必须是含 frontmatter 的完整文件）；局部增补/替换 → patch（old_string + new_string，不带 content）
2. 见到 "SKILL.md must have name and description in frontmatter"：先核对动作类型与参数组合，不要先动 frontmatter
3. 同一报错重复出现 2 次即停止同参数形态重试，换动作而非换内容
4. 多个独立补丁可一轮并行发（本例 4 处补丁单轮全过，符合批量并行写纪律）
5. patch 返回 `ok:true` 即权威回执——这与文件系统级 write 不同（write 回执≠落盘成功，须列目录/读文件实测），动作语义以工具自身 ok 字段为准
6. 已误用 edit 并收到该报错时，直接改走 patch 成本最低——不要试图只补 name/description 两行，那是整文件替换语义的校验，补字段绕不过动作语义错配

## Faster Next Time

- 技能更新决策表：改 description/正文一小段 → patch；结构性大改/重建 frontmatter → edit + 全量 content（仅限扁平样式 frontmatter，见 2026-11-09-skill-manage-folded-frontmatter-channel-matrix）；新建技能 → create
- 连续同文案报错是"动作误用"的强信号，不是"内容有错"的强信号
- 排查顺序固化：报错 → 对表（动作×参数组合）→ 换动作 → 成功；跳过"反复修内容"分支

## Applicability Boundaries

- 适用：码道 skill_manage 工具（本环境两次独立会话实测）；其他"整文件覆盖语义 + frontmatter 校验"类平台管理工具可类比
- 不适用：文件系统级 write/edit 工具（write 回执不能证明落盘，须实测；且 Read/Edit 类工具的 edit 本身就是局部替换语义，与 skill_manage 的 edit 整文件覆盖语义相反——同名动作语义因工具而异，切换工具时先确认语义）
- "edit 需全量 content"是从失败序列反推的结论（未用全量 content 复验 edit 成功路径），属推断；"patch 可用且可靠"为实证。2026-11-09 对照实验实证修正：edit 的校验器不认 YAML 折叠样式（`>-`）frontmatter，即使 content 为完整合法文件 edit 也会被拒——"edit 可行域 = 全量 content + 扁平样式"，折叠样式一律改走 patch_frontmatter/patch（见 2026-11-09-skill-manage-folded-frontmatter-channel-matrix）

## Evidence or Examples

- 2026-11-07 会话（ses_e4a7f3b4fffeEnN4ZZDzeCjyLV）：edit×4（带 content）失败 → edit×4（不带 content）失败 → patch×4 成功，共 8 失败/4 成功，两轮批量调用被浪费
- 2026-11-08 会话独立复现（评审→沉淀场景，ses_e4959da14ffejCAE7aMOLXLF5c）：action=edit 只传新增章节 → 同文案报错；改 action=patch 局部替换 → ok:true。两次独立会话复现同一误用信号，报错文案的误导性成立
- 涉及技能：web-content-scraping、sdd-spec-pipeline（generated-skills 目录）
- 错误文案原文：`SKILL.md must have name and description in frontmatter`（与文件真实状态矛盾即为误用信号）