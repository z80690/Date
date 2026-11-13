---
id: 2026-11-12-wiki-patch-word-limit-verify-shrink-loop
title: wiki 小节修订 patch 的字数上限程序化自检与超限定向微缩闭环
category: agent-ops
nature: technique
created_at: 2026-11-12T08:33:24
updated_at: 2026-11-12T08:33:24
tags: [agent-ops, patch-json, word-limit, verification-loop, wiki-revision]
keywords: [字数上限自检, 超限定向微缩, patch JSON 落盘, UTF-8 无 BOM 验证, replace_content, 概述 200 字, 架构设计 300 字, 复验闭环, 篇数计数更新, 修订派工]
problem_patterns:
  - "派工单规定每节字数上限（如概述≤200、架构设计≤300），修订须在保留既有描述的同时补入新条目，目测估字不准导致超限返工"
  - "patch JSON 落盘后仅凭眼审，未程序化验证 BOM/字数/code_refs，漏检后由应用方退回"
  - "发现超限后整段重写引入新问题或丢信息，而非定向微缩一轮收敛"
source_sessions: [ses_e393de697ffeOHIc1Pa2GDUdKw]
project: Date
severity: medium
quality_score: 84
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: A
related_experiences: ["2026-11-11-subagent-wiki-patch-code-refs-read-verify", "2026-11-12-prompt-snippet-authority-over-stale-skeleton-anchors", "2026-11-08-wiki-section-tiered-revision-judgment-contract", "2026-11-08-subagent-patch-field-drift-silent-content-loss"]
---

# wiki 小节修订 patch 的字数上限程序化自检与超限定向微缩闭环

## Scenario

只读修订 subagent（如 @general）承接 wiki/知识库小节级修订派工：patch JSON 载体、修订者禁写 wiki 原文件、每节 new_content 有显式字数上限（本例概述 ≤200、架构设计 ≤300）。典型难点是修订必须"保留既有全部描述 + 补入新条目定位 + 更新篇数计数"，在不动其他内容的前提下字数天然增长，上限余量往往只剩几个字。此类派工高频出现，字数超限是继行号失真之后第二常见的 patch 退回原因。

## Key Signals

- 派工单逐节给出字数上限（"总字数≤200/≤300"）——这是必须程序化计数而非目测的强信号。
- 首测输出显示超限幅度很小（如 304 超上限 4 字符）：超限通常是列举项冗余、连接词堆叠造成的零头，不是结构性问题。
- 修订对象的原节内容已接近上限（原节 255/300），补一条新条目定位必然顶破余量。

## Essence

字数上限的合规不能靠写时目测，必须走"落盘 → 程序化自检 → 定向微缩 → 复验"闭环。超限时做**定向微缩**（压掉语义重复的列举项、合并同义短语、删连接词），保留全部事实信息与既有描述语义，一轮即可收敛；整段重写反而有丢信息/引新错的风险。该闭环与 code_refs 取证（事前实读）互补：取证管"引用对不对"，自检闭环管"形态合不合规"，两者都过 patch 才算可交付。

## Approach

1. 动笔前从派工单提取三项硬约束：每节字数上限、section_title 逐字复制规则（以受影响小节实际标题为准，模板锚点注释不算）、code_refs 格式（`相对路径:行号`，行号必填）。
2. 修订 new_content：先保证内容完整（既有描述不丢 + 新条目定位 + 计数更新），暂不纠结字数。
3. 落盘 patch JSON（UTF-8 无 BOM）到派工单指定临时路径。
4. 程序化自检（一段脚本一次跑完）：① BOM 检查；② 逐节字符数对照上限；③ code_refs 逐条核对格式与文件存在性；④ section_title 与实际文档标题逐字比对（实际文件标题可能无模板中的 category 注释）。
5. 超限节做定向微缩：优先合并语义重复的列举、压缩同义短语与连接词；禁删事实信息、禁整段重写。微缩后回到第 4 步复验，直至全部达标。
6. 交付消息只含：patch 文件路径 + 每节修订要点一句话 + 自检结果（含最终字数），不粘贴 patch 全文。

## Faster Next Time

- 一行规则：内容完整优先、字数合规靠测——先写满再微缩，顺序反了会两头返工。
- 预算意识：原节已接近上限（如 255/300）时，新条目定位控制在 40 字以内，计数更新用最短表述（"共 19 篇"→"共 20 篇"）。
- 快捷检测：超限 ≤10 字符属零头级，微缩必收敛；超限 >30 字符通常是没删干净旧描述或重复列举，先查语义重复再动笔。
- 自检脚本一次覆盖 BOM/字数/code_refs/标题四项，比三轮眼审快且无漏检。

## Applicability Boundaries

- 适用：带显式字数上限的 wiki/知识文档 patch JSON 修订派工（主 Agent 与只读 subagent 模式均可）；主 Agent 侧作应用方校验提交 patch 时也可直接复用该自检脚本。
- 不适用：无字数约束的修订（只需 BOM/code_refs 两项）；代码 diff patch（行数与字数语义不同）；行号取证问题（见 code-refs-read-verify 与 skeleton-anchors 两条相邻经验）。
- 自检依赖本机 Python/PowerShell 可用；字符计数口径须与派工单一致（本例为字符数非词数）。
- 证据等级：单次实战闭环（两节均一轮微缩收敛），微缩策略的收敛性未经大样本反例检验。

## Evidence or Examples

- 来源会话：ses_e393de697ffeOHIc1Pa2GDUdKw（@general 修订 codebase-knowledge/知识库笔记.md 概述 + 架构设计两小节，变更源为新增 notes/架构反思与建议.md，篇数 19→20）。
- 实测迭代数据：概述 255→199（上限 200，达标）；架构设计 480→304（超限 4 字符）→4 处定向微缩→300（上限 300，达标）。
- 自检实证：落盘后脚本输出 `bom=False`、`概述 len=199`、`架构设计 len=304` → 微缩 → 复验 `架构设计 len=300、refs_ok=True`。
- 落盘产物：`C:\Users\Administrator\Desktop\Date\.codeartsdoer\temp\patch_notes.json`（UTF-8 无 BOM），两节均为 replace_content，code_refs 统一为 `notes/架构反思与建议.md:1`（新增文件取 :1），未触碰 wiki 原文件。
- 标题形态差异实证：模板小节标题带 `<!-- category:overview -->` 注释，实际文档标题为纯"概述/架构设计"——section_title 按实际文档逐字复制，patch 应用匹配才不受影响。