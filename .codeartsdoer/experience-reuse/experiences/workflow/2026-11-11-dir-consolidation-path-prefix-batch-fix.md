---
id: 2026-11-11-dir-consolidation-path-prefix-batch-fix
title: 仓库目录归拢后知识文档路径引用系统性失效：旧路径到新前缀映射的全小节批量校正
category: workflow
nature: technique
created_at: 2026-11-11T02:49:45
updated_at: 2026-11-11T10:46:07
tags: [文档修订, 路径引用, 目录归拢, 批量校正, 知识库]
keywords: [目录池归拢, 路径前缀, workspace迁移, 路径引用失效, 批量校正, 命令口径联动, 结构重组, 知识文档修订, replace_content保真, 派工修订]
problem_patterns:
  - "仓库根目录结构重组（目录池迁入子目录）后，修订知识文档时只更新变更文件清单条目本身，漏掉小节正文叙述与既有条目中的旧路径引用"
  - "把'目录搬家'当存在性问题做核实（文件都在所以判定无失真），漏掉'引用存在但位置过时'的位置类漂移；同批修订中旧路径残留"
source_sessions: ["ses_e393cb218ffev2TPbwjI5bi95s"]
project: Date
severity: medium
quality_score: 84
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: A
related_experiences: ["2026-11-11-wiki-stat-count-drift-recount-on-revision", "2026-11-11-repo-form-fact-drift-minimal-patch-s1", "2026-11-11-subagent-wiki-patch-code-refs-read-verify", "workflow/2026-11-08-ghost-reference-path-precheck", "architecture/2026-11-11-doc-path-dual-caliber-adjudication"]
---

# 仓库目录归拢后知识文档路径引用系统性失效：旧路径到新前缀映射的全小节批量校正

## Scenario

以 subagent 派工方式修订知识库/Wiki 文档（本例"工具链与环境配置"主题，影响级别 S2，四个小节 hash 全 unknown），源变更事件是仓库级**目录归拢**：根目录 00-09 目录池整体迁入 `workspace/` 下（如 `02_软件源码` → `workspace/02_软件源码`、`06_开发工具` → `workspace/06_开发工具`）。派工单预置影响级别、变更文件清单与修订要点，修订者独立执行、无法中途确认。此类结构重组在仓库演进中低频但影响面大，且失真是系统性的——所有引用旧根路径的既有文档同时过时。

## Key Signals

- 派工单核心背景直接写明"仓库执行根目录归拢，00-09 目录池迁入 workspace/ 下"——这是全库结构事件信号，影响范围远超本次变更的三个文件。
- 目标文档四个小节里散布旧路径引用：概述叙述句的 `02_软件源码/`、`06_开发工具/`；关键文件清单的三个 06 条目；架构与约定的 `02_软件源码/workflow_base`、"编译、测试、运行均在 `02_软件源码` 目录下执行"（命令口径本身内嵌路径）。
- 陷阱特征：文件全部存在（存在性核实通过），只是位置变了——按"查存在"思路核对会误判无失真。

## Essence

目录归拢造成的是**位置类漂移**：与幽灵引用（引用了不存在的路径）相反，这里被引对象都在、只是搬了家，存在性核实查不出失真；与形态漂移（"仓库是什么"过时）也不同，这里失真的是"东西在哪里"。校正单位是**旧路径→新前缀映射表**，而非逐条临时判断；且必须覆盖四类位置——概述叙述句、关键文件/目录条目、架构约定描述、命令口径（`cd 旧目录 && ...` 类可执行命令内嵌的路径）。归拢是全库事件：一次 patch 只能修一个文档，同批其余知识文档大概率也有旧路径残留，修订交付时应向派工方显式提示全库排查，而不是默认"修完这个文档就收敛了"。

## Approach

