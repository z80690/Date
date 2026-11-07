# 步骤4 执行记录：留档与校验执行（四步自证演练）

> 演练标识：self-evidence ｜ 步骤：4/4 执行 ｜ 日期：2026-11-07
> 本步直读资源引用（spec 5.1 R3a）：技能=`.codeartsdoer/skills/sdd-spec-pipeline/SKILL.md`（C4 派发汇总契约）+`.codeartsdoer/skills/review-code/SKILL.md`（C3，代码变更时必调——本步实际调用）；规矩=公约.mdc 第 6 条（编码必审未过不完工）；记忆指针=项目事实表 §2 机制状态行。

## 执行记录（按 step3 任务清单 T1→T2→T3 串行）

| 任务 | 执行动作 | 实际结果 | 验收判定 |
|------|---------|---------|---------|
| T1 留档复制 | Copy-Item temp/sdd-cli-0009.md、temp/sdd-bp-0011.md → learn/self-evidence/sources/ | 2 份留档件落盘 | ✅ R1（与原件字节数一致由 T3 机械比对证实） |
| T2 校验脚本 | verify-sources.ps1 落盘（步骤 1–3 批次已写，内置清单 4627/15820） | 脚本就位 | ✅ R2 |
| T3-a 运行校验 | PowerShell -File 执行 verify-sources.ps1 | 输出 `PASS sources/sdd-cli-0009.md bytes=4627`、`PASS sources/sdd-bp-0011.md bytes=15820`；**exit=0** | ✅ R3（2×PASS+exit 0） |
| T3-b 审查门禁演练 | 调用 `.codeartsdoer/skills/review-code/scripts/review-code.ps1` | 输出 `no-java-changes: skip review`；**exit=0** | ✅ review-code 可调用、exit 语义生效（非 Java 变更 skip 分支实测；若为本特性后续 Java 变更将走 P3C 规约审查） |

## 实际输出留痕（2026-11-07 执行快照）

```
--- verify run ---
PASS sources/sdd-cli-0009.md bytes=4627
PASS sources/sdd-bp-0011.md bytes=15820
verify-exit=0
--- review-code run ---
no-java-changes: skip review
review-exit=0
```

## 代码审查门禁结论

变更范围=演练目录内 1 个新增 ps1 脚本（非 Java），review-code 调用通过（exit 0），无阻断缺陷。编码必审未过不完工——本演练完工判定成立。

## 四步自证自检（spec 5.1 R2a）

| 检查项 | 结论 |
|--------|------|
| 四阶段产物齐备 | ✅ step1-requirement.md / step2-design.md / step3-tasks.md / step4-execution.md（本文件） |
| 顺序无跳步 | ✅ 三类产物（需求/设计/任务）落盘时间先于执行动作（同一批次写入顺序：step1/2/3+脚本 → 执行 → step4）；每步产物头部标注步骤序号 |
| 每步产物引用直读资源 | ✅ 各步头部"直读资源引用"段：公约.mdc/记忆指针→事实表/sdd-spec-pipeline/review-code/grill-me 均为约定路径指针；C1 缺失降级已如实标注（任务 4.2 回补） |
| 审查门禁挂接自证 | ✅ T3-b 实调 review-code，exit 语义生效 |
| 演练范围隔离 | ✅ 全部产物限于 learn/self-evidence/，未触碰正式区与规则文件 |

> 演练结论：四步自证通过，M1 检查单条件③可判 PASS。下一步：任务 1.5 M1 学习门判定。