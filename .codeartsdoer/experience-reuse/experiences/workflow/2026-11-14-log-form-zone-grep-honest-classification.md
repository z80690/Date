---
id: 2026-11-14-log-form-zone-grep-honest-classification
title: 混合子项目仓库日志形态先 grep 判定后如实归类：无传统 logging 框架时写"JSONL 结构化留痕"，不虚构 logging 约定
category: workflow
nature: methodology
created_at: 2026-11-14T11:30:20
updated_at: 2026-11-14T11:58:18
tags: [日志形态盘点, 结构化留痕, 规范知识文档, 分区grep, 如实归类]
keywords: [import logging 全仓判定, print 残留扫描, JSONL 追加写留痕, 事件流落盘 events.jsonl, 页面消息机制 dvwaMessagePush, record_id UTC 时间戳, 审计目录 config 源头确认, 三类留痕形态归类, 禁虚构 logging 约定, 第三方消息机制原状保留]
problem_patterns: [生成日志类规范文档时按传统 logging 模板虚构约定，实际仓库全仓无 import logging 走 JSONL 结构化留痕, 全仓 grep "logging" 命中多为配置与经验文档字样提及而非源码使用，误当源码证据导致形态误判, 第三方遗留项目的页面消息机制（非持久化）被误当日志缺陷纳入开发者规则，应识别后原状保留]
source_sessions: [ses_e2d3a7140ffeupcMttiKV9k45J]
project: Date
severity: medium
quality_score: 82
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: A
related_experiences: [2026-11-06-verify-before-write-knowledge-docs, 2026-11-14-dispatch-fact-baseline-verification-dependency-multi-source, 2026-11-06-project-knowledge-provenance-format]
---

# 混合子项目仓库日志形态先 grep 判定后如实归类：无传统 logging 框架时写"JSONL 结构化留痕"，不虚构 logging 约定

## Scenario
为混合子项目仓库（多语言、多形态留痕并存）生成"日志系统"类 project-knowledge 规范文档，由 subagent 独立执行、禁反问。派工单只给"起点事实（需核验）"：adapter/ 疑似 JSONL 留痕、workflow_base 疑似事件流落盘、第三方遗留项目疑似页面消息机制。仓库日志形态可能完全分散，文档必须落到真实形态上。

## Key Signals
- 触发判定序的第一信号：派工单给出的日志形态线索全部标注"需核验"，且明示"若某子项目无传统日志框架，如实描述"——即预期存在"非 logging 形态"的可能。
- grep 全仓 "logging" 命中 32 处，但逐条看命中几乎全是 .codeartsdoer/ 下配置、技能文档与经验文档里的字样提及，没有任何一处是源码 `import logging`——宽松关键词命中与真实形态无关，是本场景最容易误判的点。
- 追加执行 `import logging` 精确检索返回 No files found，构成"无传统日志框架"的决定性证据，形态判定由此定型。

## Essence
日志形态判定必须以"源码级精确检索"为决定性证据（`import logging` 有无），而不是以宽松关键词命中数为依据；判定为无框架后，产出口径必须如实归类为"无统一日志框架，采用 JSONL 结构化留痕"，禁止按传统 logging 模板虚构级别配置、轮转、logger 层级等仓库不存在的约定。形态盘点按"谁写（落盘点）→ 写什么结构（record 字段）→ 写到哪（目录从 config 源头确认）→ 谁消费"四问定向阅读补齐，最终按持久化证据流 / 事件流 / 非持久化消息三类归档描述。

## Approach
1. **形态定性检索**：全仓精确 grep `import logging`（决定性）与 `print(`（残留扫描）；宽松词 "logging" 命中的配置/文档字样只作线索、不作证据。
2. **无框架时的替代机制盘点**：grep `jsonl`/`.log`/消息推送函数名，枚举"替代留痕机制"清单——JSONL 流落盘、事件流文件、遗留项目页面消息等。
3. **落盘点定向阅读四问**：读每个落盘点源文件，确认（a）并发安全（线程锁/原子写+重试），（b）记录结构（record_id、UTC 时间戳、载荷字段），（c）目录位置（从 config 常量源头确认，不凭路径猜测），（d）消费者（注释或调用方）。
4. **三类形态如实归类**：持久化证据流（JSONL 追加写、带 ID+时间戳）、事件流落盘（状态迁移点即时写）、非持久化页面消息（第三方遗留，仅描述、原状保留），每类标注持久化程度与消费者。
5. **规则从源码归纳**：开发者规则逐条对应源码实证（如"演练过程必须 JSONL 留痕""禁 logging/print 残留""证据缺失禁造数"）；第三方遗留机制不写成"缺陷/待改造"，不发明仓库不存在的规则。

## Faster Next Time
- 固化为四步判定序：`import logging` 精确检索 → 替代机制枚举 → 落盘点四问定向阅读（每文件 <100 行）→ 三类形态归类。两次定向阅读即可完成整仓形态盘点，避免按错误模板虚构后返工与知识库污染。
- 警惕信号：grep 宽松词（logging/log/jsonl）命中数很多但全在文档/配置区，绝不据此写"使用 logging 框架"。
- 落盘点细节（锁、record 结构、目录常量）当场随读随记并直接回标行号进 code-links，比写完文档回头补省一轮通读。
- 第三方遗留项目的 LSP 固有报错（如全局运行时注入变量 Undefined）与本次产出无关，不作缺陷纳入。

## Applicability Boundaries
- 适用：混合子项目/多语言仓库的日志类规范知识文档生成、接手陌生仓库盘点"日志去哪了"的静态源码盘点。
- 不适用：已有统一 logging 框架的仓库（应走框架配置盘点：handler/级别/格式）；运行期日志行为验证（本方法只覆盖静态形态）。
- 与既有经验分工：派工单起点事实的通用核验纪律见《知识库生成规范文档先核实仓库实际状态再动笔》与《预填事实基线实测核验与依赖清点多源交叉判定》；code-links 溯源格式细则见《project-knowledge 文档粒度与 code-links 溯源格式清单》。本条管"日志主题的形态判定方法与归类口径"这一层特化。

## Evidence or Examples
- 项目 Date：grep `import logging` 全仓 No files found；grep "logging" 32 处命中均在 .codeartsdoer/ 配置与经验文档；dvwaMessagePush 51 处命中于 DVWA PHP 页面（setup.php/security.php/login.php 等）。
- adapter/storage.py：`append_record` JSONL 追加写，entry 携带 `record_id`（uuid_hex）+ `recorded_at`（UTC isoformat），`threading.Lock` 串行化，流含 dispatches/receipts/boundary/captures/verdicts/pairings/gate/portaudit/proxycheck，注释明示为 IF-9/IF-10 消费的证据主干。
- workflow_base/core/store.py：资产 JSON v1 原子写（tmp + os.replace + 3 次 0.2s 重试），事件流独立落 `events.jsonl`，状态迁移点即时写、执行中中间态不落盘。
- adapter/config.py:13：`AUDIT_DIR = DRILL_BASE / "audit"`，DRILL_BASE = temp/p003_drill——目录位置从 config 源头确认。
- 产出：logging_system.md（≤5KB，4 小节）+ logging_system.code-links.json（3 小节 code_refs），开发者规则 5 条全部对应源码实证；DVWA LSP 报错判定为第三方固有、与产出无关。