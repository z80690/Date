# P003 前置门禁核验报告（pre_check.md）

> 版本：v1.0 实测填充版（2026-11-12）；v0.1 评估框架版（2026-11-12，同日先行落盘，框架结构本版完整保留）
> 依据：spec.md v1.1 第 5.3 节前置门禁（G-PC1/G-PC2/G-PC3）+ 用户《P003 补充裁决：闭源拉取验证与码道模型解耦（前置门禁）》（2026-11-12）
> 状态声明：v0.1 框架中所有"待实测"项已于 2026-11-12 完成实测填充（本版）。全部结论附实测命令与原始输出摘录，无虚构；确未执行/不适用的项如实标注"未实测"，不混写。实测项已填充，本报告构成用户审阅（G-PC3）依据；获审阅通过前，禁止生成 design.md（spec 5.3.1-10）。
> 实测环境：win32 / PowerShell 5.1；纯命令行工具链（curl.exe / git.exe）；api.github.com 直连可用；github.com git 通道直连被重置，代理通道 `http://127.0.0.1:31181` 实测存活；第三方仓库全部隔离落盘于 `D:\refs\`，与工作区物理隔离。本次为纯调研评估：未部署运行任何框架、未执行任何攻击动作、未公网暴露端口。

## 1. 裁决输入登记（用户已给定事实，如实录入）

1. **ARTEX 已闭源**（用户裁决给定）：常规拉取预期必败；须实测 fork、旧版本、归档镜像等获取路径；确无源码则登记"ARTEX 仅做逻辑模拟，不实际部署"（spec 5.3.1-2），禁止写"自动拉取成功"。
2. **本机无法跑本地大模型**（用户裁决给定，Ollama 带不动）：禁用本地 Ollama 方案（spec 5.3.1-6）。
3. **码道模型通道**：当前环境 GLM-5.3-Flash 等内置能力，为拆模型层后框架模型推理的唯一接入通道；禁止公网模型 API 外连。
4. **红线重申**：四不红线（spec 4.3.1）、目标地址白名单与越界即停（spec 4.3.2/6.1）、禁公网外连、禁虚构拉取（spec 5.3.1-4）全部维持，本核验不放宽任何约束。
5. **并行关系**：本核验与先学后干学习门禁（spec 5.2）可并行开展，两者均过才进 design（spec 5.3.1-11，用户裁决明示）。

**实测复核注记（2026-11-12，如实标注与给定事实的差异）**：
- 第 1 条"ARTEX 已闭源"：**原仓库层面属实**——`curl.exe -s https://api.github.com/repos/Autumn-27/ARTEX` 返回 `HTTP_CODE=404`、`{"message": "Not Found"}`。但实测发现社区续维护开源版 `RuoJi6/ARTEX`（AGPL-3.0，保留原仓库提交历史）源码可获取，故"仅做逻辑模拟"兜底未触发；是否实际部署仍属用户决策范畴，本报告不改判、不放宽。
- 第 3 条"码道模型通道"：经 tool_search 实测复核成立——平台未提供可被外部框架 HTTP 调用的本地模型端点（见 3.3 节证据）。

## 2. 卡点 1：拉取可行性（《拉取可行性报告》，对应 G-PC1）

### 2.1 ARTEX（预期闭源，重点实测替代获取路径）

**检索路径 1（fork）**：实测命中。
- `curl.exe -s "https://api.github.com/repos/RuoJi6/ARTEX/forks?per_page=3"` → 返回 `MutualDerivativeTechnology/ARTEX`、`jianwenwang/ARTEX`、`zhl-hash/ARTEX`（原始 JSON 留存 `D:\refs\_artex_forks.json`），三者均 `"fork": true`，pushed_at 与上游同步（2026-11-11T11:26:29Z），可作为 fork 镜像退路。
- 主检索 `curl.exe -s "https://api.github.com/search/repositories?q=artex+agent"` → `"total_count": 83`（原始 JSON 留存 `D:\refs\_artex_agent.json`）。

