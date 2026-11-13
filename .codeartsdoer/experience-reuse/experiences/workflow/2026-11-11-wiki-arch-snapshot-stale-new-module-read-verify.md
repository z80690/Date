---
id: 2026-11-11-wiki-arch-snapshot-stale-new-module-read-verify
title: 生成式架构产物的快照时效判定：modules 为空先查产物年龄，过期时以实读三层证据定新模块
category: workflow
nature: methodology
created_at: 2026-11-11T01:07:50
updated_at: 2026-11-11T01:13:34
tags: [wiki增量更新, 新模块判定, 产物时效, 实读抽验, 知识库]
keywords: [architecture.json, modules 为空, 新模块判定, 产物过期, 实读抽验, 符号骨架, 包结构入口, module_tree, 孤立目录, 判定留痕]
problem_patterns:
  - "增量更新新模块判定环节机械套用'modules 为空 = 不构成新模块'口径，把过期架构产物的陈旧快照当成当前事实，漏掉真实新模块导致新文档缺位、反查覆盖出现盲区"
  - "混淆'孤立小目录不成模块'与'产物过期掩盖真模块'两种 modules=[] 语义，该建文档的不建、不该建的乱建"
source_sessions: [ses_e39bfec85ffeYWVqiFQx41gRI4]
project: Date
severity: medium
quality_score: 88
hit_count: 1
last_hit_at: 2026-11-11T02:29:14
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-08-wiki-increment-update-unmatched-file-routing, 2026-11-10-prior-reuse-recheck-checklist-baseline-drift, 2026-11-08-wiki-section-revision-patch-json-mode, 2026-11-11-wiki-stat-count-drift-recount-on-revision]
---

# 生成式架构产物的快照时效判定：modules 为空先查产物年龄，过期时以实读三层证据定新模块

## Scenario

对既有 Wiki 执行增量更新的影响分析阶段（repo-simple-wiki-update 类流程）：变更集中出现成规模的代码目录（本例 27 个文件落在 02_软件源码/workflow_base 下），需要判定其是否构成新模块、是否要生成新模块文档。判据是 architecture.json 的 `modules` 数组——上轮口径为"modules 为空则不构成新模块，禁止为孤立目录新建模块文档"。本轮该数组同样为空，但变更规模与性质与上轮截然不同（上轮 21 个纯 .md/临时文件，本轮 72 个且含真实 Python 包）。

## Key Signals

- **产物年龄信号（决定性）**：architecture.json 的生成时间早于本轮变更的 detected_at（本例产物 2026-11-06，变更 2026-11-10/11）——`modules: []` 是"上次生成时刻无模块"的陈旧快照，不是"当前无模块"的事实陈述。
- **包结构信号**：变更文件呈成规模包形态——`__init__.py`、统一入口 `cli.py`、core/adapters/tools 多个子包共 22+ 文件，与"孤立目录"（<10 个散文件的 00/06/07/08 类目录）形态截然不同。
- **项目声明信号**：README 用整节描述该目录的定位、结构与运行方式（目录池约定、入口命令）——项目自身已承认这是结构性组成部分。
- **对照信号**：同轮次 extract_symbols 对该目录提取出 199 符号/22 文件，而纯文档目录恒为 0 符号——量级差异即性质差异。

## Essence

任何生成式产物（architecture.json、scan 摘要、骨架等）都只反映其生成时刻的状态：`modules` 为空存在两种语义——"产物生成时确实无新模块"与"产物早于变更、快照已过期"。判定的入口是**产物年龄与变更时间的先后比对**，而不是数组内容本身；数组为空在过期场景下不构成"无新模块"依据。过期时改用实读三层证据组合（包结构入口 + 符号骨架规模 + 项目级声明）做替代判定，三证据同向才立新模块。"modules 空 → 不建文档"口径只在产物新鲜（与变更同源或晚于变更）时成立。

## Approach

