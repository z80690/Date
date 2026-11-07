---
id: 2026-11-07-file-protocol-fetch-cors-build-time-inline
title: file:// 直开的单文件 HTML：本地数据文件须构建期内联，运行期 fetch 被 CORS 阻断
category: coding-pattern
nature: pitfall
created_at: 2026-11-07T17:36:54
updated_at: 2026-11-07T17:40:33
tags: [file-protocol, CORS, 单文件HTML, 数据内联, 无构建前端]
keywords: [fetch file://, null origin, CORS 拦截, 构建期抄录, 来源路径标注, 数据层内联, 断网可用, 零外部依赖, 运行期零文件读取, 单文件交付页]
problem_patterns: [单文件 HTML 用 fetch('./data.json') 读本地数据文件，file:// 双击直开时报 CORS 错误或数据区空白, 设计阶段按 http 服务假设规划运行期读文件，交付后断网或 file 场景整页数据不可用]
source_sessions: [ses_e4c51e180ffeH9ipiS0EgrBtfd]
project: Date
severity: medium
quality_score: 82
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: A
related_experiences: [2026-11-07-svg-viewbox-zoom-single-source-data-layer, 2026-11-07-headless-html-verify-node-vm-dom-mock]
---

# file:// 直开的单文件 HTML：本地数据文件须构建期内联，运行期 fetch 被 CORS 阻断

## Scenario

无框架、无构建链的单文件 HTML 交付页（说明页、可视化流程图、看板），要求双击 file:// 直开、断网可用、零外部依赖，页面需展示若干本地数据（事实源文件内容、资产清单、配置快照）。设计数据通道时容易出现"数据放独立 .json/.md，页面运行期 fetch 相对路径加载"的错误方案。

## Key Signals

- 设计文档或代码里出现"页面运行期 fetch('./data.json') / XMLHttpRequest 读本地相对路径文件"——这是翻车预兆，不用等运行。
- file:// 直开后 Console 报 `CORS policy: Cross origin requests are only supported for protocol schemes: http...` 或响应为空，页面数据区空白、渲染函数拿到 undefined。
- 危险信号：把"本地文件"当"天然可读"，仅按 http 服务假设设计数据加载路径。

## Essence

浏览器同源策略把 file:// 页面的 origin 视为 **null（不透明源）**，对 file:// 资源的 fetch/XHR 默认一律拦截——这是规范行为，不是浏览器 bug。"本地文件"不等于"可读文件"：**数据必须在构建期（写页面时）进入 HTML 内联，运行期零文件读取**。通道决策是设计阶段的事，编码后发现只能返工数据通道。

## Approach

1. 设计阶段先做数据通道决策：满足"file:// 直开 + 断网可用"约束 → 运行期零文件读取，全部数据构建期抄录内联，并在设计文档写明该决策及理由（file:// fetch 受 CORS 限制）。
2. 内联数据收敛为单一数据层常量对象（如 `const DATA = {...}`），页面渲染函数只从该对象取值，不与静态文案形成双源。
3. 每个数据块标注来源文件路径与抄录时点（JS 注释或 HTML 注释均可），使固化数据可审计、后续可再同步；明确标注"数据快照时点"，避免读者误当实时数据。
4. 交付前检查点：搜页面脚本中的 `fetch(`、`XMLHttpRequest`、动态 `import(` ——file:// 交付页应为零命中。
5. 不采用 `--allow-file-access-from-files` 之类的浏览器启动参数绕过：依赖用户改启动配置的交付方案等于不可用。

## Faster Next Time

- 拿到"断网可用 / file:// 直开 / 零外部依赖"类约束时，第一步做数据通道决策，再画页面结构；数据通道错，后面全部返工。
- 评审单文件交付页时，"独立数据文件 + 运行期加载"组合直接拦截。
- 与数据层单一源模式配套使用：内联常量既是 CORS 规避手段，也天然是页面唯一文案源。

## Applicability Boundaries

- 适用：file:// 直开、零构建链、断网可用的单文件 HTML 交付页。
- 不适用：http(s) 部署的页面（正常 fetch/import 均可用）；有构建链的项目（构建期内联/打包是常规能力）；浏览器扩展、Electron 等拥有特殊文件权限的运行环境。
- 依据为浏览器同源策略规范行为（origin=null 对 file:// 资源的默认拦截），跨浏览器稳定；个别浏览器实验性开关可绕过但不可作为交付依赖。

## Evidence or Examples

- 会话 ses_e4c51e180ffeH9ipiS0EgrBtfd（P001 实现方案设计）：design.md 技术选型决策原文——"HTML 运行期零文件读取（file:// 下 fetch 受 CORS 限制会报错），事实源内容构建期抄录固化并标注来源路径"；事实源内容（协作公约 6 条、技能注册状态 11 项等）全部内联并标注 `.codeartsdoer/` 来源路径。
- 同项目 P001 后续交付页采用该决策（42KB 单文件，冒烟 19/19 通过，见 related 经验），数据通道无返工记录。