---
id: 2026-11-07-knowledge-ragsearch-tool-capability-boundary
title: Knowledge/RagSearch 检索工具能力边界：分词摘要检索、快照时效滞后与只读补充通道两态判定
category: agent-ops
nature: technique
created_at: 2026-11-07T09:11:58
updated_at: 2026-11-07T09:49:33
tags: [knowledge-retrieval, ragsearch, agent-platform, tool-boundary, hallucination-guard, snapshot-lag, retrieval-strategy]
keywords: [Knowledge 工具, RagSearch, 分词符号检索, searchTerms 滑窗, 模块摘要, 索引滞后, 快照滞后, 固定话术, 无结果识别, 治理文档, 三级渐进加载, build_index, 双路对比实验, No relevant content, 两态判定, 检索补充通道]
problem_patterns: [用 Knowledge/RagSearch 检索项目知识但不确定覆盖范围与结果时效, 检索工具返回的固定话术被误当作"可以基于自身知识回答"的许可, 会话中新建的治理文档在检索工具里搜不到被误判为不存在, 评估是否引入新检索通道替代或补充既有索引]
source_sessions: [ses_e4f5c5a83ffefUFnzHFvOEFJCW, ses_e4c659edfffeZ7DQtPEcp0LFr9]
project: Date
severity: medium
quality_score: 87
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-07-conflict-continuation-write-path-invariant, 2026-11-06-codeartsdoer-docs-retrieval, 2026-11-06-knowledge-base-tiered-maintenance-design]
---

# Knowledge/RagSearch 检索工具能力边界：分词摘要检索、快照时效滞后与只读补充通道两态判定

## Scenario

任务执行中需要评估平台内置知识检索工具（Knowledge / RagSearch）能否作为项目知识库（notes/ 治理文档）既有检索链路（索引 → 浓缩版 → 原文）的"第 0 层"补充或替代。典型疑问有三：检索机制与覆盖范围是什么？刚写入的笔记为什么查不到？引入新检索通道后写路径要不要跟着改？

## Key Signals

- **返回结构暴露内部机制**：Knowledge(mode=search) 的返回把 query 解析为 `symbols`（关键短语）+ `searchTerms`（约 2 字滑窗分词序列）+ `titleCases`，说明走的是分词符号匹配而非语义向量检索。
- **命中对象是模块级摘要快照**：命中文档全部是 `codebase-knowledge/` 与 `project-knowledge/` 两维度的模块级摘要（docId 如 `notes`、`docs`），frontmatter `updated_at` 停留在知识库生成时点；**看返回 filePath 前缀即可定性检索对象类型**（快照产物 vs 实时目录），是判定快照滞后的最快信号。
- **索引未随文件新建而更新**：会话期间新增的治理文档（notes/注册表.md 等）在检索结果中完全缺席。
- **RagSearch 固定话术是幻觉邀请**：无可检索知识库时返回 `No relevant content found in knowledge base. Please answer based on your own knowledge.`——字面引导"基于自身知识回答"，把它当作答许可就会编造；其真实语义是"知识库无结果"信号。

## Essence

两个检索工具的能力边界与决策规则：

1. **Knowledge = 摘要粒度 + 生成时点快照**：只覆盖建索引时生成的模块摘要文档，对索引生成之后新建的文件（尤其纯治理类 Markdown）天然滞后甚至永久缺席。
2. **RagSearch 固定话术 = 无结果信号**：一律按"未找到证据"处置，禁止按话术字面转向自身知识作答。
3. **两态判定**：B 路（平台工具）命中且新鲜 → 可讨论"接入"；B 路滞后或不覆盖 → 判"补充"（只读辅助）；冲突情形一律归入"补充"并继续实验，不因冲突终止评估。
4. **写路径唯一性不变量**：读通道可以多个，写入口必须唯一——"索引作为唯一写入口与查重入口"的架构不变量不因新读通道的存在而改变，否则查重与登记机制失效。

## Approach

