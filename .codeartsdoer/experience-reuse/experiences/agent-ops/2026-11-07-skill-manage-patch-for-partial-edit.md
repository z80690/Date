---
id: 2026-11-07-skill-manage-patch-for-partial-edit
title: skill_manage 局部替换必须用 patch 动作：edit 的 frontmatter 校验报错是动作误用的误导性信号
category: agent-ops
nature: pitfall
created_at: 2026-11-07T18:31:30
updated_at: 2026-11-07T18:51:27
tags: [skill_manage, 技能演进, 平台API, 局部替换, 错误诊断]
keywords: [skill_manage, patch 动作, edit 全量 content, frontmatter 校验错误, 局部替换, 技能更新, 错误信息误导, 后台技能演进, 参数组合诊断, SKILL.md]
problem_patterns: [用 skill_manage 的 edit 动做局部替换，反复报"SKILL.md must have name and description in frontmatter"但 frontmatter 实际完好, 误把报错当文件内容问题去反复修 frontmatter，连续多轮失败卡住技能更新, 需要对现有技能做小段增补却不知道哪个动作支持 old_string/new_string]
source_sessions: [ses_e4a7f3b4fffeEnN4ZZDzeCjyLV]
project: Date
severity: high
quality_score: 90
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
utility_score: 90
tier: S
related_experiences: [2026-11-07-experience-system-auto-skill-evolution, 2026-11-06-skill-doc-env-mismatch-fallback, 2026-11-07-write-receipt-not-proof-of-persistence]
---

# skill_manage 局部替换必须用 patch 动作：edit 的 frontmatter 校验报错是动作误用的误导性信号

## Scenario

后台技能演进流程（background-evolve-skills 等）需要对 generated-skills 下已存在的 SKILL.md 做局部增补/修改。调用 skill_manage 的 `edit` 动作：带增量 content 与不带 content 两种参数组合连续失败共 8 次，浪费两轮批量调用；换 `patch` 动作后 4 个补丁一轮全部成功。

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

## Faster Next Time

- 技能更新决策表：改 description/正文一小段 → patch；结构性大改 → edit + 全量 content
- 连续同文案报错是"动作误用"的强信号，不是"内容有错"的强信号
- 排查顺序固化：报错 → 对表（动作×参数组合）→ 换动作 → 成功；跳过"反复修内容"分支

## Applicability Boundaries

- 适用：码道 skill_manage 工具（本环境实测）；其他"整文件覆盖语义 + frontmatter 校验"类平台管理工具可类比
- 不适用：文件系统级 write/edit 工具（write 回执不能证明落盘，须实测；两者回执语义不同，勿混用处置）
- "edit 需全量 content"是从失败序列反推的结论（未用全量 content 复验 edit 成功路径），属推断；"patch 可用且可靠"为实证

## Evidence or Examples

- 2026-11-07 会话：edit×4（带 content）失败 → edit×4（不带 content）失败 → patch×4 成功，共 8 失败/4 成功，两轮批量调用被浪费
- 涉及技能：web-content-scraping、sdd-spec-pipeline（generated-skills 目录）
- 错误文案原文：`SKILL.md must have name and description in frontmatter`（与文件真实状态矛盾即为误用信号）