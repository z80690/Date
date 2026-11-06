---
id: 2026-11-06-codeartsdoer-skill-market-registry
title: 码道项目技能的落盘识别机制与市场查询通道
category: agent-ops
nature: technique
created_at: 2026-11-06T19:01:59
updated_at: 2026-11-06T19:19:17
tags: [codeartsdoer, skill-registry, marketplace, listskills, project-skill]
keywords: [码道, CodeArts Agent, 技能识别, 落盘即扫描, ProjectSkillStatus, listSkills, queryUserSkillList, 技能市场, 手搓技能, SKILL.md]
problem_patterns: [手搓的 SKILL.md 不确定是否被平台识别, 需要确认市场里有没有现成技能再决定是否手搓, 技能开关状态与界面显示对不上]
source_sessions: [ses_e51adb269ffeqfVMdEGO1eP4xa]
project: Date
severity: low
quality_score: 87
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-06-codeartsdoer-rule-vs-skill, 2026-11-06-parallel-tool-call-doom-loop]
---

# 码道项目技能的落盘识别机制与市场查询通道

## Scenario
在码道（CodeArts Agent）项目中手搓新技能（SKILL.md）后需要确认平台已识别；或接到"先查市场有没有现成技能、没有再手搓"类任务时，需要可复用的查询与验证通道。

## Key Signals
- "装好了没有"的困惑：SKILL.md 落盘后界面无动静——实际是**落盘即被平台扫描**，无需界面注册动作，用 listSkills 验证即可。
- 市场查询返回 `total: 0` 且技能列表为空：市场当前无现成技能（或该账号无可用技能），这是"手搓"决策的直接依据，不是工具故障。
- 技能开关状态存于项目 `.codeartsdoer/skills/ProjectSkillStatus.txt`（每行 `技能名=true/false`）——注意源文件行尾无换行时，向其追加内容会发生文本拼接污染。

## Essence
项目技能的发现链路是文件系统驱动的：`skills/<name>/SKILL.md` 落盘 → 平台动态扫描进 listSkills 清单（scope=project）；启用开关由 ProjectSkillStatus.txt 托管（与界面开关双向同步）。市场侧与本地侧是两个独立通道：`queryUserSkillList` 查云端市场，`listSkills` 查本地已识别技能——先市场后手搓的决策顺序依赖这两个通道各自可用。

## Approach
1. 查市场：调用 `queryUserSkillList`（可按 skillName 精确过滤），返回 `total=0` 即确认无现成件，转手搓。
2. 手搓落盘：在项目 `.codeartsdoer/skills/<kebab-case-name>/SKILL.md` 写入合规内容（frontmatter 与触发条件规范见关联经验），文件名严格为 `SKILL.md`（全大写）。
3. 验证识别：调用 `listSkills`，确认新技能以 `scope: "project", status: "enabled"` 出现在清单——一次调用即完成验证，勿重复调用（重复验证会触发平台循环保护，见关联经验）。
4. 开关核对：读 `ProjectSkillStatus.txt` 对照界面开关；向该文件追加条目前先确认原文件行尾有换行，追加后回读核对无拼接污染。
5. 触发边界自查：新技能 description 的触发词与相邻技能互斥（各含"不适用于…"句），防止模糊请求下同时命中。

## Faster Next Time
- 决策顺序固定：queryUserSkillList（市场）→ 无 → 手搓 → listSkills（识别验证）→ 状态文件核对，四步一天完成，不反复试界面。
- "落盘即识别"省掉了找界面注册入口的时间——写完直接 listSkills 验证，不要等界面刷新。
- 状态文件行尾检查是一行 `Get-Content -Raw` 的成本，能避免一次拼接污染修复。

## Applicability Boundaries
- 适用于码道 CodeArts Agent 的项目级技能（`project` scope）；系统级技能（scope=system）由平台内置不可手搓；云端技能走控制台，不在本地文件链路。
- 市场查询结果与账号权益相关（`total=0` 可能是"无现成"也可能是"无权限"），结论表述需留此余地。
- ProjectSkillStatus.txt 属平台托管文件，仅核对开关状态，批量改写需走界面开关（手改格式错会导致开关丢失，未实证风险程度，谨慎）。

## Evidence or Examples
- 实测：`queryUserSkillList` 返回 `{"total":0,"skills":[]}`（market_url=skills.huaweicloud.com/community）→ 三个目标技能均无现成件，手搓落地。
- 实测：手搓 lazy-exec / find-skills / grill-me 三个 SKILL.md 落盘后，`listSkills` 返回清单中出现三者（`scope:"project","status":"enabled"`），总清单 count=49，无需任何界面操作。
- 实测：`ProjectSkillStatus.txt` 原文件行尾无换行，追加三条后内容拼接为 `skill-writer=truelazy-exec=true`（污染实锤），重写为规范 5 行后回读验证干净。
- 实测：market URL 可知但站点内容需登录浏览器查看——工具通道（queryUserSkillList）是脚本可用的替代入口。