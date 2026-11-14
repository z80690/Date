---
id: 2026-11-13-glossary-advisory-and-techfinding-term-admission
title: 术语新增准入的两个补充拒收类别：优化建议属建议态非现行机制，故障归因属技术发现细节非业务术语
category: agent-ops
nature: decision
created_at: 2026-11-13T18:21:22
updated_at: 2026-11-13T18:21:22
tags: [术语表修订, 新增术语准入, 建议态判别, 技术细节判别, 零修订判定]
keywords: [建议态, 现行业务机制, 优化建议文档, 技术发现细节, 故障归因, 新增术语禁令, line_number_only, 零修订, 业务术语表, code_refs 实读核实, 术语准入三问, 只读 subagent]
problem_patterns:
  - 变更内容中出现优化建议文档里的提议（如判定源双轨制），误当"新业务机制"据以新增术语条目，把建议态内容固化进术语表
  - 变更中出现故障/环境归因类技术发现（如 Npcap loopback fast-path 限制、NBNS 整改），有名字有语义被误判为"新概念"，混淆技术细节与业务术语层级
  - 事实表收工行正文信息密度高（进度+归因+口径+建议引用混杂），直觉判"信息多应有新术语"，未先做来源性质与概念层级核查
source_sessions: [ses_e2cb661a4ffevCukjut0SdbN1t]
project: Date
severity: low
quality_score: 86
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-09-glossary-status-refresh-zero-revision-criterion, 2026-11-13-glossary-dispatch-premise-mismatch-minimal-patch, 2026-11-08-wiki-section-tiered-revision-judgment-contract, 2026-11-09-subagent-patch-code-refs-baseline-fallback]
---

# 术语新增准入的两个补充拒收类别：优化建议属建议态非现行机制，故障归因属技术发现细节非业务术语

## Scenario

以只读修订 subagent 身份接收业务术语表 S2 小节级修订派工（受影响小节：概述、术语列表）：变更源为两文件——`adapter/verdict.py`（裁决判定改基于结构化证据计数，新增 evidence_insufficient 判定路径）与 `notes/项目事实表.md` §8 特性进度（G6/G7 收工状态值刷新，收工行正文含判定源切换、round-09 重跑归因、用户裁决口径等高密度信息）。派工单预判两小节均 line_number_only，并内嵌新增术语禁令。硬约束：只输出结构化 patch JSON，禁写文件。

## Key Signals

- 事实表收工行正文信息密度极高：进度标记（G6.1~G7.4 ✅）、重跑归因（Npcap loopback fast-path 限制）、口径声明（hidden_failure 最诚实口径）、建议态内容引用（判定源双轨制出自"优化建议"文档）混杂在一行内——表面看每项都"像新概念"。
- 高危误判源 1：优化建议文档中的提议性内容（判定源双轨制）措辞与正式机制无异，仅从事实表行文无法区分"已生效"还是"建议中"。
- 高危误判源 2：故障归因类技术发现（Npcap loopback fast-path 限制、NBNS 整改）有明确的名字和语义，极易被误判为"新业务术语"。
- 派工单明文预判：判定源双轨制属建议态非现行机制、loopback fast-path/NBNS 属技术发现细节，均禁止新增术语条目——subagent 职责是验证预判并留排除记录。

## Essence

术语新增准入判据族在"状态值（任务号/ID/进度）"与"代码符号（枚举/常量/类名）"之外还有两个补充拒收类别：

1. **建议态内容 ≠ 现行业务机制**。出现在优化建议/待办/评估类文档中的提议（如判定源双轨制）是"建议态"，未获用户裁决采纳前不是现行业务机制；术语表只承载现行机制，把建议态写进去等于未裁决先固化，还会误导后续修订者与检索者把提议当事实。
2. **技术发现细节 ≠ 业务术语**。故障/环境归因类发现（如网络栈行为限制 Npcap loopback fast-path、协议整改项 NBNS）有名字有语义，但属于技术细节层级，不满足"面向业务领域"的术语准入标准——与代码枚举值/类名同级拒收。

判定动作：新增术语前做三问——是现行机制还是建议态？是业务概念还是技术发现细节？定义是否已被现有条目覆盖？三问全过才允许新增条目；任一不过 → 现有条目已覆盖变更语义 → line_number_only（new_content 为 JSON null）。

