---
name: ruff-review
description: 当 Python 编码动作发生（Write/Edit 落盘 .py 文件）或 git 提交前、或 SDD 四步流程步骤 4 完工呈报前必触发，用 Ruff 对变更 Python 文件执行静态审查并留痕报告（未过不完工）；不适用于非 Python 文件、无变更场景与用户明示豁免的提交。
---

# ruff-review — Python 审查门禁技能

## 契约 1 触发条件（三类入口，全事件驱动）

1. **落盘即审**：Write/Edit 工具完成 .py 文件落盘后，立即调用本技能审查（环境无 IDE 保存钩子，以落盘事件为触发源，等效承载"保存即审"语义）。
2. **提交前审查**：git 提交动作即将发生且变更集含 .py 文件时，提交前必调；exit 4 → 不提交不完工。
3. **SDD 步骤 4 门禁**：SDD 四步流程步骤 4（执行派工）编码产物落盘后、完工呈报前必调；exit 0 报告为完工呈报必要条件。

兜底链：落盘即审遗漏 → SDD 步骤 4 门禁与提交前审查两级兜底；发现无门禁留痕的 .py 产物，先补审再推进。三类入口均汇聚同一脚本 `scripts/ruff-review.ps1`，禁定时器/禁轮询/禁守护进程。

## 契约 2 exit 语义（取值域 {0,4}）

| 场景 | Ruff exit | 门禁 exit | 标注 |
| --- | --- | --- | --- |
| 无违规 | 0 | **0** | `pass` |
| 存在违规（F401 等） | 1 | **4** | `violations-found` + 明细入报告 |
| 文件级异常（E902 等） | 1 | **4** | `file-error(fail-closed)` |
| 进程/配置级异常 | 2 | **4** | `ruff-execution-error` |
| git 不可用 | 未调用 | **4** | `git-unavailable` |
| 报告不可写 | — | **4** | `report-unwritable` |
| 变更集无 .py | 未调用 | **0** | `no-python-changes: skip review` |

exit 0 = 完工呈报必要条件（绑定公约第 6 条"编码必审未过不完工"）。任何未预期异常收敛为 4（fail-closed，禁带病放行）。

## 契约 3 SDD 挂载说明

在 SDD 四步流程的步骤 4（执行派工）中，凡产生 Python 代码变更，本技能作为"代码审查门禁"环节**必调**——调用时机 = 该步编码产物落盘后、完工呈报前；exit 语义与门禁判定绑定（0=门禁过，4=门禁未过不完工，公约第 6 条）。与项目协作公约第 6 条"编码必审未过不完工"同一承载，无双轨并存。

## 契约 4 Ruff 底座来源指针

Ruff 0.17.2，via Scoop 安装、系统 PATH（2026-11-09 实测基线，`ruff --version` 实证）。调用形态 = `ruff check --output-format concise [--isolated] <文件集>`；ruff.toml 定制规则扩展位已预留（脚本 `--config` 参数位声明），当前默认规则（E4/E7/E9/F）起步，未创建未启用定制配置。禁用参数：`--exit-zero` / `-w --watch` / `--fix`（弱化门禁/轮询/只审不改）。

## 调用方式

```powershell
.\.codeartsdoer\skills\ruff-review\scripts\ruff-review.ps1 [-RepoRoot <项目根>] [-Files <显式列表，服务自测>] [-OutReport <报告路径>]
```

默认从 git 变更集筛选 .py 文件审查；报告默认落 `%TEMP%\ruff-review-<日期>.txt`（同日多次调用自动加时间戳，只写不改）。语言边界 = 仅 Python；非 Python 变更走豁免语义如实标注留痕，禁虚构多语言能力。本技能后续修改走人工终改（U6-6）。