---
id: 2026-11-09-ruff-exit-code-fail-closed-gate-mapping
title: Linter 门禁集成前须探针实测 exit 全通道：Ruff 异常与违规同走 exit 1，映射规则须"非零即不过"而非"仅堵 2"
category: build-env
nature: decision
created_at: 2026-11-09T02:00:58
updated_at: 2026-11-09T02:16:06
tags: [ruff, exit-code, 门禁集成, fail-closed, 探针实测]
keywords: [ruff check, exit code, E902, F401, fail-closed, 门禁映射, 非零即不过, 探针实测, exit-zero 禁用, 工具链替换]
problem_patterns:
  - 直觉假设 linter 语义"违规=1、系统级异常=2"，把 exit 2 当唯一异常通道做门禁映射；实测 Ruff 把文件级异常（E902）也归入 exit 1，异常路径漏进门禁形成 fail-open
  - 从"exit 透传"型旧工具替换到新引擎时沿用透传假设（如 PMD 包装脚本恰好产出 0/4），未为新引擎做显式 exit 映射
source_sessions: [ses_e43fcbfdeffem2p9EzxoPQPguH]
project: Date
severity: medium
quality_score: 90
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [build-env/2026-11-07-windows-make-gate-fail-equivalent-execution, workflow/2026-11-09-gate-engine-swap-explicit-exit-mapping-adjudication-matrix]
---

# Linter 门禁集成前须探针实测 exit 全通道：Ruff 异常与违规同走 exit 1，映射规则须"非零即不过"而非"仅堵 2"

## Scenario

把 linter 集成进编码质量门禁（CI gate / 提交前审查 / SDD 执行步门禁）时，需要把工具 exit code 映射为"放行/不过"裁决；典型触发场景是工具链替换——从旧引擎（如 PMD 包装脚本）切换到新引擎（如 Ruff）时，设计者按直觉假设新工具的 exit 语义沿用旧映射。假设错误的直接后果是异常路径（文件不存在、解析失败、环境故障）被误判为"通过"或漏进门禁，形成 fail-open。

## Key Signals

- 反直觉实测信号：对不存在文件跑 `ruff check`，输出 `E902 系统找不到指定的文件。 (os error 2)` 且末行 `Found 1 error.`，`exit=1` 而非直觉假设的 2——文件级异常与违规（如 F401 的 `Found 1 error.`）共用同一 exit 通道。
- 版本参数面信号：`ruff check --help` 中可见 `--exit-zero`（有违规也返回 0，弱化门禁项）与 `-w, --watch`（监视模式）——若被误用会静默破坏 fail-closed 语义。
- 工具链替换信号：旧脚本 exit 是"透传"机制（旧引擎 exit 恰好落在 0/4 两个值上，脚本 `exit $LASTEXITCODE` 直通）；新引擎 exit 取值集不同构（Ruff 常态取 0/1/2），透传假设不成立。

## Essence

linter 的 exit code 语义是**工具实现细节而非直觉约定**：Ruff 把违规与文件级异常都收敛进非零通道（常态 1，另有致命 2），"违规=1、异常=2"的二分假设不成立。因此门禁映射的正确设计不是"枚举哪些码是异常"，而是**白名单放行**：只有 exit 0 可放行，任何非零一律判"不过"（fail-closed）。覆盖面从"仅堵 exit 2"扩展到"非零即不过"，同时兜住违规与异常两条路径，比枚举式映射更宽且更安全。工具链替换时，旧"透传"与显式映射是两种不同结构，必须为新引擎重新设计映射而非沿用。

## Approach

1. **集成前三探针实测 exit 全通道**（各一条命令，记录 exit 值）：
   - 干净探针：`ruff check <无违规样例.py>` → 期望 `All checks passed!`，exit=0；
   - 违规探针：`ruff check <含未使用 import 的样例.py>`（触发 F401 等）→ 期望 `Found 1 error.`，exit=1；
   - 异常探针：`ruff check <不存在的路径>` → 期望 E902 类异常输出，记录实际 exit 值（0.17.2 实测为 1 非 2）。
