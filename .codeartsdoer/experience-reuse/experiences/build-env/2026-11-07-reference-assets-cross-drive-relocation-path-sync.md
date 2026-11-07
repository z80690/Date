---
id: 2026-11-07-reference-assets-cross-drive-relocation-path-sync
title: 参考资产跨盘搬家：复制+清理替代跨盘 Move-Item，搬家后路径引用全量同步
category: build-env
nature: technique
created_at: 2026-11-07T08:33:53
updated_at: 2026-11-07T08:33:53
tags: [cross-drive-move, path-reference-sync, read-only-files, git-repo-health, asset-safety]
keywords: [Move-Item 跨盘, PermissionDenied, 只读属性, .git 对象文件, 路径硬编码, 引用同步, 回归测试, 资产搬家, 误删风险, 隐藏失败]
problem_patterns: [参考仓库放在用户常操作的目录面临误删风险需要搬迁, 跨盘搬目录因 .git 只读对象文件删除失败而中断留下半搬家状态, 搬家成功后遗漏脚本与文档中的旧路径引用导致后续执行隐藏失败]
source_sessions: [ses_e4f5c5a83ffefUFnzHFvOEFJCW]
project: Date
severity: high
quality_score: 85
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-06-reference-repo-isolation-nesting-prevention, 2026-11-07-gitignore-rule-silent-failure-bom-crlf, 2026-11-06-git-baseline-gitignore-precheck-before-commit-planning]
---

# 参考资产跨盘搬家：复制+清理替代跨盘 Move-Item，搬家后路径引用全量同步

## Scenario

参考框架仓库（含完整 `.git` 或已删 `.git` 的源码树）存放在用户桌面等高频操作目录，用户担心误删造成不可恢复损失，要求搬迁到专用盘符根目录。资产规模大（数十至数百 MB）、含 git 内部对象，且项目中多处文档与脚本引用了旧路径。

## Key Signals

1. `Move-Item <src> <dst>` 跨盘符执行时报 `无法删除项 ...\Cairn\.git: 你没有足够的访问权限执行此操作`（PermissionDenied）——跨盘移动实为复制+删除，git 只读对象文件删不掉导致整条命令中断，留下"目标已复制、源端有残留"的半搬家状态。
2. 脚本参数硬编码旧路径（如 `$PmdClasses = "C:\...\Desktop\refs\p3c\..."`）——搬家后不报错，直到下次真实执行才失败；仅跑"无 Java 变更则跳过"的冒烟测试暴露不了路径问题。
3. 单一事实源文档（事实表/注册表）中的路径字段仍是旧值——引用不同步是静默的，不会主动报错。

## Essence

跨盘搬家的两个隐性代价：①git 仓库的 `.git/objects` 文件默认只读，删除阶段必然卡权限，须先清只读属性再删；②路径是环境事实，写进脚本参数、文档字段的一切旧路径都会在搬家后变成失效引用——**搬家操作只完成一半，另一半是引用同步**，且同步缺口只能靠"执行类验证"暴露，冒烟测试不够。

## Approach

1. 搬家采用"复制 → 验证 → 清源"三段式，不用跨盘 `Move-Item`：
   - `Copy-Item -Recurse` 复制整目录到目标盘；
   - 验证目标完整性：关键产物实存检查（如 bin 目录、构建 jar、目录结构）；
   - 验证 git 仓库健康（含 `.git` 的仓库）：`git -C <dst> log --oneline -1` 能取到正确 HEAD 即对象库完好；
   - 清源：残留删除失败时先 `attrib -r /s` 或清只读属性，再删目录，终核源端已不存在。
2. 引用盘点：搬家后立即 grep 全库旧路径特征串（盘符+目录名，如 `Desktop\refs`、`Desktop/refs`），列出所有引用点清单。
3. 分层同步：事实表/注册表等单一事实源字段 → 脚本默认参数 → 文档正文路径，逐点更新；平台托管文件（如规则文件）不可改的登记为待处理项。
4. 执行类回归：对涉及路径的脚本，构造一次能走到路径参数的真实执行（而非语义跳过的冒烟），确认新路径可达。
5. 提交留痕：引用同步纳入同一版本提交，提交说明注明"路径迁移"便于回溯。

## Faster Next Time

- 一句话判据：**跨盘搬家 = 复制+清源，同盘才可 Move-Item**；看到 PermissionDenied 指向 `.git` 内部文件就先清只读，不要怀疑权限配置。
- 搬家完成后第一件事是 grep 旧路径，而不是先汇报搬家成功——引用同步是搬家的验收条件之一。
- 涉路径脚本的回归必须走"真实执行路径"，语义跳过型冒烟测试对路径失效零检出能力。

## Applicability Boundaries

- 适用：Windows PowerShell 环境下对含 git 仓库或只读文件的大目录做跨盘符搬迁；任何"资产移动后存在多处旧路径引用"的场景。
- 不适用：同盘符移动（`Move-Item` 原子重命名即可，无复制代价）；目标位置无任何引用依赖的一次性临时文件搬迁。
- 证据强度：单项目完整实录（3 仓库、bin/jar 验证通过、脚本失效由回归暴露并修复）；`attrib` 清只读细节未逐项实测，清源失败时优先用资源管理器或手动处理兜底。

## Evidence or Examples

- 实录：`Move-Item "C:\Users\Administrator\Desktop\refs" "D:\refs"` 报两条 PermissionDenied（Cairn\.git、deepseek-super-agent\.git），但复制阶段已完成——目标盘三仓库内容完好（Cairn-bin、p3c-jar 实存）。
- 实录：清源后 `desktop-refs-gone: True`；`git -C D:\refs\Cairn log` 取到 `2ae4eef Merge pull request #125...`，git 仓库健康。
- 实录：搬家后 review-code.ps1 硬编码 `Desktop\refs\p3c` 失效，回归测试（冒烟）通过但路径未走到；随后修正参数指向 `D:\refs\p3c` 并留痕。