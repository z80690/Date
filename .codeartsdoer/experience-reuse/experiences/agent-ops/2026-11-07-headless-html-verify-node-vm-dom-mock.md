---
id: 2026-11-07-headless-html-verify-node-vm-dom-mock
title: 无 GUI 回读环境下验证 HTML 交付物：静态断言 + Node vm DOM mock 冒烟替代真浏览器
category: agent-ops
nature: technique
created_at: 2026-11-07T10:31:53
updated_at: 2026-11-07T17:40:33
tags: [验证流水线, 自包含HTML, DOM mock, Node vm, 无头验证]
keywords: [HTML 验证, browser 无回读, vm.runInNewContext, DOM mock 冒烟, 语法编译检查, 断网自包含断言, 覆盖度清单, 敏感词误报, mock 先修纪律, 交互断言]
problem_patterns: [Agent 产出 HTML 页面后无法验证渲染与交互是否正常，内置 browser 只受理打开请求、读不到内容/控制台/DOM, 验证脚本冒烟报 null 异常时误判为页面代码缺陷，实为 mock 未预注册页面真实 id, 敏感信息正则扫描初报 FAIL 未回读命中上下文就返工，实为 API 标识符误报]
source_sessions: [ses_e4c37b048ffeqGK3zYLwRrc6eC]
project: Date
severity: medium
quality_score: 88
utility_score: 100
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-07-browser-tool-open-success-no-content-read, 2026-11-07-single-command-batch-assertion-inventory, 2026-11-07-sensitive-credential-file-commit-gate-env-block]
---

# 无 GUI 回读环境下验证 HTML 交付物：静态断言 + Node vm DOM mock 冒烟替代真浏览器

## Scenario

Agent 需要产出自包含 HTML 页面（流程图/可视化看板/说明页）并验证其交互与内容正确性，但所在平台的内置 browser 类工具只受理"请求打开"、不返回任何页面内容、控制台输出或 DOM（见 related 上游经验）。真渲染验证通道不存在，交付物又不能"写了就算验过"。

## Key Signals

- browser 调用返回 `Requested to open ... success`，但工具 schema 无任何内容/截图/控制台回读字段——打开成功 ≠ 验证成功。
- 需要"控制台无报错""点击交互生效"这类运行时证据，却没有运行时观察通道。
- mock 冒烟脚本报 `Cannot read properties of null (reading 'addEventListener')`，且报错位置是页面脚本对真实 HTML id 的取用。
- 安全正则扫描报敏感词 FAIL，命中文本是 `DOMTokenList` 之类 API 标识符。

## Essence

把验证目标从"页面在人眼中正确"（需运行时观察）整体替换为"代码在规格上正确 + 脚本在模拟 DOM 中行为正确"（纯静态可判定）。HTML 页面的验证可拆解为四类可离线断言的目标：语法可编译、脚本在 mock DOM 上行为符合接口契约、零外部引用（断网可用）、关键内容与结构标记齐全。这四类断言全部可用 Node 一轮跑完，无需任何浏览器。

## Approach

四查流水线（每查独立判定，一轮批量执行）：

1. **查一·语法**：提取 HTML 中全部 `<script>` 内容，`new vm.Script(code)` 编译，抛异常即语法错误。
2. **查二·交互冒烟**：先从 HTML 提取全部真实 `id`/`data-*` 键，**预注册** mock DOM（`getElementById` 返回带 `addEventListener`/`disabled`/`classList`/`innerHTML`/`textContent` 的 stub，`querySelector` 兜底）→ `vm.runInNewContext` 执行整段页面脚本 → 逐接口断言：init 无异常、标签切换后可见性类名、缩放数值边界（clamp/复位）、详情面板展开填充与收起。
3. **查三·断网自包含**：正则断言零外部引用——无外链 `src`/`href`、无 `@import`/外部 `url()`、无 `<link>` 标签。
4. **查四·覆盖度与安全**：关键内容串清单（标题、节点文案、标注）一次跑全计数；密钥/凭证类正则初报 FAIL 时**先回读命中行上下文判定误报**，代码标识符命中不返工，真凭证才拦截。

配套纪律：

- **mock FAIL 先修 mock**：冒烟报 null 异常时，第一怀疑对象是 mock 未预注册页面真实 id，补齐后重跑；只有 mock 齐备后仍失败才判定为页面缺陷。
- 临时验证脚本（`_*.js`）跑完即删，不入库不提交。
- 验证结论以"只增不改"方式追加写入任务的留痕文件，形成可审计证据链。

## Faster Next Time

- 编写页面时保持两个习惯，验证脚本可跨任务直接复用：所有 DOM 取用统一走 `$(id)` 辅助函数；零外部依赖、数据内嵌。
- 断言清单写成一个脚本一轮跑全（pass/fail 计数收尾），避免逐项开 bash 会话。
- 敏感词扫描的误报特征先记住：`DOMTokenList`、`tokenize`、`credential` 变量名等标识符是高频误报源，回读上下文一眼可判。

## Applicability Boundaries

- 适用：单文件自包含 HTML/CSS/JS 交付物；平台 browser 工具只受理打开请求无回读（如 CodeArts Agent 内置 browser）；无构建链的纯静态页面。
- 不适用：具备截图/DOM/控制台回读的自动化工具（Playwright、hmosDeviceUI 等）存在时应优先真渲染验证；页面含异步 fetch 或外部数据依赖的部分 mock 无法覆盖，须在留痕中显式标注"未验证面"。
- 冒烟通过 ≠ 视觉正确：布局、配色、字体等纯视觉属性不在本流水线覆盖范围，只能靠 CSS 静态审查或人工查看。

## Evidence or Examples

- 会话 ses_e4c37b048ffeqGK3zYLwRrc6eC（P001 SDD 流程图可视化）：四查一轮跑出 pass=12/fail=1，7.4-H 命中 `DOMTokenList` 中的 "Token"，回读上下文判定为 API 标识符误报，未返工；mock 冒烟首跑报 `$('zoom-in')` null 异常，定位为 mock 未预注册 HTML 真实 id（`zoom-*`/`svg-*`），补齐后 19/19 交互断言全过（标签切换/缩放 clamp/节点互斥展开/泳道详情等）。
- 最终交付 42KB 单文件 HTML（三图 + 5 标签交互），commit 2861cd2；临时脚本 `_g3check.js`/`_g3domtest.js` 验证后即删。
- 本模式已同步沉淀为技能 `self-contained-html-verify`（显式调用通道）；本经验承载检索注入通道，二者互补。