**检索路径 2（旧版本/Release 归档）**：实测命中 4 个旧版本快照拷贝。
- 搜索结果中 `HAMAN23333/ARTEX`、`LyCecilion/ARTEX`、`singualow/ARTEX`、`LangfordKuo/ARTEX`：描述均为"AI 自主渗透测试系统 | 百度'agent+'攻防挑战赛冠军项目"，pushed_at 2026-10-08~10（历史快照，非活跃），archived=false。
- 原仓库 Autumn-27/ARTEX 因 404，其 Releases 归档不可达（失败证据见下）。

**检索路径 3（归档镜像/存档渠道）**：实测命中 2 个续维护/衍生版本。
- `RuoJi6/ARTEX`（主命中）：1760 stars / 1024 forks / language=Go / license AGPL-3.0 / archived=false / fork=false / pushed_at=2026-11-11T11:26:29Z / homepage=https://artex-demo-ruoji6.vercel.app/；描述"Autumn-27/ARTEX 持续维护开源版本（Internationalized version）"；README 本地实测摘录："本仓库为独立维护的 RuoJi6/ARTEX，保留 https://github.com/Autumn-27/ARTEX 的原始提交历史与 AGPL-3.0 许可证。程序发布包从本仓库 Releases 下载，Docker 镜像 ruoji6/artex 由本仓库 GitHub Actions 构建并发布。"
- `jiwoochris/artex-global`：描述"Global edition of ARTEX — an LLM multi-agent autonomous penetration-testing framework ... (upstream: Autumn-27/ARTEX, AGPL-3.0)"。
- 附注：搜索另命中 `01NGVI-QINGYI/ARIA-X`（描述"Fuses ARTEX, Cairn & PentAGI"，6 星）——与三框架同名关联但无官方背书，未采信，仅登记。

**成功路径**（实测完成）：
```
git clone --depth 1 -c "http.https://github.com/.proxy=http://127.0.0.1:31181" https://github.com/RuoJi6/ARTEX.git D:\refs\ARTEX
git -C D:\refs\ARTEX rev-parse HEAD
→ 73d5437c5a64559ed803bcd096d2a0a0014a1214
git -C D:\refs\ARTEX log -1 --format="%ci %s"
→ 2026-11-11 15:25:36 +0800 Merge pull request #135 from RuoJi6/agent/mika/github-4
```
语境匹配实测：README 标题"ARTEX — AI 自主渗透测试系统（Go 后端 + Next.js 前端）"；顶层目录含 `agent / llmhttp / llmpool / llmrec / traffic / intercept / guard / evidence / mcphttp / server / web / skills`，与"渗透测试 AI agent / 双图 / 子代理指挥所"语境匹配。

**失败证据**：
- 原仓库闭源：`curl.exe -s -o D:\refs\_autumn27_artex.json -w "HTTP_CODE=%{http_code}" https://api.github.com/repos/Autumn-27/ARTEX` → `HTTP_CODE=404`，响应体 `{"message": "Not Found", ...}`。
- github.com git 通道直连失败（两次）：`git clone --depth 1 https://github.com/RuoJi6/ARTEX.git ...` → `fatal: unable to access ...: Recv failure: Connection was reset`；`fatal: ...: Failed to connect to github.com port 443 after 21117 ms`。
- 网络根因（实测定位）：git 全局配置 `http.https://github.com/.proxy=`（空值=指名直连，覆盖通用 `http.proxy`）；curl 环境变量 `no_proxy` 白名单含 `github.com,*.githubusercontent.com` 等。强制绕过后代理实活：`curl.exe --noproxy "*" -x http://127.0.0.1:31181 https://github.com/RuoJi6/ARTEX` → `forced_proxy=200`。
- 免代理备份通道：`curl.exe -s -o NUL -w "%{http_code}" -r 0-1023 https://codeload.github.com/RuoJi6/ARTEX/tar.gz/refs/heads/main` → `codeload_direct=200`（tarball 快照退路）。

