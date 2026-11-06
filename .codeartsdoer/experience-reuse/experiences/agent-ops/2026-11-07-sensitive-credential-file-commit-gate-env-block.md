---
id: 2026-11-07-sensitive-credential-file-commit-gate-env-block
title: 提交门禁敏感排查须反向扫描未跟踪区的惯例凭据文件（.env 等）并做防护闭环
category: agent-ops
nature: pitfall
created_at: 2026-11-07T05:02:00
updated_at: 2026-11-07T05:02:00
tags: [git门禁, 敏感信息, 凭据泄露, gitignore, 提交纪律]
keywords: [敏感文件排查, .env, API 令牌, SSH 公钥, 提交前门禁, 精确暂存, gitignore 加固, 凭据泄露, 未跟踪区扫描, 排除清单]
problem_patterns:
  - 工作区根目录在会话期间被外部生成敏感惯例文件（.env 等），不在提交清单内但批量暂存时可能被通配或误带入
  - 提交门禁只核对"清单内文件与批准清单一致"，未反向扫描未跟踪区导致凭据静默入库
  - 发现敏感文件后仅从本次提交排除，未加 ignore 防护与生效验证，后续提交仍可能误带
source_sessions: [ses_e4f5c5a83ffefUFnzHFvOEFJCW]
project: Date
severity: high
quality_score: 90
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [agent-ops/2026-11-06-precise-staging-bidirectional-consistency-gate.md, agent-ops/2026-11-06-git-baseline-gitignore-precheck-before-commit-planning.md, debugging/2026-11-07-gitignore-rule-silent-failure-bom-crlf.md]
---

# 提交门禁敏感排查须反向扫描未跟踪区的惯例凭据文件（.env 等）并做防护闭环

## Scenario

多阶段任务收尾执行精确暂存与提交。清单核对类门禁（暂存区与批准清单双向一致）已通过后，例行执行敏感排查（G3 类门禁）时，除核对清单内文件外还应实查工作区根目录与未跟踪区——本例正是这一步在已暂存 65 个文件、即将提交的关口拦截了一个完全不在计划内的凭据文件。

## Key Signals

- `git status` 未跟踪区出现根目录 `.env`（不在任何清单中）；
- 读取内容确认为真实凭据双要素：API 访问令牌（`CONTEXT7_API_KEY=ctx7sk-...`）+ SSH 公钥——两类凭据并存，泄露后果明确；
- 该文件是会话期间外部过程写入的，执行代理此前从未创建过它，纯靠"反向扫描"才能发现。

## Essence

提交门禁的敏感排查存在两个方向：正向核对"清单内文件是否干净"只保证批准范围合规；**反向扫描"未跟踪区是否有不该入库的敏感惯例文件"**才能拦截清单外风险。二者缺一不可。且拦截后必须做三步闭环才算处置完成：排除出本次提交 → ignore 防护（防下次误带）→ 验证防护规则真实生效（ignore 规则存在 BOM/行尾静默失效的可能，见关联经验）。

## Approach

1. 提交前门禁固定步骤：`git status --porcelain` 扫描未跟踪区（?? 项），不默认信任"我只创建过清单内文件"；
2. 对照敏感惯例文件名单逐个核实：`.env`、`.pem`、`*.key`、`credentials*`、`*token*`、`id_rsa*` 等；`git status` 中文路径转义显示不影响识别；
3. 确认含凭据 → 立即从暂存区/提交清单排除，并在汇报中显式记录拦截项（什么文件、含什么类型凭据、如何处置）；
4. 根级 `.gitignore` 追加该文件条目作为持久防护（不是只躲过这一次）；
5. `git check-ignore <path>` 逐条验证规则生效：返回路径=生效；无输出=静默失效，需按关联经验字节级重写；
6. `.gitignore` 自身的加固改动随同次或紧随提交入库，否则防护不可持续。

## Faster Next Time

- 把"未跟踪区敏感扫描"固化为提交门禁的固定动作，与清单双向核对并列，成本仅一条命令；
- `check-ignore` 是 ignore 规则生效的唯一可信验证，规则写完不验证等于没写；
- 工作区出现 `.env` 一律先按含密钥处理，再看内容定性。

## Applicability Boundaries

- 适用于 git 项目、尤其存在平台 hook/外部过程会在会话期间写入文件的运行环境（本例风险正来源于此）；
- 不适用于已用 git-crypt/SOPS 等密钥管理方案且策略文档明示豁免的仓库；
- 不替代仓库级 secret 扫描工具；本经验解决的是"提交关口的人肉门禁补漏"。

## Evidence or Examples

- 本例实测：`.env` 286 字节，含 `CONTEXT7_API_KEY=ctx7sk-7431fd22-...` 与 `KALI_SSH_PUBLIC_KEY="ssh-ed25519 AAAA... workbuddy@kali"`；
- 处置留痕：从暂存区排除（staged 65 文件不含它）→ 根级 `.gitignore` 追加 `.env/` 与 `.obsidian/` 防护 → 首次写入因行尾问题未生效，字节级重写后 `check-ignore` 分别返回两个路径确认生效 → 修复随提交 `e02afc3` 入库；
- 时序证据：拦截发生在 `da11a01`（65 文件）提交前的 G3 步骤，凭据未进入任何提交对象。