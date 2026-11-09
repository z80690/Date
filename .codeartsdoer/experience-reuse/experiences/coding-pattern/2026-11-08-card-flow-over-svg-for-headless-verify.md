---
id: 2026-11-08-card-flow-over-svg-for-headless-verify
title: 无 GUI 回读验证约束下的可视化 HTML 选型：无几何需求时卡片流优先于 SVG
category: coding-pattern
nature: decision
created_at: 2026-11-08T03:30:49
updated_at: 2026-11-08T03:33:09
tags: [结构选型, 无头验证, 卡片流, SVG, 单文件HTML]
keywords: [DOM mock 断言, 冒烟验证成本, CSS 箭头, 单一状态机, 数据层 source 溯源, 选型决策, 可视化交付, 无框架前端, 结构简单性, vm.runInNewContext]
problem_patterns: [设计流程图/看板类页面时直觉选用 SVG 绘制节点连线，到无 GUI 回读环境下才发现 SVG 几何结构难以做 DOM mock 断言, 设计期未做"结构可验证性"预检，编码后 SVG 坐标/rect/path 使冒烟脚本断言复杂或漏验交互]
source_sessions: [ses_e488f0d98ffenfQaxb5qRxRHbA]
project: Date
severity: low
quality_score: 85
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-07-headless-html-verify-node-vm-dom-mock, 2026-11-07-svg-viewbox-zoom-single-source-data-layer, 2026-11-07-file-protocol-fetch-cors-build-time-inline]
---

# 无 GUI 回读验证约束下的可视化 HTML 选型：无几何需求时卡片流优先于 SVG

## Scenario

Agent 需要产出说明页/看板/流程图类交互可视化 HTML（单文件、file:// 直开、断网可用），所在平台无 GUI 回读通道（browser 类工具只受理打开请求、读不到内容/DOM/控制台），交付物必须走"Node vm + DOM mock 冒烟"四查流水线验证（见 related）。设计期给页面选结构时，直觉上"流程图 = SVG 绘制节点和箭头连线"，但该直觉在此验证约束下不成立。

## Key Signals

- 设计草案把页面主体建模为 `svg` + `rect/circle/path` + `marker` 连线——只考虑了视觉表现力。
- 验证方案已知依赖 vm.runInNewContext + DOM mock（无真浏览器回读），但选型时未把"结构可断言性"列为约束。
- 危险信号：选型讨论里出现"SVG 更专业/更好看"而没有出现"mock 里怎么断言它"。

## Essence

无头验证的可断言性随 DOM 结构复杂度下降。SVG 的几何属性（坐标、长度、path 段、marker 引用）在 DOM mock 中要么无法断言要么断言成本高；而纯 HTML/CSS 卡片流的交互断言只需 `getElementById` + `classList` 检查，一轮 vm.runInNewContext 即可完整驱动状态机。在"视觉精度"与"无头可验证性"二者此消彼长的场景，选型期必须先定优先级：验证通道不可用视觉回读时，可验证性优先。此决策属于设计期事务——编码后发现只能返工结构。

## Approach

1. 选型期先判定几何需求：页面是否需要缩放/拖拽/精确坐标连线？**无 → 卡片流 + CSS 箭头**（div/span + 伪元素/边框画箭头）；**有 → SVG 方案**并配套 viewBox 缩放与单一数据层模式（见 related svg 经验）。
2. 数据层收敛为单一 `DATA` 常量（唯一文案源），每个数据对象携带 `source` 字段标注事实源路径，使页面文案可溯源、修订只改数据层。
3. 交互层收敛为单一状态机：状态数与迁移显式列出（如 3 状态 6 迁移），确保 mock 驱动可穷举全迁移。
4. 未实现的扩展位（如预留的第 4 个 Tab）只留注释标记，不写空壳代码。
5. 接口契约（文件路径 / 切换协议 / DATA 结构 / 辅助函数 / 断言清单）在交付内冻结；后续更新只改数据层不动接口。

## Faster Next Time

- 选型两问直接映射方案："验证通道是无 GUI 回读吗？""页面需要几何操作吗？"——(是, 无) → 卡片流；(是, 有) → SVG + 单一数据层。
- 设计文档写明选型决策及理由，编码期不重开选型。
- 断言清单在设计期就定（随接口契约冻结），不要编码后补——这决定结构粒度是否可断言。

## Applicability Boundaries

- 适用：无 GUI 回读环境 + 说明页/图解页/看板/多标签内容页 + 无缩放拖拽精确连线需求。
- 不适用：需要 viewBox 缩放、拖拽、精确几何连线的页面（此时用 SVG 方案，见 related）；有真浏览器渲染/截图回读通道的环境（视觉精度优先级可上调，SVG 成本不再是短板）。

## Evidence or Examples

- 来源 session：为派工单 TASK-20261108-004 设计 pd004_html_viz（多标签页：公约六条图解 + SDD 流程 + Wiki 同步说明）。先例页 `sdd-workflow-visual.html`（425 行）为 SVG 形态；本次设计明确决策"卡片流 + CSS 箭头，不引入 SVG，利于无 GUI 冒烟断言"。
- 设计文档落盘 `.codeartsdoer/specs/pd004_html_viz/design.md`（Write 分节落盘 + Edit 追加 + glob 存在性复核），接口契约含四查断言清单，与 related 验证经验衔接。
- 诚实标注：本条为设计期决策推理（trace 中有明确决策理由），未含两种方案验证成本的实测对比数据；该推断需后续实现轮验证后强化。