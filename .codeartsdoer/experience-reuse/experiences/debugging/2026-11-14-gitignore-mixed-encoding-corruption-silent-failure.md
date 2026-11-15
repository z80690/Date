---
id: 2026-11-14-gitignore-mixed-encoding-corruption-silent-failure
title: .gitignore 段级混合编码损坏致整文件被判二进制：NUL 字节、后段规则静默失效与前段幸存误判面
category: debugging
nature: pitfall
created_at: 2026-11-14T17:39:43
updated_at: 2026-11-14T17:39:43
tags: [gitignore, UTF-16, NUL字节, 二进制判定, 静默失效]
keywords: [gitignore 不生效, mixed encoding, UTF-16LE, NUL byte, cannot read binary file, git 判二进制, check-ignore -v, 部分规则幸存, untracked 洪水, 字节级重写, pyc 入库]
problem_patterns:
  - 纯文本配置文件（.gitignore 等）被 read 工具/编辑器报 "Cannot read binary file"，但内容前段肉眼看完全正常
  - git 忽略规则部分生效部分失效（如 .env 被忽略但 *.mp4/*.exe 规则无输出），误判为规则写错而反复改内容
  - mp4/exe/__pycache__ 大量沦为 untracked，若推上远端会拖垮部署链路，而 git 全程零报错零警告
source_sessions: [ses_e269dc135ffew1ZXbdWts1CLWs]
project: Date
severity: medium
quality_score: 92
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [debugging/2026-11-07-gitignore-rule-silent-failure-bom-crlf, build-env/2026-11-08-utf8-nobom-write-verify-first-byte, build-env/2026-11-14-vercel-python-zero-dep-wsgi-entry-pattern]
---

# .gitignore 段级混合编码损坏致整文件被判二进制：NUL 字节、后段规则静默失效与前段幸存误判面

## Scenario

部署前复查任务（Vercel Python 入口检查）中顺带读取根级 `.gitignore`，read 工具直接报 `Cannot read binary file`；同时 `git status` 里 video.mp4、DevSidecar 安装包 exe、`__pycache__`/*.pyc 全部暴露为未跟踪（??）。该文件早前已有防护规则入库且部分规则此前验证过生效——文本配置文件被判二进制、且忽略规则"半失灵"，两个症状同时出现。

## Key Signals

- **首个可信信号**：read 工具报 `Cannot read binary file: .gitignore`——纯文本配置被判二进制，唯一合理解释是字节层混入 NUL/非法序列，直接进字节层排查，不怀疑规则语法。
- **误导线索 1（部分幸存）**：`git check-ignore` 对 `.env` 命中（exit=0）但对 `*.mp4`/`*.exe` 无输出（exit=1）。前段规则仍生效会让人误判"文件大体健康、只是个别规则有问题"。
- **误导线索 2（首字节正常）**：首 3 字节 `2E 6F 62 73`（".ob"）无 BOM——排除了"整文件带 BOM"这一既有经验假设，但**首字节正常不能排除中段编码损坏**。
- **定性信号**：全文件字节统计 `total=108 nul=46`——NUL 计数非零一步定性"混入 UTF-16/二进制序列"。
- 内容 dump 呈 UTF-16 形态：`t\u0000e\u0000m\u0000p\u0000/\u0000*\u0000.\u0000m\u0000p\u00004\u0000`——后段 4 行每字符双字节。

## Essence

完整根因链：某次写盘以后段 UTF-16LE 落盘（PS5.1 写通道默认 UTF-16LE 的已知坑，确切写操作 trace 未记录，属推断）→ 同一文件形成"前段 UTF-8 正常 + 后段 UTF-16 混入 46 个 NUL"的混合编码损坏 → git 将整个 `.gitignore` 视为二进制 → 后段 4 条规则（`temp/*.mp4`、`workspace/**/*.exe`、`*.mp4`、`*.exe`）静默失效 → mp4/exe/pyc 沦为 untracked → 若推上 GitHub 会拖垮 Vercel 部署（大文件入库）。git 全程零报错零警告，且 `.env` 规则因位于 UTF-8 前段而幸存——"部分规则生效"恰恰构成最危险的误判面。

与既有 gitignore 失效经验的边界：`gitignore-rule-silent-failure-bom-crlf` 是**模式级**杂字节（BOM 前缀/CR）使逐条模式字面不匹配，文件整体仍被 git 当文本解析；本条是**段级**编码混用使整文件被判二进制、后段规则整段失效。诊断序也不同：BOM/CRLF 条目"首字节即判"在此不够用，须下探到全文件 NUL 统计。

## Approach

诊断决策序列（四步闭环）：

1. **文本配置被判二进制 → 直接进字节层**：read/编辑器报 binary 时跳过语法排查，转字节层取证。
2. **首 3 字节排 BOM，但不据此放行**：`EF BB BF` 有则按整文件 BOM 处理（见 utf8-nobom 条目）；无则继续下一步——首字节正常≠文件健康。
3. **全文件 NUL 统计定性**：统计字节总数与 NUL 数（本例 `total=108 nul=46`）；nul>0 即存在 UTF-16 段/二进制序列，dump 内容确认形态。
4. **字节级重写 + 逐条验证**：以 UTF-8 无 BOM + LF 重写全文，逐条核对规则内容（顺带补缺失规则如 `__pycache__/`）；随后 `git check-ignore -v` 对**每一条**关键规则逐路径验证（本例 4/4 命中），禁止抽查单条后放行；修复随紧随提交入库形成闭环。

## Faster Next Time

- 最短诊断序：`read 报 binary` → `NUL 统计` → `字节级重写` → `check-ignore -v 全量复核`，分钟级闭环，全程不碰规则语法。
- **"部分规则生效"不是文件健康的证据**——.gitignore 体检必须逐规则 check-ignore；抽一条命中就放行会漏掉段级损坏。
- 见到"文本文件被判二进制"，唯一合理方向是字节层（NUL/非法序列），在内容层打转是无效功。
- 同源写通道纪律：凡经 PowerShell 管道/编码转换的写盘路径，写完即字节验证（与 BOM/CRLF、utf8-nobom 条目同一教训链）；对 .gitignore 的追加式写入尤其危险——追加段编码与前段不一致即产生本条故障形态。
- 防护类规则（屏蔽大文件/可执行文件/构建产物）失效的直接后果不止"目录脏"：大文件一旦推上远端会拖垮下游部署链路。

## Applicability Boundaries

- 适用：git 忽略类文件（`.gitignore`、`.git/info/exclude`、全局 exclude）及一切"纯文本配置被判二进制"的诊断场景；Windows + PS5.1 写通道环境高发。
- 不适用：整文件带 BOM 的判定（首 3 字节即可定性，见 utf8-nobom-write-verify-first-byte）；模式级 BOM/CRLF 杂字节不匹配（见 gitignore-rule-silent-failure-bom-crlf）；规则语法错误（先验证生效性再谈语法）。
- 证据边界：UTF-16 段的确切成因（哪次写操作、哪个通道）trace 未记录，基于本机 PS5.1 已知 UTF-16LE 落盘坑推断；其余检测、修复、验证步骤均为实测。

## Evidence or Examples

- 源会话：ses_e269dc135ffew1ZXbdWts1CLWs（Date 项目，教程第 3 步入口复查，11 条消息）；入口本体检查结论"已正确，无需改动"（该主题已另有条目 build-env/2026-11-14-vercel-python-zero-dep-wsgi-entry-pattern，本条只收录顺带发现的 gitignore 故障）。
- 损坏实况：前 2 行 `.obsidian/`、`.env` 为正常 UTF-8（故幸存）；后 4 行 `temp/*.mp4`、`workspace/**/*.exe`、`*.mp4`、`*.exe` 为 UTF-16（nul=46/total=108）。
- 修复验证链：重写后 `first3=46,111,98`（".ob"）且 `nul=0`；`git check-ignore -v` 4/4 命中——`*.mp4`→temp/toutiao_*/video.mp4、`*.exe`→workspace/06_开发工具/prepared/dev_sidecar/DevSidecar-2.3.5-windows-x86_64.exe、`__pycache__/`→api/__pycache__/index.cpython-311.pyc、`.env`→.env；untracked 洪水随之清空。
- 提交留痕：`baddcd0`（Fix .gitignore mixed UTF-16 corruption that silently disabled mp4/exe/pycache ignore rules，1 file changed, 0 insertions(+), 0 deletions(-)——"0 行变更"是 git 对二进制属性 diff 的计数形态，非空提交），推送 `4247c03..baddcd0 main -> main`。
- 无害项：重写时 `LF will be replaced by CRLF` warning 来自 core.autocrlf，不影响匹配。
- 遗留非阻塞项（trace 尾）：`workspace/02_软件源码/workflow_base/core/__pycache__/environment.cpython-311.pyc` 属历史提交中已被跟踪的 pyc，新规则不影响已跟踪文件，是否 `git rm --cached` 留待用户裁决。