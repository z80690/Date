---
id: 2026-11-13-ps-redirect-utf16-structure-corruption-orchestrator-capture
title: PowerShell 重定向第二形态 UTF-16LE 落盘且 JSON 结构被管道破坏：Python orchestrator 二进制捕获绕开管道
category: debugging
nature: pitfall
created_at: 2026-11-13T11:48:45
updated_at: 2026-11-13T11:57:27
tags: [编码失真, PowerShell重定向, UTF-16LE, JSON结构破坏, subprocess捕获]
keywords: [0xff 解码失败, UTF-16LE BOM, Invalid control character, python 重定向落盘, capture_output 二进制捕获, orchestrator 模式, PS5.1 管道转码, PYTHONIOENCODING, 脚本不可改场景, 多 job 统一捕获, 解码修正无效]
problem_patterns: ["python 脚本 JSON 输出经 PowerShell > 重定向落盘后文件变 UTF-16LE，utf-8 读取报 0xff 解码错", "改用 utf-16 解码能读出文本但 json.loads 报 Invalid control character——解码修正解决不了管道破坏", "skill 分发脚本不可改、多 job 输出需统一落盘时的捕获通道选型"]
source_sessions: [ses_e2d0191d6ffejSEq6m0pmTb0hf]
project: Date
severity: medium
quality_score: 84
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: A
related_experiences: [2026-11-10-python-print-redirect-gbk-mojibake-write-file-directly, 2026-11-09-cli-subprocess-utf8-ansi-decode-mojibake, 2026-11-11-python-wrapper-json-job-runner]
---

# PowerShell 重定向第二形态 UTF-16LE 落盘且 JSON 结构被管道破坏：Python orchestrator 二进制捕获绕开管道

## Scenario

Windows + PowerShell 5.1 环境执行 skill 分发的 Python 脚本（实例：extract_sections.py、extract_changed_snippets.py），脚本以 stdout 输出 JSON 结果，编排层需把结果落盘为 JSON 文件供后续读取。约束：脚本不可改（skill 产物，改了要随 skill 升级重做），且多个 job 需要统一捕获落盘。此时最常见的写法是 `python script.py > out.json`——踩中重定向故障链的第二形态。

## Key Signals

- **第一信号**：落盘文件用 `open(..., encoding='utf-8')` 读取报 `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte`——0xFF 头是 UTF-16LE BOM 特征，说明管道这次按 UTF-16 转码而非上一形态的 GBK。
- **误导线索**：改用 utf-16 解码能读出文本，容易就此以为"换个编码读就行"；但接着 `json.loads` 报 `Invalid control character`——**解码修正不解决问题**，因为破坏发生在转码写盘环节，文件本体已被污染，不是显示层或读取层问题。
- **与第一形态的指纹区分**：GBK 乱码形态（2026-11-10 条）内容可见但中文失真、ASCII 完好；本形态连 JSON 结构边界都被破坏，两者修复手段完全不同，凭"内容还能读"误判为编码小问题会走弯路。

## Essence

根因链：Python 脚本按 UTF-8 写 stdout → PS5.1 `>` 重定向管道按 UTF-16LE 转码落盘 → 转码过程破坏 JSON 文本的结构边界（引号/控制字符序列）→ 文件本体污染。修复 = 彻底绕开 PS 管道：写一个 **Python orchestrator**，用 `subprocess.run(..., capture_output=True)` 二进制捕获子进程 stdout 直接写盘（配 `PYTHONIOENCODING`/`PYTHONUTF8` 环境变量保证子进程输出 UTF-8），全链零编码转换损耗。该模式覆盖"脚本不可改"与"多 job 统一捕获"两个直写文件模式无法覆盖的场景。

## Approach

诊断决策序（按序排除，勿跳步）：

