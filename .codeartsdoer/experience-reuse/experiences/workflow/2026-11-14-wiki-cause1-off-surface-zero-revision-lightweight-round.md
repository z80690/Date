---
id: 2026-11-14-wiki-cause1-off-surface-zero-revision-lightweight-round
title: 变更文件不在关注面（成因 1 型）的零修订轮：affected_docs=0 轻量路径与校验基线复核口径
category: workflow
nature: decision
created_at: 2026-11-14T02:10:37
updated_at: 2026-11-14T02:10:37
tags: [wiki增量更新, 零修订轮, 成因1判定, 关注面外, 校验基线复核]
keywords: [affected_docs 0, reverse_lookup, unmatched, 成因1, module_tree归属, 轻量路径, validate total 0, 基线复核, build_index reused, 增量更新]
problem_patterns:
  - "reverse_lookup 返回 affected_docs=0 / transfer_impact=0，误以为影响分析脚本坏了或流程漏跑，发起排查或重跑"
  - "对不命中任何模块路径的工具生成日志类变更文件跳过成因判定直接置之不理，留下'为何跳过'无据可查的空洞"
  - "零修订轮只跳过修订环节，连带跳过校验链，失去全目录基线复核机会，回归缺陷漏检"
source_sessions: [ses_e29ecd91cffeATlJqZnujMKp9s]
project: Date
severity: medium
quality_score: 84
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: A
related_experiences: [2026-11-12-wiki-zero-revision-round-full-short-circuit, 2026-11-12-wiki-index-code-refs-absence-cause2-patch, 2026-11-08-wiki-increment-update-unmatched-file-routing, 2026-11-09-repeat-changed-set-reuse-prior-round-verdicts, 2026-11-14-wiki-update-plan-clear-vs-crossround-prior-note-token]
---

# 变更文件不在关注面（成因 1 型）的零修订轮：affected_docs=0 轻量路径与校验基线复核口径

## Scenario

Wiki 增量更新（repo-simple-wiki-update 类流程）新开一轮（version_token 不匹配重开），本轮 changed_files 仅 1 个文件且为工具运行时自动生成的纯追加式执行日志（如 `.workbuddy/memory/automations/<id>/memory.md`）。reverse_lookup 正式判定返回 `affected_docs=0、transfer_impact=0、unmatched=1`——修订面天然为空。与 hash 短路型零修订轮（受影响文档存在、小节 hash 未变）不同，这种"成因 1 型零修订轮"下主技能字面流程的阶段 3+4（subagent 修订派工、patch 产出、merge 合并）完全没有对象，需要一条明确的轻量路径与"什么是正常结果"的判定口径，否则容易在空环节上空转或误判脚本异常。

## Key Signals

- **修订面为空的正式证据**：reverse_lookup 输出结构化 JSON 明示 `affected_docs=[]、transfer_impact=[]、unmatched=[{...needs_further_judgment: cause_1_or_2_or_3}]`——unmatched 唯一项需要补判，其余全空。
- **变更文件的内容性质**：实读确认是工具自动生成的运行记录（签到/旅行/积分等逐日执行日志），非功能代码、非知识库内容；纯追加式，只增不改。
- **归属信号**：module_tree 中全部模块路径均不涵盖该文件所在目录（`.workbuddy/` 不在 adapter/notes/DVWA/temp/workspace 任何前缀下）。
- **校验输出形态**：validate_code_links 返回 `total=0, passed=0, failed=0`；build_index 返回 `reused 15 / updated 0 / added 0`——零修订轮下这些都是预期正常结果。

## Essence

零修订轮有两种成因机理，处置口径不同：hash 短路型（文件在关注面内、文档存在、仅内容 hash 未变）与成因 1 型（文件根本不被任何模块路径与索引 code_refs 覆盖，修订面从源头为空）。后者是**文件级**的空面而非**小节级**的短路，判定的核心是给 unmatched 文件一个完整成因 1 证据链（排除成因 2 索引漏建、成因 3 路径 normalize 问题），并把"跳过修订"与"跳过校验"区分开——修订面为空时校验链仍应跑全目录，作为零成本的全库基线复核窗口（与上轮 lint warnings 基线对比，捕捉流程外因素引入的回归）。流程闭环标准依旧是"索引与检索指南刷新完成 + 校验通过"，而非"每个环节都有写动作"。

## Approach