2. **通读 `check --help` 确认参数面**：确认显式文件列表、`--select/--config`（规则扩展位）、`--output-format/-o`（报告输出）、`--exit-zero`、`-w` 等旗标存在性。
3. **写显式映射规则并绑定门禁语义**：`exit 0 → 放行并留痕；任何非零 → 门禁不过（按宿主门禁语义统一收敛，如映射为 4=未过不完工）`；违规与异常在报告正文区分留痕（异常信息如 E902 单独标注，避免与非违规混淆）。
4. **列入禁用项**：`--exit-zero`（把违规洗白为 0，破坏 fail-closed）、`-w/--watch`（监视=轮询语义，违反事件驱动约束）——凡带"弱化判定/常驻监视"语义的旗标，在门禁脚本中显式禁用或不在命令行中出现。

## Faster Next Time

- 一句话自检："这次门禁集成的 exit 语义是实测过的，还是直觉假设的？"没实测就先跑三探针，5 分钟内完成，成本远低于门禁失效后的漏审追溯。
- 警惕信号：帮助文本里出现 `--exit-zero`、`--no-fail-on-*` 类弱化旗标 → 说明该工具默认语义可能与你假设的不同，必查 exit 取值集。
- 替换工具链时先问"新旧引擎 exit 取值集是否同构"：旧透传（恰好 0/4）≠ 新显式映射（0/1/2 需收敛），这是替换方案里的必列结构改动项。
- 诊断顺序：异常路径行为不明时，先造一个"必然异常"的输入（不存在文件/坏语法）看工具真实反应，不要等线上文件损坏才暴露通道归属。

## Applicability Boundaries

- 适用：Ruff 0.17.2 + Windows + `ruff check` 子命令实测；推广到任何"把 linter/静态分析工具 exit code 接入质量门禁"的场景（工具名与取值集不同，探针法与白名单放行原则通用）。
- 不适用：非门禁场景（如希望 CI 不因 lint 挡合时，`--exit-zero` 反而是正解——语义目标相反）；其他 Ruff 版本的 exit 取值集未标定，阈值与通道归属以当次实测为准，不硬编码本条实测值。
- 推断标注：非零收敛规则（0=放行/非零=不过）是门禁设计的通用 fail-closed 原则（官方惯例），"E902 归入 exit 1"为本次实测事实；两者来源不同，前者为方法论、后者为版本绑定事实。
- 与相邻经验分工：`workflow/2026-11-09-gate-engine-swap-explicit-exit-mapping-adjudication-matrix` 管门禁脚本换引擎时的映射结构设计与裁决矩阵（方案层），本条管集成前对具体引擎 exit 全通道的探针实测与版本绑定事实（取证层）——两者同属 fail-closed 门禁主题，替换/集成任务中配套使用。

## Evidence or Examples

- 来源会话：ses_e43fcbfdeffem2p9EzxoPQPguH（2026-11-09，Date 项目 20261109_ruff_review_gate 特性 design 阶段，spec-design-agent 子智能体执行，12 条消息）。
- 三探针实测输出：干净样例 `All checks passed!` exit=0；F401 违规样例 `Found 1 error.` exit=1；不存在路径探针输出 `E902 系统找不到指定的文件。 (os error 2)` + `Found 1 error.`，exit=1（非 2）。`ruff --version` = 0.17.2。
- 旧工具对比证据：旧 P3C 脚本（review-code.ps1）末行 `exit $LASTEXITCODE` 直透 PMD 返回码，恰好落在 0/4；Ruff 常态取值 0/1/2 不同构，设计将 fail-closed 显式映射为"非零即 4"，并把 `-w/--watch`、`--exit-zero` 列入禁用项（落位于 `.codeartsdoer/specs/20261109_ruff_review_gate/design.md` 的裁决矩阵与禁用项清单）。
- 决策收益：该映射决策把异常通道（E902 类）从潜在 fail-open 修正为 fail-closed，覆盖面宽于 spec 预设的"仅 exit 2 视为异常"方案。