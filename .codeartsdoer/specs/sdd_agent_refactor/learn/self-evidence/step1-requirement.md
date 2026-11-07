# 步骤1 建需求：SDD 学习材料留档与完整性校验（四步自证演练）

> 演练标识：self-evidence ｜ 步骤：1/4 建需求 ｜ 日期：2026-11-07
> 本步直读资源引用（spec 5.1 R3a）：规矩=`.codeartsdoer/rule/项目协作公约.mdc`（H1 注入）；记忆指针=`notes/项目事实表.md` §2；技能=grill-me（评估后判定本需求边界明确，无需澄清，未调用）；sdd-ref-distill（C1）=计划内缺失（任务 4.2 创建），降级标注——本步需求素材来自已三查材料本身（materials.md），无需外部资料查询。

## 需求描述

**背景**：任务 1.2 抓取的 2 篇 SDD 官方文档现存 `temp/`（临时目录，按项目惯例不入库），学习材料须可追溯、可机械核验完整性。

**需求条款（简化 EARS）**：
- R1：When 学习材料抓取完成，系统应将 2 篇材料原文（sdd-cli-0009.md、sdd-bp-0011.md）从 `temp/` 复制至 `learn/self-evidence/sources/` 留档，字节数与原件一致。
- R2：When 留档完成，系统应提供校验脚本 `verify-sources.ps1`（PowerShell），Where 在 `learn/self-evidence/` 执行时，输出每份留档文件的存在性与字节数比对结果（PASS/FAIL 行）。
- R3：If 任一留档文件缺失或字节数不符，Then 校验脚本输出 FAIL 行并以非零 exit code 退出；全部通过则 exit 0。

## 验收标准

1. 2 份留档文件与 temp/ 原件字节数一致（4627 / 15820）；
2. 校验脚本运行输出 2 行 PASS 且 exit 0；
3. 脚本经 review-code 门禁调用，exit 语义生效（非 Java 变更预期输出 skip，无阻断）；
4. 四步顺序无跳步，本文件为步骤 1 产物（先于步骤 2–4 存在）。

> 演练范围限定：全部产物落于 learn/self-evidence/ 演练目录，不触碰特性正式产物区。