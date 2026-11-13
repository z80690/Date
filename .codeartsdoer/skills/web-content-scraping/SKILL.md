---
name: web-content-scraping
description: |-
  >-
    外部网页正文抓取与视频链接内容还原的降级路径与实测参数：webfetch 可能静默无输出、browser 工具无内容回读、桌面版 JS
    渲染空壳的判定特征、移动版域名+iPhone UA 降级命中；头条视频页 JS-VM 墙完整绕过链路（m 端
    SSR+RENDER_DATA 解码+点播 token 直取 720p 直链，vod.bytedanceapi.com 原样拼 token）、B 站同名 UP
    交叉调研（view API 确证 mid、按内容特征词搜索枚举、B 站分流 m4a 直接转写、课件截图帧定点抽帧）、GitHub 公开元数据检索评估
    （api.github.com 免登录、owner 纯数字陷阱、license
    NOASSERTION、评分机器自查三件套、条目数/禁替用户决策校验）、图片文字用 analyzeImage 补取；视频链接走 yt-dlp
    下载→ffmpeg 抽帧/抽音频→faster-whisper 转写+analyzeImage 字幕 OCR
    双源交叉还原（工具链装法、imageio-ffmpeg 定位、analyzeImage 批量与空输出回退策略在内），多视频并行处理须逐条传 workdir
    防产物落根目录，提炼入库走学习成果-*+知识库索引登记收尾；受限网络环境官方工具渠道探索（torproject 全域被墙证据链、官方镜像站探测、winget
    manifest InstallerUrl 预判下载可达性、**winget search 先行防手搓死循环**、官方生态项目 GitHub release
    直发取捆绑二进制、可疑仓库名实核验弃用、诊断验证禁落盘脚本、同症状连续失败 2 次换路）。凡涉及抓取外部网页/文章正文作为调研输入、官方通报/权威媒体时事新闻类联网调研（安全事件复盘/执法案例/框架动态）、同名开源仓库混淆核验、webfetch 无返回、HTML
    体积大但去脚本后无正文、用户给视频/短视频链接要求看内容或核对信息、yt-dlp 报 No video formats found、GitHub
    仓库元数据评估/选型对比报告、第三方仓库浅克隆源码分析（拉取可行性核实/依赖解耦评估/耦合点 grep）、多视频批量下载转写入库、受限网络下拉取官方工具/安装包渠道探索、装软件前查包管器时使用。
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

**⚠️ 引擎可用性随时效漂移，禁沿用历史结论（2026-11-12 复测实证）**：上表 2026-11-07 记录"360 可用"已失效——2026-11-12 复测 Bing（带 setmkt=zh-CN、count=20）、360、搜狗三家 SERP **全部被反爬污染**：返回无关缓存结果（如搜"西北工业大学 NSA"命中"西北地区"百科词条、搜执法案例命中招聘网站），无报错、体积正常、最易误当"无此内容"。判别特征：关键词与结果语义明显无关即判定污染。**处置：通用搜索引擎结论仅当次实测当次有效；SERP 污染后立即转"权威站点站内搜索接口"路线（见下节渠道矩阵），不再消耗重试配额。**

官方站直猜（搜索引擎全灭后的最优路径）：

