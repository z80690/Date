---
name: windows-git-powershell-quirks
description: >-
  本机 Windows+PowerShell 5.1 环境的 Git/编码/Edit 工具实战怪癖与修复模式：git
  中文提交信息乱码的字节级验证、.gitignore BOM/CRLF 静默失效、PS5.1 语法陷阱与 ParserError 整块不执行、外部 CLI
  子进程 UTF-8 输出被 ANSI 解码致中文失真（[Console]::OutputEncoding 修复）、Edit 工具 mtime
  冲突恢复、长任务超时、bash 命令文本内嵌敏感检测正则被平台拦截（报"解析目标路径失败"）、Doom Loop 双形态遵从协议、"文件是否被本会话改动"的
  SHA256 指纹基线裁决口径。凡涉及 git 提交/验证、PowerShell
  命令构造、文件编辑冲突、外部工具输出乱码、命令被平台拦截/解析目标路径失败、工具连续重复调用被禁/平台保护警告时使用。
---

# Windows / PowerShell / Git 实战怪癖与修复

## PowerShell 5.1 语法陷阱
- 禁用 `&&`（不支持），用 `;` 顺序执行
- 空 PSCustomObject 的 `.Count` 返回 null：判空用 `$x.PSObject.Properties.Name.Count`
- `[Console]::OutputEncoding=UTF8` 会在持久会话中持续生效，污染后续命令输出——设置过一次后，后续乱码判断要考虑此因素。**反向用途（2026-11-09 实证）**：外部 CLI 以 UTF-8 输出中文（如 Ruff 的 E902 诊断"系统找不到指定的文件"），PS 5.1 子进程默认按 ANSI 解码，落盘报告/日志中文失真为乱码——在被审脚本开头加 `[Console]::OutputEncoding=[System.Text.Encoding]::UTF8`（try/catch 包裹）即修复；修复后须复验原裁决场景不受影响（修复只动显示层，裁决逻辑不应变化）
- 原生命令 stderr 会被包装成 NativeCommandError 显示（非真实失败）；长命令输出走 `| Select-Object -Last N` 会缓冲到结束才落盘
- Get-Content 与 Select-String 编码行为不一致（2026-11-08 实测）：同一 UTF-8（无 BOM）中文文件，`Get-Content` 默认按系统 ANSI 解码→控制台显示乱码，但 `Select-String` 对同文件可正确匹配中文模式并计数。纪律：①验证/展示中文文件内容一律加 `-Encoding UTF8`；②不要因 Get-Content 乱码断定文件损坏——文件本体可能正常，先用 Select-String 关键词命中计数交叉确认再定性
- PowerShell **ParserError=整块不执行**（2026-11-09 实证）：一条长命令中引号高嵌套（如双引号字符串数组内再嵌反引号转义）报解析错误时，**包括块内前段"创建文件"在内的所有语句都没跑**——后续步骤报"文件不存在"（如外部工具 E902）是假象，根因在上游解析失败。定位纪律：见"找不到文件"类报错，先怀疑前序命令是否整块未执行（把创建段拆成独立短命令重跑），勿直接去排查目标路径；复杂拼接拆为"创建段/验证段"两条命令，禁一锤子长命令
- `bash` 工具通道**按会话实测判别，勿按记忆盲写语法**（2026-11-08 两次实测相反：一例 `bash --version` 返回 wsl 乱码=WSL 通道；一例 `ls -la` 报 Get-ChildItem 参数绑定错误=PowerShell 通道，同一会话内 `git status` 与 `Get-Item | Select-Object` 语法均正常）。探针判别法：跑一条低成本命令看报错形态——报错含 Get-ChildItem/参数绑定=PowerShell 通道（直接写 PS5.1 语法）；wsl 乱码=WSL 通道（盘符路径写 /mnt/c/）。WSL 通道下，凡外部流程约定"写 .sh 后 bash 执行"的步骤（如系统技能的 _wiki_cmd.sh 模式），直接改写为等价 .ps1 后 `powershell -ExecutionPolicy Bypass -File <脚本>` 执行，命令行保持短形式
- `git diff -U 6`（-U 与数字间有空格）中 "6" 被 git 解析为 revision 报 `fatal: bad revision '6'`：短选项带值必须连写 `-U6`（或 `--unified=6`）
- 原生命令（python/git 等）成败判定用 `$LASTEXITCODE -ne 0`，勿依赖 `$?`——stderr 有输出即把 `$?` 翻成 False 产生假失败（脚本报 traceback 时两者一致，但纯警告走 stderr 时 `$?` 会误判）

