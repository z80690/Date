---
id: 2026-11-14-skeleton-first-targeted-read-module-doc-gen
title: 有源码模块知识文档全新生成的两段式阅读策略：骨架先行定全貌+装配枢纽定向补读，骨架行号直接复用为 code_refs
category: agent-ops
nature: technique
created_at: 2026-11-14T11:45:21
updated_at: 2026-11-14T11:58:18
tags: [符号骨架, 知识文档生成, 定向补读, code_refs, subagent]
keywords: [符号骨架先行, 装配枢纽, 定向阅读, 骨架行号复用, 一份数据两用, 模块知识文档, code_refs 取证, 阅读策略, subagent 派工, 装配关系]
problem_patterns:
  - 为模块生成知识文档时跳过骨架直接通读全部源文件，阅读量大且装配关系仍抓不住重点
  - code_refs 行号写完文档后回头定位，多一轮全仓搜索
  - 补读文件按文件大小或目录顺序选择，读了非枢纽文件仍未确认模块间装配关系
source_sessions: [ses_e2d3d1e96ffeHg8ncRxWaCFZ8l]
project: Date
severity: low
quality_score: 85
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-12-prompt-snippet-authority-over-stale-skeleton-anchors, 2026-11-11-code-refs-evidence-line-over-default-line, 2026-11-06-verify-before-write-knowledge-docs, 2026-11-07-dispatch-brief-embedded-fact-pack, 2026-11-14-source-module-empty-skeleton-expected-doc-gen, 2026-11-14-md-notes-module-doc-gen-stale-ref-verify]
---

# 有源码模块知识文档全新生成的两段式阅读策略：骨架先行定全貌+装配枢纽定向补读，骨架行号直接复用为 code_refs

## Scenario

以 subagent 身份承接"有源码模块"的代码仓知识文档**全新生成**派工（非修订、非纯文档仓库）。派工单提供：已核实的模块结构事实包（pyproject 配置、文件清单、符号统计）、符号骨架路径（类/函数签名+行号锚点）、切片产物路径、文档模板、`.code-links.json` 契约（wiki_section + code_refs 格式）与粒度约束（全文 ≤5KB、架构小节 ≤300 字、禁罗列全部符号清单）。subagent 独立执行、不可中途向派工方确认。

## Key Signals

- 符号骨架含全部类/枚举/函数签名与行号锚点（本例 61 符号/13 文件），一次读取即获得模块全貌：契约枚举、异常层次、核心类与函数职责分布。
- 骨架的回答边界在**符号层**：它能回答"有什么符号、各自签名是什么"，回答不了"模块间怎么装配、协议细节如何"——这正是架构小节的核心内容。
- 派工事实包（"已核实"标记的结构事实）可作信任基线，无需动笔前重复验证；补读只用于事实包与骨架都覆盖不了的装配/协议细节。

## Essence

符号骨架是**一份数据两用**的资产：① 文档内容全貌的来源（符号→职责分组→架构叙述）；② code_refs 行号的直接取证源——写文档时同步抄骨架锚点，免去写完后回头全仓定位行号的一轮搜索。补读的必要性与选择标准由此确定：只补骨架没有的信息（模块间装配、协议细节），文件按**装配关系枢纽**选择（协议接口实现文件 + 契约模型文件），2-4 个封顶；不按文件大小或目录顺序选。阅读量公式：骨架 1 次全读 + 枢纽文件 2-4 个 ≈ 全模块通读量的零头，且装配关系叙述有据可依。

## Approach

1. **骨架先行**：完整读一遍符号骨架（含行号锚点），建立模块全貌——枚举契约、异常层次、核心类/函数清单与职责分布。
2. **识别装配枢纽并定向补读 2-4 个**：从骨架与 import 关系找出"模块间装配"的枢纽文件（协议接口实现 + 契约模型），只读这些文件确认装配方向与协议细节；不通读其余源文件。
3. **行号同步抄用**：写各小节时，code_refs 行号直接抄骨架锚点（或补读文件中实读核实过的行），写完文档即完成溯源 JSON，不回头补行号。
4. **架构小节按装配写**：以"职责分组 + 核心类名 + 依赖方向"叙述（如 契约层→基础设施层→门禁层→执行裁决层的单向依赖），禁止把骨架符号清单原样罗列进文档（违反粒度约束）。
5. **交付汇报粒度证据**：汇报全文大小、各小节字数与 code_refs 总数，便于派工方验收。