1. 先用头图/封面 OCR（analyzeImage）确证来源身份与官方项目名（本次由此确证 "The Prompting Playbook"）
2. 直接猜官方 URL 模式批量测 HTTP 码；**308 = 域名可达但路径迁移**，用 `curl -sL -w "%{url_effective}"` 跟出最终路径再抓正文
3. 官网改版迁移实例：anthropic.com/engineering/* → 308 → /research/* 200
4. 从已抓到的官网列表页提取站内 slug 补充候选
5. 收尾口径：作者官方一手文章 ≈ 原文替代源，引用时标 URL+发布日期；视频/图集卡片的逐条原文不可得时如实声明+列待补充清单，对应关系标"推断"

## 视频链接内容还原流水线（2026-11-10 实证：今日头条短视频 51.9s）

用户给视频/短视频链接要求"看内容/核对信息"时，不得答"看不了"（用户明确批评），自建工具链还原：

1. **跳过 webfetch**：webfetch 抓今日头条视频页静默无输出（反爬），出现一次即放弃该路线。
2. **工具链安装**（一次装齐，清华源）：`pip install yt-dlp you-get imageio-ffmpeg faster-whisper -i https://pypi.tuna.tsinghua.edu.cn/simple`。ffmpeg 二进制由 imageio-ffmpeg 提供（`python -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"` 取路径），无需 scoop 单装。you-get 探测今日头条无输出，不作主力。
3. **探测+下载**：`yt-dlp -F <url>` 列格式（原生 toutiao extractor 自动取 ttwid，实测 480p/720p 两档）→ `yt-dlp -f 720p --write-info-json --write-thumbnail -o "temp\vid\video.%(ext)s" <url>` 一把拿视频+元数据+封面（info.json 的 id 字段可校验用户贴的链接号是否一致，截图地址栏 OCR 长数字易抄错不可作准）。
4. **抽音频+抽帧**：ffmpeg `-i` 的 stderr 里有 Duration 探时长 → `-vn -ar 16000 -ac 1` 抽 16kHz 单声道 wav → `-vf "fps=1/3"` 每 3 秒一帧 jpg（<1 分钟短视频 13-17 帧足够拼全内容）。
5. **语音转写**：faster-whisper（small/int8/cpu），先设 `$env:HF_ENDPOINT="https://hf-mirror.com"` 走镜像下模型（已缓存后重跑秒级）；`initial_prompt` 给领域词提专有名词识别率。
6. **帧字幕 OCR**：analyzeImage 传帧序列，task 里写明帧号↔秒数映射（frame_NN≈3*(NN-1) 秒），要求逐帧 OCR 烧录字幕+屏幕文字，禁合并概括。
7. **双源交叉修正**：whisper 有同音字错误（实测"平权"→"评选"、"传话筒"→"手画筒"、"小智"→"小质"），以帧字幕 OCR 为准修正并在产出中标注修正依据；纯视觉信息（参数贴片、烧录日志、软件界面文字）whisper 覆盖不到，只能靠帧 OCR。

analyzeImage 批量策略：9 帧/次可成功（服务端自动分批串行）；8 帧/次实测返回 EMPTY_OUTPUT_FALLBACK 空结果——失败后必须改参数重试（减批量至 4 帧/次实测成功、或改 task 措辞），禁原样重试。

## 多视频并行处理要点（2026-11-10 双视频实战：57MB+16MB 并行下载转写入库）

- 每视频一个独立目录 `temp/toutiao_{id}/`，视频+info.json+封面+audio.wav+transcribe.py+transcript_utf8.json 全部收在目录内，互不干扰，全流程可双线并行。
- **bash 调用必传 workdir**：忘传时 yt-dlp/ffmpeg 产物落工作区根目录，下游 ffmpeg 抽音频报"找不到 video.mp4"才暴露；修复=Move-Item 把根目录产物迁到目标目录后重跑。并行下发多条 bash 时逐条核对 workdir 是最省事的预防。
- 转写脚本直接复制上一视频的先例只改 initial_prompt 领域词（模型已缓存后转写更快）；中文输出禁靠控制台回显，脚本内直写 UTF-8 结果文件再 read。
- 时长参考：5'45" 音频 faster-whisper small/int8/CPU 约 1–2 分钟完成（600s 超时富余），20 分钟以上才需考虑后台化。
- 提炼入库收尾（内容还原的下游）：要点按"来源五要素＋核心方法＋对本项目启发＋入库处置结论"结构落 `notes/学习成果-*.md`（沿用项目先例命名），同步知识库索引登记行＋变更日志行；干货实操类标高价值并给调用场景，营销/带货类如实降级为"书目线索仅登记"，并显式声明是否触发当前 spec/design 改动（用户明示不强制时评估后写明结论）。

## 头条视频页 JS-VM 墙完整绕过链路（2026-11-10 实证：3'30" 视频成功取回 720p）

新发布/风控严的头条视频，桌面版 yt-dlp 报 "No video formats found"（页面被 JS 虚拟机保护墙拦截），you-get/m 端重定向/ixigua（要 cookies）全部失败；www 与 ixigua 返回同长（72914B）空壳页=同一反爬系统，正面攻破不现实。**绕过链路（requests 全可完成）**：

1. **移动 UA 取 SSR 分享页**：iPhone UA GET `https://m.toutiao.com/video/{id}/`——返回约 39KB 真实页（含作者名、视频标题），不含 jsvmprt。注意 `New-Item` 建目录与下载命令分开执行（workdir 目录不存在时整条命令静默失败）。
2. **解码 RENDER_DATA**：`<script id="RENDER_DATA">` 内是 URL 编码 JSON，`unquote` 后得 sessionConfig/articleInfo/seoTDK 等键；articleInfo 含 title、playAuthTokenV2、tt-videoid、mediaId、creatorUid、播放/点赞/粉丝数。
3. **兜底元数据**：`<script>` 里的 schema.org VideoObject JSON-LD（name/uploadDate/duration 如 PT3M30S/interactionStatistic）可直接 json.loads。
4. **点播直链**：playAuthTokenV2 base64 解码出 `{"GetPlayInfoToken":"Action=GetPlayInfo&Version=2019-03-15&X-Amz-..."}`；**原样字符串拼接** GET `https://vod.bytedanceapi.com/?{GetPlayInfoToken}`。两个坑：token 不可经 requests 的 params 传（会被重编码致 SignatureDoesNotMatch），必须 `url + "?" + token` 原样拼；vod.bytedance.com 本机 DNS 不通，用 vod.bytedanceapi.com。响应 `Result.Data.PlayInfoList` 是**列表**（非 dict），按 Definition 字段挑 720p 的 MainPlayUrl，requests 流式下载即得 mp4。
5. 老接口不通用（实测）：`/i{id}/slow_info/` 返回 success 但 data 空；`/vapp/lvideo/api/info/` 报业务错误 130001；先抓 cookies 再喂 yt-dlp 的路线对头条无效（验证页本身不发 cookie）。

## B 站作头条系内容的交叉调研源（2026-11-10 实证：头条作者在 B 站有同名 UP 且有专题视频）

头条视频只有口播时，作者同内容常同步发 B 站且带课件截图/目录树，信息密度远高于口播。可用接口（均无需登录）：

- `api.bilibili.com/x/web-interface/view?bvid=` 拿标题/desc/mid/cid（desc 常直接写明视频内容结构）。
- UP 视频列表 `x/space/wbi/arc/search` 无 WBI 签名=412 空响应，yt-dlp --flat-playlist 空间枚举同样 412——**别死磕**；改走搜索接口 `x/web-interface/wbi/search/type?search_type=video&keyword=`（实测 code=0 可用，翻页枚举按 author 字段过滤）。
- **按作者名精确搜索可能 0 命中**（搜索分词差异，实测"欧工Ai"为关键词枚举结果为空）——改用内容特征词搜索（如"AI 单片机 工作流"），结果里按 author==目标 UP 过滤更稳；view API 拿到 mid 后以 mid 确证身份。
- CC 字幕 `x/player/v2?bvid=&cid=` 返回 code=0 但字幕常为空（UP 未传），别指望；主力仍是下载+转写。
- **yt-dlp 下载 B 站视频 ffmpeg 不在 PATH 时**：报错但视频流(f30xxx.mp4)+音频流(f30xxx.m4a)已分别落盘——直接把 m4a 喂 faster-whisper 即可，无需 ffmpeg 合并/抽音频；抽帧用 mp4 视频流。
- 课件帧是金矿：115s 视频约 20s 处即抓到作者完整标准项目目录树、86s 处抓到学员聊天记录实证——口播类视频按转写时间线定点抽帧（每 2s 一帧）+analyzeImage 精读。

## GitHub 公开元数据评估模式（2026-11-10 实证：9 仓库选型评估一轮成功）

"去 GitHub 找恰好 N 个项目做评估对比、你只管评我拍板"类任务的落法：

1. **元数据获取**：`api.github.com/repos/{owner}/{repo}` 免登录即可（60 次/时限流足够），urllib 标准库直调，带 `User-Agent` 头（无 UA 会被拒）。取 stars/open_issues/pushed_at/license/html_url 作客观依据。
2. **repo 全名陷阱（本会话踩坑）**：owner 可能是非典型用户名（纯数字，如小智设备端仓库就是 `78/xiaozhi-esp32`）——自动化脚本**禁按经验拆分/补正前缀**，直接使用完整全名请求；曾因画蛇添足把 `78/` 当旧前缀拆掉致 404→元数据 null。首次候选清单先逐个实测 404/200 再进评分。
3. **license 字段多值为 NOASSERTION**（Renode/QEMU/WebGoat 实测）：如实标注，不猜测具体许可证；单许可证仓库才给 SPDX 名（MIT/Apache-2.0/GPL-3.0 实测正常返回）。
4. **评分纪律（机器自查三件套）**：①客观维度（活跃度/许可证）依据引用 API 实测值+快照日期；主观维度依据写可核对的公开事实描述；②元数据获取失败的维度记"无法评估"并注明原因，**禁编造**；③报告全文禁出现"已选定/最终选定为/推荐采用为最终"类替用户决策表述——写入前全文扫描，命中即拒绝落库；决策状态字段锁定"待用户决策"。
5. **双形态落盘**：机器自查库（JSON，条目数硬校验如"恰好 5 个"）+ 人类可读 md 存档（仓库/元数据/逐维度评分与依据/相关性说明/快照日期/决策状态字段齐备），并经门禁机制提交用户置"等待确认"。

## 处置细则（2026-11-10 增补）

- **analyzeImage 空输出回退**：服务偶发 EMPTY_OUTPUT_FALLBACK（即使 4 帧/次也会遇到）；同一输入连续失败 ≤2 次即换单帧或换邻近时间点帧，禁原样重试第 3 次；一轮内勿对同一帧组重复发起多个调用（重复槽位浪费且部分返回空）。
- **PowerShell 内联 python -c 引号冲突**：python 代码含双引号字符串（如 `r'..."..."'` 正则）时 PS 解析器会拆散引号报 ParserError（"[" 后缺少类型名称/字符串缺少终止符）。**直接写成 .py 文件再 `python file.py`**，一次成本杜绝引号地狱；抓取/转写流水线一律按此执行。

## 实测留痕（2026-11-07）

- 今日头条微头条 `www.toutiao.com/w/{id}/`：桌面版 72KB 全为 JS VM 保护脚本；`m.toutiao.com/w/{id}/` + iPhone UA → 69KB 含完整标题+正文。
- 头条图集：仅头图有带签名的直链可下载（p3-sign.toutiaoimg.com），其余卡片需 APP 打开，抓不到属预期。
- Anthropic 官网：/engineering/* 全部 308，跟随得 /research/* 200（building-effective-agents / writing-tools-for-agents / claude-code-best-practices / demystifying-evals-for-ai-agents 四篇命中）；同期所有搜索引擎均无该分享会转载，直猜官方 URL 是唯一命中路径。

## 受限网络环境的官方工具渠道探索（2026-11-11 实战：Tor 拉取，"必须弄通"类派工）

用户点名"工具必须拉到本地并调通、不许调不通就完事"时，渠道探索按证据链穷尽（每步留证据），降级纪律（≤3 次）不适用于用户点名的硬目标：

0. **先 `winget search <工具名>` 再手搓（2026-11-11 最重教训，两次被强令）**：装任何软件第一步必查包管器（winget search / scoop search）——DevSidecar 明明有官方 winget 包（`docmirror.dev-sidecar` 2.3.5，winget install 一次成功、装到 Program Files、启动后 127.0.0.1:31181 HTTP 代理实测响应），却因未查包管而误判"无包管只能便携 zip"，手搓 NSIS 提取+闪退诊断 6+ 次触发用户两次强令回滚。**winget 包存在 = 免提权/静默/路径/闪退全部由包管器兜底，手搓路线全部作废**。
1. **诊断验证禁落盘脚本**：探针/验证类操作（端口探测、握手测试、bootstrap 查询）一律用内联命令或内置工具（netstat、PowerShell 原生 TcpClient、Test-NetConnection），禁写 probe_*/verify_*/tor_setup 类落盘脚本——用户对"手搓脚本泛滥"执行了强制回滚（8 个脚本一次清零）。
2. **同症状连续失败 2 次必须换实现路径**：Electron 启动闪退类诊断在同一入口反复试探 6+ 次属死循环违规（用户强令"再违废弃会话"）。二分定位（如逐轮只留单一网桥验证配置解析）可用，但同一入口的重复失败不许超 2 次。

