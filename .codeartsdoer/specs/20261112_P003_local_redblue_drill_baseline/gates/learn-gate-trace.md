# G0 学习门禁留痕：学习材料清单（L1~L4）+ 材料三查（learn-gate-trace.md）

> 任务：0.1 编制学习材料清单（L1~L4）+ learn-gate 材料三查；产出物落位 spec 0.1 涉及路径 `gates/learn-gate-trace.md`
> 编制日期：2026-11-12（检索执行日）；执行代理：学习研读代理（P003 G0 任务 0.1/0.2）
> 网络纪律执行记录：api.github.com 直连可用；CCTV（news.cctv.com/search.cctv.com）、CNCERT（cert.org.cn）、网信办（cac.gov.cn）、西工大新闻站直连可用；Bing/360/搜狗 SERP 反爬污染不采信；Wikipedia/BBC/DOJ/Krebs/Talos/公安部（mps.gov.cn 521）直连不可达未采信；webfetch 平台通道对境外站点同样不可达（实测 `Unable to connect`）；按用户裁决 A-1 全程未使用代理通道。

## 1. L1 三大框架官方文档（离线研读，本地仓库文档为准）

| # | 材料 | 出处（本地文件路径 / 公开 URL） | 用途 |
|---|---|---|---|
| L1-1 | ARTEX README（架构章：双图/事件驱动闭环/worker trace 交换/共享 todolist/审批门/LLM env/部署五法/许可与免责） | `D:\refs\ARTEX\README.md`（640 行全文研读；上游 https://github.com/RuoJi6/ARTEX ，AGPL-3.0） | 框架定位/双图/子代理指挥所/模型依赖/部署要点 |
| L1-2 | ARTEX 漏洞多流量证据设计文档 | `D:\refs\ARTEX\docs\漏洞流量证据.md`（99 行全文） | 证据链/流量绑定/审计导出设计 |
| L1-3 | ARTEX Jev/System One 拦截裁判接入核验 | `D:\refs\ARTEX\docs\jev-integration-review.md`（25 行全文） | 审批裁决外部化设计参考 |
| L1-4 | ARTEX traffic 包源码头注释 | `D:\refs\ARTEX\traffic\traffic.go:1-5`（实测 rg/直读核验） | traffic=请求记录子系统（go-mitmproxy 嵌入、全量明文留痕、SQLite sidecar）；**无"伪装/心跳"原生语义**（spec R7 中"HTTPS 伪装+加密心跳"为演练侧衍生用法，非 ARTEX 原生功能，已在笔记中区分） |
| L1-5 | PentAGI README（Overview/Features/Capability Boundaries/Architecture/Agent Supervision 473-541/Docker Access 683-707/安装配置） | `D:\refs\PentAGI\README.md`（4247 行，定点研读 1-120/102-281/477-586/683-712；上游 https://github.com/vxcontrol/pentagi ） | 框架定位/多角色分工/沙箱执行/模型依赖/外连面 |
| L1-6 | PentAGI 模型解耦耦合点实测证据 | `.codeartsdoer/specs/20261112_P003_local_redblue_drill_baseline/pre_check.md` 3.1~3.5（`.env.example`/`config.go` 行级证据） | 模型依赖点（本单已有 G-PC2 实测，笔记直接引用不重复实测） |
| L1-7 | Cairn（xcosmosbox）README | `D:\refs\Cairn\README.md`（273 行全文；上游 https://github.com/xcosmosbox/Cairn ，MIT） | 知识图谱构建端/查询端分离/mock provider 设计 |
| L1-8 | Cairn（oritera）README | 公开 URL https://github.com/oritera/Cairn 经 `api.github.com/repos/oritera/Cairn/readme`（Accept: application/vnd.github.raw）2026-11-12 直取存 `$env:TEMP\oritera_cairn_readme.md`（205 行） | **黑板架构 Fact/Intent/Hint 真实出处**（ARTEX README:599 引用的参考项目） |

### L1 材料三查

