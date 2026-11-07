# M7 交付门证据文件

## ①标识

- 门禁号/名称：M7 交付门（sdd_agent_refactor 特性）
- 对应条款：spec 5.10 M7、5.9（交付）、5.3 R8（M6 硬前置）、5.11 U6 纪律（SPEC_OPTIMIZATION.md 留档）
- 前置核对：M6 放行证据在档（gates/m6-strip-gate.md，2026-11-08）✅ 硬前置满足

## ②判定时间戳

- 2026-11-08（五项交付物清点完成后即时判定）

## ③检查单逐项结论

| # | 检查项 | 结论 | 证据指针 |
|---|--------|------|---------|
| 1 | M6 放行证据存在（硬前置） | **过** | `gates/m6-strip-gate.md`（六项全过放行，2026-11-08） |
| 2 | 五项交付物齐套 | **过** | ①可运行两智能体：`agents/examiner.md`/`agents/grader.md` v2（R1 实考+V1 实证）；②考核记录：`exam/R1/` 四件套（98%≥80% 放行）+`exam/V1/` 全套（100%）；③对比评分结果：**U6-4 取消**——交付物口径=取消说明（`exam/OLD/events.md` ROUND-CANCELLED 行+spec v5 门禁表 M5 行，OLD 轮出题/作答产物留档备查）；④剥离核对清单与终态机制清单：`gates/strip-checklist.md`（换绑标记在档）；⑤能力迁移核验记录：`gates/migration-verify.md`（终判 C1/C3/C4 三项全过） |
| 3 | 终检检索（旧框架挂载点为零，档案区除外） | **过** | 复核 `gates/m6-variant-scan.txt` 终扫结论：现行区活跃命中=0（豁免口径判定在 M6 判定文件③-1） |
| 4 | 功能正常为底线 | **过** | 全链无未修复异常：M1–M4 四门放行+M6 六项全过；已知偏差（子代理换行缺陷/格式变体）均由主智能体复验修复且不影响功能 |
| 5 | SPEC_OPTIMIZATION.md 留档（U6-5） | **过** | `.codeartsdoer/SPEC_OPTIMIZATION.md`（最终产出代码块+本文件即留档口径） |

## ④放行结论

**放行**（五项交付物齐套+终检通过+留档在档；缺一不收工条件满足——无缺项）

## ⑤缺口清单

- 无。待人工事项（非 AI 执行项，U6-6）：见 SPEC_OPTIMIZATION.md"待人工复核清单"与"人工修改建议清单"。

## ⑥签署区

- 判定依据条款：spec 5.9 R1a/R2a/R3a、5.10 M7、5.3 R8a、5.11 U6；design M7 行
- 变更日志留痕指针：`notes/知识库索引.md` 变更日志 2026-11-08 行（"M7 交付门证据落盘"）
- H7 留痕指针：`notes/项目事实表.md` §6（M7 停驻行）
- 执行方：主智能体
- **停驻声明：当前阶段=M7 提交候选停驻**。git 提交动作待用户终判授权后执行（8.2：禁止自动提交）；不通过→记录意见整改后重新走交付呈报循环。

## 提交候选（变更范围清单，待人工终判）

- 新增：specs/sdd_agent_refactor/（spec/design/tasks 四阶段产物+learn/+exam/{R1,V1,OLD}+e2e/+gates/ 七证据文件+scan 留档）
- 修改：agents/examiner.md、agents/grader.md（v2 六步 SOP）；skills/register-feature、review-code、sdd-spec-pipeline（SKILL.md 扩展/换载体）；notes/知识库索引.md（登记+变更日志）；notes/项目事实表.md（§6 特性进度）；.codeartsdoer/mcp/mcp_settings.json（cairn-mcp 移除）
- 移动：notes/注册表.md → notes/档案区/注册表.md（退役归档）
- 新增留档：.codeartsdoer/SPEC_OPTIMIZATION.md
- 排除：temp/（不入库，M7 后清理 temp/compare）、.env（持久安全红线）