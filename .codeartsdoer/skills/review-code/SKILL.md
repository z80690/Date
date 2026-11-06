---
name: review-code
description: 当编码动作发生（Write/Edit 落盘 Java 文件）或提交前需要质量审查时触发，用 P3C 规约对变更 Java 文件执行静态审查并留痕报告（未过不完工）；不适用于非 Java 文件、无变更场景与用户明示豁免的提交。
---
1. 运行本技能 scripts/review-code.ps1，参数 RepoRoot=项目根、OutReport=报告路径（%TEMP%\p3c-review-<日期>.txt）。
2. exit 0=无 Java 变更或无违规→放行并留痕；exit 4=有违规→逐条修复后复检，未过不完工。
3. 报告五要素落执行轨迹：审查范围（增量/全量）、发现项数、严重级别、复核状态（未复核/已复核留痕/已豁免留痕）、命令与结果原文。
4. 语言边界=仅 Java（P3C 能力边界），非 Java 变更按 G4 豁免语义如实标注留痕，禁虚构多语言能力。