# P3C 框架加载状态核查报告

> 核查日期：2026-11-08 ｜ 核查性质：仅核对挂载状态与约束生效情况，未执行任何真实编码、未运行 PMD 审查

## 1. P3C 当前挂载状态

**已挂载**（以项目技能 `review-code` 为承载，底层 PMD 引擎底座实存可调用）。

只读核验证据（全部 PASS）：

| 核验项 | 路径 | 结果 |
| --- | --- | --- |
| P3C 仓库底座 | `D:\refs\p3c` | True |
| PMD 编译产物 classes | `D:\refs\p3c\p3c-pmd\target\classes` | True |
| PMD 依赖 jar（dep 目录） | `D:\refs\p3c\p3c-pmd\target\dep\*` | 24 个文件 |
| P3C 规约集（ali-naming 等） | `D:\refs\p3c\p3c-pmd\src\main\resources\rulesets\java\ali-naming.xml` | True |
| 审查脚本 | `.codeartsdoer/skills/review-code/scripts/review-code.ps1` | True |
| 技能注册运行时状态 | `listSkills` → review-code (project) | enabled |
| 技能注册落盘状态 | `.codeartsdoer/skills/ProjectSkillStatus.txt` 第 6 行 | `review-code=true` |

历史验收佐证：p3c-pmd 2.1.1 构建 BUILD SUCCESS、官方测试 214/214 全绿、故意违规样例黑盒审查检出 2/2（均 2026-11-07 实测在档，见 `specs/kb_arch_foundation/st1-evidence.md` §3）。

## 2. 加载机制简述

P3C **不是 MCP 工具、不是独立常驻规则**，而是"项目技能 + 本地构建底座"的事件触发式挂载：`review-code` 技能（编码动作落盘 Java 文件或提交前触发）调用 `review-code.ps1`，脚本以 `java -cp` 方式驱动 `D:\refs\p3c` 下的 PMD CLI 加载 P3C 规约集执行静态审查。本次会话未发生 Java 编码动作，故审查链路处于待命未触发状态，P3C 规约本体未常驻当前对话上下文（符合按需加载设计）。

## 3. 编码任务调用 P3C 的约束确认

**约束存在且生效**，约束链条（规则层 → 技能层 → 流程层）：

1. **规则层**：`项目协作公约.mdc` 第 6 条——"编码必审未过不完工"（公约约束源头）。
2. **技能层**：`review-code/SKILL.md` description——编码动作落盘 Java 文件/提交前必触发 P3C 规约静态审查并留痕，exit 语义绑定门禁（0=过，4=未过不完工）。
3. **流程层**：SDD 四步流程执行步（第 4 步）代码审查门禁环节必调，与"代码审查门禁"同一承载，无双轨并存。

**边界说明**：约束的适用边界为 Java 文件变更（P3C 能力边界）；非 Java 变更走"豁免语义标注留痕"，禁静默跳过（经验佐证：`experience-reuse/experiences/workflow/2026-11-07-gate-exemption-semantic-annotation.md`）。即准确表述为"编码任务（Java 变更）必须经 review-code 调用 P3C 审查"，而非无条件全局强制。

## 4. 派工单要求 × 规则层条款交叉比对

| # | 派工单要求 | 核查结果 | 规则/证据出处 |
| --- | --- | --- | --- |
| 1 | 确认"编码任务必须调用 P3C"约束是否存在 | 存在（编码必审，Java 边界） | 公约第 6 条 + review-code SKILL.md |
| 2 | 说明加载/挂载方式 | 项目技能 + 本地底座（D:\refs\p3c），事件触发，非 MCP/常驻规则 | review-code.ps1 参数、listSkills 运行时 |
| 3 | 不写任何业务代码 | 遵守：零编码，仅本报告落盘 | — |
| 4 | 反馈文件落 `.codeartsdoer/` 下 | 本文件即产物 | — |
| 5 | 派工单原文置于文末代码块 | 见下 | — |

## 5. 派工单原文

```
【派工单：仅核对 P3C 框架加载状态，不执行编码】

任务目标：核对底层 P3C 框架是否已挂载，并确认编码任务强制调用约束是否生效。不执行任何真实编码。

执行要求：
1. 回顾当前项目规则（如"项目协作公约"）与已注册技能，确认是否存在"编码任务必须调用 P3C 框架"的约束。
2. 说明 P3C 框架当前的加载/挂载方式（例如：是作为独立技能、MCP 工具、脚本，还是常驻规则？是否已被加载进当前上下文？）。
3. 不写任何业务代码。仅在计划文档目录（如 `.codeartsdoer/` 或 `specs/`）下新建一个 Markdown 反馈文件（命名如 `p3c_status_check.md`）。
4. 文件内容需包含：
   - P3C 当前挂载状态（已挂载/未挂载/疑似未挂载）
   - 加载机制简述（一两句话）
   - 编码任务调用 P3C 的约束确认
5. 将本派工单原文放在文件底部的代码块中，并附上一两句对派工单含义的解释（即：本次只核对不编码）。
```

**派工单含义解释**：本单是一份"环境自检"性质的派工——只核查 P3C 框架是否已在当前智能体环境中挂载、编码必审约束是否生效，全程禁止任何业务编码与审查实跑，产出物仅为这份状态反馈文件。