1. **官方主域先探**：HEAD/GET 逐个测（torproject 全域实测超时：dist/www/archive/mirror.torproject.org——"无法连接到远程服务器"=被墙特征，404=域通但无此路径，getaddrinfo failed=DNS 不通，三类要区分记录）。
2. **官方认可镜像站**：逐个 GET 版本目录索引（`href="(\d+\.\d+\.(\d+\.)?\d+)/"` 正则递归下钻版本目录）；实测 TUNA/USTC/SJTU/netcologne 均无 tor dist（404）——镜像站没镜像≠镜像站挂了，如实记录"无此内容"。
3. **winget manifest 预判**：官方包在 winget 有 manifest（`raw.githubusercontent.com/microsoft/winget-pkgs/master/manifests/<首字母>/<Publisher>/<App>/<ver>/<Publisher.App.installer.yaml>`）——**先读 InstallerUrl 判断下载域可达性，再决定是否跑 winget**（TorProject 包 InstallerUrl 指向 archive.torproject.org 同被墙，winget 必白跑）。此法同样适用于预判任何 winget 包的真实下载源。
4. **落点=官方生态项目的 GitHub release 直发**（GitHub 直连可达时最优）：工具的官方生态配套项目常在 GitHub 直发安装包且**内置捆绑目标二进制**（实测：OnionShare MSI 139MB 内置 tor.exe；onionshare/onionshare org 与 torproject 官方关联）。org 关联仓库枚举 `/orgs/{org}/repos` 查分发仓库（torbrowser-releases 实测空资产也是结论）。
5. **可信第三方镜像仓库备选**：`api.github.com/search/repositories?q=<工具名>-expert-bundle` 命中专用镜像仓库（如 matinrco/tor 的 expert bundle zip，版本旧但可达可用）；完整安装包镜像同理（实测 `q=tor-browser+mirror` 命中 hr0ark/tor-mirror——官方 portable 安装器全量镜像，releases 资产含 `tor-browser-windows-x86_64-portable-<ver>.exe` 108MB，DevSidecar 31181 加速 `curl -L` 下载成功）。
6. **可疑仓库弃用判据**：release 资产名与仓库描述矛盾即弃（实测：701★ 的 Tor-Portable 描述为 portable Tor、release 资产却叫 AntiTor_*，名实不符内容可疑）；高星数不豁免名实核验。
7. 下载大文件用后台 bash（`Invoke-WebRequest -OutFile` + 540s 超时）+ 轮询文件大小；产物统一落 `prepared/<工具名>/` 并以大小阈值判完成度。
8. **Tor Browser 13.5+ 无静态网桥列表文件（2026-11-11 实证：6 路径全 404 的根因）**：内置网桥已改为 **moat API 动态预取**——tor-browser-build 仓库的 `projects/moat-settings/config` 仅指向 `gitlab.torproject.org/tpo/anti-censorship/rdsys-admin`（构建配置，非网桥数据）；拉 `bridges_list.*.txt` 类静态文件必 404，勿再穷举路径。**网桥的正解=调 rdsys moat API**（Tor Browser 同款：POST `/moat/circumvention/settings`，domain fronting 参数在 rdsys-admin 仓库）——本轮未完成，待办。
9. **官方构建 fork 与隔离克隆**：官方构建组织 fork `tor-actions/tor-browser-build`（GitHub API `search/repositories?q=<名>+in:name` 定位）；`git clone --depth 1` 浅克隆到 refs 隔离区（公约仓库隔离；stderr 的 "Cloning into..." 显示为 NativeCommandError 假错误，`Test-Path` 判真）；仓库结构演进后（moat-settings/browser/lyrebird=obfs4proxy 新名）先列 `projects/` 目录再搜文件。
10. **mitm 名单内域名的 -k 通道**：dev-sidecar 拦截名单内域名（github.com/raw.githubusercontent.com/api.github.com）在 CA 卸载后 SSL 一律被拒——`curl -x http://127.0.0.1:31181 -k` 跳过验证即可拉取（调研用途，内容来自真实源）；PowerShell Invoke-RestMethod 无 -k 等价项，改用 curl.exe。