**替代方案**：若确无源码 → "ARTEX 仅做逻辑模拟，不实际部署"：指挥所逻辑（双图/子代理）以学习成果笔记 + 逻辑推演方式承载，不做实际部署。**本次实测源码已获取，该兜底未触发**；RuoJi6/ARTEX 的 fork 镜像（3 个）、旧版本快照（4 个）、codeload tarball 通道均可作进一步退路。

**结论**：**获取路径成功**（三选一之第一项）——源码地址 https://github.com/RuoJi6/ARTEX （AGPL-3.0），浅克隆落盘 `D:\refs\ARTEX`（HEAD=73d5437）。原仓库闭源属实，但"仅逻辑模拟"兜底未启用；是否实际部署待用户在 design 阶段裁决。

### 2.2 PentAGI（裁决预期：可拉取，须实测确认）

**官方渠道拉取**：实测成功。
- `curl.exe -s "https://api.github.com/search/repositories?q=pentagi"` → `"total_count": 134`，top-1：`vxcontrol/pentagi`（33981 stars，"Fully autonomous AI Agents system capable of performing complex penetration testing tasks"，updated_at=2026-11-12T08:09:00Z，archived=False，fork=False）——官方仓库确认为活跃开源，与裁决预期一致（原始 JSON 留存 `D:\refs\_pentagi.json`）。
- 浅克隆：`git clone --depth 1 -c "http.https://github.com/.proxy=http://127.0.0.1:31181" https://github.com/vxcontrol/pentagi.git D:\refs\PentAGI` → `Updating files: 100% (1728/1728), done.`；`git -C D:\refs\PentAGI rev-parse HEAD` → `cffed9485aa1cca70762cd08a57ac62a80406258`；最后提交 `2026-10-23 06:20:46 +0700 docs: the README links Graphiti to its public repository...`。

**依赖检测与补全**：未实测（不适用）——本次为纯源码分析（只读 grep），按派工纪律禁止实际部署运行框架，故无运行期依赖缺失清单可登记；该项留待 design/执行阶段在部署动作发生时实测。源码结构完整性已核验：backend/frontend/examples/observability/build/scripts 等目录齐备，`backend/pkg/config/config.go`、`.env.example`（623 行）等关键文件均在。

**端口绑定核验**：未实测（未部署，无端口绑定行为发生）；design 阶段约束登记：仅绑回环。PentAGI 源码默认监听实测：`.env.example:257-258` `SERVER_PORT=8443`、`SERVER_HOST=0.0.0.0`——**部署时须显式改绑回环**，此为静态证据登记。

**成功路径**：代理通道浅克隆官方仓库（已完成，落盘 `D:\refs\PentAGI`）。
**失败证据**：仅网络层直连失败（与 2.1 同根因，Connection was reset），代理通道下无失败。
**替代方案**：无需（官方活跃开源，首选拉取即成功）。

### 2.3 Cairn（裁决预期：可拉取，须实测确认）

**官方渠道拉取**：无需拉取——本地资产实测健康：
```
git -C D:\refs\Cairn rev-parse HEAD
→ 2ae4eef654e99e5d84de43b72e7dc65247c18bf1
git -C D:\refs\Cairn log -1 --format="%ci %s"
→ 2026-10-29 00:01:32 +0800 Merge pull request #125: preserve neighbor snapshots and human edits after graph changes
git -C D:\refs\Cairn status --short
→ （无输出，工作区干净）
```
仓库结构实测：Go 项目（core / service / build / deploy / graph-viewer / e2e 等）。

**依赖检测与补全**：未实测（不适用）——未部署运行，纯只读源码分析。
**端口绑定核验**：未实测（未部署）；design 阶段约束登记：仅绑回环。
**重启背景登记**：2026-11-08 退役归档、本单由用户重启（spec 5.4.1-5）；重新接入方式待附录 A-2 裁决（暂挂）。
**成功路径**：既存资产验证通过。
**失败证据**：无。
**替代方案**：无需。

## 3. 卡点 2：模型解耦评估（《模型解耦评估》，对应 G-PC2）

