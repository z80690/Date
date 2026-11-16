# SDD 四步自检脚本 — 实现方案（design.md）

- 版本：v1.0　日期：2026-11-16　上游：spec.md v1.0（已读全文）
- 承接 EARS：U1/E1-E4/S1 → 本设计逐条落位

## 存量分析

- 复用：项目现有纯 stdlib Python 约定（adapter/ 风格：Path 推导路径、exit code 可判）。
- 新增：单文件 `sdd_check.py`，无既有同类工具（已查 .workbuddy/scripts 无残留门禁脚本）。
- 不引入：无第三方依赖、无 DB、无定时器。

## 实现设计

### 产物清单映射（承接 E1-E4）
STEP_FILES 有序表 = [(1, spec.md), (2, design.md), (3, tasks.md), (4, apply_record.md)]。
按序检查 `is_file()` 且 `stat().st_size > 0`，缺一即记 FAIL 并带步骤号。

### 退出码（承接 S1/E4）
- 目录不存在或非目录 → 打印错误，exit 2。
- 任一产物缺失/空 → 打印逐项 FAIL，exit 1。
- 四项齐全 → 打印 PASS + "4/4"，exit 0。

### CLI
`python sdd_check.py <目录路径>`；无参数时打印用法，exit 2。

## 决策与理由

- 产物名用 `apply_record.md` 而非代码文件：本验证任务的执行记录即第 4 步产物，便于机械判定；真实编码项目第 4 步产物是代码，届时改判定项为代码路径（留接口）。
- 只验存在与非空：内容对错机器判不了，交人工门禁（对齐 EARS 范围外 + 六条公约"编码必审"）。

## 追溯表

| EARS | 设计落位 |
|---|---|
| U1 | CLI + STEP_FILES 检查 |
| E1-E4 | STEP_FILES 逐项检查 + 缺失步骤提示 |
| S1 | 目录校验分支 exit 2 |
| AC1-AC3 | 退出码设计 |
| AC4 | 纯 stdlib + 行数约束 |
