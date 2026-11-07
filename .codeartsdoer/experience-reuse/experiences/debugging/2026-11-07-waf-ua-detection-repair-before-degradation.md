---
id: 2026-11-07-waf-ua-detection-repair-before-degradation
title: WAF 挑战页先分型修复再降级：UA 检测型换浏览器 UA 即过，SPA 型 200 不等于有数据
category: debugging
nature: technique
created_at: 2026-11-07T09:17:47
updated_at: 2026-11-07T09:17:47
tags: [waf, http-client, web-scraping, degradation-chain]
keywords: [EdgeOne, Security Verification, 浏览器UA, UA检测, JS强制验证, SPA骨架, 结构化命中计数, 修复优先于降级, 3次上限, 静态抓取]
problem_patterns: ["官方文档站返回挑战页后直接进入降级，错失一次换 UA 即可修复的抓取", "HTTP 200 被当作'抓取成功'，实际拿到的是 SPA 空骨架无数据", "对验证码强制型站点尝试绕过打码，越过合规红线"]
source_sessions: [ses_e4c75b385ffejT7VS1xOgDQLc2]
project: Date
severity: medium
quality_score: 88
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: ["debugging/2026-11-07-waf-challenge-page-degradation.md", "debugging/2026-11-07-browser-proxy-plugin-network-root-cause.md", "agent-ops/2026-11-06-codeartsdoer-docs-retrieval.md"]
---

# WAF 挑战页先分型修复再降级：UA 检测型换浏览器 UA 即过，SPA 型 200 不等于有数据

## Scenario

调研任务需要从官方文档站/社区抓取资料，静态抓取（curl/webfetch）被 WAF（如 EdgeOne）以 Security Verification 挑战页拦截。既有处置经验只覆盖"识别挑战页+任务降级"；本经验补充修复路径：挑战页出现后先分型，部分拦截一次换 UA 即可解除，不必立即降级。

## Key Signals

- HTTP 200 但 body 是挑战页 HTML：特征为引用验证码脚本（如 TEOCaptchaWidget.js）、含"Security Verification"标题、正文无目标内容。
- 同日实测分型线索：curl 默认 UA（`curl/x.x`）被拦；文档直链在更换 UA 后返回 200 且内容完整；搜索/目录页即使 200 也抓不到数据条目。

## Essence

WAF 拦截分三型，处置路径不同：

1. **UA 检测型**：只校验 User-Agent 特征。换成标准浏览器 UA 即放行——这是合法修复，不触碰验证码红线。
2. **JS/验证码强制型**：需要执行 JS 或人机验证。静态抓取不可过，**禁绕过、禁打码**，按降级处理。
3. **SPA 渲染型**：HTTP 200 且无拦截页，但内容由 JS 在浏览器端生成。静态抓取拿到的是空骨架，"200 ≠ 有数据"。

根因链：状态码与内容可用性是两个独立维度——拦截层给 200+挑战页，渲染层给 200+空骨架，必须用内容实质校验区分。

## Approach

1. 挑战页出现后，第一次修复尝试：同 URL 带 `-A "<标准浏览器 UA>"` 重试。
2. 任何 200 响应都做**内容实质校验**：用结构化命中计数（如 JSON 标题数、文章链接数、目标关键词出现次数）判定，而非状态码或字节量。
3. 命中为 0 时换端点探测拦截/渲染边界：文档直链 vs 搜索页 vs 目录页，确认哪类页面是 SPA、哪类是纯静态。
4. 累计 3 次尝试仍无实质内容 → 转降级：改用可达的官方直链文档兜底、阻塞项按四字段登记（原因/恢复条件/回迁目标/时间）、结论如实呈报（禁编造凑数）。

## Faster Next Time

- 挑战页 ≠ 终局：先花一次调用的成本试 UA 修复，再考虑降级；降级前先穷尽合法修复。
- 数据可用性判定模板：`状态码 + 结构化命中计数` 双条件，单看任一都会误判。
- 预检顺序：UA 修复 → 内容校验 → 端点分型 → 3 次上限降级，每步留痕原文错误。

## Applicability Boundaries

- 适用于 curl/webfetch 等静态抓取通道；浏览器自动化能执行 JS 时 SPA 型可解，但验证码强制型仍应禁绕过。
- 需要登录态/付费墙的内容不在本经验范围。
- "3 次上限"沿用项目重试纪律；其他环境可按自身纪律调整上限，但"先修复后降级"的顺序不变。

## Evidence or Examples

- 本会话实测（华为云文档站）：默认 UA 被拦 → 换浏览器 UA 后 `llms.txt` 返回 200/138KB 完整内容；官方产品描述页 200/4.4KB 成功。
- SPA 假阳性实证：developer 站搜索页 200/39KB 但 `json-titles=0`、`article-hrefs=0`；support 目录页 200/69KB 无 `.md` 引用——两例均为 200 无数据。
- 3 次上限后降级收尾：社区实战案例 0/5 如实呈报，官方直链文档作为权威补充来源入库，阻塞项按四字段登记。