## git 中文提交信息乱码（数据级 vs 显示级先分清）
- commit -m 中文经命令行传输会存成乱码字节；-F 文件也可能因读取编码出错
- **验证真伪必须字节级**：用 .NET Process（StandardOutputEncoding=UTF8）直读 `git cat-file commit HEAD`，落文件后 Read 检查；控制台/Out-File/管道路径全是污染源，不可作依据
- 修复：[IO.File]::WriteAllText 写提交信息文件，git commit --amend -F 该文件
- 从 git 历史字节级检出旧版文件（对比测试/退役归档场景，2026-11-08 实证）：PowerShell 管道与 `>` 重定向会按编码转码污染内容，用 `cmd /c "git show HEAD:<repo路径> > <目标文件>"`（cmd 重定向=字节流）检出；检出后以字节数+行数与预期交叉核对，来源版本号（`git log -1 --format=%h`）记录在档

## bash 命令文本内嵌敏感模式触发平台拦截（2026-11-09 实证，两次复现）
- 现象：bash 命令**文本里**包含敏感模式字面量——即使只是引号内、用于扫描其他文件内容的检测正则（如 `while($true)`、`Start-Process`、`Invoke-WebRequest`、watch/轮询族）——命令不执行，报"从命令中解析目标路径失败"：平台命令安全检测把检测模式本身当成了可疑命令
- 解法（职责分离）：执行类操作留 bash；**内容模式扫描一律改走专用 Grep 工具**（不经过命令通道）；扫描结论需回填 %TEMP% 留痕文件时用 Edit/write 工具补录，禁把敏感正则字面量塞回 bash 命令
- 识别特征：命令含多支路正则字符串且报错为"解析目标路径失败"（非 PS 语法错误形态、非参数绑定错误）→ 优先怀疑平台拦截而非语法问题，勿盲目原样重试

## "文件是否被本会话改动"的裁决口径（SHA256 指纹基线，2026-11-09 实证）
- git status 的 M 状态可能是**历史遗留**（特性开始前已存在），git diff 相对 HEAD 的变更不能证明"是本会话改的"——直接拿 git status/diff 当零改动证据会被历史脏状态误导
- 权威证据：任务起点固化关键文件指纹基线（Get-FileHash SHA256+字节数，落 %TEMP% 留痕）→ 收尾同哈希复验，一致=本会话零触碰；跨任务沿用此口径
- 两者并用时在留痕中如实分工：指纹=本会话改动裁决；git diff=相对上次提交的仓库状态（历史遗留 M 注明"基线前已存在"）

## 提交范围裁剪与双向核对（特性收工提交，2026-11-08 实战）

- 候选清单为基+执行中补漏：交付门拟定的变更范围清单先行；`git add` 前先 `git status --short` 实查全集，清单漏列的本特性产物（如新建技能目录、学习成果文件）补入暂存；非本特性增量（经验库演化/其他技能/运行时痕迹/docs 修改）**不入本次提交**，如实留待后续，防范围膨胀。
- G2 双向核对：暂存后 `git diff --cached --name-only | Select-String "<排除模式清单>"`（.env/temp/运行时痕迹/非本特性目录逐个列模式）→零命中即通过；`git diff --cached --stat` 交叉看规模合理性（行数量级与产物预期相符）。
- 提交后复检：`git status --short | Select-String "<本特性相关路径>"` 确认干净；残留命中若属排除范围文件的文件名巧合（如经验库文件名含本特性关键词）则属正常，如实区分。
- 提交动作本身会触发 hook 碰活跃留痕文件 mtime：提交后的收尾留痕 edit 会再报一次冲突——重读+原锚点重执行一次即可（内容通常未变）；提交后新增的留痕将随下次提交入库，**不为留痕再发一次提交**（防"留痕→提交→留痕"无限循环）。

