# SDD 四步自检脚本 — 任务规划（tasks.md）

- 版本：v1.0　日期：2026-11-16　上游：spec.md v1.0 + design.md v1.0（均已读全文）
- 执行序硬依赖：T1 → T2 → T3 → T4（禁跳）

## T1 产物清单与路径处理（承接 U1/S1）
- [ ] 定义 STEP_FILES 有序表（四步→文件名）
- [ ] 校验入参目录存在且为目录，否则 exit 2
- [ ] 验证方式：`python sdd_check.py /not/exist` → exit 2

## T2 逐项检查（承接 E1-E4）
- [ ] 遍历 STEP_FILES，`is_file()` + 非空判定
- [ ] 缺失项记录步骤号与文件名
- [ ] 验证方式：空目录下跑 → 列出四个缺失步骤

## T3 退出码与输出（承接 AC1-AC3）
- [ ] 全绿打印 PASS + 4/4，exit 0
- [ ] 有缺失打印 FAIL 清单，exit 1
- [ ] 验证方式：造齐全目录 → PASS；删一文件 → FAIL

## T4 约束自查（承接 AC4）
- [ ] 纯 stdlib；单文件 ≤500 行；函数 ≤30 行
- [ ] 落盘脚本 `.workbuddy/specs/sdd_four_step_selfcheck/sdd_check.py`
- [ ] 验证方式：wc -l + 人工审函数长度 + 无 import 第三方

## 执行记录
- 第 4 步产物：`apply_record.md`（本任务执行实况与测试结果）