| 材料 | 质量（官方背书/引用度/活跃度） | 相关性（与本地攻防演练匹配） | 保真度（真实出处可回查） | 结论 |
|---|---|---|---|---|
| L1-1~L1-4 ARTEX | RuoJi6/ARTEX 为原仓库（Autumn-27，2026-11 实测 404 闭源）社区续维护版：1760 stars/1024 forks/AGPL-3.0/2026-11-11 仍在 push；百度"agent+"攻防挑战赛冠军项目（多个历史快照仓库描述一致佐证，pre_check.md 2.1 已登记） | 高：双图/子代理指挥所/traffic 记录代理/审批门即本单 G1~G8 直接对象 | 高：本地文件路径逐行可回查；git HEAD=73d5437 已登记 | **采信** |
| L1-5/L1-6 PentAGI | vxcontrol/pentagi 官方仓库：33981 stars/2026-10-23 最后提交/2026-10-05 发 v2.2.0；README 含官方能力边界声明（维护活跃且声明严谨） | 高：沙箱执行/外连面清单/模型 provider 解耦即本单 2.2/2.5/2.6 直接对象 | 高：本地文件行级可回查 + pre_check 实测命令留痕 | **采信** |
| L1-7 Cairn（xcosmosbox） | MIT，2026-10-29 最后提交，官方 README+configs 完整 | **中低：经 git 历史与全库 grep 核验，该仓库无"黑板机制 Fact/Intent/Hint"**（blackboard 零命中；fact/intent/hint 仅 2 处普通注释词）；实为 Skill 文档知识图谱工具 | 高（本地可回查），但**与 spec"L1 三仓库含黑板机制 Cairn"的预期不符——同名混淆** | **剔除其"黑板机制"用途**；降级登记为同名不同项目参考（其"构建端 LLM 提议/查询端零 LLM/mock 一等公民"设计与本单回执模式仍有弱相关，笔记如实区分） |
| L1-8 Cairn（oritera） | AGPL-3.0，5075 stars/993 forks（api.github.com 实测）；README 自述腾讯云 Hackathon AI 渗透挑战赛第 2 期 610 队 1345 人、唯一 AK（54/54）、决赛第 3；ARTEX README:599 官方引用 | 高：黑板架构/Fact-Intent-Hint/OODA/Stigmergy 正是 spec 与 tasks 语境所指机制；worker 后端复用 Claude Code/Codex/Pi CLI 与本单方案 a（码道智能体承担决策）同构 | 高：api.github.com 原始 JSON+README 全文已落盘临时文件，URL 与检索日期已标注 | **采信**（替代 L1-7 承载黑板机制学习内容） |

**L1 剔除留痕**：D:\refs\Cairn（xcosmosbox/Cairn）从"黑板机制官方文档"用途中剔除——判定依据为 git log --grep blackboard 零命中、git grep blackboard@HEAD 零命中、README 全文无黑板机制（2026-11-12 实测）。剔除不删文件，降级为同名参考。

## 2. L2 真实案例正例（官方通报/主流媒体公开报道）

| # | 材料 | 出处 | 检索方式 |
|---|---|---|---|
| L2-1 | 西北工业大学遭美国 NSA 网络攻击事件：校方声明+警情通报+调查报告发布+系列披露（四篇） | 央视网（新闻频道）四篇正文全文已取：① 2022-06-22 https://news.cctv.com/2022/06/22/ARTI9bPFX4Oi1YE9CiFY8h7t220622.shtml ② 2022-09-05 https://news.cctv.com/2022/09/05/ARTIDV9zd9FdH8Lj1SkFByls220905.shtml ③ 2022-09-05 https://news.cctv.com/2022/09/05/ARTIwaNJzj7fyUaKMDrKYKwl220905.shtml ④ 2022-09-27 https://news.cctv.com/2022/09/27/ARTI1YjUCAzciKAsNQsy1Rxd220927.shtml | search.cctv.com 站内搜索直取（2026-11-12） |
| L2-2 | 国家授时中心遭美国 NSA 网络攻击事件技术分析报告（国家安全机关 2025-10-19 披露，CNCERT 溯源） | 央视网 2025-10-19：https://news.cctv.com/2025/10/19/ARTIG1WFMxk7uWacFF6rbEvA251019.shtml（正文全文已取） | 同上 |

### L2 材料三查

