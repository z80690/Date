---
name: web-content-scraping
description: 外部网页正文抓取的降级路径与实测参数：webfetch 可能静默无输出、browser 工具无内容回读、桌面版 JS 渲染空壳的判定特征、移动版域名+iPhone UA 降级命中、图片文字用 analyzeImage 补取。凡涉及抓取外部网页/文章正文作为调研输入、webfetch 无返回、HTML 体积大但去脚本后无正文时使用。
---

# 外部网页正文抓取降级路径

## 降级顺序（按序尝试，命中即停）

1. **webfetch**：可能静默无输出（无报错也无内容）。出现即直接降级，不重试。
2. **browser 工具**：只返回"请求打开成功"，读不到渲染结果与控制台——对内容抓取无效，仅适合给用户人眼看（同 self-contained-html-verify 中的结论）。
3. **curl 桌面版**：带浏览器 UA + `-o` 落盘临时文件再解析（不要管道直读）。**空壳判定**（满足即弃，不纠缠）：
   - 去除 `<script>`/`<style>`/标签后可见文本长度≈0；
   - 文章 ID/正文关键词不在 HTML 中；
   - 含 `jsvmprt`（JS 虚拟机保护特征）。
4. **curl 移动版**：换移动域名（`www.`→`m.`）+ iPhone UA，一次命中完整正文的实测成功率最高。

## 正文提取模式

```powershell
# 剥 script→style→标签→压缩空白，标题取 <title>
$raw = Get-Content $tmp -Raw -Encoding UTF8
$txt = $raw -replace '(?s)<script[^>]*>.*?</script>','' -replace '(?s)<style[^>]*>.*?</style>','' -replace '<[^>]+>',' ' -replace '\s+',' '
```

## 图片内容补取（网页关键内容在图里时）

- `analyzeImage` 的 `task` 参数必填（漏传会报错），`imagePath` 传本地临时文件路径；先用 `curl -o` 下载图片。
- 头图可能只是封面（识别不到正文属正常），图集卡片直链抓不到就明确告知用户，按已有摘要工作并在产出中标注来源。

## 两类拦截病根（对症下药，先判型再换招）

| 病根 | 特征 | 解法 |
|------|------|------|
| **UA 检测** | 带 UA 即 200，域名不用换（实例：华为云 EdgeOne 文档站） | 只补浏览器 UA |
| **JS 渲染/反爬** | 换 UA 没用，HTML 全是保护脚本（实例：今日头条桌面版） | 换移动版域名 + 移动 UA |

## 找不到正文转载时：搜索降级链 + 官方站直猜

死磕单一来源是错误工作方式（用户明确批评"死在这个网站里找，互联网一大堆文章，用搜索引擎找"）。应多渠道并行。

搜索引擎实测可用性（2026-11-07，curl 实测）：

| 引擎 | 状态 |
|------|------|
| 360（www.so.com/s?q=） | ✅ 可用，通用引擎里结果质量最好；但结果里的 `/link?m=...` 加密中转已失效（返回 404 页），拿不到真实目标 URL |
| 百度 | ❌ 安全验证页拦截（title=百度安全验证） |
| Bing 中国区 | ❌ 引号短语被泛化（`"Code with Claude"` 搜出单词词典结果） |
| DuckDuckGo lite / YouTube | ❌ 被墙，无输出（临时文件都不产生） |
| 搜狗微信 | 可达但命中率低 |
| 头条站内 so.toutiao.com | 可达但返回泛化旧文 |

官方站直猜（搜索引擎全灭后的最优路径）：

1. 先用头图/封面 OCR（analyzeImage）确证来源身份与官方项目名（本次由此确证 "The Prompting Playbook"）
2. 直接猜官方 URL 模式批量测 HTTP 码；**308 = 域名可达但路径迁移**，用 `curl -sL -w "%{url_effective}"` 跟出最终路径再抓正文
3. 官网改版迁移实例：anthropic.com/engineering/* → 308 → /research/* 200
4. 从已抓到的官网列表页提取站内 slug 补充候选
5. 收尾口径：作者官方一手文章 ≈ 原文替代源，引用时标 URL+发布日期；视频/图集卡片的逐条原文不可得时如实声明+列待补充清单，对应关系标"推断"

## 实测留痕（2026-11-07）

- 今日头条微头条 `www.toutiao.com/w/{id}/`：桌面版 72KB 全为 JS VM 保护脚本；`m.toutiao.com/w/{id}/` + iPhone UA → 69KB 含完整标题+正文。
- 头条图集：仅头图有带签名的直链可下载（p3-sign.toutiaoimg.com），其余卡片需 APP 打开，抓不到属预期。
- Anthropic 官网：/engineering/* 全部 308，跟随得 /research/* 200（building-effective-agents / writing-tools-for-agents / claude-code-best-practices / demystifying-evals-for-ai-agents 四篇命中）；同期所有搜索引擎均无该分享会转载，直猜官方 URL 是唯一命中路径。