同族经验：视频链接内容还原中"头条作者多平台身份调研"也走同款多源交叉——B 站 view API（拿 mid 确证身份）→ 搜索接口按内容特征词枚举（按 author 字段过滤）→ YouTube/正文站点轮询可达性，每步证据落盘后呈报。

## 第三方仓库浅克隆+只读 grep 耦合/可行性分析（2026-11-12 实证：三框架 design 前置门禁实测）

"评估某框架能否拉取/某依赖（LLM、数据库等）是否解耦"类调研派工，是 GitHub 元数据评估模式的源码层延伸：

1. **流程**：api.github.com 搜索确认官方仓库（单次批量查询省认证限额；stars/pushed_at/archived/fork/license 定性活跃度）→ `git clone --depth 1` 浅克隆到隔离目录（如 D:\refs\，与项目 .git 物理隔离；先 Test-Path 防重，目录非空直接复用）→ 只读 grep 配置面与调用面 → 文件:行级证据表 → 分级结论。
2. **拉取结论三选一**：A=公开源码可直接拉取（给地址）/ B=仅 fork/归档镜像可取（给地址与状态）/ C=确无可用源码。原仓库 404 也是实测结论（"已闭源"类用户口径的核实证据），但下 C 前必须搜 fork/镜像/社区续维护版（本次实证：原仓库 404 而 RuoJi6/ARTEX 续维护版 1760 星可拉取——用户口径获实证修正，如实呈报修正事实，不改判用户决策权）。
3. **grep 策略**：先宽词（OPENAI|API_KEY|BASE_URL|model|provider）扫 .env.example / config*.go / docker-compose 定配置面；再收窄定位调用初始化单点（工厂/命名空间形态，如 `llm.NewClient`、`pkg/providers`）；按子目录分区搜（如查询端 service vs 构建端 build），避免上千处泛命中淹没结论；"某目录 grep 客户端构造零命中"本身就是该端零依赖的实证。
4. **分级口径**：低=纯配置重定向（endpoint/env 可指本地）/ 中=少量适配层代码 / 高=强耦合需大改；每一级逐点附文件:行证据。分区给结论（如 Cairn：查询端零 LLM 零 embedding 成立 + 构建端单一工厂内置 mock）。
5. **证据纪律**：每条结论附命令+输出摘录；查不到写"未找到"；搜索 total_count 与 top 命中的 full_name/updated_at 留痕；平台能力类结论（如"无本地模型端点"）须 tool_search 实测留证，禁虚构端点存在。
6. **产出纪律**：三方案对比表（推理来源/公网外连风险/改造量/与底座原则契合度）+ 每框架一行结论行；报告落盘后列目录+读文件验证非空并写入返回摘要；全文禁替用户决策（改造决策权留用户）。