1. **查产物年龄**：读取 architecture.json 的 built_at/生成时间（或文件 mtime），与本轮变更的 detected_at 比对；产物晚于或覆盖变更 → 维持原口径（modules 空 = 不成模块）；产物早于变更 → 进入实读抽验。
2. **实读三层证据**：① 抽读目录的包结构入口（`__init__.py`、`cli.py` 等组织文件）确认是真实代码包而非散文件堆；② 跑一次符号骨架提取（extract_symbols），用 symbols/files 数量做规模量证；③ 实读 README/项目级声明文件，确认项目自身如何定位该目录。
3. **三证据同向裁决**：真实包结构 + 符号规模显著（对比纯文档目录的 0 符号基线）+ 有项目级声明 → 判定新模块成立，走新模块文档生成流程并合并进 module_tree；任一证据缺失或目录仅 <10 个散文件 → 维持"不成模块"结论，按孤立目录路由到既有主题修订。
4. **判定留痕**：把"产物过期（附时间戳对比）+ 三层实读证据（附符号数/文件数）"写入 update_plan 判定结论，供后续校验与经验修订追溯。

## Faster Next Time

- 一行决策规则：`modules: []` 先问"产物几岁"——产物旧于变更即视为快照失效，转实读；产物新鲜才允许按数组内容下结论。
- 判定表：modules 空 + 产物过期 + 包形态文件 ≥20 → 实抽验大概率立新模块；modules 空 + 产物新鲜 → 不成模块（原口径）；modules 空 + 目录散文件 <10 → 孤立目录，路由到主题修订。
- ROI：一次时间戳比对（秒级）+ 一次符号提取（本例 199 符号/22 文件，数十秒）即可避免"真新模块整轮无文档"的覆盖缺口——漏建后果由 build_index 反查缺口、后续轮次反复补判来偿还，成本远高于当轮判定。
- 反模式：把旧口径当铁律，产物过期场景下仍拒绝建文档（覆盖缺口）；反向过度——见到新目录就建模块（孤立小目录产生 orphan 页面）；只看 modules 数组不看产物时间戳就下结论。

## Applicability Boundaries

- 适用：以生成式产物为判据的任何增量流程（架构分析、scan 产物、符号骨架、依赖图等）——产物快照只反映生成时刻，凡产物年龄早于本轮输入变更，其"空/无"结论须实读复核后才可用。
- 不适用：产物与变更同批生成或产物含增量刷新机制的场景（快照即现状）；变更集为纯文档/配置的轮次（无代码包形态信号，原口径直接可用）；全量首次生成（无历史产物可比）。
- 与相邻经验分工：2026-11-08-wiki-increment-update-unmatched-file-routing 管"unmatched 文件三级路由框架"（本条是对其第二级判据在产物过期场景下的实证修正，refine 已裁决为边界区分共存：产物新鲜走原口径，产物过期走本条实读三层证据）；2026-11-10-prior-reuse-recheck-checklist-baseline-drift 管"上轮判定留痕的数值重算复核"（数值时效），本条管"结构性产物的存在性时效"（快照时效），两者互补不重叠。

## Evidence or Examples

- 源会话 ses_e39bfec85ffeYWVqiFQx41gRI4（docgen-apply 主 Agent，Date 项目 Wiki 增量更新，version_token 213→347）。
- 产物过期实证：architecture.json 生成于 2026-11-06（modules=[]），本轮变更 detected_at 为 2026-11-10/11；实读 cli.py 确认真实包结构（Store/Scheduler/ReceiptCenter/SecurityValidator 十大组件装配 + embedded/security_research 双适配器），README 声明 00-09 目录池与 workflow_base 定位。
- 判定与闭环实证：extract_symbols 提取 199 符号/22 文件 → 判定新模块成立并生成新文档；build_index 终局 `added: 1`、`code_paths_verified: 56`、status=success，progress.json final_status=completed——判定正确性由全链校验背书。
- 对照实证：上一轮（version_token 213，21 个纯 .md 变更）产物新鲜，modules=[] 判"无新模块"成立——两轮结论相反但判定规则一致，证明规则本身自洽、口径需带时效前提。