- **质量**：西工大事件=西安市公安机关立案、CNCERT/国家计算机病毒应急处理中心与 360 联合技术团队发布调查报告，央视网（中央主流媒体）刊发；授时中心事件=国家安全机关披露+CNCERT 发布技术细节，央视网刊发。官方背书充分。
- **相关性**：两案要点覆盖 spec 所列"路由出入口控制（邮件/手机入口）/内网潜伏（消痕/DLL 劫持/日志替换）/跳板特征（多级跳板/匿名节点/加密隧道）"全部关键词。
- **保真度**：四篇+一篇 URL 均为可回查的央视网公开页面，2026-11-12 实测直取正文，无二手转述失真。
- **结论**：L2-1/L2-2 均**采信**；无剔除。

## 3. L3 真实案例反例（业余攻击者暴露特征→落网/被检出的公开复盘）

| # | 材料 | 出处 | 检索方式 |
|---|---|---|---|
| L3-1 | 《"群发神器"沦为犯罪帮凶 网警揭秘黑客案件》（吕某扫描挂马案+袁某僵尸账号案，双案例） | 央视网 2025-12-04：https://news.cctv.com/2025/12/04/ARTIr2ceGxPeIiIRbHCYREBc251204.shtml（正文全文已取） | search.cctv.com 搜"黑客"（2026-11-12） |
| L3-2 | 《涉案超1.2亿元 4个黑客犯罪团伙落网》（黑产工具销售运营 15 人+开发者 2 人落网） | 央视网 2024-10-30：https://news.cctv.com/2024/10/30/ARTIVuibpb4wufnwc24XgGkW241030.shtml（正文摘要已取） | search.cctv.com 搜"黑客 落网" |

### L3 材料三查

- **质量**：两篇均为央视网新闻频道刊发的网警办案披露（主流媒体公开报道+警方通报性质）；涉案罪名（非法控制计算机信息系统罪）、强制措施、涉案金额均为官方口径。
- **相关性**：反例要点完整——为什么会暴露（暗链即时触发监测/软件数字指纹/工具物证留存/资金与生活侧信道）→如何被检测（网警巡检+指纹溯源+关联预警）。
- **保真度**：URL 可回查，正文直取未转述。
- **结论**：L3-1/L3-2 均**采信**；无剔除。
- **检索受限登记**：公安部 mps.gov.cn（HTTP 521）、裁判文书网（登录+JS 渲染）不可直取；国际 OPSEC 失败案例（Mirai 作者 DOJ 认罪、Lapsus$ 落网等）因境外源（justice.gov/bbc.com/en.wikipedia.org/krebsonsecurity.com）直连全部被重置且 webfetch 平台通道同样不可达，未采信任何细节、不编造——本单 L3 以国内官方公开报道承载，够用。

## 4. L4 近 3 个月（2026-08~2026-11）AI 攻防编排框架使用调研（仅公开合法来源）

| # | 材料 | 出处 | 检索日期 |
|---|---|---|---|
| L4-1 | PentAGI release 动态（v2.2.0@2026-10-05 等 5 个 tag）+ README 官方能力边界声明 + trendshift 徽章自述 | api.github.com `repos/vxcontrol/pentagi/releases?per_page=5` 实测；`D:\refs\PentAGI\README.md`（本地克隆 HEAD=cffed948） | 2026-11-12 |
| L4-2 | RuoJi6/ARTEX release 动态（近 3 个月连发 v0.3.25~v0.3.29）+ fork 镜像同步证据 | api.github.com `repos/RuoJi6/ARTEX/releases?per_page=5` 实测；pre_check.md 2.1（forks JSON 留存 D:\refs\_artex_forks.json） | 2026-11-12 |
| L4-3 | oritera/Cairn 生态指标（stars=5075/forks=993/created 2026-04-19/pushed 2026-09-07/无近三月 release）+ ARTEX README 官方引用关系 | api.github.com `repos/oritera/Cairn` 实测；`D:\refs\ARTEX\README.md:599` | 2026-11-12 |
| L4-4 | xcosmosbox/Cairn 活跃度（2026-10-29 最后提交，协作看板模式） | pre_check.md 2.3（本地克隆 HEAD=2ae4eef）；`D:\refs\Cairn\README.md`（issue #7/#9 看板入口） | 2026-11-12 |
| L4-5 | ARTEX v0.3.25 后接入 Jev/System One 拦截裁判（版本功能动态） | `D:\refs\ARTEX\docs\jev-integration-review.md`（核验日期 2026-11-03，自述"历史 v0.3.25 不含 Jev 接入"） | 2026-11-12 |