1. 落盘文件 utf-8 读取报 **0xff 解码错** → 判定 PS 重定向 UTF-16 形态；此时**不要再尝试换解码重读**——即使读出文本，结构可能已坏，直接进下一步定性。
2. 解码读出后 `json.loads` 报错（Invalid control character 等）→ 确认管道破坏了文件本体，该落盘链路整体作废，换通道而非修数据。
3. 修复分派（按约束选通道）：
   - 脚本**可改** → 脚本内 `open(..., encoding="utf-8")` 直写结果文件（2026-11-10 条），stdout 只留进度行；
   - 脚本**不可改**或需**多 job 统一捕获** → Python orchestrator：`subprocess.run([sys.executable, script, args...], capture_output=True, env={...PYTHONIOENCODING/PYTHONUTF8...})`，对 `result.stdout`（bytes）直接二进制写盘。
4. 验证：落盘文件 `json.loads` 通过 + 字节数与 job 实际输出量级一致（每个 job 单独核对 rc 与 bytes），无 0xff 头。

## Faster Next Time

- 预防模式：凡"脚本产物 JSON 需落盘供编排读取"的场景，禁走 PS `>` 重定向，直接上 Python orchestrator 或脚本直写——本机 PS5.1 下 stdout 重定向落盘没有可靠形态。
- 本机 PS5.1 中文/结构失真四故障链补全：**print 经重定向 GBK 化** → 脚本内直写（2026-11-10 条）；**print 经重定向 UTF-16 化+结构破坏** → orchestrator 捕获（本条）；**外部 CLI 进捕获层 ANSI 解码** → `[Console]::OutputEncoding`（2026-11-09 条）；**读文件显示层乱码** → 先验文件本体再定性（2026-11-08 条）。四者按"故障层"定位，修复手段互不通用。
- 最短定位路径：0xff 头 → UTF-16 形态；乱码但 ASCII 完好 → GBK 形态；两者都以"文件本体已污染"为共同结论，重跑换通道优于逆向还原。
- 反模式：把 orchestrator 产物再经 PS 管道二次重定向；只在读取侧反复换编码尝试而不怀疑落盘链路。

## Applicability Boundaries

- 适用：Windows + PowerShell 5.1 下 Python（或任何 UTF-8 stdout 程序）输出经 `>`/管道落盘的场景；多 job 批量执行需统一捕获；脚本不可改的 skill/第三方分发脚本消费。
- 不适用：PowerShell 7+ 与 Linux/macOS（重定向字节透传，无此问题）；脚本内已直写文件且无需捕获 stdout 的场景；单条命令手动调试场景（控制台直看输出不经落盘）。
- 边界：`[Console]::OutputEncoding=UTF8` 对 `>` 落盘层的修复效果未实测（见 2026-11-10 条边界注记），orchestrator 是已实测的唯一可靠路径；orchestrator 自身脚本内路径一律 `C:/` 正斜杠 Windows 风格，避免引入双解释器路径问题。

## Evidence or Examples

- 来源会话 ses_e2d0191d6ffejSEq6m0pmTb0hf（docgen-apply fork #1，Date 项目 Wiki 增量更新，2026-11-13）。
- 失败链实测：`python extract_sections.py > out.json` 落盘 → utf-8 读报 `can't decode byte 0xff in position 0` → 改 utf-16 解码读出文本 → `json.loads` 报 `Invalid control character`（7 个 JSON 全部解析失败）。
- 修复实证：Python orchestrator（capture_output=True + PYTHONUTF8 env，逐 job 二进制落盘）后 7 个 job 全部 `rc=0`，bytes 实测 sections_P003=1874 / sections_temp=2698 / sections_notes=2727 / sections_business_term=4304 / sections_dependency=1805 / sections_error=2663 / changed_snippets=21995，全部 `json.loads` 通过。
- 通道选型佐证：该场景脚本为 skill 分发产物不可改、且一次要捕获 7 个 job，正是直写文件模式（脚本可改前提）无法覆盖的组合，orchestrator 模式一次落位。