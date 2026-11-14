---
id: 2026-11-13-lsp-diagnostics-path-attribution-triage
title: 写盘后 LSP 诊断噪音按文件路径归属甄别——诊断 file 不在本次变更/产出集合内即为无关噪音，不阻断交付
category: agent-ops
nature: decision
created_at: 2026-11-13T18:46:22
updated_at: 2026-11-13T18:49:48
tags: [LSP诊断, 噪音甄别, 第三方仓库, 路径归属, 写盘误报]
keywords: [LSP diagnostics, 诊断噪音, DVWA, 第三方克隆仓库, 路径归属, 误归因, 写盘后诊断, PHP 报错, 甄别规则, 不阻断交付]
problem_patterns:
  - 写盘（如 patch JSON）后 IDE 推送大量 LSP 报错，误归因为刚写的内容存在质量问题，对无关文件发起无效排查
  - 工作区常驻第三方克隆仓库（DVWA 类 PHP 项目），每次写盘后重复出现其文件报错，新会话/新 subagent 首次遇到时反复消耗甄别成本
source_sessions: [ses_e2cb71dbbffe4pGvhUi74Bf1b2]
project: Date
severity: low
quality_score: 85
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-11-third-party-repo-clone-vetting-not-a-module, 2026-11-12-write-tool-yaml-validation-false-error-bash-bypass]
---

# 写盘后 LSP 诊断噪音按文件路径归属甄别——诊断 file 不在本次变更/产出集合内即为无关噪音，不阻断交付

## Scenario

只读 subagent 执行 wiki 小节级修订派工，主产物是写入 `.codeartsdoer/temp/` 的结构化 patch JSON（非源码文件）。写盘完成后，IDE 连续推送多批 LSP ERROR 诊断（20+ 条）。任务边界：产出 patch 后做格式校验并返回交付确认，禁止直写 wiki 文档。

## Key Signals

- 诊断推送紧随写盘动作出现，时序上容易诱导"是我刚写的内容有问题"的归因——但被诊断文件与本次写盘路径零交集。
- 全部诊断的 file 字段指向 DVWA 第三方克隆仓库的 PHP 文件（`DVWA/setup.php` 未定义变量 `$DBMS` 等、`DVWA/vulnerabilities/sqli/source/{low,impossible,index}.php` 未定义常量/变量），属于靶场资产的固有静态分析噪音。
- 本次产物（patch JSON）自身无任何诊断报错；随后的程序化格式校验（无 BOM、严格 JSON、逐 patch 字段形态）全部通过，与甄别结论互证。

## Essence

诊断推送的时序跟随写盘动作，但**诊断来源与写盘动作之间没有因果关系**——Agent 运行环境中，平台会在任意写盘后推送当前工作区的全量待处理诊断，这与人工 IDE 场景（报错通常紧跟自己编辑的文件）不同。甄别的唯一依据是**诊断的 file 字段路径归属**：诊断文件不在本次变更/产出路径集合内 → 无关噪音，留一句甄别说明后继续交付；有交集 → 仅排查交集文件。工作区含第三方克隆仓库（DVWA 类）时，其文件报错是常驻噪音源，每次写盘都可能重复出现，不值得进入排查循环。

## Approach

1. **收集诊断归属集合**：逐条读取 LSP 诊断的 `file` 字段（不看错误内容先看归属），汇总为诊断文件集合。
2. **比对路径交集**：诊断文件集合 ∩ 本次写盘/变更路径集合——空集 → 全部为无关噪音；非空 → 仅交集内的诊断为候选真实问题。
3. **噪音留痕后继续交付**：对空集结论留一句显式说明（如"报错均来自 DVWA 第三方克隆仓库 PHP 文件，与本任务无关"），使甄别决策可审计，然后继续执行后续校验与交付，不发起对噪音文件的排查。
4. **反向纪律**：诊断文件恰为任务产物本身（如写的 JSON/源码被报错）时，必须当作真实质量问题排查，不得套用本规则跳过。

## Faster Next Time

- 一步判定：看诊断的第一条 `file` 字段是否指向本次写盘的路径——不是 → 大概率整批噪音，抽验 2-3 条确认即可收口。
- 提前免疫：会话开始时记住工作区常驻的第三方克隆仓库（本工作区 = DVWA），写盘后见到这些路径的报错直接跳过。
- ROI：甄别成本 ≈ 读几个 file 字段；漏判代价是把无关报错当真问题排查数轮，或反向把真实产物报错当噪音放过（后者由 Approach 第 4 步的交集检查兜底）。

## Applicability Boundaries

- 适用：任何写盘后收到 IDE/LSP 全量诊断推送的 Agent 环境（CodeArts 类 IDE 平台实证；通用 Agent 模式同样适用）；工作区含第三方克隆仓库、测试靶场等非任务资产的场景。
- 不适用：诊断文件在本次变更/产出集合内（真实问题，必须排查）；显式打开/编辑某文件后针对该文件的诊断（因果成立，不是噪音）；无 file 字段的聚合告警（先补归属信息再甄别）。
- 与相邻经验分工：`2026-11-11-third-party-repo-clone-vetting-not-a-module` 管第三方克隆仓库在 wiki 模块判定中的处置（不建模块不展开），本条管其 LSP 诊断噪音维度的甄别，是该仓库处置的互补面；`2026-11-12-write-tool-yaml-validation-false-error-bash-bypass` 管写工具自身假报错的绕行，本条管与写盘无因果的外来诊断噪音，两者构成"工具反馈真伪/相关性甄别"的两类形态。
- 证据等级：单次实战闭环（20+ 条噪音诊断一次甄别通过 + 程序化校验互证），无失败对照；"常驻噪音源重复出现"为合理推断，复用中验证。

## Evidence or Examples

- 源会话 ses_e2cb71dbbffe4pGvhUi74Bf1b2（@general wiki 修订 subagent，trace 内联提供；写盘对象 `.codeartsdoer/temp/_patch_adapter.json`）。
- 噪音样本：`DVWA/setup.php` [22:6] Undefined variable '$DBMS' 等 20 条、`DVWA/vulnerabilities/sqli/source/low.php` [8:8] Undefined constant 'MYSQL'、`impossible.php` [16:13] Undefined variable '$db'、`index.php` [52:21] Undefined variable '$number_of_rows'——全部为 PHP 未定义变量/常量类静态分析错误。
- 甄别留痕：subagent 显式记录"LSP 报错均来自 DVWA 第三方克隆仓库的 PHP 文件，与本任务无关"，随后 patch 校验输出 `no-BOM strict-json-OK`，交付未受影响。