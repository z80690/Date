---
id: 2026-11-14-homogeneous-module-library-doc-representative-sampling
title: 结构同质模块库知识文档的代表抽样与分组表格生成法
category: workflow
nature: methodology
created_at: 2026-11-14T12:22:50
updated_at: 2026-11-14T12:26:15
tags: [doc-generation, representative-sampling, grouping-table, granularity-control, codebase-knowledge]
keywords: [同质模块库, codebase-knowledge, 分组表格, 代表抽样, 分级实现, 粒度上限, 符号骨架空, PHP 不被符号扫描支持, module_id, code-links]
problem_patterns: ["多成员同质模块库文档任务粒度失控、逐成员长篇展开超上限", "符号骨架与切片产物为空时误判项目无内容"]
source_sessions: [ses_e2d40ce36ffeJQItyP11NY36lZ]
project: Date
severity: low
quality_score: 84
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: A
related_experiences: [2026-11-14-php-include-chain-injection-lsp-false-positive, agent-ops/2026-11-14-md-notes-module-doc-gen-stale-ref-verify, agent-ops/2026-11-14-skeleton-first-targeted-read-module-doc-gen]
---

# 结构同质模块库知识文档的代表抽样与分组表格生成法

## Scenario
为大模块库生成 codebase-knowledge 模块文档的典型约束组合：成员多（本次 DVWA/vulnerabilities 19 个漏洞模块、169 文件）、结构同质、全文粒度上限硬性（≤5KB）且禁止逐成员长篇展开；任务还要求同批产出 .code-links.json（逐节 code_refs 且行号必填）。若逐个通读全部成员文件，token 成本高且极易超粒度。

## Key Signals
- 适用触发信号：任务描述同时出现"成员结构同质" + "粒度上限"（全文 KB 上限 + 单节字数上限）+ "禁止逐成员展开"——三条件齐即代表抽样法适用。
- 过程信号：符号骨架为空、切片产物极少。若误读为"项目无内容"会走错路径；纯 PHP 项目（符号扫描器不支持 PHP）预期如此，应直读源文件而非依赖扫描产物。

## Essence
同质结构意味着信息高度冗余：确认一个成员的骨架（入口装载 + 分级实现模式）即确认全部成员的模式，剩余差异仅在"额外文件"层面。因此文档信息密度应来自**模式描述 + 分组覆盖**，而非逐成员展开。本次实测：抽 2 个代表成员（sqli、xss_r）读 source/low.php 与 source/impossible.php 加各自 index.php，即确认四级实现通用模式（low 直接拼接 → impossible 预处理 + 参数绑定 + Anti-CSRF + 输入校验）与装载方式（index.php 按安全级别 switch 后 require_once source/{level}.php），随后一次写入成功，产物 2.7KB，远低于 5KB 上限，零返工。

## Approach
1. 目录列举确认成员清单——拿到准确的成员数与名单，作为分组表格的覆盖基准。
2. 抽 2-3 个代表成员：选覆盖不同类型的最典型成员（本次 sqli 代表注入类、xss_r 代表跨站类），读入口文件 + 最低/最高两级实现，确认同质模式与装载机制。
3. 正文用分组表格覆盖全部成员：按类型分组、每组一行（成员列表 + 一句话职责）；特殊文件（src/ 控制器、openapi.yml、辅助输入页等）在表格注释行补充，不另开长篇。
4. 各节粒度自检后一次写入 .md 与 .code-links.json；code_refs 行号以抽读时确认的实际文件行为准。
5. 写入后源码侧 LSP 报错按关联经验判定，不阻塞交付。

## Faster Next Time
- 判据前置：任务描述出现"结构同质/同质模块"+"粒度上限"即直接套用本执行序，不做全量通读。
- 骨架空速判：纯 PHP 项目符号骨架为空、切片产物极少属预期，直接以目录列举 + 代表抽读替代符号扫描产物。
- 粒度保险：分组表格天然把架构节压在百字级，配合"每组一行"约束可稳定满足 300 字内限制；全文控制在 3KB 量级可为粒度余量兜底。

## Applicability Boundaries
- 适用：成员结构同质（同一套入口/实现/说明文件布局）的多成员模块库知识文档任务；粒度受限场景。
- 不适用：成员结构异质、各成员需独立描述架构时应逐成员展开；成员极少（≤3）时抽样反增往返；要求逐成员详尽档案的场景与本法的粒度目标互斥。
- 相邻经验分工：`agent-ops/2026-11-14-skeleton-first-targeted-read-module-doc-gen` 管符号骨架可用时的"骨架先行+定向补读"路径；`agent-ops/2026-11-14-md-notes-module-doc-gen-stale-ref-verify` 管纯文档（笔记目录）模块的空骨架预期与清单抽样——本条管"骨架为空但确为代码模块库"的第三种形态，按骨架可用性与模块内容形态三选一。

## Evidence or Examples
- 本次 trace：DVWA/vulnerabilities 19 模块清单（api、authbypass、bac、brute、captcha、cryptography、csp、csrf、exec、fi、javascript、open_redirect、sqli、sqli_blind、upload、weak_id、xss_d、xss_r、xss_s）经目录列举确认；代表抽读 sqli（含 session-input.php 等额外文件）与 xss_r；产物 漏洞演练模块库.md 2736B + .code-links.json 1288B，module_id 为 dvwa_vuln，一次写入成功，无返工轮次。
- ROI：抽 2 个代表模块约 5 个文件替代 169 文件全量通读；文档一次成型，零修订轮次。