# G2.1 Cairn 部署与模型解耦留痕（gates/deploy-trace-cairn.md）

> 承接 tasks.md 2.1（spec 5.3.1-6、4.3.2-3、5.4.1-1；design M1-1/M2-3）｜执行时间：2026-11-12｜执行者=主智能体
> 方案 D 裁决口径：Cairn=xcosmosbox/Cairn 本地版经 MCP 接入（A-2 终定），oritera 不采用。

## 1. 资产与形态

| 项 | 值 | 证据 |
|---|---|---|
| 来源 | xcosmosbox/Cairn（D:\refs\Cairn，HEAD=2ae4eef，**原仓库只读不动**） | git rev-parse 2026-11-07 留痕+pre_check §4 |
| 运行副本 | D:\refs\Cairn-build（robocopy /E /XD .git，源码级修复在此进行，原仓库零改动） | robocopy exit 1（正常复制） |
| 构建产物 | bin\cairn-mcp.exe（17,012,736 B，2026-11-12 20:57）+bin\cairn-ingest.exe | go build 实测 |
| 接入形态 | **MCP（stdio 传输）**——cairn-mcp --config 拉起，智能体直接调用；CLI 形态弃用（A-2） | stdio 冒烟 EXIT=0 |
| 监听核验（IF-5） | stdio 传输=**零网络端口**（stdin/stdout JSON-RPC），天然仅回环合规；未启用 HTTP/SSE 模式（-listen 空） | main.go -listen 空=stdio |

## 2. 重大缺陷修复（本单对上游的实质 bug，可回馈上游）

- **现象**：cairn-mcp/cairn-ingest 在 Windows 打开任何 knowledge.db 报 `SQL logic error: out of memory (1)`（2026-11-07 旧构建与新构建皆复现；Python sqlite3 读同一文件正常）。
- **根因**（三分支探针定位）：core/storage/sqlite.go OpenSQLite 用 `url.URL{Scheme:"file", Path:filepath.ToSlash(abs)}` 构造 DSN——Windows 盘符路径 `C:/...` 被 Go URL.String() 生成 **`file://C:/...`（双斜杠，盘符落入 authority 位）**，modernc.org/sqlite 驱动对该形态报 OOM。
- **修复**（副本内）：Path 规范化 `"/" + strings.TrimPrefix(filepath.ToSlash(abs), "/")` → 生成 `file:///C:/...`（三斜杠）。
- **验证**：6 分支 DSN 探针全 OK（nodes=17）；修复版 cairn-mcp.exe stdio 冒烟：initialize 握手合法返回+`1 个知识库 loaded`（p003-drill）。
- **附带升级**：副本 modernc.org/sqlite v1.30.1→v1.34.4（go get 实测）；原仓库 go.mod 未动。

## 3. 模型解耦（方案 a 落位）

- **查询端零 LLM 铁律**：cairn-mcp 查询端只读、零 LLM、零 embedding（`make verify` 架构不变量，pre_check 3.1 实测）——本单查询端部署**天然零模型依赖**，无外连面（IF-5/J2/J3 口径满足）。
- **构建端 mock**：mock provider 为一等公民（build/internal/llm/factory.go:12-13 `case "mock"` 实测）；ingest CLI 实测**硬编码 openai_compatible**（build/cmd/cairn-ingest/main.go:70，CAIRN_LLM_PROVIDER env 不生效）——因此 ingest 的模型推理走 2.4 本地哑端点（OpenAI 兼容占位，绑 127.0.0.1:7810）。
- **禁 Ollama 核验**：配置链零 Ollama 端点（.env/无 ollama 引用，待 2.5 全局复核）。
- **知识库**：temp\cairn-p003.db（176,128 B，由上游 docs/coordination/.../knowledge.sql dump 经 Python sqlite3 重建，16 表含 nodes_fts5）；ingest 全量管线因 SQLite OOM 三次重试降级→P003 演练知识（三份学习成果）的图谱化蒸馏填充=**未决项**（路径：码道智能体承担蒸馏=方案 a，经哑端点回执或手工入库；不阻塞 MCP 服务就绪）。
- **源目录结构**：temp\cairn-kb-src\p003-drill-knowledge\{SKILL.md, references\×3}（扫描规则=SKILL.md 锚点+references/*.md，build/internal/discovery/scanner.go:22-45 实测）。

## 4. MCP 注册（codearts-platform-registration 契约）

- 注册文件：`.codeartsdoer/mcp/mcp_settings.json`（写前备份=mcp_settings.json.bak-20261112）。
- 条目：`cairn-mcp`：command=`D:\refs\Cairn-build\bin\cairn-mcp.exe`（绝对路径）+args=`["--config","C:\\...\\temp\\mcp-local.yaml"]`+env=`{}`（零凭据）。
- 第一层验证：PARSE=OK / CMD_EXISTS=True / **ENV_COUNT=0**（三项全过，2026-11-12）。
- **运行时可见性**：需新会话重载后经 listSkills/工具调用实证（会话边界登记，T3 先例）；stdio 冒烟（握手+KB 加载）已在本会话直接验证。

## 5. 验收对照

- spec 5.3.1-6（拆模型层，配置屏蔽不删源码）：✅ 副本修复+零源码删除；查询端天然零 LLM。
- spec 4.3.2-3（端口仅回环）：✅ stdio 零端口；未开 HTTP 监听。
- design M1-1（本地直跑形态）/M2-3（mock 一等公民复用）：✅。
- 【验证方式】stdio 握手 EXIT=0+KB loaded 回执可复放；IF-5 核验=零监听端口。

（完）