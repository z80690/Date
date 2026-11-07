# e2e 步骤2 建设计：进度速览脚本实现方案

> M4 全链路演练（tasks 5.1）｜ 步骤：2/4 建设计 ｜ 日期：2026-11-08
> 直读资源引用（spec 5.1 R3a）：技能=**sdd-ref-distill（C1 辅用**：设计时点复用步骤 1 蒸馏要点之"可重放/留档"原则，未重复调用——引用步骤 1 产出**）+sdd-spec-pipeline（C4 阶段契约）**；规矩=公约.mdc；记忆指针=项目事实表。

## 设计方案

| 项 | 决策 | 理由 |
|----|------|------|
| 语言 | PowerShell 5.1 全 ASCII | 本机 native；怪癖纪律（windows-git-powershell-quirks） |
| 清单形态 | 内置 $expected 数组（9 项：m1–m7 门禁文件+migration-verify+m6-variant-scan） | 免外部配置，机械可核验 |
| 判定逻辑 | Test-Path 逐项→PASS/MISSING 行；missing>0 → exit 1，全存在 → exit 0 | 与步骤 1 R3 对应；与 review-code exit 语义同构 |
| 落盘 | `e2e/progress-scan.ps1` | 演练产物集中 |
| 可重放 | 无时间耦合、无外部依赖、幂等 | design §2.1.3-7 留档可重放原则（C1 蒸馏要点③引用） |

**衔接设计**：脚本当前时点输出 m1–m3 PASS + m4–m7 MISSING + scan 文件 MISSING → exit 1 为**预期正确行为**（特性未推进完）；随门禁推进重放，全 PASS 时 exit 0——脚本生命周期覆盖 M4→M7。

> 产物齐备判定：本文件+步骤 1 齐备后进入步骤 3（C4 阶段契约：spec/design 存在方可建任务）。