1. **双路对比实验**：选取 3 个以上主题（含"应该在库的老主题"+"会话中刚新建的主题"），A 路走既有链路（索引 + 浓缩版定位锚点），B 路走平台工具同主题查询；逐主题记录双方命中与路径差异。老主题命中而新主题缺席 → 证实快照时效边界。
2. **先看 filePath 前缀定性**：B 路返回结果的路径前缀（快照产物 vs 实时目录）直接暴露检索对象类型，无需反复换查询词。
3. **解读返回结构字段**：`searchTerms` 分词形态说明匹配方式（符号匹配非语义），`updated_at` 停留时点说明数据新鲜度上限。
4. **固定话术处置**：RagSearch 出现固定话术 → 一律记为"无结果"，转自建索引路径。
5. **两态收敛**：B 路命中且新鲜 → 讨论"接入"；滞后或不覆盖 → 判"补充"，写路径维持唯一走索引；冲突不终止实验。
6. **空返回不重试**：无企业知识库 ID 的空返回属能力边界，登记结论后立即停止重试（同工具连续重复调用会触发平台 Doom Loop 保护）。
7. **留痕收口**：实验报告落盘（对比表 + 判定结论 + 不变量核验行），可选项（如快照重建 build_index）登记 U 编号待后续实验。

## Faster Next Time

- 首次用任何项目知识检索工具前，先跑"新旧双主题探针"一次即可测出覆盖边界与时效，无需读文档。
- 查不到刚写入的内容时，**先怀疑快照滞后，再怀疑工具故障**：看返回 filePath 前缀与 updated_at 即可定性。
- 看到 "Please answer based on your own knowledge" 类固定话术 → 立即归类为无结果信号，防止幻觉。
- 需要"当前最新状态"的查询（治理文档、未决事项、阶段状态）直接走索引文件 + read，不要绕道检索工具。
- 评估新检索通道永远先问一句："写路径还能保持唯一吗？"——读通道可以多个，写入口必须唯一。

## Applicability Boundaries

- 适用：CodeArts Agent（码道）平台内置 Knowledge/RagSearch 工具；任何"预构建索引快照 + 定时刷新"模型的平台检索工具；同样适用于评估其他 RAG/向量检索产物的新鲜度。
- 不适用：实时 grep/glob/语义代码检索类工具（直接读文件系统，不受快照滞后影响）；实时索引（写即更新倒排）的检索系统。
- RagSearch 的 `knowledgeIds` 参数依赖企业知识库接入，无接入时该工具不可用属预期行为。
- 快照刷新周期、build_index 手动重建的触发成本为【推断/未实证】，引入前须单独实验。

## Evidence or Examples

- 实测（2026-11-07，会话 ses_e4f5c5a83ffefUFnzHFvOEFJCW）：主题①"三库分工判定规则"命中 `codebase-knowledge/知识库笔记.md`（updated_at 2026-11-06，内容停留在知识库初始化笔记）；主题②"H4 规则变化钩子"命中的 docs 摘要中公约还是 7 条旧版；主题③"register-feature 五步准入"仅命中 project-knowledge 参考文档，notes/ 下同日新建的注册表/索引文档零命中。
- RagSearch 实测：`knowledgeIds` 必填，本项目无可用知识库，三次检索均返回固定话术（其中一次调用被用户权限拒绝——重复调用无增量，一次即止）。
- 实测（会话 ses_e4c659edfffeZ7DQtPEcp0LFr9）：对既有索引中明确存在的 3 个主题做同义查询，锚点命中 0/3；返回 filePath 全部指向平台预构建知识产物，frontmatter `updated_at` 滞后于当天——检索对象是预构建快照而非实时文件系统。
- 决策落点：实验判定为"Knowledge 接入为只读补充、索引唯一为写路径与权威查询路径"，与实验冲突处置原则（见 related: conflict-continuation-write-path-invariant）组合使用；快照重建 build_index 登记 U 编号待后续实验。