## GitHub issues 检索做工具安全争议调研（2026-11-11 实证：dev-sidecar"查黑历史"派工）

"调研某工具有无人反映偷数据/后门/安全漏洞"类派工的命令行落法：

1. **通道**：`curl.exe -x http://127.0.0.1:31181 -k -s "https://api.github.com/search/issues?q=repo%3A<owner>%2F<repo>+<URL编码关键词>&per_page=5"`——中文关键词先 URL 编码；经 dev-sidecar 通道访问其 mitm 名单内域名（api.github.com 在名单内）必须加 `-k`（CA 已按红线卸载，证书链不被信任）。
2. **解析层污染不影响事实提取**：响应 JSON 经 PowerShell 管道 ConvertFrom-Json 会因 GBK 污染报错——原始 JSON 文本已完整含全部事实（total_count/items[].number/title/state/body/html_url），直接读原始输出提取事实链即可，勿纠缠解析器。
3. **查什么**：拦截范围争议（"明文请求被转成 SSL"类抓包实证，如 dev-sidecar #474）、核心模块崩溃（mitm 未捕获异常 #742）、静默失效模式（配置 enabled 但参数空致功能静默降级 #728）、远程配置注入面（默认配置注入来自第三方仓库的页面脚本 #684 running.json 实证）、仓库活跃度（stars/pushed_at/license 佐证维护动力）。"偷数据/后门"指控零命中本身也是调研结论（如实呈现）。
4. **输出纪律**：逐条列 issue 编号+状态+一句话事实+链接，禁臆测；活跃度数据引用 API 实测值。

