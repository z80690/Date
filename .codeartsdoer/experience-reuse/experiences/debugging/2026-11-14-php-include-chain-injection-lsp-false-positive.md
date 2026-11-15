---
id: 2026-11-14-php-include-chain-injection-lsp-false-positive
title: PHP include 链注入型代码库的 LSP 未定义符号误报判定
category: debugging
nature: pitfall
created_at: 2026-11-14T12:22:50
updated_at: 2026-11-14T12:26:15
tags: [lsp-diagnostics, php, false-positive, static-analysis, dynamic-variable]
keywords: [Undefined variable, Undefined constant, LSP 误报, PHP include 链, 全局注入, 动态变量, dvwaDatabaseConnect, 静态分析噪声, other files, 误报判定]
problem_patterns: ["写文件后 LSP 报大量 Undefined variable/constant 且报错落在 other files，疑似产物缺陷", "PHP 过程式项目静态分析噪声导致误判任务失败或误改无关原代码"]
source_sessions: [ses_e2d40ce36ffeJQItyP11NY36lZ]
project: Date
severity: low
quality_score: 86
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-14-homogeneous-module-library-doc-representative-sampling, agent-ops/2026-11-13-lsp-diagnostics-path-attribution-triage]
---

# PHP include 链注入型代码库的 LSP 未定义符号误报判定

## Scenario
在 PHP 过程式脚本项目（典型如 DVWA 类教学/遗留平台）中执行写文件操作时，工具链会对项目内其他 PHP 源码批量触发 LSP diagnostics。本次任务产物是 Markdown 文档与 JSON，写入成功后却立即收到 setup.php 与 vulnerabilities/sqli 下多个源文件的 "Undefined variable" / "Undefined constant" 错误，字面上极易误判为产物缺陷或任务失败信号。

## Key Signals
- 最早可信信号：写文件工具返回成功的同时附带 LSP errors detected in **other files**（报错文件不是本次产物本身）。
- 报错形态：setup.php 报 `$DBMS`、`$MYSQL_USER/$MYSQL_PASS/$MYSQL_SERVER`、`$DVWAOS` 等 20+ 条 Undefined variable；sqli/source/low.php 报 `$_DVWA` 未定义与 `MYSQL`/`SQLITE` 未定义常量；impossible.php 报 `$db` 未定义；index.php 报 `$number_of_rows` 未定义。
- 误导线索：报错数量大（20+ 条）且与产物文件毫无关联，若按报错去"修复"会污染与任务无关的原始代码。

## Essence
根因是 PHP 动态变量模式与静态分析器的天然冲突：这类代码库的变量与常量不靠显式声明，而由 include 链与框架函数在运行时注入——`$db` 由 `dvwaDatabaseConnect()` 注入（trace 直接可见）、`$_DVWA` 来自全局配置 include、`MYSQL`/`SQLITE` 常量由数据库抽象层 `define()`（此两项为代码上下文推断）。静态分析器无法解析该注入链，于是把每个运行时注入符号报为未定义。这是源码原有模式，不是任何一次写操作的缺陷。

## Approach
收到 LSP 未定义符号报错时按序执行判定树：
1. 先看报错文件归属：全部是 other files（非本次产物）→ 进入第 2 步；报错文件就是产物本身 → 才需真实排查。
2. 对报错符号做注入来源归因：查符号是否由框架 include 链、全局配置、`define()` 常量、框架连接/引导函数注入。命中任一 → 判定为源码原有模式（误报）。
3. 误报处理分支：不修改原代码、不回滚产物，仅在交付说明中注明"LSP 报错均为源码原有动态变量模式，与产物无关"。
4. 仅当产物自身文件被报错，或报错符号无法归因到任何注入来源时，才视为真实缺陷进入常规排查。

## Faster Next Time
- 一句话判据：PHP 无显式类型声明的代码库 + 报错全部落在 other files + 符号名是框架惯用全局名（`$_CONFIG` 类、`$db`、全大写常量）→ 三条件齐即按误报处理，零排查成本。
- 写文件后先确认报错文件清单，再决定是否读报错内容，避免被 20+ 条报错的声势带偏去"修复"无关源码。

## Applicability Boundaries
- 适用：PHP 过程式 / include 链注入型项目（DVWA、遗留 CMS 类）；其他动态注入型语言（全局注册表模式）可类比套用判定树。
- 不适用：产物文件自身报错；强类型或显式 autoload 环境下符号确实缺失的真实缺陷；报错符号无法归因到注入来源时不得套用本判据。
- 与相邻经验分层：`agent-ops/2026-11-13-lsp-diagnostics-path-attribution-triage` 为第一层判定（诊断 file 不在本次变更/产出集合内即无关噪音、不阻断交付）；本条为第二层深化——确认无关后继续对报错符号做注入来源归因，并明确禁止修改原代码。先走第一层，需要解释"为什么报错"或防止误改源码时进入本条。

## Evidence or Examples
- 本次 trace：产物为 漏洞演练模块库.md（2736B）与 .code-links.json（1288B），写入成功；LSP 报错集中于 DVWA/setup.php（`$DBMS`、`$MYSQL_*`、`$DVWAOS`、`$phpGD` 等）与 DVWA/vulnerabilities/sqli/*（`$_DVWA`、`MYSQL`/`SQLITE`、`$db`、`$sqlite_db`、`$number_of_rows`），最终判定与产物无关，任务正常交付，无返工。
- 归因证据强度：`$db` ← `dvwaDatabaseConnect()` 为 trace 直接可见；`$_DVWA` ← config include、`MYSQL`/`SQLITE` ← 抽象层 define 为代码上下文推断，置信度高但非本 trace 直接验证。