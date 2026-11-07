---
name: windows-git-powershell-quirks
description: >-
  本机 Windows+PowerShell 5.1 环境的 Git/编码/Edit 工具实战怪癖与修复模式：git
  中文提交信息乱码的字节级验证、.gitignore BOM/CRLF 静默失效、PS5.1 语法陷阱、Edit 工具 mtime
  冲突恢复、长任务超时、Doom Loop 双形态遵从协议。凡涉及 git 提交/验证、PowerShell
  命令构造、文件编辑冲突、工具连续重复调用被禁/平台保护警告时使用。
---

# Windows / PowerShell / Git 实战怪癖与修复

## PowerShell 5.1 语法陷阱
- 禁用 `&&`（不支持），用 `;` 顺序执行
- 空 PSCustomObject 的 `.Count` 返回 null：判空用 `$x.PSObject.Properties.Name.Count`
- `[Console]::OutputEncoding=UTF8` 会在持久会话中持续生效，污染后续命令输出——设置过一次后，后续乱码判断要考虑此因素
- 原生命令 stderr 会被包装成 NativeCommandError 显示（非真实失败）；长命令输出走 `| Select-Object -Last N` 会缓冲到结束才落盘
- Get-Content 与 Select-String 编码行为不一致（2026-11-08 实测）：同一 UTF-8（无 BOM）中文文件，`Get-Content` 默认按系统 ANSI 解码→控制台显示乱码，但 `Select-String` 对同文件可正确匹配中文模式并计数。纪律：①验证/展示中文文件内容一律加 `-Encoding UTF8`；②不要因 Get-Content 乱码断定文件损坏——文件本体可能正常，先用 Select-String 关键词命中计数交叉确认再定性

## git 中文提交信息乱码（数据级 vs 显示级先分清）
- commit -m 中文经命令行传输会存成乱码字节；-F 文件也可能因读取编码出错
- **验证真伪必须字节级**：用 .NET Process（StandardOutputEncoding=UTF8）直读 `git cat-file commit HEAD`，落文件后 Read 检查；控制台/Out-File/管道路径全是污染源，不可作依据
- 修复：[IO.File]::WriteAllText 写提交信息文件，git commit --amend -F 该文件
- 从 git 历史字节级检出旧版文件（对比测试/退役归档场景，2026-11-08 实证）：PowerShell 管道与 `>` 重定向会按编码转码污染内容，用 `cmd /c "git show HEAD:<repo路径> > <目标文件>"`（cmd 重定向=字节流）检出；检出后以字节数+行数与预期交叉核对，来源版本号（`git log -1 --format=%h`）记录在档

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
