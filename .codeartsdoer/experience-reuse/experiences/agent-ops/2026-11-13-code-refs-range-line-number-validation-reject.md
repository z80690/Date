---
id: 2026-11-13-code-refs-range-line-number-validation-reject
title: code_refs 区间行号被校验器拒绝（"缺少行号"文案误导）：确定性拆单行号本地修复，禁升级重试 subagent
category: agent-ops
nature: pitfall
created_at: 2026-11-13T13:23:45
updated_at: 2026-11-13T13:23:45
tags: [code-refs, 校验器契约, 区间行号, 确定性修复, wiki校验]
keywords: [validate_code_links, 缺少行号, 区间行号, code-links.json, 单行号格式, 确定性错误, 本地修复, 重试决策, 校验流水线, subagent patch]
problem_patterns:
  - "subagent patch 的 code_refs 写区间行号 `path:16-20`，validate_code_links 报 error `缺少行号`——文案误导排查方向，实为校验器只接受单行号格式、不支持区间写法，而非行号真缺失"
  - "校验失败一律走纠正式重试 subagent，把可本地 edit 修复的确定性格式错误升级为整轮重派，浪费一轮派工与等待"
source_sessions: [ses_e2cb1b7b7ffe0zGnKiSyEBCaRk]
project: Date
severity: low
quality_score: 85
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-08-wiki-update-script-behavior-contract-blindspots, 2026-11-11-subagent-wiki-patch-code-refs-read-verify, 2026-11-13-merge-code-refs-replace-semantics-union-guard, 2026-11-08-wiki-section-revision-patch-json-mode]
---

# code_refs 区间行号被校验器拒绝（"缺少行号"文案误导）：确定性拆单行号本地修复，禁升级重试 subagent

## Scenario

Wiki 增量更新主流程 merge 之后跑校验流水线（validate_code_links → redact_secrets → lint_wiki）。subagent 产出的 patch 中 code_refs 写了区间行号 `temp/p003_drill/drill_round06_captured.py:16-20`（指 import 区，行号已实读核实），merge_section_patch 原样并入 `.code-links.json`，随后校验器整篇判 failed。编排者需要决策：走纠正式重试 subagent，还是本地修复。

## Key Signals

- 校验输出指纹：`{"location": "links[1].code_refs[0]", "actual": "temp/p003_drill/drill_round06_captured.py:16-20", "expected": "\"路径:行号\"（如 \"src/main/java/X.java:5\"）", "error": "缺少行号"}`——`expected` 已明示单行号格式，`actual` 的值一眼可辨区间写法；"缺少行号"字面与实际根因（格式不支持区间）不符。
- 其余 3 篇文档全部 passed——失败仅 1 处、且是纯格式问题，无内容性疑点。
- 该 code_refs 来自 subagent 的 line_number_only patch（关系小节，正文未变仅刷引用），行号区间语义为"行范围引用"（import 区 16-20 行），subagent 交付消息已注明实读核实。

## Essence

校验器对 code_refs 的格式契约是**单行号**（`路径:行号`），区间写法（`路径:起-止`）整条被拒且报错文案误导。校验失败应先按错误性质分流：**确定性格式错误**（区间行号、缺行号、路径风格）本地直接 edit 中间产物修复后复验；只有**内容正确性问题**（引用指向错误内容、行号与断言不符）才值得走纠正式重试 subagent。区间行号的前提是 subagent 已实读核实行号范围，拆分为逐行单行号不损失语义，本地修复是安全的。

## Approach

1. **校验失败先分类**：读 `actual` vs `expected` 字段——纯格式差异（区间、缺分隔符）→ 本地修；`actual` 指向的行号与文档断言可能不符 → 才重试。
2. **本地拆分**：edit 对应 `.code-links.json`，把 `path:16-20` 拆为 `path:16`、`path:17`、…、`path:20` 多条单行号（或按引用意图取锚点行，如 import 区取首行 16）。
3. **复验**：重跑 validate_code_links 直至全 passed（本例 4/4），再继续 redact_secrets / lint_wiki。
4. **预防上游**：后续给 subagent 的派工 prompt 中明确"code_refs 行号必须是单行号（`路径:行号`），禁止区间写法 `路径:起-止`"，把契约前置到生产端而不是靠校验端拦截。

## Faster Next Time

- 一行决策规则：**确定性错误本地修，语义性错误才重试**；`expected` 字段给出格式样例时，对照 `actual` 即可秒判。
- 报错文案对照："缺少行号" = 格式不支持区间/非单行号（本坑），不要去找"哪一行缺了"；真缺行号的形态是 `actual` 为纯路径无冒号行号。
- ROI：本地 edit 一次复验通过 vs 重试 subagent 一轮（派工 + 实读 + 重新 merge + 再校验），至少省一个完整往返。
- 反模式：见校验 failed 就无条件走纠正式重试流程；把区间行号"修复"成只保留起止两端（`:16` + `:20`，语义残缺）；不预防上游导致每轮都靠校验端兜底。

## Applicability Boundaries

- 适用：validate_code_links 消费 `.code-links.json` 的 wiki/知识文档校验流水线；一般化到任何"校验器对结构化引用有单值格式契约、报错文案不精确描述根因"的场景——先对照 expected 样例判根因。
- 不适用：code_refs 指向的文件/行号本身不存在（真缺失，需回源核实）；replace_content 型 patch 的正文质量问题（语义层，须重试）；区间语义确需保留且下游支持范围引用的场合（本流水线不支持）。
- 与相邻经验分工：script-behavior-contract-blindspots 管 merge/H1/frontmatter 盲区与参数契约（merge 侧），本条管校验器格式契约与修复决策（validate 侧）；code-refs-read-verify 管 subagent 实读取证顺序（生产端），本条管校验失败的分流修复（消费端）；union-guard 管 merge 的 code_refs 并集保护语义（merge 合并行为）。
- 证据等级：单次成功闭环（1 处区间行号拆 5 条单行号，复验 4/4 passed）；"取锚点行"分支未在本次实际触发，属推断补全，待复用检验。

## Evidence or Examples

- 源会话 ses_e2cb1b7b7ffe0zGnKiSyEBCaRk（docgen-apply fork #1，Date 项目）。
- 失败实测：临时素材与知识萃取.code-links.json 的 links[1].code_refs[0] = `temp/p003_drill/drill_round06_captured.py:16-20` → validate_code_links `{"status": "failed", "passed": 3, "failed": 1, "error": "缺少行号"}`，runner 首失败短路退出。
- 修复实测：edit 将区间拆为 5 条单行号（16/17/18/19/20），复验 `{"status": "passed", "total": 4, "passed": 4, "failed": 0}`；后续 redact_secrets（0 可疑）与 lint_wiki（0 errors）一次通过，未重派任何 subagent。
- 行号语义佐证：subagent 交付消息注明"实读源码核实 import 区仍为行 16-20"——区间行号本身经实读核实，拆分无损。