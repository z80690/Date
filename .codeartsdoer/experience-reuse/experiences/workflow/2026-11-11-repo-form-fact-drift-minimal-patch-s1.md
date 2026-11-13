---
id: 2026-11-11-repo-form-fact-drift-minimal-patch-s1
title: 规范文档事实性陈述漂移与口径漂移的二分判定：权威源零变更时影响级别收缩为单小节事实句最小修订
category: workflow
nature: methodology
created_at: 2026-11-11T00:56:32
updated_at: 2026-11-11T00:56:32
tags: [文档修订, 事实漂移, 影响级别, 最小派工, 知识库]
keywords: [事实性陈述, 仓库形态漂移, 口径未变, 权威源零变更, 影响级别S1, 概述小节, replace_content, UTF-8无BOM验证, patch JSON, 逐字保留]
problem_patterns:
  - "仓库新增源码目录等结构性变更后，误判为规范口径大改而扩大派工范围重写多个小节"
  - "概述小节中'纯文档仓库/无源代码'类仓库形态描述随仓库演进而过时，仅存在性核实查不出表述失真"
source_sessions: [ses_e39b11113ffe1Q3f5ykyrShVAW]
project: Date
severity: low
quality_score: 84
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: A
related_experiences: [2026-11-08-wiki-section-revision-patch-json-mode, 2026-11-08-wiki-section-tiered-revision-judgment-contract, 2026-11-11-wiki-stat-count-drift-recount-on-revision, 2026-11-11-subagent-wiki-patch-code-refs-read-verify]
---

# 规范文档事实性陈述漂移与口径漂移的二分判定：权威源零变更时影响级别收缩为单小节事实句最小修订

## Scenario

以 subagent 派工方式修订知识库/Wiki 规范类文档（本例"项目协作公约"文档），源变更事件是仓库结构性变化：根目录 README 新增、仓库从"纯 Markdown 文档仓库"演变为"知识库与 Python 工作流底座源码并存"。此类变更在增量修订派工中高频出现，且极易与"规范条文大改"混淆——变更文件清单看起来动静不小，但规范口径本身可能一字未动。修订者独立执行、无法中途确认，派工单已预置影响级别（S1，仅概述小节受影响）与受影响小节当前内容。

## Key Signals

- 变更文件类型是"仓库结构/形态"类事实变化（新增源码目录、README 改写），而非规范条文变更——本例公约的两大权威载体（内容权威源与生效权威源 .mdc）均零变更。
- 概述小节首句"本仓库是纯 Markdown 文档仓库（Obsidian 知识库），无任何源代码"是仓库性质的事实性陈述，与规范口径（六条精简规矩的枚举描述）同段共存——事实句过时但口径句有效，两种句子必须区别对待。
- 直觉陷阱：README 新增源码目录看似"仓库大变"，若按"大变更 → 大范围联动"直觉会重写多个小节并误改口径句；而实读权威源确认零变更后，真实影响只有一句事实陈述。

## Essence

规范文档小节修订前先做**漂移类型二分**，判定入口是权威源 diff 是否为零：口径漂移（条文条数/条目/维度变化，权威源有 diff）→ 多小节联动换口径（见 wiki-section-revision-patch-json-mode）；事实漂移（仓库形态、技术栈构成、统计计数等描述过时，权威源零 diff）→ 影响级别收缩，派工范围锁定到含过时事实陈述的最小小节集合。事实句修正时**约定性描述逐字保留**——事实陈述描述"仓库是什么"，约定描述规定"行为怎么做"，后者不随前者失效；replace_content 是整段覆盖，只许改事实句、禁止趁机润色口径句。

## Approach

