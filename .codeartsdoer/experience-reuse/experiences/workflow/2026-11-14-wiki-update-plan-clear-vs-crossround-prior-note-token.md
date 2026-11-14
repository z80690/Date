---
id: 2026-11-14-wiki-update-plan-clear-vs-crossround-prior-note-token
title: update_plan 轮末清空会吞掉成因判定留痕：判定依据迁移 stage note_<token> 追加式留痕
category: workflow
nature: pitfall
created_at: 2026-11-14T02:10:37
updated_at: 2026-11-14T02:10:37
tags: [wiki增量更新, 留痕迁移, 跨轮先验, progress.json, 流程矛盾]
keywords: [update_plan 清空, note_token, 跨轮先验, 判定留痕, progress.json, stage_2 note, 追加式记录, 成因判定, 先验复用, 增量更新]
problem_patterns:
  - "按既有经验把成因判定留痕写进 update_plan note，轮末 Stage 6 清空 update_plan 时留痕一并消失，下一轮同批变更无法复用先验判定"
  - "为保留历史把新判定覆盖写进旧 batch_note 字段，历史实证被冲掉，复盘时无法追溯各轮判定依据"
source_sessions: [ses_e29ecd91cffeATlJqZnujMKp9s]
project: Date
severity: medium
quality_score: 82
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: A
related_experiences: [2026-11-12-wiki-index-code-refs-absence-cause2-patch, 2026-11-09-repeat-changed-set-reuse-prior-round-verdicts, 2026-11-12-wiki-zero-revision-round-full-short-circuit, 2026-11-11-programmatic-atomic-json-state-rewrite, 2026-11-14-wiki-cause1-off-surface-zero-revision-lightweight-round]
---

# update_plan 轮末清空会吞掉成因判定留痕：判定依据迁移 stage note_<token> 追加式留痕

## Scenario

Wiki 增量更新流程（repo-simple-wiki-update 类）中，unmatched 文件的成因判定依据需要留痕供校验与复盘追溯（既有经验的指导是"在 update_plan note 中记一行"）。但主技能流程同时要求：Stage 6（最终落盘阶段）要**清空 update_plan** 并把本轮 update_plan 整体写入留痕迁移。两条要求直接矛盾——成因判定的留痕写进 update_plan，轮末就被清空动作吞掉；而下一轮若出现同批/同类变更，"复用上轮判定先验"恰恰依赖这些留痕存活（例如"该文件上轮已判成因 1"的先验）。单轮执行时不会暴露，跨轮复现时才显现为留痕丢失。

## Key Signals

- **矛盾结构**：流程规则 A"判定留痕写入 update_plan note" vs 流程规则 B"Stage 6 清空 update_plan"——A 的载体被 B 销毁，属流程设计时未对齐的隐性冲突。
- **留痕丢失的后果形态**：下一轮同批变更重报时，无法从 progress.json 找到上轮"为何判成因 1/成因 2"的依据，只能重新走一遍四步证据链；若代理不重走而凭印象复用，则判定无据可查。
- **覆盖式记录的风险信号**：若为省事把新轮判定覆盖写进既有 `batch_note` 之类的共享字段，历史轮次的实证细节被冲掉，审计链断裂。

## Essence

留痕的存活期必须与先验的消费期对齐：update_plan 是**单轮工作面**（轮末清空是设计行为，用于宣告本轮修订面处置完毕），而成因判定依据是**跨轮先验资产**（供后续轮次复用与复盘）。跨生命周期的信息不能寄存在单生命周期载体上。正确做法是把判定依据从 update_plan 迁移到按轮次命名的持久字段——`note_<version_token>`——并用**追加而非覆盖**的方式落盘：每轮新增自己的 `note_<token>`/`update_note_<token>` 键，历史键原样保留。这样 Stage 6 清空 update_plan 不再损失任何跨轮信息，先验复用与历史审计同时成立。

## Approach

1. **轮内正常留痕**：判定完成时照常把依据记入 update_plan note（供本轮校验环节读取）。
2. **Stage 6 清空前迁移**：执行 update_plan 清空动作前，把成因判定依据（判定结论 + 关键证据：内容性质、module_tree 归属、索引 grep 结果、路径一致性）压缩成一行写入 `stages.stage_2.note_<version_token>`（如 `note_557`），键名带轮次令牌保证轮间不冲突。
3. **追加式轮次记录纪律**：各 stage 的新增记录一律用 `note_<token>`/`update_note_<token>` 新键追加，禁止覆盖历史 `batch_note` 或旧轮 `note_<token>`；历史实证永久保留。
4. **落盘方式**：progress.json 局部更新用 edit 工具按最小块逐键替换（一次只动一个键值对，不跨 stage 块边界），避免吞相邻键名；超长 JSON 块改写改用独立 Python 脚本原子完成。
5. **下一轮复用入口**：新轮次做成因判定前，先扫描 `note_<token>` 键族查同路径历史判定，命中即复用先验并注明来源，未命中再走完整证据链。

## Faster Next Time

- 一行决策规则：写留痕前先问"这个信息的消费期是本轮还是跨轮"——跨轮信息禁写 update_plan，直接进 `note_<token>`；轮末清空 update_plan 前必查是否有未迁移的判定依据。
- 键名设计：`note_<version_token>` 天然防轮间冲突与防覆盖，比日期键更贴合流程已有的令牌体系。
- ROI：同批变更高频复现的定时更新场景下，一轮的成因判定证据链（实读+归属+grep+路径四步）在后续轮次零成本复用；避免留痕丢失导致的重复取证或凭印象复用。
- 反模式：把跨轮判定依据只写 update_plan note（轮末即失）；覆盖写 batch_note（历史丢失）；为图省事在 progress.json 里做跨 stage 块的大段 edit（吞相邻键）。

## Applicability Boundaries

- 适用：带"轮末清空工作面 + 跨轮先验复用"双机制的增量流程；progress.json 类含 stages 结构的状态文件；凡"判定依据需要留痕且流程存在清空动作"的场景。
- 不适用：信息消费期仅限本轮的临时备注（留在 update_plan 即可，勿污染持久字段）；无 update_plan 清空动作的流程（矛盾不存在，无需迁移）；首次全量生成（无历史先验可复用）。
- 与相邻经验分工：2026-11-12-wiki-index-code-refs-absence-cause2-patch 给出了"update_plan note 留痕"的原指导，本条实证其与 Stage 6 清空的矛盾并给出修正载体（迁移后原单轮留痕做法仍可保留）；2026-11-09-repeat-changed-set-reuse-prior-round-verdicts 管先验复用的判定纪律（本条解决其依赖的留痕存活问题）；2026-11-11-programmatic-atomic-json-state-rewrite 管超长 JSON 块的原子改写（本条 Approach 第 4 步的降级通道）。

## Evidence or Examples

- 源会话 ses_e29ecd91cffeATlJqZnujMKp9s（docgen-apply fork #1，Date 项目，version_token 557 轮）。
- 实证落盘：本轮成因 1 判定证据链（实读为 WorkBuddy 运行日志 / module_tree 5 模块均不涵盖 / grep `workbuddy` 0 命中 / 路径一致）在 Stage 6 清空 update_plan 前迁移至 `stages.stage_2.note_557`；各 stage 记录以 `note_557`、`update_note_557` 等新键追加，历史 batch_note 未动。
- 落盘方式实证：progress.json 全部更新通过 8 次小粒度 edit 逐键完成（mode/started_at/stage_2 判定/stage_3、stage_4 轮次记录/update_context/update_plan 清空/顶层 completed），未触碰相邻键名，零编辑事故。