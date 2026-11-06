# ST1 准出证据汇编（kb_arch_foundation）

> 状态机 ST1（环境）准出证据集中登记处。迁移守卫依据：notes/阶段状态机运行规则.md §2。最后核验：2026-11-07。

## 1. Cairn 构建与验证（tasks 6.1–6.3）

| 项 | 结果 | 证据 |
|----|------|------|
| 6.1 诊断 | Go 1.26.5 ✓、GNU Make 4.4.1 ✓、Makefile 在库（make all=download→build 8 二进制→verify） | 诊断命令留痕 |
| 6.2 构建 | `make all`：go mod download ✓ → **build 成功（bin/ 8 个二进制：cairn/cairn-mcp/cairnd/cairnctl/cairn-ingest/cairn-incremental/cairn-rebalance/cairn-evolve）** | %TEMP%\cairn-build.log |
| 6.3 verify | go vet ✓ + binaries ✓；**check-invariants 步骤失败**（Windows make 的 sh -c 多行引号解析缺陷，原文："\: -c: line 2: unexpected EOF while looking for matching\"") → **修复=PowerShell 逐条等价执行 4 查**（扫描 75 个生产 Go 文件）：①ResolveLatest 有调用点（2 处）✓ ②查询端零 LLM ✓ ③零 embedding/faiss/hnsw ✓ ④查询端只读（0 写入调用）✓ ——语义与 Makefile 110 行起的 grep 断言逐条等价，差异=执行载体（make/sh→PowerShell），原因与过程留痕本文件 | 本文件+cairn-build.log |
| 6.4 接入 | cairn-mcp 可执行（exit 0，stdio 服务无 --help 输出属正常）；**cairn CLI 备用路线实证可用**（find/impact/status/sentinel/why/timeline/show 7 子命令，exit 0）；MCP 平台注册（写 mcp_settings.json）属配置实施→留待 ST5（门禁二后）；主备择一可用原则已满足（CLI 先行可用）；Windows 兼容修复：Makefile 产物无 .exe 后缀→复制 cairn-mcp.exe/cairn.exe 副本（bin/ 产物后处理，未改源码） | 本文件 |
| 6.5 蒸馏 | cairnd 轮询守护进程**弃用不运行**（与禁定时任务冲突）；蒸馏更新=文档变更事件触发 cairn-incremental 单次命令、全量重建=cairn-ingest | 本文件 |
| 6.6 嵌套核查 | 无 .gitmodules；项目 git ls-files 63 文件零 refs/Cairn/p3c/deepseek 污染；Cairn/Super-agent 的 .git 原样 | 核查命令留痕 |

## 2. Super-agent 实证登记（tasks 7.1–7.3）

| 项 | 结果 | 证据 |
|----|------|------|
| 7.1 七层职责 | **实读 docs/zh/architecture.md 全文相符**：Channel（入站/出站适配）→Ingress（Fast/Slow→Thread key）→Engine（路由批处理/Thread/Eval/Ticket/Assignment）→Harness（Session/异步 ReAct/模型/工具/daemon）→Store（SQLite/Spill/read_object）→Env（沙箱目录与进程）→Watchdog（看卡住的 Worker）；Router=序点（入站走 Engine 出站走 Router）、Worker 拿执行工具做完向上汇报、Worker Session 不能直接回信道；bypass=subscription 跳过 Eval；公开来源=Super-agent 设计探索 §2–§6+deepseek-ai/dsh-superagent-prototype | refs/deepseek-super-agent/docs/zh/architecture.md（51 行全文） |
| 7.2 模型配置 9 处 | grep 实证 235 处命中（核心：src/harness/model.ts=createModelFromEnv/HttpOpenAI/MockModel；src/harness/providers.ts=resolveLiveApi/PROVIDER_PRESETS；src/memory/embedding.ts=HashedEmbedding；DS_AGENT_SLOW_PATH；gateway） | grep 留痕 |
| 剔除方案 | **零配置旁路**（源码实证）：createModelFromEnv({})→MockModel、resolveLiveApi({})→null、"Slow Path is off unless DS_AGENT_SLOW_PATH=model"——**不配置任何 DS_AGENT_*/OPENAI_*/DEEPSEEK_* 环境变量、不创建 gateway.config.json 即天然走确定性零模型路径**，无需改源码；#9 保留默认离线 HashedEmbedding；#6 Router=执行代理（平台模型）、Worker=平台 subagent（平台模型）；零 API key | src/harness/model.ts+providers.ts 实证 |
| 7.3 骨架保留 | Router（序点/分派/唯一对外汇报）/Worker（隔离会话、向上汇报）/triggers（Trigger 批处理）/Watchdog（旁挂监督）/审批分离——全部保留为架构参照与 ST5 编排对接基线；**平台模型端口=一切 LLM 调用唯一出口**登记为架构不变量（禁独立模型供应商配置） | architecture.md+design §2.2.2-IX |

## 3. P3C 验收（tasks 8.1–8.4）

| 项 | 结果 | 证据 |
|----|------|------|
| 8.1 拉取与构建【已完成待验收】 | refs\p3c 克隆 1 次成功；Maven 3.9.16 构建 p3c-pmd-2.1.1 BUILD SUCCESS（6:44）；官方测试 **214/214 全绿** | %TEMP%\p3c-test.log+事实表 |
| 8.2 .git 删除授权 | 仅限 refs/p3c（用户 2026-11-06 授权，2026-11-07 执行）；取舍=删后无法 git pull，更新须重新克隆；Cairn/Super-agent 的 .git 原样 | 事实表环境状态 |
| 8.3 样例审查 | **已验收（2026-11-07）**：审查命令=`java -cp "p3c-pmd\target\classes;p3c-pmd\target\dep\*" net.sourceforge.pmd.PMD -d p3c-sample -f text -R rulesets\java\ali-naming.xml`（规则集实存验证 ✓）；violation 报告原文：`SampleViolation.java:1:【badName】不符合 UpperCamelCase 命名风格`、`SampleViolation.java:4: 方法名【DoSomething】不符合 lowerCamelCase 命名风格`（exit 4=检出违规，与故意违规样例预期一致）；模型配置差异=P3C 天然零模型配置点（纯静态规约），与 Super-agent 9 处剔除的差异=前者零配置即满足、后者零配置旁路 | 本文件+审查命令留痕 |
| 8.4 版本实证 | JDK 17.0.20.1（MS OpenJDK）+Maven 3.9.16 构建 p3c-pmd-2.1.1 成功=实测匹配；凭据清单=零 API key/零账号/零模型配置；U13 关闭 | mvn -version/java -version 留痕 |

## 4. 未决事项状态（ST1 收口快照）

- U10 已收口（p3c 克隆达成）；U13 已收口（版本匹配实测）；U12 已收口（构建成功，唯一残损=make check-invariants 的 Windows sh 兼容缺陷，已用等价执行补验，非构建阻点）；U11 部分收口（MCP 服务可运行，平台注册待 ST5，CLI 备用可用）；U9 维持待用户澄清（hyra-results 记忆与磁盘不符）。