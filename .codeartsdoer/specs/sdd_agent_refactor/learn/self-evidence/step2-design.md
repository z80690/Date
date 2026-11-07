# 步骤2 建设计：留档与校验脚本实现方案（四步自证演练）

> 演练标识：self-evidence ｜ 步骤：2/4 建设计 ｜ 日期：2026-11-07
> 本步直读资源引用（spec 5.1 R3a）：技能=`.codeartsdoer/skills/sdd-spec-pipeline/SKILL.md`（C4 阶段契约，步骤 1→2 衔接约束：spec.md 已存在方可建设计——官方命令前置条件同构）；规矩=公约.mdc；记忆指针=项目事实表；sdd-ref-distill（C1 辅用）=计划内缺失降级标注（设计方案无需外部资料，C1 缺席不影响本步）。

## 设计方案

**架构**：清单内置式校验脚本（单文件，无外部依赖）。

| 项 | 决策 | 理由 |
|----|------|------|
| 语言 | PowerShell 5.1 兼容（全 ASCII 脚本体） | 本机环境 native；windows-git-powershell-quirks 实证"全 ASCII 更稳" |
| 清单形态 | 脚本内 $expected 数组（文件名+期望字节数） | 2 文件规模小，内置清单免配置文件解析，降低失败面 |
| 校验逻辑 | Test-Path → Get-Item Length → 与期望值比对 → 逐行输出 PASS/FAIL | 机械可核验，输出可留档 |
| 退出语义 | fail=0 → exit 0；fail>0 → exit 1 | 与 review-code exit 语义（0=过/非0=未过）同构，便于门禁挂接 |
| 落盘位置 | `learn/self-evidence/verify-sources.ps1` + 留档件 `learn/self-evidence/sources/` | 演练产物集中，不污染正式区 |

**数据流**：temp/ 原件 --Copy-Item--> sources/ 留档件 --脚本比对--> PASS/FAIL 输出 + exit code。

**风险**：字节数硬编码依赖抓取时点快照——演练范围内原件不动（temp/ 不清理），比对锚定当日抓取值（4627/15820），可复核。

> 产物齐备判定：本文件+步骤1 文件齐备后，方进入步骤 3 建任务（禁跳步）。