1. **unmatched 文件走四步证据链定性成因 1**：① 实读文件内容判性质（是否功能代码/知识内容）；② 查 module_tree 归属（是否有模块路径涵盖）；③ grep docs 全目录/索引确认无该路径引用（0 命中 → 排除成因 2 索引漏建，勿读 architecture.json）；④ 比对 state.json 路径与文件系统实际路径（一致 → 排除成因 3）。四步齐备才判成因 1。
2. **跳过阶段 3+4，但阶段 3.5+4.5 校验链照跑全目录**：validate（total=0 属正常）、redact_secrets（全文件扫描）、lint_wiki（与上轮 warnings 基线对比——本轮 0 errors / 15 warnings 全为 orphan-page-candidate，与上轮一致即基线无回归）。
3. **阶段 5 判空跳过、阶段 6 build_index 照常**：无新增/删除模块则不更新 index.md；build_index 预期全 reused，该输出作为零修订轮的闭环验证证据；overview.md + WikiRetrieval.md 照常再生并做阶段 7 标记完整性验证。
4. **判定留痕持久化后再清空 update_plan**：成因判定证据链在轮末 update_plan 清空前迁移至 stage_2 的 `note_<version_token>` 字段（见相邻经验 2026-11-14-wiki-update-plan-clear-vs-crossround-prior-note-token），报告"降级记录/隔离文档"表如实写"无降级"。

## Faster Next Time

- 一行决策规则：reverse_lookup 空手而归（affected_docs=0）≠ 脚本坏了，先对 unmatched 做成因判定；判成成因 1 即走轻量路径——跳修订不跳校验。
- 看到 validate `total=0` 与 build_index 全 reused：成因 1 型零修订轮的正常证据，勿发起排查重跑。
- lint 的价值在基线对比：零修订轮跑 lint 不是空转，是免费的全库回归窗口；把上轮 warnings 清单当作基线，本轮只看增量差异。
- ROI：省去阶段 3+4 的 subagent 派工与排查往返；同时借校验链完成全库基线复核，比按字面流程逐环节找活干快一个数量级。
- 反模式：把 affected_docs=0 当影响分析故障重跑；跳过成因判定直接静默跳过 unmatched（留痕缺失导致下一轮同批变更无法复用先验）；连校验链一起跳过（失去回归检测窗口）。

## Applicability Boundaries

- 适用：带 reverse_lookup 影响分析 + unmatched 成因补判机制的增量更新流程；变更集全部由工具运行时日志/临时产物构成的轮次；每日定时更新中检测器重报运行日志的高频场景。
- 不适用：unmatched 文件按 module_tree 应归属某既有文档但索引 code_refs 为空的场景（那是成因 2，须补判入修订，见 2026-11-12-wiki-index-code-refs-absence-cause2-patch）；受影响文档存在但小节 hash 全 unchanged 的短路型零修订轮（见 2026-11-12-wiki-zero-revision-round-full-short-circuit）；真有内容变更或新增模块的常规轮次。
- 与相邻经验分工：hash 短路型经验管"有文档对象、小节级短路"；成因 2 经验管"文档存在但索引漏建"；本条管"文档对象从源头为空（成因 1）+ 轻量路径与校验基线口径"；留痕迁移经验管"判定依据如何跨轮存活"——四者按修订面空的不同成因互补。

## Evidence or Examples

- 源会话 ses_e29ecd91cffeATlJqZnujMKp9s（docgen-apply fork #1，Date 项目，version_token 540→557 全新轮次，变更 1/953≈0.1%）。
- 判定实证：变更文件实读为 WorkBuddy 自动化签到/旅行的逐日执行日志；module_tree 5 模块路径均不涵盖 `.workbuddy/`；docs 全目录 grep `workbuddy` 0 命中（排除成因 2）；state.json 路径与文件系统一致（排除成因 3）。
- 轻量路径实证：reverse_lookup `{"affected_docs": [], "transfer_impact": [], "unmatched_count": 1}`；阶段 3.5+4.5 校验 validate passed (total=0)、redact 19 文件 0 可疑、lint 0 errors/15 warnings（全 orphan-page-candidate，与上轮基线一致）。
- 闭环实证：build_index success `{"reused": 15, "updated": 0, "added": 0, "total": 15}`，code_paths_verified=216，wiki_relations=4；WikiRetrieval.md 标记完整（WIKI_RETRIEVAL_START/END 在 Line 1/60）、占位符 0 残留；progress.json 顶层 completed，判定证据链留痕于 stage_2.note_557。