---
id: 2026-11-12-wiki-zero-revision-round-full-short-circuit
title: 令牌递增但内容 hash 全 unchanged 的零修订轮：全短路特例成立，fix_code_links 无操作、build_index 全 reused 属正常证据
category: workflow
nature: decision
created_at: 2026-11-12T08:28:10
updated_at: 2026-11-12T08:28:10
tags: [wiki增量更新, 零修订轮, hash短路, 全短路特例, 定时更新]
keywords: [version_token, hash_status unchanged, 全短路, 零修订轮, fix_code_links, code-links.json 残留, build_index reused, 空转轮, 检测器状态推进, 增量更新]
problem_patterns:
  - "按主技能字面流程执行到 fix_code_links 环节，发现 wiki 目录无 .code-links.json 可刷，误以为流程缺了环节而在'找文件/造空文件'上空转"
  - "build_index 输出 reused N / updated 0 / added 0，误判为索引构建异常或流程漏跑，发起不必要的排查或重跑"
  - "把 version_token 递增当作内容变更证据，对 hash 全 unchanged 的轮次仍启动 subagent 修订派工"
source_sessions: [ses_e32e25b09ffeSjYrHNrWK7ATrq]
project: Date
severity: medium
quality_score: 87
hit_count: 6
last_hit_at: 2026-11-13T12:52:04
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-12-wiki-update-version-token-expiry-restart, 2026-11-09-wiki-hash-shortcut-requires-merge-pass, 2026-11-11-wiki-added-mislabeled-merkle-reset-hash-triage, 2026-11-09-repeat-changed-set-reuse-prior-round-verdicts]
---

# 令牌递增但内容 hash 全 unchanged 的零修订轮：全短路特例成立，fix_code_links 无操作、build_index 全 reused 属正常证据

## Scenario

每日定时触发的 Wiki 增量更新（repo-simple-wiki-update 类流程）：阶段 0 令牌比对发现 `progress.json.update_context.version_token`（上轮 422）≠ state.json 本轮令牌（423），按令牌判定规则重开更新流程。重开后跑阶段 1/2，却发现本轮 changed_files 与上轮**完全同批**（同一批 3 个文件），且 reverse_lookup 报出的全部受影响小节 `hash_status` 均为 **unchanged**——变更文件的实际内容与上轮基线完全一致，进入"流程重开但内容零修订"的空转轮。此类轮次在每日定时更新任务中高频复现（检测器状态推进、文件 mtime/元数据变化、同批变更重报均可触发），而主技能的字面流程是按"有内容变更"轮次设计的，逐环节照走会在无操作环节上空转。

## Key Signals

- **三信号组合判定零修订轮**：① version_token 递增（422→423，说明变更检测器状态推进过）；② changed_files 与上轮完全同批（路径与 status 逐一相同）；③ 所有受影响小节 `hash_status=unchanged`（内容 hash 与上轮基线一致）。三者同时成立 = 令牌推进只是检测器状态变化，内容未变。
- **fix_code_links 环节无对象可刷**：wiki 目录无 `.code-links.json` 残留——上轮 build_index 消费后已删除（属正常行为）；且 hash 完全一致意味着行号天然无偏移，无行号可刷。主技能字面流程要求跑该脚本，但脚本实况是仅支持单 `.code-links.json` 文件模式（`--code-links-file` 必选参数），全短路轮下无输入文件，强行执行无意义。
- **build_index 全 reused**：`build_stats: {reused: 8, updated: 0, added: 0}`——零修订轮下索引条目全部复用是**预期正确结果**，不是索引构建异常。

## Essence

version_token 是变更**检测器**的状态推进信号，不是内容变更信号；源文件内容 hash 比对才是内容权威。轮次级判定以此为准：token 递增 + changed 同批 + hash 全 unchanged = 零修订轮，此时增量更新全流程的"修订面"天然为空——全短路特例成立（无 changed 小节 + 无新模块 + unmatched 补判后清零），阶段 3+4 的 subagent 调度、patch 产出、merge 合并整体无对象；fix_code_links 无操作（无 .code-links.json 可刷、行号无偏移）；build_index 全 reused 是零修订轮的**闭环验证证据**而非异常。流程闭环标准是"索引与检索指南刷新完成 + 各项校验通过"，而非"每个环节都产生了写动作"。

## Approach

