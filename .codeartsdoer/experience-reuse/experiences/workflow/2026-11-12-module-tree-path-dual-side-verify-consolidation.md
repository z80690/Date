---
id: 2026-11-12-module-tree-path-dual-side-verify-consolidation
title: 变更路径前缀与 module_tree 失配时双侧验证确认目录归拢并修正结构产物路径字段
category: workflow
nature: technique
created_at: 2026-11-12T08:03:10
updated_at: 2026-11-12T08:03:10
tags: [wiki增量更新, module_tree, 目录归拢, 双侧验证, 路径修正]
keywords: [module_tree, path 字段, 前缀失配, 双侧验证, 目录归拢, 结构产物, Test-Path, extract_symbols 回验, 既有模块迁移, 增量更新]
problem_patterns:
  - "变更文件路径带新前缀而 module_tree 既有模块 path 无此前缀时，误判为新模块候选启动建文档流程，实际只是目录整体迁移"
  - "只验证新路径存在就确认迁移，旧路径残留未核实，可能把'新增目录'误判为'迁移'"
source_sessions: [ses_e3930e653ffejnN62cpj5ECw5v]
project: Date
severity: low
quality_score: 83
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: A
related_experiences: ["2026-11-11-dir-consolidation-path-prefix-batch-fix", "2026-11-11-wiki-arch-snapshot-stale-new-module-read-verify", "2026-11-12-wiki-update-version-token-expiry-restart"]
---

# 变更路径前缀与 module_tree 失配时双侧验证确认目录归拢并修正结构产物路径字段

## Scenario

增量更新流程的模块归属判定环节（repo-simple-wiki-update 类）：变更文件路径带新前缀（如 `workspace/02_软件源码/...`），而 module_tree 中既有模块的 path 字段无此前缀（记的是 `02_软件源码`）；派工单未预置归拢背景，无现成迁移映射表可抄。此时有三种可能解释：模块整体迁移（归拢）、新增了同名兄弟目录（新模块候选）、变更路径本身就是新模块。误判方向会分别导致：漏更新结构产物、错误启动新模块建文档、或两者都做错。

## Key Signals

- **前缀失配信号**：变更文件路径前缀与 module_tree 某既有模块 path 的关系是"多了父级前缀"而非"全新路径"——`workspace/02_软件源码/workflow_base/cli.py` 相对 module_tree 记录的 `02_软件源码` 只是外层多了一个目录段。
- **双侧验证证据**：根目录下旧路径实测不存在（Test-Path 旧 = False）+ 新前缀路径实测存在（Test-Path 新 = True）→ 目录整体迁移坐实，而非新增兄弟目录。
- **规模回验证据**：迁移后重新跑 extract_symbols 得 201 符号/23 文件，与迁移前规模同量级 → 既有模块身份不变，仅位置字段过时。
- **归档区对照证据**：同前缀下另有仅 3 个 md 散文件、符号提取仅 5 符号/1 文件的目录，且 README 目录池声明其为"工具/流程归档流向"→ 不成新模块，路由既有主题。

## Essence

module_tree 的 path 字段是生成时快照：目录归拢后旧字段系统性过时。前缀失配的裁决入口是**双侧验证**（旧路径不存在 + 新路径存在同向成立才判迁移），单侧验证不足以区分"迁移"与"新增"。迁移确认后的动作分两层：结构产物层（修正 module_tree path 字段，module_id 不变）与文档层（全文档路径前缀与 cd 命令联动校正——另有专门经验管文档层批量校正）；两层的校正对象不同，都做才收敛。迁移场景下既有模块不重新判定新模块，规模回验只作身份佐证。

## Approach

1. **前缀失配先双侧验证**：对旧 path 与新前缀路径分别做存在性检测（Test-Path/glob 实测，勿凭 glob 对点前缀目录返回空而误断），两者同向（旧 False + 新 True）才判归拢迁移。
2. **修正结构产物**：更新 module_tree 中该模块的 path 字段为新前缀路径，module_id/children 结构原样保留——模块身份不因位置变化作废。
3. **触发文档层联动**：以"旧根 → 新前缀"映射表驱动全部受影响文档的路径校正（叙述句、条目、约定、命令口径四类位置），详见 dir-consolidation 经验，本条不重复展开。
4. **规模回验**：迁移后对模块路径重新 extract_symbols，符号/文件数与历史同量级 → 佐证既有模块身份不变；量级与形态变化大则转 arch-snapshot-stale 经验的三证据实读判定。
5. **同前缀其余目录逐个定性**：散文件少、符号弱、有归档区声明的目录不成新模块，路由既有主题修订；判定留痕写进 update_plan。

## Faster Next Time

- 一行决策规则：变更前缀 = 既有模块 path 多出一个父级目录段 → 双侧验证；验证通过即修 module_tree path 字段并联动文档层，不启动新模块判定。
- ROI：两次存在性检测（秒级）即可避免整轮误判方向——误判新模块会生成 orphan 文档，漏修正则模块归属路由全部失灵。
- 反模式：单侧验证（只看新路径存在）就判迁移；双侧验证通过后只改结构产物、漏掉文档层路径联动（引用失真留给后续轮次）；把迁移当新模块重建文档（浪费且产生重复条目）。

## Applicability Boundaries

- 适用：以 module_tree 为归属账本的增量流程中，变更路径前缀与既有模块 path 失配的判定；一般化到"结构产物字段 vs 磁盘现状"的失配裁决。
- 不适用：全新路径（无既有模块可对照，直接走新模块三证据判定）；派工单已预置迁移映射表的场景（直接用映射表，无需自主双侧验证）；文档正文内路径引用的批量校正（归 dir-consolidation 经验管）。
- 与相邻经验分工：2026-11-11-dir-consolidation-path-prefix-batch-fix 管"确认归拢后文档层怎么修"，本条管"无预置背景下如何自主发现归拢并修结构产物层"——前者是本条 Approach 第 3 步的展开，上下游衔接不重叠；2026-11-11-wiki-arch-snapshot-stale-new-module-read-verify 管"新模块判定"，本条管"既有模块迁移判定"，互斥场景。

## Evidence or Examples

- 源会话 ses_e3930e653ffejnN62cpj5ECw5v（docgen-apply fork #1，Date 项目 Wiki 增量更新，version_token 393）。
- 双侧验证实证：根目录 `02_软件源码` 实测不存在（False），`workspace/02_软件源码` 实测存在（True）→ module_tree 中 software_src 模块 path 修正为 `workspace/02_软件源码`，module_id 不变。
- 规模回验实证：迁移后 extract_symbols 提取 201 符号/23 文件（历史轮次 199 符号/22 文件，同量级）→ 既有模块身份佐证成立。
- 归档区对照实证：`workspace/06_开发工具` 仅 3 个 md 散文件 + 5 符号/1 文件（md 被跳过）+ README 目录池声明"工具/流程 → 06"→ 判不成新模块，路由既有主题 tooling_and_environment 修订。
- 联动收敛实证：6 篇受影响文档全部完成路径前缀与 cd 命令联动校正，抽查确认无旧前缀残留，build_index 98 code_paths 验证通过。