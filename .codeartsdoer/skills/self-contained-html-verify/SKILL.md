---
name: self-contained-html-verify
description: 单文件自包含 HTML（可视化流程图/说明页）的交付模式与无 GUI 四查验证流水线：本机 browser 工具只能"请求打开"无内容/控制台回读，须改用 Node vm 编译 + DOM mock 冒烟执行页面脚本 + 正则扫描替代真 GUI 验证。凡涉及生成/交付自包含 HTML 页面、执行编码必审四查中的 HTML 验证、browser 打开后无法读回渲染结果时使用。
---

# 自包含 HTML 交付与无 GUI 四查验证

## 交付模式（写 HTML 时直接照做）

1. **零外部依赖**：不引 CDN/字体/link/@import/url(https…)，单文件双击 file:// 直开，断网全功能可用（公约第 2 条 + 验收硬条款）。
2. **数据层单一文案源**：全部图结构/详情文案集中在一个 JS 常量对象（如 DETAILS），DOM 卡片区由 JS 从该对象渲染；同一文案禁止在 SVG 与 DOM 卡片各写一份（防两源漂移）。改文案只动数据层，渲染逻辑不动。
3. **SVG 缩放方案**：viewBox 恒定 + 修改 svg 的 width/height 属性实现缩放（滚动条自然正确、布局不重排）；不用 transform: scale（会产生滚动区域错位）。
4. **同文档多 SVG**：每个 SVG 的 marker id 必须独立（arwF1/arwF2/arwF3…），同 id 跨 SVG 引用不保证生效。
5. **兼容降级**：detectCompat() 加载时特性检测（CSS.supports/SVGElement/DOMTokenList/addEventListener），失败仅显示顶部提示条，不抛未捕获错误、不阻断其余功能。
6. **交互接口约定**：switchTab / toggleNode（互斥展开，同一时刻至多一个）/ setZoom（clamp 上下限）/ resetZoom / detectCompat；缩放控件对非图视图（资产/帮助页）禁用置灰。

## 无 GUI 四查验证流水线（Node 内置模块即可，无第三方依赖）

browser 工具只返回"打开成功"，读不到渲染结果与控制台 → 以下流水线为等价验证：

1. **查一（JS 语法/控制台）**：正则提取 `<script>…</script>` 内容，`new vm.Script(code)` 编译——语法错误在此暴露。
2. **查二（交互功能，DOM mock 冒烟）**：
   - 从 HTML 提取全部 `id="…"` 与 `data-key="…"`，**预注册**成 mock 元素表（getElementById/querySelector/querySelectorAll 都查这张表）；
   - mock 元素实现：getAttribute/setAttribute/addEventListener/classList(Set)/style/innerHTML/textContent/scrollIntoView；
   - sandbox 提供 document + Math + console + CSS/SVGElement/DOMTokenList 桩，`vm.runInNewContext(code, sandbox)` 执行整个页面脚本（init 零异常即控制台无报错证据）；
   - 逐接口断言：标签切换显隐、缩放 clamp 与复位、SVG 宽高随缩放更新、节点互斥展开/收起、数据层渲染产物内容。
   - **FAIL 先修 mock 再判页面**：冒烟最常见失败原因是 mock 漏注册 HTML 真实 id（如 zoom-*、svg-*），补注册后重跑；确认 mock 完整仍 FAIL 才是页面缺陷。
3. **查三（断网自包含）**：正则断言零 `src|href="http…`、零 `@import`、零 `url(https…`、零 `<link`。
4. **查四（覆盖度+敏感信息）**：把验收条款落成关键串清单（每条 `html.includes()`），一次跑全；敏感正则（password/token/secret/api_key/PRIVATE KEY）初报命中**必须定位上下文判误报**——API 名（如 DOMTokenList 命中 token）不算违规。
5. **结构核验补充**：按图计数（泳道数/消息数/状态转移数/关键标注重复次数，如"自信度 ≥80%"须 ×4），用分段正则（先截取单个 `<svg id=…>…</svg>` 再计数）而非全文计数。

## 留痕与清理纪律

- 临时验证脚本命名 `_g3check.js`/`_g3domtest.js` 放项目根，跑完即删，绝不入库；验证结果（逐项 PASS/FAIL+误报定位）写入 TASK.md 阶段进展区（只增不改）。
- 性能结论以实测体积（Get-Item Length）+ 静态渲染无网络请求为据；单文件 <100KB 即远低于 2s/500ms 目标。
- 需求覆盖用"覆盖编号组织"法（需求点编 ①~⑥ → 设计/任务/验证逐项映射，防漏防编造，来源：经验库 2026-11-07-stage1-evidence-baseline-and-halt-reporting）。