1. **权威源零变更判定**：对照规范文本的权威载体（内容权威源 + 生效权威源）是否有实际变更——有 diff → 走口径联动模式；零 diff → 判定为纯事实漂移，进入最小修订模式。
2. **扫描事实性陈述**：在受影响小节正文中圈出仓库形态/技术栈/文件构成类描述（"纯 X 仓库""无 Y""仅含 Z"），逐一核对当前实况（实读 README/列目录），锁定最小小节集合。
3. **单句事实修正**：仅重写事实句为当前实况（如"Obsidian 知识库与 Python 工作流底座源码并存"），同段约定性描述（规矩条数、枚举列举）逐字保留；整段替换后通读确认无顺手动到的句子。
4. **subagent 执行侧双实读**：实读变更文件确认仓库现状（验证派工单声称），实读 Wiki 目标小节确认与派工单预置内容逐字一致后才动笔，不一致以实读为准。
5. **patch 落盘与字节级 BOM 验证**：patch JSON 写入派工单指定临时路径后，用 bash 十六进制输出验证首字节——`7B`（`{`）开头即 UTF-8 无 BOM；若为 `EF BB BF` 开头则混入 BOM 须重写。声称"无 BOM"必须以字节证据收尾，不以 write 成功回执为凭。

## Faster Next Time

- 一行决策规则：权威源零 diff + 小节含"仓库是什么"类事实句 → 影响级别降为 S1，patch 只含事实句所在小节；权威源有 diff → 按"受影响小节全部进 patch"联动换口径。
- ROI：单小节 patch（本例仅概述节、约 170 字、一条 replace_content）对比多节联动的派工编制与合并成本，派工单编制从"全量对照"降为"一句核对"；事实句失真若漏修，知识库与仓库实况脱节，后续所有以该概述为入口的任务都会带着错误前提。
- 反模式：把仓库结构变更当口径变更全量重写（顺手动约定句引入失真）；只修事实句却忘了 replace_content 是整段覆盖、把同段口径句抄漏或抄错；声称 UTF-8 无 BOM 却不做字节级验证，靠"写入成功"回执当凭据。

## Applicability Boundaries

- 适用：规范类/知识库类文档的小节级修订派工，变更源为仓库结构性事实变化（新增源码/目录/文档类型），且规范权威载体未变更；也适用于判定入口前置——主 Agent 编制派工单时划定影响级别。
- 不适用：规范条文本身变更（口径漂移，走多小节联动）；统计计数类表述漂移（"共 N 篇"类，须实测重数，见 wiki-stat-count-drift-recount-on-revision）；节级 action 分流与行号锚点构造（见 wiki-section-tiered-revision-judgment-contract）。
- 与相邻经验分工：wiki-section-revision-patch-json-mode 管"口径漂移的联动换口径 + patch 载体契约"；stat-count-drift 管"计数快照过时须实测"；本条管"权威源零变更时的漂移类型判定入口与最小派工收缩"，三者按漂移类型互补不重叠。
- 证据等级：单次成功闭环（双实读 + patch 落盘 + 字节验证通过），无失败对照样本；"权威源零 diff → 最小修订"判定链在口径/事实混合漂移场景下的稳定性待复用检验。

## Evidence or Examples

- 来源会话：ses_e39b11113ffe1Q3f5ykyrShVAW（@general subagent 执行"修订协作公约概述小节"派工，影响级别 S1）。
- 实读链路：README.md 前 10 行（确认仓库已含"通用工作流底座（device_workflow_api）"Python 源码，第 1 行为标题行、支撑 code_refs）→ Wiki 文档第 13 行概述小节（与派工单预置内容逐字一致）。
- 修订结果：概述首句"本仓库是纯 Markdown 文档仓库（Obsidian 知识库），无任何源代码"改为"Obsidian 知识库与 Python 工作流底座源码（02_软件源码/workflow_base）并存"，其余六条精简规矩描述逐字保留，全文约 170 字（≤200 字约束），code_refs 为 `README.md:1`。
- 落盘产物：`C:\Users\Administrator\Desktop\Date\.codeartsdoer\temp\patch_collab.json`，bash 十六进制验证首字节 `7B 0D 0A`（`{` + CRLF，UTF-8 无 BOM 确证）。