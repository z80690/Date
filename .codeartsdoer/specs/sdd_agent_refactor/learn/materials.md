# SDD 学习材料清单与三查核验（任务 1.2 产出物）

> 特性：sdd_agent_refactor ｜ 任务 1.2 ｜ 执行日期：2026-11-07
> 验收回链：spec 5.1 R1a/b（材料先评估后引用）；design §3.1 环节①
> 检索路径实证：llms.txt 官方机器可读索引（`https://support.huaweicloud.com/codeartsagent/llms.txt`，138014 字节，2026-11-07 带 UA 抓取成功）→ 关键词"规范驱动|SDD"命中 2 条 → .md 直链全文抓取。SPA 搜索页不可达怪癖已在事实表登记（R0-4 处置：直连已知可达路径，未触发重试）。

## 一、入选材料清单（逐条三查）

### M1-SDD-01：SDD 命令概述（CLI 用户手册章节）

| 字段 | 值 |
|------|-----|
| 来源指针 | https://support.huaweicloud.com/usermanual-cli/codeartsagent_cli_0009.md |
| 本地留档 | temp/sdd-cli-0009.md（4627 字节） |
| 核验日期 | 2026-11-07 |
| 来源权威性 | ✅ 华为云官方文档站 support.huaweicloud.com 用户手册（usermanual-cli 类目，llms.txt 索引收录） |
| 内容保真 | ✅ .md 直链原文（非 JS 渲染页），标题/命令表/操作步骤/配图引用结构完整；命令表四行与正文步骤五节互证一致 |
| 时效核验 | ✅ 官方 llms.txt 现行索引收录（索引抓取日=2026-11-07）；文档内无显式发布日期，以"官方索引现行收录+抓取日"为时效依据（如实标注） |
| 三查结论 | **通过** |

核心内容：SDD（Specification-Driven Development）规格驱动开发模式定义；四命令（/sdd-new→spec.md、/sdd-design→design.md、/sdd-tasks→tasks.md、/sdd-apply→按 tasks 逐项执行编码）；产物路径约定 `{项目根路径}/.codeartsdoer/specs/{产物文件夹名}/`；阶段间硬依赖（design 需 spec 已存在、tasks 需 spec+design、apply 需三者齐备）。

### M1-SDD-02：SDD 开发模式标准工作流与斜杠命令实践（官方最佳实践）

| 字段 | 值 |
|------|-----|
| 来源指针 | https://support.huaweicloud.com/bestpractice-codeartsagent/codeartsagent_bp_0011.md |
| 本地留档 | temp/sdd-bp-0011.md（15820 字节） |
| 核验日期 | 2026-11-07 |
| 来源权威性 | ✅ 华为云官方文档站最佳实践类目（bestpractice-codeartsagent，llms.txt 索引收录） |
| 内容保真 | ✅ .md 直链原文，四阶段流程图引用/双命令表/对比表/实操示例（用户登录案例）齐备；与 M1-SDD-01 的命令表交叉比对一致 |
| 时效核验 | ✅ 同上（官方索引现行收录+抓取日；交叉印证：与 CLI 手册命令口径完全一致，无版本漂移迹象） |
| 三查结论 | **通过** |

核心内容：两种使用方式（标准 SDD 工作流=智能体主导+每阶段人工确认；斜杠命令模式=开发者自主调度，可跳过/重复）；场景选型（新项目 0→1 用标准工作流；迭代期用斜杠命令增量开发）；每阶段产物确认后进入下一环节；增量修订路径（改 spec 后重跑 design/tasks）。

## 二、淘汰记录

| 候选 | 淘汰原因 | 处置 |
|------|---------|------|
| developer/bbs 搜索页检索 | SPA 骨架 JS 渲染，静态抓取 0 条数据（事实表在案怪癖，未再重试） | 非材料，仅检索路径记录 |
| temp/llms.txt 中其余 37 类目条目 | 与"规范驱动开发"主题不直接相关（计费/安装/其他功能类目） | 不引用，留索引待查 |

## 三、三查纪律确认

- ✅ 入选材料 2/2 均通过三查；未经三查材料零引用
- ✅ 每条带来源指针（URL 可回查）+核验日期+本地留档
- ✅ 淘汰记录与检索路径在档（R0-4 处置合规：未触发 3 次重试上限）

> 执行者：主智能体 ｜ 下一步：任务 1.3 学习沉淀与知识库登记