1. **提取迁移映射表**：从派工单/归拢事件记录提取"旧根 → 新前缀"对照（本例 `02_软件源码/` → `workspace/02_软件源码/`、`06_开发工具/` → `workspace/06_开发工具/`），校正一律以映射表为准，不逐条现想。
2. **全文圈查旧根**：实读目标文档全文，逐一圈出含旧根的路径引用，按四类位置登记（叙述句/条目/约定/命令口径），命令口径中的 `cd` 目标目录同样算路径引用。
3. **逐小节批量加前缀**：replace_content 整段替换时，未受归拢影响的描述（机制条款、红线、验证口径）逐字保留，禁止趁机润色；校正只动路径 token。
4. **留痕校正清单**：在交付说明中列出"哪些条目改了前缀"，供派工方对照复核；引用新路径的条目先实读确认新位置真实存在再写入。
5. **全库残留提示**：交付时附一句"归拢影响全库，其余知识文档的旧路径引用建议另行 grep 排查"，把单文档修复升级为事件级收敛意识。

## Faster Next Time

- 一行决策规则：变更背景含"归拢/迁移/重组/搬迁"类词 → 必触发"旧路径引用全量圈查"，校正范围与变更文件清单无关——清单外的既有条目照样过时。
- ROI：一次映射表圈查（分钟级）杜绝"按 wiki 入口找文件扑空"的失真；漏修后果是后续所有以该文档为入口的任务按旧路径定位失败，返工成本远高于校正成本。
- 反模式：只改变更文件清单条目、漏掉正文叙述与命令口径；用存在性核实代替前缀校正（文件在旧判断里"存在"就跳过）；把归拢当普通目录变更不做全库提示。

## Applicability Boundaries

- 适用：仓库级结构重组（目录池归拢、批量迁移、根目录重命名）后的知识文档/Wiki 修订；派工方与执行方分离、修订者无法全库巡视的场景。
- 不适用：单文件/单目录级移动（影响面小，直接改引用即可，无需映射表流程）；引用不存在的幽灵引用（归 ghost-reference-path-precheck 管）；统计计数漂移（"共 N 篇/N 条"类，归 stat-count-drift 管）；仓库形态句漂移（归 repo-form-fact-drift 管）。
- 与相邻经验分工：stat-count-drift 管"数字快照过时须实测重数"；repo-form-fact-drift 管"仓库是什么的形态句过时"；subagent-wiki-patch-code-refs-read-verify 管"行号取证与 patch 载体契约"；ghost-reference-path-precheck 管"引用不存在"；本条管"引用存在但位置过时"——五者按漂移类型互补不重叠；doc-path-dual-caliber-adjudication 管其前置裁决（路径引用属分区逻辑口径须保留还是构成描述须校正），先裁决再进本条映射表批量校正。
- 证据等级：单次成功闭环（四小节 patch 齐备落盘、新路径条目经实读确认）；路径校正要点由派工单预置、执行方实读执行，非执行方独立发现；无失败对照样本。

## Evidence or Examples

- 来源会话：ses_e393cb218ffev2TPbwjI5bi95s（@general subagent 执行"修订工具链环境主题"派工，影响级别 S2，四小节）。
- 实读链路：wiki 目标文档全文 → `.codeartsdoer/rule/项目协作公约.mdc` 实文（确认 6 条精简规矩，文档中"共 7 条/第七条"为旧口径残留）→ 三个 06 文件新路径（`workspace/06_开发工具/` 下）实读确认 → glob 确认 `workspace/02_软件源码/workflow_base/core/environment.py` 存在 → grep 骨架 `software_src.txt` 确认 `route()` 位于 environment.py:59。
- 修订结果：概述与架构约定路径前缀批量校正、关键文件三个 06 条目加 `workspace/` 前缀、"共 7 条"改"共 6 条"、第七条旧口径改为第 6 条裁决顺序（规则>知识库>记忆>推断）——本例是**位置漂移 + 数字口径漂移混合**的处置实例：前者走本条映射表批量校正，后者走 stat-count-drift 的权威源实读重数，两法同批并行不冲突。
- 落盘产物：`C:\Users\Administrator\Desktop\Date\.codeartsdoer\temp\patch_tooling.json`（四小节 replace_content，UTF-8 无 BOM），write 成功，未直接改动 wiki 文件。