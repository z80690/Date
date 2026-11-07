---
name: windows-git-powershell-quirks
description: 本机 Windows+PowerShell 5.1 环境的 Git/编码/Edit 工具实战怪癖与修复模式：git 中文提交信息乱码的字节级验证、.gitignore BOM/CRLF 静默失效、PS5.1 语法陷阱、Edit 工具 mtime 冲突恢复、长任务超时。凡涉及 git 提交/验证、PowerShell 命令构造、文件编辑冲突时使用。
---

# Windows / PowerShell / Git 实战怪癖与修复

## PowerShell 5.1 语法陷阱
- 禁用 `&&`（不支持），用 `;` 顺序执行
- 空 PSCustomObject 的 `.Count` 返回 null：判空用 `$x.PSObject.Properties.Name.Count`
- `[Console]::OutputEncoding=UTF8` 会在持久会话中持续生效，污染后续命令输出——设置过一次后，后续乱码判断要考虑此因素
- 原生命令 stderr 会被包装成 NativeCommandError 显示（非真实失败）；长命令输出走 `| Select-Object -Last N` 会缓冲到结束才落盘

## git 中文提交信息乱码（数据级 vs 显示级先分清）
- commit -m 中文经命令行传输会存成乱码字节；-F 文件也可能因读取编码出错
- **验证真伪必须字节级**：用 .NET Process（StandardOutputEncoding=UTF8）直读 `git cat-file commit HEAD`，落文件后 Read 检查；控制台/Out-File/管道路径全是污染源，不可作依据
- 修复：[IO.File]::WriteAllText 写提交信息文件，git commit --amend -F 该文件

## .gitignore 静默失效
- write 工具产物带 BOM/CRLF 时忽略规则**静默不生效**（status 仍列出目标文件）
- 修复：`[IO.File]::WriteAllText(path, "pattern1`npattern2`n")`（LF、无 BOM）
- 验证：`git check-ignore <路径>` 有输出=生效

## Edit 工具冲突恢复（hook 触碰文件）
- 知识库文件常被平台 hook 触碰 mtime：Edit 报"modified since last read"→ 重 Read 确认内容（通常无损）→ 基于最新内容重新 Edit
- grep/grep 式查看不算 Edit 前置的 read，必须用 Read 工具
- oldString 失配：缩小锚点（只锚定目标行）重试
- 长文件重写优先 write 全文；局部改用 edit+小锚点

## 长任务与后台
- bash 约 10 分钟总超时会杀后台进程；长构建/下载必须后台运行+输出实时落文件（禁管道尾过滤，会吞全部日志）+轮询文件增长与进程存活双信号
- 多语句长命令易解析失败：写成 .ps1 脚本文件再 `-File` 执行（脚本内容全 ASCII 更稳）
- WAF/验证码拦截页（如华为云 EdgeOne）：先诊断再降级——**实测 EdgeOne 多为 UA 检测而非强制 JS 验证：curl/webfetch 无 UA 即返回 Security Verification 页，带标准浏览器 UA（`-A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ... Chrome/126..."`) 即 200 直抓**（成功例：llms.txt 138KB、官方 .md 直链）。修复顺序=①带浏览器 UA 重试 → ②换同源镜像/直链变体 → ③3 次上限后降级（U 四字段登记：阻塞原因/恢复条件/回迁目标/进入时间）。禁第三方打码、禁绕过类手段
- 跨盘搬迁含 .git 的目录（Move-Item 跨盘=复制+删除）：源端 .git 内只读文件会删不掉留残留——先 `Get-ChildItem -Recurse -Force | % { $_.Attributes = 'Normal' }` 清属性再 `Remove-Item -Recurse -Force`；搬迁后验证 git 仓库健康（status 干净+HEAD 一致），并同步更新所有硬编码路径引用（脚本默认参数/事实表/注册表）
