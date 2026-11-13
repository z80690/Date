---
id: 2026-11-12-wiki-added-diagnostic-probes-body-exclusion
title: Wiki 小节修订中 added 文件的正文收录判据：诊断探针与内部常量不入正文、仅登记 code_refs
category: workflow
nature: decision
created_at: 2026-11-12T08:38:10
updated_at: 2026-11-12T08:38:10
tags: [文档修订, 正文收录判据, 探针脚本, patch决策, 知识库]
keywords: [probe脚本, 一次性诊断, 不入正文, code_refs, added文件, 架构层面, 粒度控制, wiki-patches, line_number_only, 禁落盘脚本]
problem_patterns:
  - "Wiki 小节修订收到含 added 临时探针脚本的变更清单，不知新文件是否写入模块架构正文：误收录会污染架构粒度，误忽略又可能漏登记引用"
  - "modified 文件的内部常量清单（键值字典）与新增代码风格细节是否要写入架构/编码规范正文难判定，罗列实现细节会产生噪声"
source_sessions: [ses_e393e3306ffeU0N50gjNyn6ZSs]
project: Date
severity: low
quality_score: 84
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: A
related_experiences: [2026-11-08-wiki-section-same-layer-action-criteria, 2026-11-11-dir-consolidation-path-prefix-batch-fix, 2026-11-11-wiki-verbatim-consistency-line-number-only, 2026-11-08-wiki-section-revision-patch-json-mode]
---

# Wiki 小节修订中 added 文件的正文收录判据：诊断探针与内部常量不入正文、仅登记 code_refs

## Scenario

patch JSON 小节级修订 subagent 派工（本例修订"工作流底座"模块文档 6 个小节，hash 全 unknown 视为 changed 全量处理），变更文件清单含两类文件：modified 的模块组件（职责未变但内部有调整）与 added 的一次性诊断探针脚本（用于外部资源可达性探测，落在测试/工具目录）。修订者须决定：added 文件要不要写进模块架构小节正文、modified 文件新增的内部常量与代码风格细节要不要补进正文或编码规范。决策错误有两个方向——把探针写进正文污染架构粒度，或因忽略而漏掉 code_refs 登记。

## Key Signals

- 探针特征信号：文件名含 `probe_`/诊断类前缀、位于 `tests/` 或工具目录、用途是一次性外部资源探测（如查询若干 GitHub 镜像仓库的 release 资产）、无长期维护职责。
- 项目规范红线信号：架构反思文档明文"诊断与验证一律用内联命令、禁落盘验证脚本"，且该整改建议稿未裁决、现状仍在原目录——红线强化"不入正文"判定，但不改变"探针现状真实存在"的事实。
- 架构正文既有粒度信号：架构小节对子目录的描述只列有持久意义的组件（unittest 测试、模拟宿主类、验收评测脚本），一次性产物与既有粒度不同层。
- modified 文件的内部常量信号：文件头部的键值字典常量（准备对象清单类）属实现细节而非模块职责描述，与其"四步流水线"的架构语义不在同一抽象层。

## Essence

正文收录判据是"是否属模块架构层面的持久组件"，而不是"是否出现在变更文件清单里"。一次性诊断探针、内部辅助脚本、数据常量清单即使真实存在且被 added/modified，也不属架构层面，不写正文，仅登记 code_refs（从符号骨架取最新行号）；项目规范红线（禁落盘验证脚本）只是强化依据——即使无红线，"不属模块架构层面"本身已足以判定。探针不入正文不代表不登记引用：code_refs 以"真实存在"为准，与正文收录决策解耦。

## Approach

1. 对变更清单中每个 added 文件做持久性判定：有稳定职责、会被长期引用的组件 → 候选入正文；一次性探测/诊断/临时验证脚本 → 只进 code_refs 不进正文。
2. added 的一次性产物不影响既有小节正文：架构小节按原有粒度保持不变，走 `line_number_only`，code_refs 中登记该文件关键符号的骨架行号。
3. modified 文件的内部常量清单（键值字典类）不入正文：正文只重述其职责与流水线语义；若职责未变，正文不动仅刷新行号。
4. 项目规范若存在"禁落盘验证脚本"类红线，作为强化依据写入交付摘要留痕；红线建议稿未裁决时按现状处理——探针仍在原目录不代表要入正文。
5. 禁止因代码风格变化向编码规范小节新增条目；新增纪律若与既有条目（如 XxxError 异常类约定）同层面，倾向维持 line_number_only。

## Faster Next Time

- 一行判据：added 文件名含 `probe`/`diagnostic`/`tmp` 或用途为一次性外部探测 → 只进 code_refs 不进正文。
- ROI：逐文件持久性判定（每文件一句话）即可完成收录决策，避免"新增文件全写进正文"的粒度污染或"探针无引用登记"的引用脱节。
- 反模式：因为"文件是新增的"就把探针写进架构小节；因为项目规范禁落盘脚本就跳过 code_refs 登记（引用集合应反映现状而非理想状态）；把内部常量键值清单罗列进正文充当"内容详实"。

## Applicability Boundaries

- 适用：patch JSON 小节级修订流程中对 added/modified 文件的正文收录决策；架构设计与编码规范小节的粒度控制；hash 全 unknown 视为 changed 的全量处理轮。
- 不适用：added 文件确属持久新组件（新适配器、新核心类、新持久化目录）——应入正文并更新子目录描述；项目裁决要求探针脚本移出或删除后的后续轮次（按新结构重新处理）。
- 与相邻经验分工：`wiki-section-same-layer-action-criteria` 管逐节 replace/line_number_only 的同层面判据（本条是其对"added 文件"这一输入类型的细化）；`dir-consolidation-path-prefix-batch-fix` 管目录归拢后旧路径前缀批量校正（本例配置与命令/关系小节的 `cd` 前缀与路径前缀校正走该条，不赘述）；`wiki-verbatim-consistency-line-number-only` 管 line_number_only 的保真要求。

## Evidence or Examples

- 源会话 ses_e393e3306ffeU0N50gjNyn6ZSs（@general subagent 修订 codebase-knowledge/工作流底座（workflow_base）.md，6 小节，hash 全 unknown）。
- 决策实证：probe_tor_alt2.py（added，GitHub 镜像 release 探测：matinrco/tor、onionshare、rigwild/tor-downloader）不入正文、架构设计/技术栈/编码规范三节 line_number_only；prepare.py 的 PREP_OBJECTS 三键常量清单与"官方渠道获取失败如实记录"纪律均不补入正文，code_refs 刷新至骨架新行号（如 prepare.py:34 PREP_DIR）。
- 红线依据：notes/架构反思与建议.md 记载"手搓脚本泛滥违规……诊断与验证一律用内联命令禁落盘验证脚本"，建议将 tests/ 内驱动脚本移出（建议稿未裁决，现状仍在 tests/）。
- 落盘产物：`.codeartsdoer/temp/patch_workflow_base.json`（UTF-8 无 BOM，六小节 patch：概述/配置与命令/关系 replace_content + 架构设计/技术栈/编码规范 line_number_only），write 成功，未直接改动 wiki 文件。