## Approach

1. **变更源分层阅读**：事实表/进度类变更行信息密度高，先拆解为"进度值/归因细节/口径声明/建议引用"四类，再逐类过准入判据，不要整行整体判断。
2. **来源性质核查**：对疑似新概念追问权威出处——出自优化建议/待办/评估类文档 → 建议态，拒收；出自用户裁决留痕且已生效的机制描述 → 现行机制，才进入定义覆盖比对。
3. **概念层级核查**：对有名字有语义的新发现（故障归因、协议名、环境限制），问"这是业务概念还是技术实现/环境细节"——技术细节一律不入术语表。
4. **定义覆盖比对收尾**：实现层强化与口径类变更逐条对照现有术语定义（如"裁决"定义已含"三类结论+证据链断裂如实判证据不足"，verdict.py 的 evidence_insufficient 判定路径细化已被覆盖）。
5. **输出零修订 patch 并留排除记录**：两小节均 line_number_only、code_refs 实读核实后输出（基线为空时新建引用，每条须有实读证据）；排除理由（建议态/技术细节/已覆盖）保留在执行记录备查。

## Faster Next Time

- 准入三问口诀：建议态？技术细节？已覆盖？——任一命中即拒收，全部通过才新增。
- 速查信号：名词出现在"优化建议/待办/整改项"清单里 → 建议态；名词是对故障/异常的环境归因（某某限制/某某整改）→ 技术发现细节。
- 事实表收工行的"归因+待办"混排是误判高发区：归因细节（loopback fast-path）和待办项（NBNS 整改）都在正文里但都不是术语候选。
- ROI：三问核查一轮目扫可完成；误新增"建议态伪术语"的后果是术语表被污染且随 patch 合并传播，返工成本远高于核查成本。

## Applicability Boundaries

- 适用：术语表/领域概念类 Wiki 小节的只读 subagent 修订派工；变更源为状态事实表或含建议态引用、技术归因细节的高密度进度文档。
- 不适用：业务概念本身增删改（走同层面分流判定契约）；派工单声称的引用结构实读缺失（走空集不虚构判据）；授权直改文档场景。
- 与相邻经验分工：`2026-11-09-glossary-status-refresh-zero-revision-criterion` 管状态值禁令（拒收源=任务号/ID/进度门禁），本条补两个新拒收类别——建议态内容（拒收源=优化建议文档）与技术发现细节（拒收源=故障/环境归因），四类合起来构成术语新增准入的完整闸门；`2026-11-13-glossary-dispatch-premise-mismatch-minimal-patch` 管实现层强化型零修订与引用结构存在性（拒收源=函数名/常量名），本条与其"定义已覆盖"判据衔接；`2026-11-08-wiki-section-tiered-revision-judgment-contract` 是"改与不改"的节级分流通用上游框架。
- 证据等级：单次实战闭环（判据来自派工单明文预判并被执行验证，属正例固化，无踩坑修复对照）；两类拒收判据在后续同类派工中的稳定性待复用检验。

## Evidence or Examples

- 源会话 ses_e2cb661a4ffevCukjut0SdbN1t（@general 修订 subagent，业务术语表 S2 派工，trace 内联提供）。
- 建议态拒收实证：派工单明文"判定源双轨制等出现在'优化建议'文档中属建议态，非现行业务机制，禁止新增术语条目"——判定源双轨制未被写入术语表。
- 技术细节拒收实证：round-09 重跑归因"Npcap loopback fast-path 限制（8788/8443 演练流量 0 帧/5432 335 帧在）"与"NBNS 整改（裁决 C 保留不改）"均判为技术发现细节，未入术语表。
- 已覆盖实证："裁决"定义已含"成功/失败/证据不足三类结论；证据链断裂时如实判证据不足"——`verdict_from_counts` 结构化证据计数与 34-36 行 evidence_insufficient 判定分支（adapter/verdict.py:9、:34 实读核实）属该定义的实现细化。
- code_refs 新建实证：wiki 正文无引用行（基线为空），实读核实后新建 3 条——adapter/verdict.py:9、adapter/verdict.py:34、notes/项目事实表.md:79（G6/G7 收工行）；每条均有实读证据，非虚构。