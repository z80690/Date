---
id: 2026-11-09-repeat-changed-set-reuse-prior-round-verdicts
title: 增量更新遇跨轮重复变更集先沿用上轮判定作先验：实读复核一致即收敛，不重走全量归属判定
category: workflow
nature: technique
created_at: 2026-11-09T13:56:12
updated_at: 2026-11-09T13:56:12
tags: [增量更新, 先验复用, 重复变更集, 判定收敛, 效率捷径]
keywords: [version_token, changed_files, filter_note, 先验沿用, 成因判定, 归属判定, 实读复核, 定时增量, update_context, 判定留痕]
problem_patterns:
  - 定时/高频增量更新中，本轮 changed_files 与上一轮完全相同（token 前进但文件集合重复），从头重走规模分级、三级归属判定与成因补判，重复消耗判定成本
  - 上轮已完成闭环并留有判定留痕（filter_note、成因标注、骨架结论），本轮执行者不知道这些留痕可作先验复用
  - 把先验当结论直接沿用不复核，文件性质已变时沿用过期判定导致漏改或误过滤
source_sessions: [ses_e412aeab2ffevse91wcDeqR5Mm]
project: Date
severity: low
quality_score: 87
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-08-wiki-increment-update-unmatched-file-routing, 2026-11-09-wiki-hash-shortcut-requires-merge-pass, 2026-11-08-wiki-update-script-behavior-contract-blindspots]
---

# 增量更新遇跨轮重复变更集先沿用上轮判定作先验：实读复核一致即收敛，不重走全量归属判定

## Scenario

周期性触发的增量更新流程（本例每日定时 Wiki 增量更新）：上一轮增量已完成闭环（progress.json status=completed），本轮 state.json 报告新的 version_token 与 changed_files。约束：每轮都必须给出"哪些文件进入修订面、哪些文件显式跳过"的判定并留痕，判定错误会漏改或误过滤；但流程本身高频重复，判定成本需要收敛。

## Key Signals

- version_token 前进（如 187 → 198）但 changed_files 的路径与 status 集合与上一轮完全相同——token 只证明"新一轮扫描发生"，不证明"判定结论失效"。
- 上轮 progress.json 的 `update_context` 留有结构化判定留痕：filter_note（哪个文件因何过滤）、成因标注、骨架结论——先验的可靠载体是这些落盘字段，不是记忆。
- 高频重复场景下重复文件的典型构成：工具运行时日志（路径固定、内容每日追加）+ 低频变更的权威文档——前者的判定结论跨轮恒定，后者仍需实读看内容。
- 本轮骨架结论可直接先验：纯文档仓库 .md 不出符号（0 符号 warning）这一结论与变更文件内容无关，跨轮恒真。

## Essence

上轮判定留痕构成先验，但先验只作假设不作结论：**路径集合相同 + 上轮留有结构化判定留痕 → 先按上轮结论收敛判定面，再对每个沿用结论做一次实读复核；复核一致即沿用，不一致以实读为准**。判定的可信度来自"留痕 + 复核"双要件，缺一不可——只看留痕会沿用过期结论，只做实读则浪费了留痕的先验价值。归属判定（模块路由/成因过滤）的结论在文件路径不变时通常稳定，变更的是文件内容，而内容只影响"小节级修订面"，不影响"文件级归属"——这是先验可复用的机制基础。

## Approach

1. **比对变更集合**：本轮 state.json 的 changed_files 与上轮 progress.json 留存的 changed_files 逐项比对（路径 + status）；完全相同才进入先验流程，有任何差异则差异项走全量判定。
2. **提取先验**：从上轮 progress.json 读 filter_note、unmatched 成因判定、骨架结论等结构化留痕，形成本轮预判定。
3. **实读复核每个沿用结论**：过滤类结论（如工具日志）实读文件确认性质未变（仍是日志而非新语义内容）；修订面结论实读变更文件确认变更性质，为后续小节级判定取材。
4. **分歧即全量**：任一结论复核不一致（文件性质变化、新增语义内容），该文件从先验中剔除，按无先验路径重新判定；其余一致项正常沿用。
5. **本轮留痕刷新**：沿用的先验结论写入本轮 update_plan（标注"沿用上轮先验 + 复核一致"），保持每轮判定可独立审计。

## Faster Next Time

- ROI：重复变更集下判定成本从"规模分级 + 三级归属 + unmatched 补判"收敛为"1 次集合比对 + N 次实读复核"（本例 2 个文件 2 次实读），高频定时场景每轮节省一整段判定流程。
- 快捷信号：filter_note 字段存在且语义完整 → 先验可提取；文件为工具运行时日志路径 → 沿用概率极高（路径固定、性质恒定）；文件为权威文档 → 只沿用"归属"，内容仍需实读。
- 反模式：无留痕轮次强行凭记忆复用上轮结论；变更集合有差异仍整体套用；把"沿用先验"写成判定结论而不做实读复核；沿用后不留痕（下轮失去先验载体）。

## Applicability Boundaries

- 适用：任何"扫描变更 → 逐文件归属判定"的两段式增量流程的连续轮次（Wiki 增量更新、文档索引增量、代码影响分析），前提是上轮判定留有结构化留痕。
- 不适用：首轮更新（无先验可提）；上轮流程被中断未形成闭环留痕；变更文件集合与上轮有实质差异（差异项必须全量判定）；判定规则本身已改版的场景（旧结论按新规则重算）。
- 与相邻经验分工：unmatched-file-routing 条管"无先验时三级归属判定怎么做"，本条管"连续轮次间判定成本如何收敛"——先验的产出正是该条的判定留痕，两者构成"首轮全量、后续先验复用"的成本递减链路；hash-shortcut 条管小节级短路机制，本条管文件级判定复用，层次不同。

## Evidence or Examples

- 源会话 ses_e412aeab2ffevse91wcDeqR5Mm（docgen-apply fork #1，Date 项目，version_token 187 → 198）。
- 先验提取实测：上轮（187）progress.json `update_context.filter_note` 明确记录".workbuddy/memory/automations/dec4f4ef-.../memory.md 为工具自动化执行日志（WorkBuddy 签到记录），不在 Wiki 关注层面（成因 1），过滤；实际处理 notes/项目事实表.md"。
- 复核一致实测：本轮实读 `.workbuddy/...memory.md` 确认仍为签到执行日志（命令/退出码/积分余额）→ 成因 1 沿用；实读 `notes/项目事实表.md` 确认本轮变更为新增 §7 特性进度条目 + 核验日期刷新 → 归属 notes 模块沿用、内容变更取材用于小节级判定。
- 骨架先验沿用实测：extract_symbols 输出 0 符号（.md 不支持，warning）与上轮一致，直接沿用"骨架为空、subagent 直读源文档实文"结论，未走降级评估。
- 收敛验证：判定面确定后 merge 3/3 success、validate_code_links 2/2 passed、build_index reused 5/updated 2——先验复用未引入漏改或误过滤。