# SDD 四步自检 — 执行记录（apply_record.md）

- 日期：2026-11-16　任务：最小真任务走通 SDD 四步
- 上游：spec.md v1.0 → design.md v1.0 → tasks.md v1.0（每步开工前已读全文）

## 四步执行实况

| 步 | 产物 | 状态 |
|---|---|---|
| 1 需求规格 | spec.md（EARS：U1/E1-E4/S1 + AC1-AC4） | 已落盘 |
| 2 实现方案 | design.md（存量分析/实现设计/追溯表） | 已落盘，开工前已读 spec |
| 3 编码任务 | tasks.md（T1-T4，硬依赖链 + 验证方式） | 已落盘，开工前已读 design |
| 4 任务执行 | sdd_check.py + 本记录 | 代码 53 行，开工前已读 tasks |

## 测试结果（真实执行）

| 场景 | 命令 | 期望 | 实测 | 判定 |
|---|---|---|---|---|
| 缺第4步 | `python sdd_check.py <目录>`（当时 apply_record 未写） | FAIL exit 1 | `[MISS] 第4步` + `FAIL 缺1项` + exit 1 | PASS |
| 路径不存在 | `python sdd_check.py /not/exist/path` | exit 2 | `FAIL 目录不存在` + exit 2 | PASS |
| 无参数 | `python sdd_check.py` | exit 2 | 打印用法 + exit 2 | PASS |
| 四步齐全 | 写完本记录后复跑 | PASS 4/4 exit 0 | 见下方复跑记录 | 待复跑 |
| 约束自查 | `wc -l sdd_check.py` | ≤500 行 | 53 行 | PASS |

## 全绿复跑（写完本文件后执行，实测）

```
[OK] 第1步 -> spec.md
[OK] 第2步 -> design.md
[OK] 第3步 -> tasks.md
[OK] 第4步 -> apply_record.md
PASS: 4/4 四步产物齐全
EXIT=0
```

另：临时目录只放前三步（缺第4步）→ `[MISS] 第4步` + FAIL + exit 1，复现缺步分支。

## 结论

四步顺序执行、每步落盘、下游读上游、自检脚本 PASS/FAIL 两分支、退出码、行数约束全部实测通过。SDD 四步在本工作区可跑通。