## Faster Next Time

- 阅读策略一行规则（模块文档生成三分支判定链）：清单全 .md/纯文档模块 → 模块级空骨架属预期路径（见 2026-11-14-md-notes-module-doc-gen-stale-ref-verify）；清单含源码 + 骨架空/切片少 → 先查语言支持范围定性空因（见 2026-11-14-source-module-empty-skeleton-expected-doc-gen）；骨架健康可用 → 骨架 1 读全貌 + 枢纽 2-4 个补装配（本经验）；骨架对本轮变更文件失真 → 切换行号权威源（见相邻经验 prompt-snippet-authority），不要在本经验路径上硬抄骨架行号。
- 警惕信号：补读超过 4 个文件仍未确认装配关系 → 说明骨架统计与实际结构不符（骨架不健康），停下核对骨架健康度，而非继续堆阅读。
- ROI：省去通读全部源文件的轮次与 token；code_refs 行号免二次定位；架构小节从"符号罗列"升级为"装配关系叙述"，一次通过粒度验收。
- 反模式：跳过骨架直接通读源文件；按文件大小/顺序选补读对象；写完文档再回头全仓搜行号。

## Applicability Boundaries

- 适用：有源码模块、派工单提供符号骨架/切片产物的知识文档全新生成（subagent 独立执行模式，平台无关，CodeArts 类 IDE 实证）；泛化到任何"骨架/索引先行 + 定向补读"的代码理解与文档任务。
- 不适用：符号骨架对本轮新增/变更文件失真或缺失（行号权威源切换见 `2026-11-12-prompt-snippet-authority-over-stale-skeleton-anchors`——该条明确把"骨架可直接用"场景列为不适用，本条正是该场景的展开，两经验互补成对）；纯文档仓库零预提取产物场景（见 `2026-11-06-doc-repo-zero-extraction-knowledge-gen`）；修订场景中同一文件内的内容证据行选择（见 `2026-11-11-code-refs-evidence-line-over-default-line`）。
- 与相邻经验分工：dispatch-brief-embedded-fact-pack 是本条的输入前提（事实包作信任基线免重复验证）；verify-before-write 管"派工单现状断言需核实"，本条假设事实包已核实、聚焦阅读策略本身。
- 证据等级：单次顺畅闭环（61 符号骨架 1 读 + 4 个枢纽文件定向补读 → 3.2KB 文档 + 14 条 code_refs 一次通过，无返工无弯路），无失败对照；"补读上限 4 个"来自派工模板的合理约束，复用中检验。

## Evidence or Examples

- 源会话 ses_e2d3d1e96ffeHg8ncRxWaCFZ8l（@general subagent，Date 项目 P003 演练适配器模块文档生成，2026-11-14）。
- 骨架实证：`.codeartsdoer/.codebase/branches/master/docs/skeleton/adapter.txt`（61 符号/13 文件，行号锚点齐全）。
- 枢纽补读实证（4 个）：gate.py（门禁放行检查）、receipt.py（回执协议状态机、派发五重前置）、verdict.py（J1~J5 纯判定 + evidence_insufficient 不造数）、models.py（契约枚举与 frozen dataclass）。
- 产出实证：`P003演练适配器.md` 约 3.2KB（各节低于粒度上限）+ 同名 `.code-links.json`（3 个 wiki_section、14 条 code_refs，行号全部抄自骨架），一次通过无返工。
- 同会话噪音甄别复用命中：写盘后 IDE 推送 DVWA PHP 文件 LSP 报错，subagent 按路径归属甄别直接判定为第三方克隆噪音，未消耗排查轮次（`2026-11-13-lsp-diagnostics-path-attribution-triage` 预言的"新 subagent 首遇"场景再次验证）。