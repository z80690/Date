---
id: 2026-11-06-config-audit-tool-keep-or-remove-decision
title: 配置实查探测定制投入评估工具去留（零反问决策法）
category: agent-ops
nature: decision
created_at: 2026-11-06T20:20:20
updated_at: 2026-11-06T20:24:59
tags: [工具去留, 配置实查, 定制投入, 撤销收益, 弱依赖]
keywords: [vault, Obsidian, app.json, workspace.json, community-plugins, 出厂默认配置, 撤销评估, 去留裁决, 冗余判断, 零定制]
problem_patterns: [被要求评估某可视化工具或笔记库的去留但用户禁止反问, 需要判断工具集成是否冗余应否撤销]
source_sessions: [ses_e4f472e57ffeK1eNXlpjLq4sys]
project: Date
severity: medium
quality_score: 88
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-06-doc-repo-zero-extraction-knowledge-gen, 2026-11-06-project-knowledge-provenance-format, 2026-11-06-design-stage-self-serve-evidence-decisions]
---

# 配置实查探测定制投入评估工具去留（零反问决策法）

## Scenario
用户把"去留/撤销/是否冗余"的裁决权下放给 Agent（"你自己读文件判断……给出需要保留/撤销/弱依赖的明确结论及理由"），并禁止反问。对象是已集成的可视化工具或库（如 Obsidian vault、编辑器 workspace、构建工具配置）。需要在无用户输入的情况下给出有证据支撑的明确结论。

## Key Signals
- 派工说明确写"你自己读文件判断后把结论写进 design.md"，反问路径被封死。
- 可探测证据全部在配置目录（如 `.obsidian/` 下 4 个配置文件实存），无需用户提供任何信息。

## Essence
工具去留的本质权衡是"撤销收益 vs 保留成本"，两者都可从配置实查推导：用户定制投入趋零 ⇒ 撤销收益趋零（重装软件即恢复默认配置，删了也换不来什么）；承载机制对其私有功能零依赖 ⇒ 保留成本趋零（纯标准格式+相对路径，不构成冗余）。双向趋零时结论取"弱依赖、维持现状、不撤销"，撤销方案只记录备查、不进执行清单——不发起用户未要求的破坏性动作。

## Approach
1. 读工具配置目录全部文件，探测定制投入：用户配置是否为空对象 `{}`、有无社区插件文件（如 community-plugins.json）、核心插件开关是否全部出厂默认、workspace/会话文件中的实际使用记录。
2. 读库内内容文件，检查是否使用该工具私有语法（如 wikilink、私有 frontmatter 字段），确认承载机制是否依赖其私有功能。
3. 与既有机制（docs、specs 等纯 Markdown 流程）交叉比对主题覆盖，判断内容是否冗余。
4. 三项证据齐了再下结论：定制投入低 + 私有功能零依赖 + 内容不冗余 ⇒ "弱依赖保留"；任一项反转（深度定制/强依赖/确有重叠）才进入撤销或整合评估。
5. 结论写进下一阶段产物，撤销备查方案一并记录，但撤销动作不列入执行清单。

## Faster Next Time
- 检查顺序固定：配置空/无插件/出厂默认/使用记录 → 私有语法 → 主题交叉比对，一轮并行读取即可出结论，无需反问。
- 警惕信号：不要因为"软件在用"就推断有价值；价值看定制投入与机制依赖，不看软件本身是否存在。
- 撤销评估永远给"备查方案+不执行"，把破坏性动作的决定权留给用户裁决。

## Applicability Boundaries
- 适用：Agent 被授权自主评估工具/库去留且禁反问的场景；证据为配置文件+内容文件的场景（Obsidian vault、编辑器配置、构建工具取舍同理）。
- 不适用：配置含真实定制（自定义插件、主题、模板）或机制强依赖私有功能时——此时应进入正式撤销/迁移评估而非默认保留；用户已明确要求撤销时直接执行其裁决，无需此评估。
- 与《禁反问裁决下设计阶段读盘判断闭环（结论落盘+未决显式化）》的分工：那条是禁反问场景的通用判断闭环；本条是"工具去留"决策的证据判定特化，"双向趋零⇒弱依赖保留"的结论规则为本条独有。
- 反模式：把"配置文件存在"当作"有使用价值"；以个人对工具的偏好替代证据。

## Evidence or Examples
- 项目 Date（2026-11-06 实查）：`.obsidian/app.json`、`appearance.json` 均为空 `{}`；`core-plugins.json` 33 项全为出厂默认、无 community-plugins.json；`workspace.json` 为默认布局，仅打开过 notes/知识库初始化.md 一次（验证性使用）。
- notes/ 仅 1 篇 8 行纯标准 Markdown，零私有语法；vault 内容与 docs/ Wiki 主题零重叠。
- 结论落盘 `.codeartsdoer/specs/kb_maintenance/design.md`（549 行）："弱依赖、维持现状、不撤销、不冗余"，撤销方案仅记录备查；另建议 `.obsidian/` 排除出首次提交范围（列为待裁决未决项）。