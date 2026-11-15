---
id: 2026-11-08-wiki-section-revision-patch-json-mode
title: 知识库 Wiki 小节修订的建议-合并分离模式：patch JSON 落盘固定目录 + 权威源实读核实口径
category: workflow
nature: methodology
created_at: 2026-11-08T02:33:44
updated_at: 2026-11-08T02:33:44
tags: [文档修订, patch分离, 核实先行, 口径同步, 知识库]
keywords: [wiki-patches, patch JSON, 小节修订, replace_content, section_title, code_refs, 权威源实读, 口径联动更新, 提炼不抄录, UTF-8 无 BOM, 合并脚本, updated_at 自动刷新]
problem_patterns:
  - 派工修订 Wiki/知识库文档小节但修订者不持直改权限，直改会绕过合并脚本并破坏 updated_at 自动维护链
  - 规范文档大改版（如公约 7 条改 6 条）后 Wiki 小节仍是旧口径，不知哪些小节需联动改写、漏改必留旧口径残句
  - 派工单声明"已核实/逐字一致"但修订者需独立确认变更对照材料与实文一致后才动笔
source_sessions: [ses_e48be4b84ffepvfkcHuGMEfP5w]
project: Date
severity: medium
quality_score: 87
hit_count: 14
last_hit_at: 2026-11-15T04:35:40
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-06-verify-before-write-knowledge-docs, 2026-11-06-multi-copy-authority-layering-pointerization, 2026-11-06-project-knowledge-provenance-format, 2026-11-06-annotated-incremental-revision-grep-verify]
---

# 知识库 Wiki 小节修订的建议-合并分离模式：patch JSON 落盘固定目录 + 权威源实读核实口径

## Scenario

以 subagent 派工方式修订 project-knowledge 类 Wiki 规范文档的若干小节（本例 4 小节：概述/关键文件与位置/架构与约定/开发者应遵守的规则）。派工单提供：变更对照材料（旧版口径描述 + 新版实文）、受影响小节当前内容、模板小节写法规范（概述 ≤200 字、提炼清单不抄全文等）。硬约束：**不要直接修改 Wiki 文档**，产出结构化 patch 由上游合并脚本统一应用。修订者独立执行、无法中途确认。

## Key Signals

- 痛点信号：Wiki 文档的 `updated_at` 由合并脚本自动刷新——修订者直改文档或手写该字段都会破坏自动维护链。
- 痛点信号：派工单写明"已同步为相同 6 条，已核实"——这是声明不是证据，按声明动笔等于把核实责任转嫁给不可验证的转述。
- 痛点信号：同一套旧口径渗透多个小节（概述写"七条行为规范六维度"、架构写"七条五组"、开发者清单列 7 条）——只改其中一处，其余小节残留旧口径，合并后文档自相矛盾。
- 参考行号被标注"可自行核实行号后调整"——派工方明示行号未经验证。

## Essence

修订建议与文档合并职责分离：修订者不直改文档，只产出结构化 patch（`section_title` + `replace_content` + `new_content` + `code_refs`）落盘到固定临时目录，由合并脚本统一应用并刷新元数据。patch 的**内容口径以实读权威源实文逐字比对为准**，不以派工单的对照描述或"已核实"声明为准；受影响小节**全部联动换口径**，杜绝单点改写残留旧口径。

## Approach

1. **实读比对变更结果**：把派工单声称的新口径（本例"6 条精简规矩"）与各权威载体实文逐字比对，确认一致后才按新口径动笔；旧口径描述仅作对照背景，不作为写入依据。
2. **核实派工单参考行号**：凡标注"可自行核实后调整"的行号，实读确认后再写进 `code_refs`；核实结果与派工单不一致时以实读为准。
3. **受影响小节逐节联动换口径**：每个含旧口径的小节都执行 `replace_content`，按新条数重述（本例：七条五组 → 六条三组），删除已废维度（沟通方式/经验分级/网络规范/五级优先级），不留残句。
4. **清单类小节提炼不抄录**：逐条给出主题词 + 要点（本例 6 条主题词：SDD 流程/材料评估/仓库隔离/规矩冻结/事件触发/事实仲裁），禁止整段粘贴原文充当提炼。
5. **载体小节标注权威角色**：关键文件小节为每个载体文件标注角色（内容权威源/生效权威源/派生缓存永不仲裁）与当前同步状态，语义争议裁定文本一并注明。
6. **patch JSON 落盘**：写入固定目录 `.codeartsdoer/temp/wiki-patches/<文档名>.json`（UTF-8 无 BOM），结构为 `{"wiki_file": ..., "patches": [{"section_title", "action", "new_content", "code_refs"}]}`；不手写 `updated_at`，不触碰 Wiki 文档本身。

## Faster Next Time

- ROI：实读比对只需 2 个文件 + 1 处行号的读取成本，避免按半新半旧口径产出 patch 导致合并后整轮返工；patch 字段结构固定，同类任务可直接复用模板，产出即交付。
- 警惕信号：派工单出现"已核实/逐字一致/已同步"字样 → 仍需实读；出现"可自行核实…后调整" → 必核；受影响小节清单里任何两节共享同一套旧口径 → 全部进 patch。
- 反模式：直改 Wiki 文档绕过合并脚本；patch 里手写 `updated_at`；只改开发者清单小节而漏掉概述/架构小节；整段抄录原文替代提炼；把派工单的旧版描述当作 wiki 现状直接采信而不读当前小节内容。

## Applicability Boundaries

- 适用：Wiki/知识库文档由合并脚本统一管理、修订者以派工方式介入的小节级修订；规范类文档大改版（条数/结构/维度变更）后的口径联动更新。
- 不适用：授权直改的普通文档增量编辑（走统一标注 + grep 计数核验，见 annotated-incremental-revision-grep-verify）；全新文档生成场景（现状核实与行号溯源分工见 verify-before-write-knowledge-docs）；多副本权威分层机制的设计（见 multi-copy-authority-layering-pointerization）。
- 与相邻经验分工：provenance-format 管 `.code-links.json` 溯源字段格式（wiki_section/code_refs），本条的 patch JSON 是修订建议载体、由合并脚本消费，两者不混用。
- 证据等级：单次实战闭环（实读核实 + patch 落盘成功）；合并脚本的应用结果在本 trace 之外（下游环节），模式稳定性待同类任务复用检验。

## Evidence or Examples

- 源会话 ses_e48be4b84ffepvfkcHuGMEfP5w（Wiki 小节修订 subagent 派工）：协作公约旧版 7 条 → 新版 6 条精简规矩。
- 实读核实证据：`docs/项目协作公约-最终稿.md` 与 `.codeartsdoer/rule/项目协作公约.mdc` 均为 6 条且逐字一致（各 6 行实读比对）；`notes/阶段状态机运行规则.md:74` 确为 §8 公约权威源登记行（派工单给的行号核实无误）。
- patch 落盘：`.codeartsdoer/temp/wiki-patches/collaboration_conventions.json`，4 小节 `replace_content`（概述/关键文件与位置/架构与约定/开发者应遵守的规则），每节 ≤200 字。
- code_refs 核实结果：`docs/项目协作公约-最终稿.md:1`（新公约首条）、`:6`（末条）、`.codeartsdoer/rule/项目协作公约.mdc:1`、`notes/阶段状态机运行规则.md:74`（§8 权威源）。