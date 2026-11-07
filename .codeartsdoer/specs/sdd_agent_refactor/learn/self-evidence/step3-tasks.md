# 步骤3 建任务：留档与校验任务清单（四步自证演练）

> 演练标识：self-evidence ｜ 步骤：3/4 建任务 ｜ 日期：2026-11-07
> 本步直读资源引用（spec 5.1 R3a）：技能=`.codeartsdoer/skills/sdd-spec-pipeline/SKILL.md`（C4 任务分解契约：任务带编号/依赖/产出/验收）；规矩=公约.mdc 第 6 条（编码必审未过不完工→编入任务 T3）；记忆指针=项目事实表。

## 任务清单

| 编号 | 任务 | 前置 | 动作 | 产出 | 验收标准（回链需求条款） |
|------|------|------|------|------|---------|
| T1 | 留档复制 | step2 | Copy-Item temp/sdd-cli-0009.md、temp/sdd-bp-0011.md → learn/self-evidence/sources/ | 2 份留档件 | R1：字节数与原件一致（4627/15820） |
| T2 | 生成校验脚本 | T1 | write verify-sources.ps1（内置清单+比对+exit 语义） | verify-sources.ps1 | R2：可执行、输出 PASS/FAIL 行 |
| T3 | 运行校验+审查门禁演练 | T2 | ①运行脚本记录输出与 exit code；②调用 review-code 门禁（编码变更必审，公约第 6 条） | step4-execution.md（含实际输出留痕） | R3：exit 0 且 2×PASS；review-code 可调用、exit 语义生效 |

**执行顺序**：T1→T2→T3 严格串行；T3 未过不完工（公约第 6 条），退回 T2 修复。

> 产物齐备判定：step1/step2/本文件齐备后方可进入步骤 4 执行（三类产物先于执行动作——spec 5.7 R1a 同构自证）。