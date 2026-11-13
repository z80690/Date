# G3.5 演练适配层实现留痕（gates/g35-adapter-trace.md）

> 承接 tasks.md 3.5（spec 1.4-2、4.2-1、4.3.2-1/2/3、4.3.3-1/2、4.4-2、5.5.1-7、5.7.1-3；design IF-1~IF-10、A/B/C/D 模块）｜实现时间：2026-11-13｜执行者=主智能体（用户指令：写不完不许停）

## 1. 交付物清单（adapter/，contract v1，纯 stdlib 零第三方依赖）

| 文件 | 承接契约 | 要点 |
|---|---|---|
| adapter/errors.py | 全部异常映射 | ErrorCode StrEnum 20 项（与 design 2.2.2 逐条对应）+AdapterException(code, message, detail) |
| adapter/models.py | IF-1~IF-10 载荷 | DrillAction/TriggerKind（二值）/CheckContext/RoundState/StepState 枚举+TaskHandle/ReceiptAck/CheckResult/StopResult/Listener/BindAuditResult/AliveResult/CaptureResult/StepRecord dataclass |
| adapter/config.py | 启动护栏 | whitelist.json 加载（缺失/损坏→阻断）+temp/p003_drill/ 目录布局（spec 6.4-1） |
| adapter/whitelist.py | **IF-3** | W1~W5 集合匹配；**仅接受 IP 字面量**（主机名会触发 DNS 外发查询→直接拒绝）；deny_log.jsonl 拦截留痕（deny_log_id 可回查）；assert_loadable 启动护栏（E_WL_CONFIG_MISSING） |
| adapter/boundary.py | **IF-4** | 全局阻断开关：越界事件→停+禁外发+awaiting_user；已建立连接→E_BLOCK_FAILED 升级呈报；reset 仅限用户裁决释放 |
| adapter/portaudit.py | **IF-5** | tasklist+netstat -ano（artex/cairn PID 过滤）+docker ps（pentagi 端口映射）；0.0.0.0/::/公网→E_BIND_NON_LOOPBACK 阻断+留痕；cairn stdio 零端口天然合规 |
| adapter/proxycheck.py | **IF-6** | DevSidecar/tor/obfs4proxy 进程存活检测；存活→E_PROXY_STOP_FAILED 阻断启动（只核验不删除，A-1 口径） |
| adapter/receipt.py | **IF-1/IF-2 核心** | DrillEngine 状态机：dispatch 校验链（round running→boundary 未触发→IF-3→action→框架就绪 FRAMEWORK_READY）→受理；receipt 驱动迁移（success 全完→VERDICT_PENDING；failed→ROUND_FAILED）；Fact 登记 evidence 流（Cairn MCP 由智能体侧按引用登记） |
| adapter/gate.py | IF-7 | L1~L4 证据文件+知识库索引登记+考核放行留痕链核验（缺失→E_KB_NOT_REGISTERED） |
| adapter/capture.py | **IF-8** | dumpcap 会话 start/stop/health_check；health_check 仅随回执事件（无定时循环）；中断→E_CAPTURE_BROKEN 整轮无效 |
| adapter/verdict.py | **IF-9** | verdict_from_counts 纯判定函数（J1~J5 量化：全 0+伪装有效→hidden_success；任一命中→hidden_failure 列失败项；证据缺→evidence_insufficient）+collect_evidence（tshark display filter 采集，缺工具→E_EVIDENCE_MISSING 不造数） |
| adapter/pairing.py | **IF-10** | 步骤配对：capture_ref+audit_ref 缺一→E_PAIR_MISSING；特征分析+防御检测方法缺→E_DEFENSE_PAIR_ABSENT |
| adapter/storage.py | 留痕底座 | JSONL 流（dispatches/receipts/deny_log/boundary/captures/verdicts/pairings/gate/portaudit/proxycheck）落 temp/p003_drill/audit/（.gitignore 排除区） |
| adapter/whitelist.json | W1~W5 | W1=127.0.0.0/8、W2=::1、**W3=192.168.16.0/20**（env-ready-trace 实测值）、W4/W5=空集（禁自动发现；W5 待 DVWA GitHub 源码部署后登记）——任何变更须用户拍板 |
| pyproject.toml | Ruff 门禁 | ruff 0.17.2：line-length 100 + select E/F/W/I/UP/B；pytest testpaths |
| tests/test_adapter.py | T1/T2/T3/T5/T8/T10/T11 | 20 个用例（tmp_path 隔离证据目录，不污染真实审计流） |

## 2. 门禁结果

- **Ruff（0.17.2）**：`ruff check adapter/ tests/` → **All checks passed!**（E501 长行 26 处迭代修复：ruff --fix 18 处+手动拆行 8 处）
- **pytest**：`python -m pytest tests/test_adapter.py` → **20/20 PASSED**（T1 白名单内放行/外拒绝+拦截日志、T2 回执状态机+空结论/未知句柄拒绝、T3 端口合规判定矩阵、T5 触发二值、T8 越界即停+已建连接升级、T10 配对三态、T11 代理存活、IF-9 判定三结论+缺证据拒绝）——sessionfinish 的 PermissionError 为 pytest 临时目录清理的 Windows 噪音，与测试结果无关（FSM 判定 PASS）
- 【验证方式】两命令可复放：`ruff check adapter/ tests/`+`python -m pytest tests/test_adapter.py -q`

## 3. 设计决策登记（结论+理由）

1. **仅 IP 字面量过 IF-3**：解析主机名本身会发出 DNS 查询（可能外发）——直接拒绝保守合规。
2. **纯 stdlib 零依赖**：端口/进程核验走 Windows 官方命令（netstat/tasklist/docker ps）子进程——避免第三方依赖风险，Ruff 最简。
3. **FRAMEWORK_READY 与 deploy-selfcheck 同源**：pentagi=False（镜像暂缓）、artex/cairn=True——部署状态变更时单点更新。
4. **verdict 两层设计**：纯判定函数（可单测）+证据采集（tshark 子进程，缺失即 insufficient）——不虚构任何计数。
5. **留痕即证据**：全部接口操作落 JSONL（temp/p003_drill/audit/）——IF-9/IF-10 的直接数据源，回查可复放。

## 4. 未尽事项

- IF-11~IF-15（报告/知识库登记/事实表/重置/待裁决登记）属 G6/G7 组承接，本组未实现（tasks.md G3.5 范围=IF-1~IF-10+D2 对接 ✅）。
- collect_evidence 的 tshark 实测路径待 Wireshark 装毕后 G4 首轮演练实跑验证（单元测试覆盖判定逻辑，tshark 路径为真实环境集成项）。
- W5 登记待 DVWA GitHub 源码方案部署形态确定（3.2 续）。

（完）