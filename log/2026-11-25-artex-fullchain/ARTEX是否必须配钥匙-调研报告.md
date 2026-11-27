# ARTEX 是否必须配钥匙 + GitHub 议题调研

日期：2026-11-25 18:xx
范围：本地源码/文档 + GitHub 议题（RuoJi6/ARTEX 分支仓库）+ OpenRouter 官方错误文档 + 密钥目录实测

## 一、用户对 ARTEX 的核心疑问（原话拆解）

1. ARTEX 必须配个 key 吗？
2. GitHub 议题里有没有解决方案？（用户提到原作者文档被删、让我们去分支找）
3. 这个 OpenRouter 错误能不能解决？

## 二、结论先行

**必须配模型，但不一定必须是"钥匙"。**

| 用途 | 要不要模型/钥匙 |
|---|---|
| 只看界面、演示数据（Demo 模式） | 不要，纯前端跑，不用模型密钥 |
| 真跑探索/扫描/自动写发现 | 要，必须有 LLM 端点 |
| LLM 端点来源 | 官方两种：环境变量 key，或 UI「LLM 配置」页填 key |

ARTEX 官方文档原文：
- README:107 `> 依赖数据库 PostgreSQL；探索需配置 LLM（ANTHROPIC_API_KEY 或 OPENAI_API_KEY，也可在 UI 里配）。`
- README:314 `**LLM**：export ANTHROPIC_API_KEY=sk-...（或 OPENAI_API_KEY），也可在 UI 的「LLM 配置」页填写。可选：ARTEX_LLM_PROVIDER / ARTEX_LLM_MODEL / ARTEX_LLM_BASE_URL / ARTEX_LLM_PROXY。`
- README:418 `ARTEX 是一套 LLM 多 agent 驱动的自主渗透系统`
- README:71 Demo 模式明确 `不需要 Go、PostgreSQL 或模型密钥`

一句话：它本质就是靠大模型当脑子的程序。没脑子（模型），界面能看，活干不了。

## 三、GitHub 议题调研结果

仓库真身（本地 .git/config + README 确认）：
- 现用分支仓库：`RuoJi6/ARTEX`（独立维护，保留原作者提交历史 + AGPL-3.0）
- 原作者仓库：`Autumn-27/ARTEX`（用户说"文档被删"——README:12 印证原仓库已不在维护方，程序包从 RuoJi6 的 Releases 下载）
- go.mod module 名仍是 `github.com/Autumn-27/artex`

翻遍了 OPEN(22) + CLOSED(47) 议题，跟"钥匙/模型"强相关的：

| 议题 | 标题 | 关键内容 |
|---|---|---|
| **#187** | **openrouter Request path cannot be relayed code 400** | 跟我们的错误一字不差。提问者填 `https://openrouter.ai/api/v1`，GET 模型没问题，POST 报 400。**2026-11-25 当天提问、当天自己关闭，零评论、无关联提交、无公开解法。** |
| #68 | 疑问 LLM 模型支持 | 问是否只支持 Anthropic/OpenAI 官方格式。回复：可用 OpenCode 格式，但要加 `x-opencode-session` 请求头；另一人先说"试几种格式都不行"，后来说"通过中转格式解决"。 |
| #170 | 大模型不支持 Gemini？ | 4 条评论，非核心 |
| #32 | 设置 llm 报错 apikey 是对的 | 2 条评论，非核心 |
| #41 | Workers 只支持 1 个模型 | 本地模型用户，讨论多模型并发 |
| #149/#168/#161 | Token 消耗太大 | 侧面印证：ARTEX 全靠模型烧 token |

**结论**：GitHub 上没有人给出这个 400 错误的公开解法。#187 是最直接的同类问题，提问者自己关了，没留下"怎么修"。用户估计"议题里有解决方案"——实测没有。

## 四、OpenRouter 错误深挖（对照实验）

先认错：之前我说"你这台机器把请求挡了"是错的。抓完整响应头坐实：
- `Server: cloudflare`、`x-openrouter-error-origin: client`、`CF-RAY: ...-LAX`、`Set-Cookie: __cf_bm`
- 请求**到了** OpenRouter 服务器，是它自己回的 400。

三组对照（同一把 key）：
| 实验 | 结果 |
|---|---|
| 假 key 打对话路径 | 401 User not found |
| 真 key 打不存在的路径 | 404 Not Found |
| 真 key 打对话路径 | **400 Request path cannot be relayed** |

由此定性：
- key 有效（GET /key 显示普通 key、0.1 美元额度、0 消耗、非管理/非配置钥匙）
- 路径写对了（`https://openrouter.ai/api/v1` + `/chat/completions` 就是官方地址，试过 /v1、/api、无前缀等变体都不是这个错）
- 请求确实到达 OpenRouter 且通过 key 校验
- 是 OpenRouter relay 层对**对话类请求**的统一拒绝（chat/completions、messages、responses 全试过，都 400）

六种绕过尝试全部失败：裸请求、官方头(HTTP-Referer/X-Title)、浏览器指纹、anthropic 格式端点、responses 新端点、换 Python TLS 栈。

官方错误文档（errors-and-debugging）里**没有** "Request path cannot be relayed" 这条——这是未公开的拦截，只能定性、不能从文档查到根因或解法。

## 五、其他钥匙/通道实测（都堵）

| 来源 | 结果 |
|---|---|
| DeepSeek key | 401 api key invalid，失效 |
| 智谱 2 把 | 401 身份验证失败，失效 |
| 超算互联网 key | 端点 404，地址不对 |
| jev / typesafe.ai key | 不是聊天接口，是"打分/选择"专用（POST /v1/systemone），接不了 ARTEX |
| WorkBuddy 内部网关 60156 | 认证能过但无 OpenAI 路径（404/000），且是内部 hook 服务，不给第三方程序用 |

## 六、诚实结论 + 可行路

1. **GitHub 没解法。** 议题 #187 就是同一个错，自己关了没留方案。
2. **ARTEX 必须配模型才能干活**，这是设计（LLM 多 agent），不是配置 bug。
3. **你这把 OpenRouter 钥匙是好的**，错在 OpenRouter 服务端 relay 层拒对话请求，非 key、非格式、非本机。
4. 当前机器上凑不齐"有效且对话能通的 OpenAI 端点"，所以 ARTEX 自主跑这条路暂时走不通。

**要真正跑起来，只有这几条：**
- A. 换一把别家的有效 key（且该家对话端点在你这网络能通）
- B. 换个网络出口（换环境）再试这把 OpenRouter key
- C. 装本地模型（Ollama / lmstudio，吐 OpenAI 兼容接口）给 ARTEX 配 `ARTEX_LLM_BASE_URL`，完全不要外部 key（用户之前说不用本地模型，故仅列出）
- D. 只用 Demo 模式看界面，不跑真实探索（README:71）

全程只划边界、没改用户任何配置、没留后台服务。
