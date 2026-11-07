# SPEC_OPTIMIZATION 留档（U6-5：本文件即留档）

> 特性：sdd_agent_refactor ｜ 用户强硬指令 U6（2026-11-08 七条）执行结果留档 ｜ 2026-11-08
> 状态：**M1–M4+M6 全放行，M5 按 U6-4 取消，M7 提交候选停驻待人工终判**

## 一、U6 七条指令执行对照

```
1. 考核题量永久改 5 题/80% 放行 → spec v5 全局注记在档（今后轮次适用）；
   M2 已完成的 50 题轮（R1=98% 放行）不追溯。
   [执行方式：examiner/grader 配置 50→5 修改已列入人工修改建议清单（U6-6 AI 不直改）]
2. 40 分钟硬限 → 实际耗时约 22 分钟（< 40 分钟），未触发 TIMEOUT.md；
   阶段节点：指令接收→spec v5→M6 剥离+终扫→M6 判定→M7 清点+停驻。
3. 学习时机 → 学习已在需求阶段完成（SDD 官方文档 2 篇+材料三查）；
   干中遇阻即查（H3/H7 语义实查、Cairn/SuperAgent README 只读提炼），未阻断主流程，无事后学。
4. 流程极简 → V1 轮：M3 阶段已完成（既成事实保留，未新增验证轮）；
   OLD/NEW 对比：取消（OLD 轮出题+作答完成、批改中止留痕 ROUND-CANCELLED，NEW 轮未开始）；
   扫描：仅 1 次终扫（m6-variant-scan.txt，首轮即终轮）；未反复改写（减法最小变更集）。
5. 留档 → 本文件（最终产出见下方代码块）。
6. 规则文件人工终改 → 指令下达后 AI 零直改 SKILL.md/.mdc；
   指令下达前已直改的 5 个文件列"待人工复核清单"；今后的修改全部列"人工修改建议清单"。
7. 满足性 → 以上 1–6 全满足，未触发"任务失败立即停"。
```

## 二、最终产出（代码块）

```
特性：sdd_agent_refactor（规范驱动接入与两智能体改造）
门禁链：M1 学习门=放行 → M2 考核门=放行(R1 轮 98%≥80%,PASS48/PARTIAL2/FAIL0)
        → M3 改造门=放行(V1 轮 S1 实出 50 题+S2 实批 100%)
        → M4 全链路门=放行(e2e 四步演练,C1/C3/C4 调用实证)
        → M5 对比门=已取消(U6-4)
        → M6 剥离门=放行(六项全过,剃旧上新换绑完成)
        → M7 交付门=放行(五项交付物齐套)→提交候选停驻待人工终判

交付物：
  ①可运行两智能体   .codeartsdoer/agents/examiner.md / grader.md（v2 六步 SOP,事件驱动）
  ②考核记录         .codeartsdoer/specs/sdd_agent_refactor/exam/R1/（四件套+events 四事件链）
                    .codeartsdoer/specs/sdd_agent_refactor/exam/V1/（验证轮全套）
  ③对比评分结果     U6-4 取消（取消说明:exam/OLD/events.md ROUND-CANCELLED 行）
  ④剥离核对清单     .codeartsdoer/specs/sdd_agent_refactor/gates/strip-checklist.md（换绑标记在档）
  ⑤能力迁移核验     .codeartsdoer/specs/sdd_agent_refactor/gates/migration-verify.md（C1/C3/C4 终判全过）
  留档              .codeartsdoer/SPEC_OPTIMIZATION.md（本文件）

剥离结果：
  图框架壳子  mcp_settings.json cairn-mcp 条目已移除（JSON 置空 mcpServers）
  注册表本体  notes/注册表.md → notes/档案区/注册表.md（退役归档,原值可追溯）
  路由职能    不迁移(U5)；新逻辑由四步直读约定表+知识库索引承载
  1 次终扫    gates/m6-variant-scan.txt（现行区活跃命中=0,豁免口径判定在 M6 判定文件）

规格产物：.codeartsdoer/specs/sdd_agent_refactor/
  spec.md(v5) / design.md(v2) / tasks.md / learn/(三查+沉淀+自证四件套) / e2e/(演练五产物)
  gates/(m1,m2,m3,m4,m6,m7 六门禁证据+migration-verify+strip-checklist+m6-variant-scan.txt)
```

## 三、待人工复核清单（U6-6：指令下达前 AI 已直改的文件，请人工复核）

```
1. .codeartsdoer/agents/examiner.md        （v2:四触发时机+六步 SOP+全 deny 技能）
2. .codeartsdoer/agents/grader.md          （v2:唯一时机+六步 SOP+独立性红线）
3. .codeartsdoer/skills/register-feature/SKILL.md（换载体:查重/登记改知识库索引+事实表）
4. .codeartsdoer/skills/review-code/SKILL.md     （增补第 5 条 SDD 挂载段,本体零改动）
5. .codeartsdoer/skills/sdd-spec-pipeline/SKILL.md（增补 C4 编排范式段）
   ——以上变更均过 review-code 门禁（exit 0），变更日志有痕；如需调整请人工直改。
```

## 四、人工修改建议清单（U6-6：AI 仅建议，不直改）

```
1. examiner.md/grader.md：题量 50→5（U6-1 永久口径）——建议改六步 SOP 步骤③
   与 description 中"50 题"字样为"5 题"（其余逻辑不变）。
2. notes/复用评估表.md：建议加注记"注册表已剥离（2026-11-08），冻结职能由知识库索引承载"。
3. notes/阶段状态机运行规则.md：1 处注册表历史描述建议加剥离注记（不删历史，只加注）。
4. temp/compare/（旧版配置副本）：M5 已取消，建议人工确认后删除。
```

## 五、提交候选与终判

```
提交候选：见 gates/m7-delivery-gate.md"提交候选（变更范围清单）"
git 提交：待用户终判授权后执行（禁自动提交）；不通过→整改后重新呈报循环。
```