1. **重开流程后先看 hash_status 分布，不看令牌**：令牌不匹配只回答"是否重开"；重开后立即跑阶段 2 reverse_lookup，按小节 hash_status 判断本轮是否零修订轮。
2. **核验全短路三条件**：受影响文档所有小节 hash_status 全 unchanged、update_plan 的 new_modules 为空、unmatched 文件补判后清零。三者齐备才走本路径；任一不满足则按常规增量路径处理。
3. **跳过阶段 3+4，fix_code_links 记降级无操作**：不调 subagent、不产 patch；在修订报告"降级记录"表写明"fix_code_links | 无 .code-links.json 可刷（上轮 build_index 已删）+ hash 一致行号无偏移 | 无操作，直接进阶段 6 | 无影响"。
4. **阶段 6 build_index 照常执行**：预期全 reused，该输出作为零修订轮的闭环验证证据；overview.md + WikiRetrieval.md 照常再生。
5. **阶段 7 验证照常执行**：检索模板标记完整、无占位符残留、.code-links.json 零残留、索引 JSON 有效（format_errors=[]）全部通过后，修订报告如实写"零内容修订"，progress.json 置 completed。

## Faster Next Time

- 一行决策规则：轮次级判定只认 hash_status 全 unchanged——全 unchanged 即短路整轮修订面，勿按主技能字面流程逐环节寻找可执行动作。
- 看到无 `.code-links.json` 可刷：这是上轮 build_index 消费后删除的正常终态（该脚本消费后删除属设计行为），不是流程缺环节；零修订轮本就无行号可刷，勿造空文件凑数。
- 看到 build_index `reused N / updated 0 / added 0`：零修订轮的正常证据，与 hash 全 unchanged 相互印证；不是索引异常，勿发起排查或重跑。
- ROI：三个快捷信号把"按字面流程在无操作环节空转 + 误判排查"的成本压为零；本仓库每日定时更新下空转轮高频复现，单轮节省的是完整排查往返与误派工成本。
- 反模式：强行造空 `.code-links.json` 喂给 fix_code_links；把全 reused 当索引构建失败回滚重跑；把令牌递增当内容变更证据启动 subagent 派工；把"零修订"写成"更新失败"误导下游。

## Applicability Boundaries

- 适用：带 hash 短路机制的增量更新流程中"流程重开/重启但内容未变"的轮次；每日定时更新类任务（变更集被检测器重报、元数据级变化触发令牌推进）的高频空转轮。
- 不适用：存在任一 `hash_status=changed` 小节的轮次（须发 line_number_only 或 replace_content patch 并走 merge 刷 source_hashes，见相邻经验——那是"有 changed 对象的零修订"，本条是"根本没有 changed 对象"）；真有内容变更或新增模块的轮次；无 hash 短路机制的流程；首轮全量生成。
- 与相邻经验分工：`2026-11-12-wiki-update-version-token-expiry-restart` 管阶段 0"令牌不匹配→重开"的判定（本条是其重开之后的续篇）；`2026-11-09-wiki-hash-shortcut-requires-merge-pass` 管"有 changed 小节但判定零修订"时仍须发 patch 走 merge 的闭环（与本条构成有无 changed 对象的互补两侧）；`2026-11-11-wiki-added-mislabeled-merkle-reset-hash-triage` 管"全量 added 误标时以 hash 甄别"（与本条共享"hash 为内容权威"的原则）；`2026-11-09-repeat-changed-set-reuse-prior-round-verdicts` 管"同批变更复用上轮判定先验"（本条中 unmatched 沿用先验清零即其应用）。

## Evidence or Examples

- 源会话 ses_e32e25b09ffeSjYrHNrWK7ATrq（docgen-apply fork #1，Date 项目，version_token 422→423，变更 3/349≈0.9%，.workbuddy 运行时日志判成因 1 过滤后有效 2 个 notes 文件）。
- 零修订轮实证：reverse_lookup 报两篇受影响文档（codebase-knowledge/知识库笔记.md S2、project-knowledge/documentation_system S1）所有小节 hash_status=unchanged，notes 两文件内容 hash 与上轮基线（8cade6051e5c / dd7743c822bb）完全一致；unmatched 仅 1 项（.workbuddy/.../memory.md）实读确认为自动化签到运行日志判成因 1，与上轮同判。
- fix_code_links 实况：`fix_code_links.py --help` 显示必选参数 `--code-links-file`（单文件模式）；wiki 目录无 .code-links.json 残留 → 无操作，修订报告降级记录留痕。
- 闭环验证：build_index status=success，`{"reused": 8, "updated": 0, "added": 0, "total": 8}`，code_paths_verified=69，.code-links.json 已删除；阶段 7 检查 WikiRetrieval.md 标记完整（WIKI_RETRIEVAL_START/END）、code-links 残留 0、索引 JSON 有效 format_errors=[]。
- 复现频率：Date 项目为每日定时 Wiki 更新任务，检测器状态推进型空转轮自 2026-11-11 起已连续复现（token 414→422→423 跨多轮，其中多轮内容零变更）。