---
id: 2026-11-07-framework-capability-verify-official-test-suite
title: 第三方框架"跑通"的验收标准：官方测试套件全绿才算能力可用，编译通过只是必要条件
category: testing
nature: technique
created_at: 2026-11-07T01:17:00
updated_at: 2026-11-07T01:26:24
tags: [verification, test-suite, maven-surefire, p3c, acceptance]
keywords: [框架验收, 功能级验证, 官方测试套件, mvn test, surefire, classpath 组装, BUILD SUCCESS, 编译通过不等于可用, NoPluginFoundForPrefixException]
problem_patterns: [构建 BUILD SUCCESS 后仍不确定框架审查/处理能力是否真实可用, 手工拼 classpath 运行框架引擎反复报插件或依赖错误, 需要向用户证明"拉取的框架在本机能干活"而非仅编译成功]
source_sessions: [ses_e4f5c5a83ffefUFnzHFvOEFJCW]
project: Date
severity: low
quality_score: 84
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: A
related_experiences: [2026-11-07-maven-download-degradation-chain-sha512-verify, 2026-11-07-background-long-task-log-pipeline-pitfalls]
---

# 第三方框架"跑通"的验收标准：官方测试套件全绿才算能力可用，编译通过只是必要条件

## Scenario

克隆第三方框架（本例 alibaba/p3c 的 p3c-pmd 静态审查引擎）并完成构建后，用户要求的验收标准是"配置好、可以跑通"——需要给出"审查能力在本机真实可用"的证据，而不是停在 BUILD SUCCESS。

## Key Signals

1. BUILD SUCCESS（p3c-pmd-2.1.1 jar 产出，6:44 min）只证明编译链路通，不证明规则引擎能对真实代码执行审查。
2. 手工拼 classpath 路线（`mvn dependency:build-classpath` 自组依赖再调引擎）直接报 `[ERROR] NoPluginFoundForPrefixException`——框架内部模块结构/插件前缀与直觉不符，手拼路线每一步都在猜。
3. 转官方测试套件：`mvn test` 由 surefire 自动组装 classpath，测试用例本身就是"规则引擎对真实违规样例执行审查"——`Tests run: 214, Failures: 0, Errors: 0, Skipped: 0` 全绿。

## Essence

验收"拉来的框架能干活"的正确证据等级是：**官方测试套件全绿 > 自写样例冒烟 > 编译通过**。官方测试套件有三重优势：用例即框架作者的意图规格（覆盖真实使用路径）；构建配置自带正确的依赖组装（避开手拼 classpath 的模块结构陷阱）；结果可量化（214/214 是可呈报的验收数字）。编译通过只是必要条件——jar 能产出但引擎跑不起来或规则全失效的情况，BUILD SUCCESS 完全发现不了。

## Approach

1. 构建成功后不收工，先盘点框架自带的测试资产（`src/test`、CI 配置里的 test 命令），确认存在可执行的官方套件。
2. 直接跑框架原生的测试入口（Maven 项目即根/模块目录 `mvn test`），禁自拼 classpath、禁自写"验证用"调用脚本——除非官方套件确实缺失。
3. 以汇总行作为验收证据：`Tests run: N, Failures: 0, Errors: 0`；有 Failures 则逐条看是否环境性（编码/路径）还是真实缺陷，环境性问题回 build-env 层修，不污染验收结论。
4. 呈报时把证据等级写明："编译通过【必要条件】+ 官方套件 214/214 全绿【能力级证据】"，让用户看到证据强度的差异而非单一"成功"。

## Faster Next Time

- 决策规则一句话：**框架有官方测试套件就跑套件，没套件才退而自写冒烟样例；手拼 classpath 是最后手段**。
- 警告信号：`NoPluginFoundForPrefixException`、`Unable to get dependency information` 这类插件/前缀解析错误出现在手拼路线时，说明对框架内部结构理解不足，立即止损转官方入口，不逐个修插件版本。
- 汇报模板：能力验证结论 = 证据等级 + 量化数字 + 环境（OS/JDK/工具版本），三者齐套才构成可复查的"跑通"。

## Applicability Boundaries

- 适用：有测试资产的第三方框架/库接入验收（Maven/Gradle/npm/pytest 生态同理）；需要向用户或门禁证明"能力可用"的场景。
- 不适用：官方测试套件需要外部凭据/专用环境（数据库、云账号）的框架——此时降级为自写冒烟并如实标注证据等级；纯 CLI 小工具（无测试资产，直接跑一次真实任务即可）。
- 边界说明：全绿证明"框架作者预期的能力可用"，不等于覆盖用户的特定用法；特定用法（如对本项目代码跑审查）应在套件全绿基础上另行抽样冒烟。

## Evidence or Examples

- 验收实录（2026-11-07）：p3c-pmd BUILD SUCCESS 后手拼 classpath 报 NoPluginFoundForPrefixException → 改 `mvn test` → `Tests run: 214, Failures: 0, Errors: 0, Skipped: 0`（含 SetRulesTest 12 例、UseRightCaseForDateFormatRuleTest 等），环境 JDK 17.0.20.1 + Maven 3.9.16 + Windows。
- 证据等级呈报原话："官方测试 214/214 全绿（Failures 0 / Errors 0）——审查引擎真实可跑，非仅编译通过"。