## 权威官方来源调研渠道矩阵（2026-11-12 实证：安全事件/官方通报/执法案例类时事派工）

"查官方通报/权威媒体报道做正反例调研"类派工，通用搜索引擎被污染时的可用渠道与链路：

1. **直连可达清单（本机实测）**：api.github.com、CCTV（news.cctv.com + search.cctv.com）、CNCERT（cert.org.cn，首页 301 需 `-L` 跟随到 /portal/index.htm）、网信办 cac.gov.cn、高校新闻站（如 news.nwpu.edu.cn）。**不可达勿试**：mps.gov.cn（HTTP 521 防护）、裁判文书网（登录+JS 墙）、境外全域（Wikipedia/BBC/DOJ/Krebs/Talos 直连 HTTP=000 重置）。
2. **webfetch 平台通道对境外被墙站点同样不可达**（实测报 "Unable to connect"）——平台侧通道不能绕过网络层封锁，境外源不可达时 webfetch 不是退路，直接放弃境外源并在产出中如实登记"渠道受限未采信"，禁编造境外案例细节。
3. **CCTV 站内搜索链路（本节核心技巧，五步）**：①`search.cctv.com/search.php?qtext=<URL编码>&type=web` 直连可用；②结果条目链接是 `link_p.php?targetpage=<URL编码跳转>` 格式，**真实 URL 提取自 `lanmu1="<url>"` 属性**（正则 `lanmu1="([^"]+)"`）；③**多词长查询可能零命中**（AND 匹配，如"黑客 非法控制计算机信息系统 判刑"空结果），改 2 词组合或单词重试；④候选文章页批量抓取读 `<title>` 快筛（比 SERP 提取标题更稳，一次 6-8 页循环 curl）；⑤正文用 UTF8 读+`<p[^>]*>([^<]{15,500})</p>` 正则取段——**Get-Content 不加 `-Encoding UTF8` 时标题显示为 GBK mojibake 乱码（"瑗垮寳宸ヤ笟澶у"形态），文件本体是好的，重读即可辨**。
4. **api.github.com 取仓库 README 原文**（github.com 页面/git 通道被墙时的文档全文通道）：`curl.exe -s -H "Accept: application/vnd.github.raw" "https://api.github.com/repos/<owner>/<repo>/readme"` 直接返回 Markdown 原文，配合 repos 元数据端点一并核验 stars/pushed_at/license。已存在的本地浅克隆仓库优先读本地（离线研读、路径可回查）。
5. **同名仓库混淆核验四步（2026-11-12 Cairn 张冠李戴实证）**：spec/上游材料声称"某仓库含某机制"时，落笔前必须核验——①`git -C <仓库> remote -v` 确认 owner 身份；②`git log -i --grep="<机制关键词>"` + `git grep -l -i "<关键词>" $(git rev-parse HEAD)` 全历史+全树双查；③README 全文关键词验证；④核验失败时沿**引用关系追溯真身**（本次：目标仓库 README 无黑板机制，但上游 ARTEX README 的"参考"节引用 oritera/Cairn——真身经引用链定位，README 经 api.github.com raw 通道补取）。**引用任何开源仓库必须带 owner 前缀**（同名仓库极易混淆，spec 编制阶段已实证踩中）；核验不符的预期在 trace/留痕文件中登记剔除并降级为同名参考，不删文件。
6. **产出纪律**：每条材料标注 URL+检索日期（一手来源优先于二手转述）；渠道受限未取得的内容登记"未决"而非放弃登记；调研结论落盘后列目录+读文件验证非空并写入返回摘要。
