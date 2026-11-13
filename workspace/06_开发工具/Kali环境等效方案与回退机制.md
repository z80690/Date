# Kali 环境等效方案与回退机制（任务 4.2）

> 口径：spec 5.2.1 规则 2/3——嵌入式 Kali 回退、业务行为一致；攻防 Kali 主用、
> Kali 未就绪拒绝启动，是否切换 Windows 等效环境由用户决策（5.2.3 异常 2）。

## 一、路由规则（环境编排器已实现）

| 类目环境声明 | Windows 可用 | Windows 不可用 | Kali 未就绪 |
|--------------|-------------|---------------|-------------|
| windows 优先（kali 回退） | Windows 本机直启 | 自动回退 Kali，行为一致 | — |
| kali 主用 | — | — | 拒绝启动 + 提示可由用户决策切换 Windows 等效 |

- 路由实现：`workflow_base/core/environment.py` `route()`；环境卡片来自类目级契约声明。
- 回退判据：Windows 依赖无法落地时记录失败原因并输出 Kali 回退指引（不静默降级）。

## 二、Kali 等效启动方案（嵌入式回退用）

1. WSL/Kali 本机内安装 Python 3.11。
2. 同一份源码目录（`02_软件源码/workflow_base`）在 Kali 内直接运行，命令与 Windows 完全一致：
   `python -m workflow_base.cli selfcheck` / `mount` / `serve`。
3. 落盘目录同构：`04_测试验证`（Kali 内路径挂载点自行映射），闭环判据（注册+下发+回执=跑通）与 Windows 一致。
4. 回环红线不变：全部监听 127.0.0.1。

## 三、攻防 Kali 主用与用户决策切换

- 攻防类目环境声明 `primary=kali`（见 adapters/security_research.py 类目契约）。
- Kali 未就绪时：`route()` 抛 KALI_NOT_READY，任务拒绝启动（第一道防线联动）。
- 切换 Windows 等效环境必须由用户显式决策（底座不自动切换），切换后走同一套受理链与红线校验。

## 四、验证口径

- Windows 某依赖无法落地 → Kali 内等效流程跑通同样的挂载与任务下发、闭环判据一致（规则 2）。
- 当前 Windows 主路径已全绿（50 测试 + 闭环验证 all_pass），Kali 等效流程在切机时按本文件执行并回填验证记录。