## .gitignore 静默失效
- write 工具产物带 BOM/CRLF 时忽略规则**静默不生效**（status 仍列出目标文件）
- 修复：`[IO.File]::WriteAllText(path, "pattern1`npattern2`n")`（LF、无 BOM）
- 验证：`git check-ignore <路径>` 有输出=生效

## Edit 工具冲突恢复（hook 触碰文件）
- 知识库文件常被平台 hook 触碰 mtime：Edit 报"modified since last read"→ 重 Read 确认内容（通常无损）→ 基于最新内容重新 Edit
- grep/grep 式查看不算 Edit 前置的 read，必须用 Read 工具
- oldString 失配：缩小锚点（只锚定目标行）重试
- 长文件重写优先 write 全文；局部改用 edit+小锚点
- 高频触碰文件的批量操作策略（2026-11-08 实证：知识库索引/项目事实表/事件流水等活跃留痕文件，单轮任务 4+ 次命中 mtime 冲突）：①接受"活跃留痕文件首次 edit 失败一次"为常态，失败即用 `Read(limit=1, offset=目标行号)` 精准重读目标行后**立即** edit（窗口最小化，禁重读全文拖延）②同文件多处修订在同轮并行 edit 中，前一 edit 成功即改变 mtime，后一 edit 易报冲突——同文件多 edit 顺序执行更稳；跨文件并行不受影响 ③用 bash Get-Content 读过的文件不算已读，edit 前仍须 Read 工具正式读取（实测 mcp_settings.json 场景）

## 长任务与后台
- bash 约 10 分钟总超时会杀后台进程；长构建/下载必须后台运行+输出实时落文件（禁管道尾过滤，会吞全部日志）+轮询文件增长与进程存活双信号
- 多语句长命令易解析失败：写成 .ps1 脚本文件再 `-File` 执行（脚本内容全 ASCII 更稳）
- WAF/验证码拦截页（如华为云 EdgeOne）：先诊断再降级——**实测 EdgeOne 多为 UA 检测而非强制 JS 验证：curl/webfetch 无 UA 即返回 Security Verification 页，带标准浏览器 UA（`-A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ... Chrome/126..."`) 即 200 直抓**（成功例：llms.txt 138KB、官方 .md 直链）。修复顺序=①带浏览器 UA 重试 → ②换同源镜像/直链变体 → ③3 次上限后降级（U 四字段登记：阻塞原因/恢复条件/回迁目标/进入时间）。禁第三方打码、禁绕过类手段
- 跨盘搬迁含 .git 的目录（Move-Item 跨盘=复制+删除）：源端 .git 内只读文件会删不掉留残留——先 `Get-ChildItem -Recurse -Force | % { $_.Attributes = 'Normal' }` 清属性再 `Remove-Item -Recurse -Force`；搬迁后验证 git 仓库健康（status 干净+HEAD 一致），并同步更新所有硬编码路径引用（脚本默认参数/事实表/注册表）

## Doom Loop 双形态与遵从协议
- 形态 1：同一工具连续重复调用被平台权限拒绝（实测：listSkills 连续多次调用中后续全部 "user rejected"）
- 形态 2：同一动作命中平台保护触发警告（实测：Knowledge 检索 + 用户拒绝某次调用后警告出现）
- **遵从协议**：立即停止该工具的全部调用（零依赖继续）→ 向用户声明"Doom Loop 已检测+重复的是什么+已完成的工作+数据已充分（首次结果即为权威，重复调用是冗余确认）"→ 用文件编辑类操作（edit/write/commit，非被禁工具）完成剩余收尾 → 下一轮用户输入解除禁用
- 预防：首次调用结果已含全部所需信息时，禁用重复调用做"再确认"（幂等纪律：先到先处理一次，冗余确认即违规）；同轮多工具调用控制总数，避免触发平台保护
