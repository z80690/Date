# 浓缩版：官方文档-码道热门Skills清单-desktop0003

- 原文路径：docs/官方文档-码道热门Skills清单-desktop0003.md
- 最后核验日期：2026-11-06

## 核心要点

- 码道内置 15 个热门 Skill，覆盖五大类：
  - 文档办公：docx（Word 文档创建编辑）、xlsx（Excel 表格公式图表透视表）、ppt-expert（演示文稿生成，20+ 视觉风格中英双语）、pdf（读取合并拆分填表加水印）
  - 创意设计：poster-generation（海报生成）、canvas-design（画布设计，输出 png/pdf）、portrait-cutout（人像抠图，保留发丝衣物细节）、tech-graph（技术图表，架构/流程/时序/ER 图，导出 SVG/PNG/HTML）
  - 写作内容：humanizer（去 AI 味）、novel-writing（长篇网文大纲到章节）、brainstorming（创造性工作前意图探索）
  - 开发工具：code-refactoring（不改行为的结构优化）、personal-workbench（个人工作台 HTML 单文件）
  - 研究检索：market-researcher（市场调研 TAM/SAM/SOM）、wechat-article-search（公众号文章检索）
- 触发方式：自然语言描述业务需求，按触发词自动加载；也可直接把具体技能添加到任务对话调用。
- 组合使用：支持多 Skill 串联（如检索→分析→出报告）。
- 优先级：指令明确指定 .docx/.xlsx/.pptx/.pdf 格式时，对应输出 Skill 优先执行。

## 关键结论

- 本地 5 个自建技能（find-skills/grill-me/lazy-exec/ruleinit/skill-writer）均不在此 15 个内置技能之列，标识零重叠——即本地技能无内置技能竞争同一触发场景。
- 该清单是技能"原版对照"的排除性证据：不能用于证明本地技能有官方原版。

## 可直接引用的结论

1. 查某类任务是否有内置技能 → 先查本浓缩版五大类清单，再决定是否到市场检索。
2. 内置技能触发靠 description 触发词自动加载（与 bp0010 三层渐进加载一致）。