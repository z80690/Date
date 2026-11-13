# G2.4 本地哑端点部署留痕（gates/deploy-trace-mockep.md）

> 承接 tasks.md 2.4（design 2.1.2 MockEP 组件、M2 理由③、R4）｜执行时间：2026-11-12

- 脚本：`temp\mock_llm_server.py`（Python 3.11 标准库 http.server，零第三方依赖）。
- 监听：**127.0.0.1:7810**（仅回环；IF-5 口径=非 0.0.0.0，实测绑定地址写死 HOST="127.0.0.1"）。
- 行为：GET /health→`{"status":"ok"}`；POST /v1/chat/completions→OpenAI 兼容占位 JSON（确定性非空响应，零模型推理）；GET /v1/models→占位模型列表。
- 启动方式：WMI Win32_Process.Create（python 全路径，Start-Process 传参被吞怪癖规避）→ReturnValue=0，PID=15176（2026-11-12 20:5x 实测，长驻后台保活）。
- 存在意义登记：让 PentAGI/ARTEX 模型配置合法化并确保任何误调用落 127.0.0.1 而非云端（R4 防哑端点误配公网）；真实决策全部来自码道智能体（方案 a 回执模式）。
- 外连核验：脚本无任何出站请求代码（零 urllib/requests 调用）；绑定硬编码回环。
- 【验证方式】/health 与 /v1/chat/completions 回执可复放（本轮实测输出在案）。

# G2.5 模型解耦配置落位（阶段性）——PentAGI .env

> 承接 tasks.md 2.5（spec 5.3.1-6；design M2-1；pre_check 3.1 清单底稿）｜生成脚本 temp\gen_pentagi_env.py（.env.example 全量→逐行覆写→UTF-8 无 BOM LF）

关键项核验（Select-String 实测 2026-11-12）：

| 配置项 | 值 | 状态 |
|---|---|---|
| SERVER_HOST | 127.0.0.1（原 .env.example:258 为 0.0.0.0，已覆盖） | ✅ 回环 |
| SERVER_PORT | 8443 | ✅ |
| LLM_SERVER_URL | http://127.0.0.1:7810/v1（哑端点） | ✅ 方案 a |
| LLM_SERVER_KEY/PROVIDER | placeholder 占位非空/openai_compatible | ✅ |
| PROXY_URL | （空） | ✅ R1 兜底 |
| OPEN_AI_KEY/ANTHROPIC_API_KEY/GEMINI/GIGACHAT/OPENROUTER/DEEPSEEK/OLLAMA_HOST | （全空） | ✅ 九组厂商端点禁用 |
| TAVILY/FIRECRAWL/TRIVERSAAL/PERPLEXITY/GOOGLE/SPOTIOS/SEARXNG API KEY | （全空） | ✅ search 八家禁用 |
| GRAPHITI_URL/UPDATE_CHECK_URL | （空） | ✅ 子栈外连禁用 |

- 配置落位完成；**栈启动验证被 R9 阻塞**（Docker Desktop 不可用，呈报中）；compose 启动后补 IF-5 监听核验+T4 抓包。
- ARTEX env（ARTEX_LLM_BASE_URL→哑端点+PROXY 置空）随 2.3 部署执行落位（依赖 PostgreSQL 就绪，呈报中）。

（完）