---
id: 2026-11-14-wiki-subagent-artifact-defects-pre-build-index
title: Wiki subagent 批量产物入索引前的三类缺陷形态：双语标题残留、code-links 裸名错名、旧树残留清理
category: agent-ops
nature: pitfall
created_at: 2026-11-14T11:00:24
updated_at: 2026-11-14T11:18:16
tags:
  - wiki
  - subagent 产物
  - code-links
  - 校验流水线
  - 索引构建
keywords:
  - 双语标题残留
  - wiki_section 不匹配
  - code-links 裸名
  - 文件名前缀
  - build_index 吸收
  - 旧残留清理
  - 全量重建
  - validate_code_links
  - 修复方向裁决
  - docs_with_code_links 偏小
problem_patterns:
  - zh 语言 wiki 文档被 subagent 写成双语标题（## 概述 / Overview），而 .code-links.json 用纯中文小节名，validate_code_links 报 wiki_section 与文档标题不匹配，修复方向误判会反向污染 code-links
  - subagent 把 README 类文档的 code-links 写成裸名 .code-links.json（缺 wiki 文件名前缀），validate 按目录扫描能通过，build_index 按文件名配对却吸收不到，引用静默丢失
  - 全量重建后 docs 目录残留旧主题目录与旧文档，未在 build_index 之前清理，旧条目混入新索引或清理时机错失
source_sessions:
  - ses_e2d2f7062ffe4MwhDPtvKkbwi2
project: Date
severity: medium
quality_score: 87
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences:
  - 2026-11-06-project-knowledge-provenance-format
  - 2026-11-08-wiki-update-script-behavior-contract-blindspots
  - 2026-11-07-subagent-delivery-spot-check-acceptance
  - 2026-11-14-wiki-degrade-stats-clone-exclusion
---

# Wiki subagent 批量产物入索引前的三类缺陷形态：双语标题残留、code-links 裸名错名、旧树残留清理

## Scenario

主 Agent 并行派发多个 subagent 生成 wiki 文档与同名 `.code-links.json` 侧车文件，随后走 validate_code_links → redact_secrets → lint_wiki → build_index 校验流水线。subagent 隔离会话各自理解模板与语言规则，批量产物在"校验通过 → 索引消费"之间存在三类高频缺陷形态，修复时机全部在 build_index 之前。

## Key Signals

- validate_code_links 报 `wiki_section 与文档 '## ' 标题不匹配`，expected 列出双语标题（'概述 / Overview'…），actual 是纯中文（'概述'）——说明文档保留了双语标题、code-links 用了纯中文，两处口径漂移。
- docs 目录出现裸名 `.code-links.json`（应为 `README.code-links.json`）：validate 不报错（按目录收集并校验内容），build_index 却按"与 wiki 文档同名配对"吸收不到。
- docs 根目录下存在不属于新模块树的旧主题目录/旧文档（全量重建语义下的历史残留）。
- build_index 输出的 `docs_with_code_links` 小于实际携带 code-links 的文档数——有侧车文件未被吸收的量化信号。

## Essence

validate_code_links 与 build_index 的配对口径不同：前者校验"侧车文件存在 + 格式 + wiki_section 与文档标题一致性"，后者按"wiki 文件名 ↔ 同名 code-links"配对吸收引用。裸名/错名侧车文件绕过 validate 的报错面，却在索引环节静默丢引用。三缺陷的修复方向各有裁决：标题漂移改文档（zh 语言标题必须纯中文，禁止反向把 code-links 改成双语迁就错误标题）；裸名重命名补前缀；旧残留按新 module_tree 清理。

## Approach

1. build_index 前跑三查清单：① grep 全部 wiki 文档的 `## ` 标题行中的" / "双语残留（zh 语言下修复方向=把文档标题改成纯中文，与其他文档一致）；② glob 找裸名 `.code-links.json` 及无对应 wiki 文档的孤儿侧车文件，重命名补 `<wiki文档名>.code-links.json` 前缀；③ 对照新 module_tree 列清理清单，删除旧主题目录与旧文档。
2. 清理与修复完成后重跑 validate_code_links，确认 failed=0，再进 build_index。
3. build_index 后核对 stdout：`docs_with_code_links` 应等于预期携带 code-links 的文档数；偏小即仍有侧车文件未被吸收，回查命名。

## Faster Next Time

- 派工 subagent 时在 prompt 固化两条硬约束：zh 语言标题纯中文（禁双语）；code-links 文件名必须为 `<wiki文档名>.code-links.json`（禁裸名）。
- 校验失败先读 expected/actual 的漂移方向再定修复对象：actual 纯中文、expected 双语 → 改文档标题，不是改 code-links。
- 警告信号：`docs_with_code_links < 实际侧车文件数` → 存在裸名/孤儿侧车文件未被索引吸收。
- 交付级抽验兜底：subagent 返回后对产物文件名与标题格式做秒级 glob/grep 抽验（参考关联条目），缺陷在索引前暴露成本最低。

## Applicability Boundaries

- 适用：repo-simple-wiki / repo-simple-wiki-update 的 subagent 并行生成 + 脚本校验流水线；任何"subagent 产 JSON 侧车文件 + 下游按文件名配对消费"的流水线形态。
- 不适用：subagent 只产单一文档、无侧车文件的流程；validate 与索引消费配对口径一致的工具链。

## Evidence or Examples

- 本例来源：session ses_e2d2f7062ffe4MwhDPtvKkbwi2（2026-11-13，Date 仓库全量重建）。
- validate 首跑：total 15 / passed 14 / failed 4，4 条全部指向 `codebase-knowledge/DVWA漏洞演练平台/应用框架与部署配置.code-links.json` 的 wiki_section；将 6 个双语标题改为纯中文后重跑 passed 15/15。
- 裸名修复：`DVWA漏洞演练平台/.code-links.json` → `README.code-links.json`；`项目工作区/.code-links.json` → `README.code-links.json`。
- 清理与索引：删除 5 个旧主题目录 + 2 个旧 codebase 文档后 build_index success（total_docs 15、docs_with_code_links 15、code_paths_verified 262）。
- 同会话高频噪音：写盘后 IDE 推送的 DVWA PHP 源码 LSP 报错属第三方克隆静态分析误报，与本产物无关，按路径归属甄别（见 `agent-ops/2026-11-13-lsp-diagnostics-path-attribution-triage`）。