---
id: 2026-11-14-wiki-unchanged-baseline-increment-body-refs-routing
title: 基线小节 unchanged 时的增量补判修订：逐文件同层面判定分流"正文改写 vs 仅登记引用"
category: workflow
nature: decision
created_at: 2026-11-14T13:07:39
updated_at: 2026-11-14T13:07:39
tags: [wiki 增量更新, 小节修订, 增量补判, 内容分流, 溯源登记]
keywords: hash_status unchanged, 增量 hash 无记录, 补判修订, 同层面判定, 状态数据动态, 资产类新增, replace_content, code_refs 登记, 统计计数联动, patch JSON
problem_patterns:
  - Wiki 小节修订派工中受影响小节 hash_status=unchanged，误以为基线未变无需修订，漏掉本轮基线外新增/修改文件对小节正文的影响
  - modified 状态类文件引入特性进度、门禁位等状态数据动态，误写进描述层小节正文污染组织结构叙述粒度
  - 批次新增同类资产文件时不知正文该逐篇展开还是点名归组，总篇数/分类计数与清单不同步造成文档自相矛盾
source_sessions: [ses_e2fa4d230ffeR1dG6JHqjXTA9t]
project: Date
severity: medium
quality_score: 86
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-08-wiki-section-same-layer-action-criteria, 2026-11-12-wiki-added-diagnostic-probes-body-exclusion, 2026-11-11-wiki-added-mislabeled-merkle-reset-hash-triage, 2026-11-11-wiki-stat-count-drift-recount-on-revision]
---

# 基线小节 unchanged 时的增量补判修订：逐文件同层面判定分流"正文改写 vs 仅登记引用"

## Scenario

Wiki 增量更新的小节级修订派工（修订者持 patch JSON 输出契约、不直改文档）。本轮变更集规模小而混杂：若干 added 的同类资产文件（如系列笔记/学习成果）+ 一两个 modified 的状态类文件（如项目事实表）。派工单点名受影响小节时标注其 hash_status=unchanged（既有基线），但变更清单中存在该小节覆盖路径下、上次扫描基线中没有 hash 记录的增量文件。

## Key Signals

触发信号不是小节 hash 变化，而是派工单中的组合声明：

1. 受影响小节 hash_status=unchanged——按常规判据（hash changed 才改正文）应跳过。
2. 同一份派工单明确存在增量文件（added/modified），且声明"增量 hash 无记录按 changed 处理，需修订正文"。
3. 增量文件性质异质：同类资产扩容（与既有"沉淀类别"同层）与状态数据动态（进度、门禁位、执行位）混在同一变更集。

若只认小节 hash，会把第 2 类信号短路掉，产出"零修订"——这正是本经验要防的漏判方向。

## Essence

小节 hash unchanged 只证明"该小节正文自上轮以来未变"，不证明"本轮增量对该小节无影响"。增量文件缺少基线 hash 记录时，必须逐文件补判同层面归属，判定不得沿用小节 hash 短路。补判的核心二分：

1. **资产类新增（同层面）**：新增文件与既有小节关注点同层（如同一沉淀类别的成员扩容）→ replace_content 改写正文，且必须联动统计计数（总篇数、分类计数）与清单列举，二者只改其一会造成文档自相矛盾。正文中点名主题+批次属性即可，逐篇展开是粒度下沉。
2. **状态类修改（不同层面）**：modified 文件引入的是状态数据动态（特性进度、门禁位、当前执行位等）→ 不属于描述层小节"提供什么能力/如何组织"的关注点，正文一字不写，仅以 code_refs 登记引用锚点留痕。

补判是"逐文件"的：同一变更集内两种方向可以并存，一个 patch 的不同小节各自独立裁决。

## Approach

1. **入口判定**：收到小节修订派工时，先看"小节 hash_status"与"变更文件清单"两个输入是否矛盾（unchanged 但有覆盖路径下的增量文件）。增量文件在基线中无 hash 记录 → 视同 changed，进入补判，不因 unchanged 直接短路。
2. **逐文件同层面判定**：对每个增量文件问"它属于该小节已有关注点的哪个成员维度"——是既有沉淀类别的扩容（同层面），还是运行状态/进度登记（不同层面）。
3. **同层面 → 正文改写**：replace_content 更新正文；同步核对并刷新统计计数与类别列举；批次新增的同类文件在正文中点名主题与批次属性，不做逐篇展开。
4. **不同层面 → 仅登记引用**：正文零改动，把文件以 `相对路径:行号` 形式登记进该小节 code_refs（状态文件锚定到实际变更行，资产文件锚定到标题行）。
5. **code_refs 增量语义**：保留既有引用、追加本轮新增引用，构成"既有+新增"的完整列表再交付 patch；不要只交新增部分。
6. **交付前自检**：正文中的计数、列举、批次属性与变更清单一一对应；不同层面内容确认未混入正文。

## Faster Next Time

- 检查单（收到派工即过一遍）：
  - [ ] 小节 unchanged ≠ 无需修订，先查变更清单里有无该小节覆盖路径下的增量文件；
  - [ ] 增量文件逐个标注"资产类/状态类"，二分流后再动笔；
  - [ ] 改正文必查统计计数（总数、分类数）是否联动；
  - [ ] 状态类内容核对未进正文、已进 code_refs；
  - [ ] code_refs 输出 = 既有引用 ∪ 本轮新增引用。
- 警示信号：派工单里同时出现"unchanged 基线"与"需修订正文"的声明，就是补判场景的路标，不要按字面 hash 语义否掉后者。
- ROI：一次判定避免双向返工——漏判方向（零修订留过时口径，下轮增量更新再补救）与污染方向（状态动态写进正文，粒度失真、下轮清洗）各要一轮派工。

## Applicability Boundaries

- 适用：小节级修订派工（patch JSON 契约）中"unchanged 基线 + 基线外增量文件"的组合；同类资产批次新增与状态文件修改混合的变更集。
- 不适用：
  - 小节 hash_status=changed 的常规修订（直接走同层面 action 判据，见相关经验）；
  - 变更状态全量 added 的数据库重置误标场景（先做 hash/骨架甄别，见相关经验）；
  - added 文件是诊断探针、内部常量等实现细节（判定理由是"实现细节下沉"，不是本经验的"状态数据动态"，但落点动作相同）。
- 前提约束：修订者不持直改权限、以 patch JSON 交付；派工单自带变更文件清单与小节基线声明，修订者不自行重扫全库。

## Evidence or Examples

来源会话：ses_e2fa4d230ffeR1dG6JHqjXTA9t（Wiki 文档小节级修订 subagent，单轮闭环）。

- 变更集：3 added（三篇系列学习成果，均为标题行 1）+ 1 modified（项目事实表，hunk 行 67-83 新增特性进度整节）。
- 受影响小节"概述/架构设计"hash_status=unchanged；派工单声明"增量 hash 无记录按 changed 处理，需修订正文"。
- 裁决结果：三篇学习成果与"学习成果沉淀"关注点同层面 → 两小节均 replace_content，篇数统计 22→25、学习成果 4→7 联动刷新，正文中点名三篇主题与批次交付物属性；项目事实表新增的特性进度/门禁位属状态数据动态 → 不写入正文细节，仅 code_refs 登记（notes/项目事实表.md:70）。
- code_refs 交付形态：既有 3 条引用全部保留 + 追加 4 条（3 篇新增文件 :1 + 事实表变更行），共 7 条随 patch 输出。
- 符号骨架为 0（纯 Markdown 变更）属预期，行号锚点直接引用 .md 实际行号，不构成跳过修订的理由。