### 3.1 框架模型调用耦合点盘点（D:\refs 只读 grep 实测留痕）

**PentAGI**（证据文件:行）：
- 配置面：`.env.example:76-77`（`OPEN_AI_KEY`/`OPEN_AI_SERVER_URL`）、`:79-80`（`ANTHROPIC_API_KEY`/`ANTHROPIC_SERVER_URL`）、`:94-141`（GEMINI/BEDROCK/DEEPSEEK/GLM/KIMI/QWEN/MINIMAX/MISTRAL/XAI 九组厂商 provider）、`:144-154`（**Custom：`LLM_SERVER_URL`/`LLM_SERVER_KEY`/`LLM_SERVER_MODEL`/`LLM_SERVER_PROVIDER`/`LLM_SERVER_API_TYPE`(azure|azure_ad)**——任意 OpenAI 兼容端点）、`:156-165`（Ollama 本地 `http://ollama-server:11434`）、`:167-174`（`EMBEDDING_URL`/`_KEY`/`_MODEL`/`_PROVIDER` 独立可配）、`:207-209`（`PROXY_URL`：注释原文"HTTP proxy for every backend LLM, embedding, search and update-check call (local endpoints included)"）、`:381-382`（`LLM_FALLBACK_PROVIDER`）。
- 注入单点：`backend/pkg/config/config.go:99-137` 全部 provider env 经 `env:` tag 注入（`config.go:100-101` 默认 `https://api.openai.com/v1`）。
- 调用初始化集中：`backend/pkg/providers/providers.go` ProviderController 接口（`NewFlowProvider / NewAssistantProvider / Embedder() / GetProvider`）；`providers.go:210-212` custom provider 校验（"LLM_SERVER_URL is set but LLM_SERVER_KEY is empty" → warning）；`backend/pkg/providers/provider/provider.go:31` 注释"Custom fronts behind LLM_SERVER_URL"。
- 安装向导同收敛到同名 env：`backend/cmd/installer/wizard/controller/controller.go:154-156、338-342、538-570`。
- grep `OPEN_AI_KEY|LLM_SERVER_URL|ANTHROPIC_API_KEY` 于 backend/*.go 共 39 处命中，全部位于 config 定义/向导/校验，无业务代码硬编码云端 endpoint。

**Cairn**（证据文件:行）：
- 查询端零 LLM 复核（历史实证 2026-11-07"4/4 等价断言 PASS"复核**仍成立**）：`service/internal` 内 grep `anthropic\.New|openai\.New|NewLLM|LLMAnnotator|llm\.Client|NewAnthropic` → **No files found**；grep `cfg\.LLM|\.LLM\.` 仅命中 config 层三文件（`validator.go:82-87` provider 必填校验、`defaults.go:67-80` 默认值、`config.go:222-230` env 覆盖），均为配置装载非调用；源码自证注释：`service/internal/service/sentinel.go:6`"纯 CPU、零 LLM"、`knowledge_service.go:66`"纯 CPU、零 LLM"、`core/metrics/metrics.go:14`"绝不引入 embedding（R-no-embedding）"、`core/observe/diff.go:13`"零 LLM 零向量（R-ev-4）"。
- 构建端（索引/图谱构建）：LLM 客户端层 `build/internal/llm/`（`llm.go` Client 接口 + Config 支持 `anthropic | openai_compatible | anthropic_compatible | mock`；`factory.go` NewClient switch——**`case "mock": return NewMockClient()`，mock 为上游一等公民**；`mock.go` MockClient 线程安全确定性实现）；`build/cmd/cairnd/main.go:119-129` `--fake` 开关 → `runner.FakePRSummarizer{}`；调用点全部经单一工厂：`cairn-ingest/main.go:69`、`cairn-incremental/main.go:58`、`cairn-rebalance/main.go:62`、`build/internal/controller/runner/runner.go:109`；上游 e2e 自身已实证重定向可行：`build/test/e2e/real-build/main.go:139` 等用 `Provider:"openai_compatible"` + 自定义 `Endpoint`（`dkconfig.DeepSeekEndpoint`）。
- 配置面：`service/internal/config/config.go:60-68` LLMConfig（provider / api_key_env / model / **endpoint 自定义**）；env 覆盖 `CAIRN_LLM_API_KEY / CAIRN_LLM_PROVIDER / CAIRN_LLM_MODEL`（config.go:222-230）。
- 并发面：`core/parallel/parallel.go:15` `MaxConcurrency = 300`（全局 LLM 并发上限单点）。
- embedding：全仓库无 embedding 调用实现，R-no-embedding 为源码铁律。

**ARTEX**（顺带实测，供 design 参考）：
- `.env.example:10-15`：`ANTHROPIC_API_KEY / OPENAI_API_KEY / ARTEX_LLM_PROVIDER / ARTEX_LLM_MODEL / ARTEX_LLM_BASE_URL / ARTEX_LLM_PROXY`。
- `agent/provider.go:143-166`：`FromEnv()` 单点读取（注释明示 `ARTEX_LLM_BASE_URL = endpoint (optional)`、`ARTEX_LLM_PROXY = proxy URL (optional; http/https/socks5)`）。
- `config.example.json:2`："本文件仅含 database 与 skill_dir 两项；LLM 等其余配置走环境变量或应用内设置"。

### 3.2 拆模型层可行性结论

三框架均判定**可拆 = 适配层屏蔽方案（不删源码）**，解耦难度分级：**低（纯配置重定向）**：
- PentAGI：`LLM_SERVER_URL` 指向本地端点 + `LLM_SERVER_KEY` 任意非空值即启用 custom provider；调用面集中于 providers 工厂。
- Cairn：查询端天然零 LLM 零 embedding（无需拆）；构建端单一工厂 + 内置 `mock` provider + `Endpoint` 字段可配，上游 e2e 已有自定义 endpoint 实证。唯一实质约束：构建/索引阶段需真实推理才能产出图谱（mock 仅跑通流程），此为功能性问题而非耦合问题。
- ARTEX：`ARTEX_LLM_BASE_URL` 单 env 重定向，FromEnv 单入口。

### 3.3 码道模型接入方式（实测评估，不决策）

- 环境事实（如实记录）：本会话运行于 CodeArts Agent 平台，模型为 GLM-5.3-Flash（平台内置能力，随会话存在，不提供独立 HTTP 服务）。
- **方案 c 实测不可行**：`tool_search` 检索"本地模型端点 OpenAI 兼容 HTTP 服务 local model endpoint" → 命中 10 个工具（browser / analyzeImage / webfetch / uploadUserSkillToHuawei / cronCreate / security_scan / hmosDeviceUI / hmosDevice / hmosTestLedger / skillSearch），**无任何"本地模型服务端点"类工具**——平台未提供可被外部框架 HTTP 调用的本地模型端点（未虚构端点存在）。
- 三方案对比（每项标注：推理来源 / 公网外连风险 / 改造量 / 与"模型只规划不直控执行靠回执"底座原则契合度）：

| 方案 | 内容 | 推理来源 | 公网外连风险 | 改造量 | 契合度 |
| --- | --- | --- | --- | --- | --- |
| a：框架剥离 LLM 调用 | 配置屏蔽/mock，调度决策由码道智能体承担，框架只做状态记录与回执 | 码道平台内置模型 | **零外连** | 低~中（Cairn `--fake` 原生；ARTEX FromEnv 置空旁路；PentAGI custom 绑哑端点+回执补决策） | **最高**（完全符合回执模式） |
| b：本地 OpenAI 兼容 mock 服务 | 绑 127.0.0.1 返回确定性响应 | 无真实推理 | **零外连**（回环） | 低（三框架均原生支持自定义 endpoint/内置 mock） | 中（跑通流程与回执链路，规划零贡献） |
| c：平台模型端点直连 | —— | 平台端点 | —— | —— | —— **不可行（实测证据见上）** |

- 每框架结论行：ARTEX=可解耦（低），建议 a（必要时叠加 b 验证回执链路），公网外连风险低；PentAGI=可解耦（低），建议 b 为主 + a 回执补足，公网外连风险中（默认 env 指向云端 API，且 search/scraper/graphiti 子栈各有外连面，须逐项显式绑本地或禁用）；Cairn=可解耦（低，原生最友好），建议 a/b 均可，公网外连风险低（查询端零外连；构建端 Endpoint 可绑回环）。
- 最终改造决策权在用户，本报告仅呈可行性。

### 3.4 公网模型外连风险核验

- 本阶段为静态评估（未部署运行，无流量产生）：无 Wireshark 抓包证据可登记；抓包证明属《模型解耦方案》交付物（spec 5.3.1-8），随该方案交付时执行，届时对齐 J2 公网 IP=0、J3 异常外连=0（spec 5.7.1-3）。
- 静态判定（源码证据）：ARTEX=低（`ARTEX_LLM_BASE_URL` 绑 127.0.0.1 / `ARTEX_LLM_PROXY` 显式控向即消除）；PentAGI=中（`.env.example` 默认值 `https://api.openai.com/v1` 等云端 endpoint 必须显式改绑本地/置空）；Cairn=低（查询端零外连；构建端 Endpoint 可绑回环）。

### 3.5 结论

三框架模型调用面均为**低耦合、可配置重定向**，拆模型层可行（适配层屏蔽，不删源码）；方案 c 不可行（实测）；建议方向 a/b 组合，与"回执模式"底座原则契合；待用户裁决后进 design。

## 4. G-PC 门禁状态

| 门禁 | 状态 | 说明 |
|---|---|---|
| G-PC1 拉取可行性核验 | **实测完成，待用户审阅** | 第 2 节 ARTEX/PentAGI/Cairn 实测项已全部填充并留证据（v1.0）；提交用户审阅 |
| G-PC2 模型解耦评估核验 | **评估完成，待用户审阅** | 第 3 节耦合点盘点/拆层可行性/接入方式/外连风险已填充（3.4 抓包证明项留待《模型解耦方案》交付）；提交用户审阅 |
| G-PC3 design 放行 | 已放行【用户裁决 2026-11-12】 | 用户审阅本报告后明确放行，并裁决两项：① ARTEX 采用社区续维护版 RuoJi6/ARTEX（获取路径 A 定案）；② 模型解耦采用方案 a（回执模式：码道智能体承担决策，框架只负责调度与工具调用，不直连外部模型）。放行范围=进入 design 阶段；先学后干门禁（spec 5.2）未取消，作为编码/部署执行阶段的前置门禁继续生效；附录 A（A-1~A-4）维持暂挂 | |

## 5. 审阅记录

- 提交状态：实测填充完成（v1.0，2026-11-12），待提交用户审阅
- 用户审阅结论：已审阅通过并放行 G-PC3【用户裁决 2026-11-12】；裁决两项：ARTEX=RuoJi6/ARTEX 社区续维护版；模型解耦=方案 a 回执模式
- 驳回记录：无

## 附录 实测产物清单

| 路径 | 内容 | 证据 |
| --- | --- | --- |
| `D:\refs\ARTEX` | RuoJi6/ARTEX 浅克隆（HEAD=73d5437c5a64559ed803bcd096d2a0a0014a1214，2026-11-11） | git rev-parse / log 实测 |
| `D:\refs\PentAGI` | vxcontrol/pentagi 浅克隆（HEAD=cffed9485aa1cca70762cd08a57ac62a80406258，2026-10-23） | git rev-parse / log 实测 |
| `D:\refs\Cairn` | 既存资产（HEAD=2ae4eef654e99e5d84de43b72e7dc65247c18bf1，工作区干净） | git rev-parse / status 实测 |
| `D:\refs\_artex_agent.json` / `_pentagi.json` / `_autumn27_artex.json` / `_artex_forks.json` | api.github.com 原始响应留存 | curl.exe 落盘 |

（完）