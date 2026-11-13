---
id: 2026-11-13-pytest-sessionfinish-winerror5-cleanup-noise
title: "pytest 全 PASSED 尾部 PermissionError(WinError 5) 是 sessionfinish 临时目录清理噪音，按测试计数定性勿误判失败"
category: debugging
nature: pitfall
created_at: 2026-11-13T10:08:40
updated_at: 2026-11-13T10:08:40
tags: [pytest, Windows, 收尾噪音, 误判失败, WinError 5]
keywords: [PermissionError WinError 5, pytest-of-Administrator pytest-current, sessionfinish 钩子, cleanup_numbered_dir, cleanup_dead_symlinks, _pytest tmpdir, 测试计数定性, basetemp 重定向, Defender 目录锁, 汇总行被吞]
problem_patterns: [pytest 输出全部测试 PASSED 后尾部冒出 PermissionError，summary 与 exit code 被截断，误以为测试失败而重跑, Windows 上 pytest 收尾清理临时目录触发 WinError 5 拒绝访问，噪音掩盖真实测试结果判读]
source_sessions: [ses_e2f4e2eebffe77jZBS1o85Z7rc]
project: Date
severity: low
quality_score: 86
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-10-os-replace-winerror5-transient-lock-retry, 2026-11-07-powershell-stderr-native-command-error-false-failure]
---

# pytest 全 PASSED 尾部 PermissionError(WinError 5) 是 sessionfinish 临时目录清理噪音，按测试计数定性勿误判失败

## Scenario

Windows（Defender 实时防护开启）上执行 `python -m pytest`，全部测试用例已打印 `PASSED [100%]`，随后 session 尾部抛出 `PermissionError: [WinError 5] 拒绝访问`，路径指向 `...\AppData\Local\Temp\pytest-of-<user>\pytest-current`——最后的汇总统计行与 exit code 被吞。第一反应极易判为"测试环境异常/门禁未过"而重跑。

## Key Signals

- **位置信号**：异常出现在所有测试结果行之后（如 `tests/test_adapter.py::TestVerdict::test_missing_counts_raise PASSED [100%]` 之后）——不是测试体抛的。
- **路径信号**：报错路径含 `Temp\pytest-of-<user>\pytest-current`——是 pytest 的编号临时目录（tmp_path factory），非项目代码路径。
- **栈信号**：traceback 顶层栈帧为 `_pytest/tmpdir.py` 的 `pytest_sessionfinish → tmp_path_factory._exit_stack.close() → cleanup_numbered_dir → cleanup_dead_symlinks → os.stat`——清理钩子在扫描符号链接时撞上被锁目录。

## Essence

根因链条：pytest 结束时 sessionfinish 钩子递归清理 `pytest-of-<user>` 编号临时目录 → `cleanup_dead_symlinks` 对历史目录做 `resolve().exists()`/`os.stat` → 该目录正被 Defender 扫描或句柄未释放（Windows 目录锁瞬时态）→ 抛 WinError 5。**异常发生在测试执行全部完成之后**，属于收尾清理噪音：它改变不了任何测试结果，只影响尾部汇总的可读性。判定规则因此确立：测试是否通过只看测试结果段（PASSED/FAILED 计数与用例总数比对），收尾段的异常不参与门禁判定，更不构成重跑理由。

## Approach

1. **先定性后行动**：数测试结果段的 PASSED/FAILED 数量并与收集用例总数比对；一致即通过，收尾 WinError 5 记为噪音（与 `2026-11-07-powershell-stderr-native-command-error-false-failure` 的"尾部 stderr 不定性失败"同属结果段/收尾段切分判定）。
2. **需要干净汇总时**（报告/留痕场景）：
   ```
   python -m pytest tests/ --basetemp=C:/project/temp/pytest-tmp
   ```
   basetemp 指到项目内自定义目录，绕开系统 Temp 上 Defender 的锁竞争；或 `-p no:cacheprovider` 减少收尾写入面。
3. **门禁脚本防误判**：CI/门禁包装层用 exit code 而非"输出末行无异常"判定成败——噪音会出现在末行，exit code 不会说谎。
4. **不要做的事**：不要因收尾异常重跑整轮测试；不要去手动清理 `pytest-of-<user>` 目录（锁释放后 pytest 自行轮转）；不要把 WinError 5 写进门禁失败记录。

## Faster Next Time

- 判定口诀：**异常栈在 sessionfinish = 收尾噪音；异常栈在测试函数 = 真失败**——先看栈帧归属再看异常内容。
- 结果段/收尾段切分法：pytest 输出按最后一个 `PASSED/FAILED [100%]` 行切成两段，门禁判定只消费前段+exit code。
- Windows 上批量跑测试且要看干净报告时，**首轮就带 `--basetemp`** 指向项目内路径，省掉一次噪音判读。
- 同族信号归并：`os.replace` 写文件的 Defender 瞬时锁（见 related 经验）与本次 tmp 清理锁同根因（Windows 目录瞬时锁），处置都是"重试或绕路径"，都不是代码缺陷。

## Applicability Boundaries

- 适用：Windows + Defender 实时防护环境下 pytest 收尾噪音判定；tmp_path/tmpdir 相关清理异常。
- 不适用：测试执行**中途**出现的 WinError 5（那是测试体或 fixture 的真失败，按常规失败处理）；Linux/macOS（无 Defender 目录锁，收尾异常罕见）；pytest 版本差异可能导致清理钩子栈帧路径不同（本例实测于 pytest with python 3.11 / Windows Server 系宿主），但"sessionfinish 归属 = 噪音"的判定原则不变。

## Evidence or Examples

- 本例实录（ses_e2f4e2eebffe77jZBS1o85Z7rc，2026-11-13，P003 适配层门禁）：`python -m pytest tests/test_adapter.py` 输出 20/20 全 PASSED（末行 `tests/test_adapter.py::TestVerdict::test_missing_counts_raise PASSED [100%]`），随后尾部抛 `PermissionError: [WinError 5] ... 'C:\\Users\\Administrator\\AppData\\Local\\Temp\\pytest-of-Administrator\\pytest-current'`，summary 被吞；重跑取干净汇总仍复现同噪音；按计数定性为噪音非门禁失败，门禁放行并登记于 gates 留痕（未因噪音重跑第二轮门禁判定）。
- 栈帧证据：traceback 顶层 `File "..._pytest\warnings.py", line 119, in pytest_sessionfinish` → `tmpdir.py line 340 in pytest_sessionfinish → tmp_path_factory._exit_stack.close()` → `pathlib.py line 356 in cleanup_dead_symlinks: if not left_dir.resolve().exists()`。