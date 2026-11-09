---
id: 2026-11-08-dom-mock-id-set-drift-false-pass
title: DOM mock 冒烟假通过的盲区治理：页面真实 id 集合与 mock 预注册集合双向比对
category: testing
nature: pitfall
created_at: 2026-11-08T09:46:14
updated_at: 2026-11-08T09:46:14
tags: [dom-mock, 冒烟验证, 假通过, 验证盲区, vm-sandbox]
keywords: [DOM mock, 预注册, id 双向比对, 动态拼接 id, getElementById null, TypeError, forEach 中断, 标签切换空白, 冒烟假通过, 验证契约]
problem_patterns:
  - "mock 驱动验证全绿但真实运行报错：mock 预期表与被测物真实 DOM 结构漂移"
  - "脚本动态拼接 id（'xxx-'+n）的取用目标在页面缺失时静默变 null，缺陷表现为半态而非显式报错"
source_sessions: [ses_e486e6efcffe4mlzuelSbo3ypG]
project: Date
severity: high
quality_score: 90
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-07-headless-html-verify-node-vm-dom-mock, 2026-11-08-edge-headless-screenshot-real-render-verify]
---

# DOM mock 冒烟假通过的盲区治理：页面真实 id 集合与 mock 预注册集合双向比对

## Scenario

单文件 HTML（或任何 JS 驱动页面）在无 GUI 环境交付时，常用 Node vm + DOM mock 冒烟执行页面脚本来替代真实浏览器验证。mock 元素表通常从 HTML 静态提取 id 后**人工整理/预注册**——这份人工表本身就可能偏离页面真实 DOM。当脚本以动态拼接方式取用 id 时，人工表极易"按脚本预期"反向构造，把页面缺陷掩盖成满分通过。

## Key Signals

- 冒烟断言全部通过（甚至满分），但真实用户在浏览器操作后报障：点击切换后大片内容空白。
- 页面脚本存在动态拼接 id 的取用（如 `$('tab-' + n)`），而 mock 表为拼接结果人工预想了注册项（tab-1/2/3），页面实际元素并没有这些 id。
- 运行期不是显式报错给用户，而是静默半态：`getElementById` 返回 null → 后续 `.classList` 抛 TypeError → forEach 循环中断 → 旧视图已隐藏、新视图未显示。

## Essence

mock 驱动验证的有效性上限 = mock 表与被测物真实结构的**一致度**。人工预注册天然存在反向污染：脚本想取什么就注册什么，页面缺什么反而被掩盖。本例 53/53 全过是假象——缺陷类型恰恰是"mock 有而页面无"。因此验证契约必须把"页面真实 id 集合 ≡ mock 预期集合"作为**双向集合断言**固化进流水线，而不是靠人工维护 mock 表的一致性。

## Approach

1. **静态提取页面 id 全集 P**：正则解析 HTML 中全部 `id="…"` 属性。
2. **静态提取脚本字面量取用集合 R**：扫描脚本内 `$('字面量')`/`getElementById('字面量')` 引用；断言 R ⊆ P（脚本引用的每个字面量 id 必须在页面存在）。
3. **双向集合断言**：P 中每个元素 mock 表必须注册（页面有 mock 无 = FAIL）；mock 表中每个元素 P 必须存在（mock 有页面无 = FAIL）。**禁止人工补录迁就**——发现差集时先判定漂移方向并修复对应侧，不允许把缺失项直接加进 mock 表蒙混。
4. **动态拼接 id 单列高危核查**：对 `'xxx-' + n` 形态，枚举全部拼接结果（n 的取值范围）逐一核对页面是否存在对应 id。
5. **FAIL 分流纪律**：mock 多注册（掩盖页面缺陷）→ 必须修页面；页面有而 mock 漏注册（mock 不完整）→ 修 mock。旧纪律"FAIL 先修 mock 再判页面"仅适用于后者。

## Faster Next Time

- 把第 1–3 步做成验证脚本里交互冒烟之前固定的一"查"，一次升级永久封堵此类盲区。
- 高危信号组合：`$('xxx-'+n)` 动态拼接 + 人工预注册 mock 表 + 首次交付即"满分冒烟"——三者同时出现时优先怀疑假通过。
- 交付前保留一层真实渲染兜底证据（headless 截图），见 related 的 debugging 篇；两层证据矛盾时以真实渲染为准。

## Applicability Boundaries

- 适用：任何"从 HTML/模板静态构造 mock 元素表再在 vm/沙箱执行页面脚本"的验证流水线，不限于单文件 HTML。
- 不适用：mock 由工具从真实 DOM 自动生成（如 jsdom 直接加载 HTML）的场景——一致性由工具保证，但集合断言仍可留作回归门禁。
- 局限：集合比对只覆盖 id 取用类缺陷；事件绑定参数错误、CSS 显隐逻辑错误等仍需真实渲染验证兜底。

## Evidence or Examples

- 项目实证（2026-11-08，会话 ses_e486e6efcffe4mlzuelSbo3ypG）：交付单文件多标签 HTML，`activateTab` 经 `$('tab-'+n)` 取按钮，页面 3 个 tab 按钮实际无 id；mock 验证脚本人工预注册了 tab-1/2/3，53/53 全过后交付。用户浏览器点击 Tab2/3 后整片空白。修复 = 按钮补 id；验证升级 = 第五查（P ≡ mock 双向比对 + R ⊆ P 字面量核查）+ 全量回归 62/62，并用 Edge headless 截图实证三 Tab 渲染正常。
- 教训锚点：冒烟通过数 53 → 62 的增量全部来自新断言；旧 53 项没有任何一项能抓住该缺陷——通过数量多不等于覆盖了对的缺陷类型。