---
id: 2026-11-07-deliberate-violation-sample-smoke-verification
title: 审查类框架的功能级验收：构造已知违规样例跑生产入口，断言检出数吻合
category: testing
nature: technique
created_at: 2026-11-07T06:42:01
updated_at: 2026-11-07T06:42:01
tags: [验收测试, smoke 测试, 静态分析, 审查框架, 违规样例]
keywords: [故意违规样例, PMD CLI, p3c ruleset, 检出数断言, exit code 语义, 黑盒验收, 端到端调用链, UpperCamelCase, 规约集加载, 功能级验证]
problem_patterns: [官方测试套件全绿后仍无法证明以生产方式调用时能真实检出问题, 向用户证明框架"能干活"缺少黑盒证据, 不知如何设计可精确断言的审查框架验收用例]
source_sessions: [ses_e4f5c5a83ffefUFnzHFvOEFJCW]
project: Date
severity: medium
quality_score: 87
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-07-framework-capability-verify-official-test-suite]
---

# 审查类框架的功能级验收：构造已知违规样例跑生产入口，断言检出数吻合

## Scenario

第三方审查/检查框架（静态分析类：PMD+P3C、Checkstyle、ESLint 等）已完成构建、官方测试套件全绿，但仍需向用户证明**"以生产方式调用时能真实检出问题"**——官方测试验证的是引擎内部正确性，不覆盖"外部 CLI + 规约集 + 真实代码"这条生产调用链。验收需要一个端到端的黑盒证据。

## Key Signals

- 官方测试全绿但从未经生产入口跑过真实代码，"审查能力可用"的结论缺一环。
- 手工拼 classpath 直接调引擎内部 API 会遇到依赖组装地狱（如 NoPluginFoundForPrefixException），且即便跑通也仍是白盒路径。

## Essence

用**故意违规样例**做 smoke 验证：构造一个违规点数量与类型已知的样例文件，用框架的生产入口（CLI + 官方规约集）执行真实审查，断言"检出数 = 预期数"。样例法同时验证了 CLI 参数、规约集加载、规则匹配、报告输出、退出码语义整条链路——这是官方测试套件覆盖不到的部分。

## Approach

1. 构造样例文件：违规点**少而明确**（2–3 处即可），每处对应目标规约集里最典型的规则，逐一加注释标明预期违规（如类名 `badName` 违反 UpperCamelCase、方法名 `DoSomething` 违反 lowerCamelCase）。
2. 查清框架退出码语义再跑（PMD：4 = 发现违规，非错误），避免把"检出违规"误判为"运行失败"。
3. 用生产入口执行审查并输出报告，逐条核对：检出条目数 = 预期数，且每条指到的正是注释标注的行。
4. 留痕三件套：样例文件路径、审查命令原文、检出报告摘录 + exit code，作为验收证据落盘。
5. 与官方测试互补使用：官方套件（白盒，引擎正确性）+ 违规样例（黑盒，生产链路可用）双证据齐套才算"能力验收通过"。

## Faster Next Time

- 验收模板一句话：**"已知违规 → 预期检出数写死 → 生产入口跑一遍 → 数字对上即通过"**。
- 违规样例可沉淀为固定 fixture，换框架版本回归时复用（样例不变，检出数应稳定）。
- 对生成类（非审查类）框架，同法改为"已知输入 → 预期输出"对拍样例，思路一致。

## Applicability Boundaries

- 适用：静态分析/审查/lint 类框架的功能级验收；任何需要向用户证明"生产调用链可用"的场景。
- 不适用：替代官方测试套件——样例法只验证端到端链路，不能证明规则全集正确；两者是互补关系。
- 样例违规点必须是规约集中确实存在的规则，否则"零检出"无法区分"链路坏"还是"规则不存在"。

## Evidence or Examples

- 本会话实例：构造 `SampleViolation.java`（2 处命名违规），以 `java -cp <p3c-pmd 及依赖> net.sourceforge.pmd.PMD -d <样例目录> -R <ali-naming ruleset>` 生产方式执行，检出恰好 2 条（`【badName】不符合UpperCamelCase命名风格`、方法名`【DoSomething】不符合lowerCamelCase`），exit 4 = 发现违规，与预期完全吻合。
- 前置链路：p3c-pmd-2.1.1 构建 BUILD SUCCESS + 官方测试 214/214 全绿（白盒证据）→ 样例审查通过（黑盒证据）→ 双证据齐套后该框架标记"已验收"。
- 依赖组装教训：`mvn dependency:copy-dependencies` 拉齐 24 个 jar 后用完整 classpath 调 PMD CLI，避免手工拼 classpath 的插件解析失败。