### L4 材料三查

- **质量**：全部为一手数据（api.github.com 原始 JSON / 官方仓库文档原文），非媒体二手转述。
- **相关性**：直接回答"三框架近三月是否活跃、向什么方向演进、与本单回执模式的契合度"。
- **保真度**：每条标注检索日期与 API 端点/本地文件路径，可回查。
- **结论**：L4-1~L4-5 均**采信**；无剔除。
- **未决登记**：oritera/Cairn README 引用的两篇微信公众号复盘文章（mp.weixin.qq.com 链接，README"Further Reading"节）——微信链接需 JS 环境，本机 curl 直连受限，**正文细节未采信、不转述**，仅登记链接存在；列为未决项 1。

## 5. 剔除/未决汇总

| 编号 | 事项 | 性质 | 处置 |
|---|---|---|---|
| 剔除-1 | D:\refs\Cairn（xcosmosbox/Cairn）"黑板机制官方文档"用途 | 保真度不符（同名混淆：知识图谱工具≠黑板架构 Cairn） | 从该用途剔除并留痕（本文件 §1）；改采 oritera/Cairn 承载；原仓库降级为同名参考；三份学习成果笔记中如实区分两个 Cairn |
| 未决-1 | oritera/Cairn 微信复盘文章正文 | 渠道受限 | 登记链接存在，正文未采信；后续如获用户裁决开放渠道再补研 |
| 未决-2 | 国际 OPSEC 失败公开复盘（DOJ/BBC/Krebs/Talos） | 网络不可达（直连重置+webfetch 不通） | 不编造；L3 由国内官方公开报道承载 |
| 未决-3 | "国家授时中心"为 tasks.md 0.1 预置候选，已核实命中（2025-10-19 官方通报） | 已闭环 | 采信 L2-2，非未决 |

## 6. 三查总结论（一行）

L1 采信 8 条/剔除 1 条用途（xcosmosbox Cairn 黑板用途，改采 oritera Cairn）；L2 采信 2 条/剔除 0；L3 采信 2 条/剔除 0；L4 采信 5 条/剔除 0；未决 2 项（微信复盘正文、国际 OPSEC 复盘，均因渠道受限如实登记，不影响门禁材料四类俱全）。

## 7. 放行判定（0.5，learn-gate 门禁终判）

> 判定时间：2026-11-12｜判定者=主智能体｜依据=spec 5.2.1-1/4/5（四环留痕链任一环缺失即判门禁违规）

| 环 | 任务 | 核验证据 | 结论 |
|---|---|---|---|
| ①学习 | 0.1 材料清单+三查 | 本文件 §1~§6（L1 采信8剔1/L2×2/L3×2/L4×5，未决2项如实登记） | ✅ |
| ②落盘 | 0.2 三份成果 | notes/学习成果-三大框架官方文档.md（23,346 B）+学习成果-真实案例正反例.md（16,085 B）+学习成果-攻防框架近三月使用调研.md（15,404 B），实测存在非空 | ✅ |
| ③登记 | 0.3 知识库索引 | notes/知识库索引.md 笔记层三行已登记+变更日志行追加（2026-11-12） | ✅ |
| ④考核 | 0.4 R1 轮 | exam/R1/ 四件套（questions 4,340 B/key 8,281 B/answers 10,003 B/review-report 6,197 B）+events E1~E4 链完整（两处拼接缺陷拆行修复留痕）；PASS×5/PARTIAL×0/FAIL×0，总分 100/100，综合自信度 100%≥80%，批改官独立判"放行" | ✅ |

**放行判定=通过**：四环完整，learn-gate 门禁放行，开放 G1~G8 执行（spec 5.2.1-1）。
范围注记：考核与学习范围不含 oritera（用户方案 D 裁决，tasks.md 头部注记）；本判定记录经 H7 联动刷新 notes/项目事实表.md。

（完）