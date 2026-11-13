---
id: 2026-11-11-dual-python-interpreter-path-contract
title: 双 Python 解释器的路径契约：解释器身份随调用通道变化，/mnt/c 与 C:/ 跟 traceback 形态选边
category: build-env
nature: pitfall
created_at: 2026-11-11T01:07:50
updated_at: 2026-11-11T01:07:50
tags: [WSL, 双解释器, 路径契约, WindowsPython, traceback指纹]
keywords: [/mnt/c, C:/, Windows Python, WSL Python, interop, FileNotFoundError, traceback 路径形态, io.open, 命令文件执行, 直调短命令]
problem_patterns:
  - "按既有'/mnt/c 契约'经验把独立 Python 脚本内部路径写成 WSL 形态，执行报 FileNotFoundError，误判为文件缺失或脚本写错"
  - "把'bash 是 WSL'当成整条链路的路径格式依据，忽视命令文件内执行与直调短命令两条通道解析到不同 Python 解释器"
  - "失败后先去找'文件是否存在'，未意识到 /mnt/c 对 Windows Python 根本不可解析，排查方向从一开始就错"
source_sessions: [ses_e39bfec85ffeYWVqiFQx41gRI4]
project: Date
severity: medium
quality_score: 87
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-09-wsl-bash-drive-letter-path-relativized, 2026-11-08-wsl-bash-mount-c-path-contract, 2026-11-08-wsl-bash-channel-mismatch-ps1-fallback]
---

# 双 Python 解释器的路径契约：解释器身份随调用通道变化，/mnt/c 与 C:/ 跟 traceback 形态选边

## Scenario

Windows + WSL 环境下执行"写命令文件再执行"或"写一次性 Python 脚本再调用"的流程（如增量更新收尾阶段用脚本对 JSON 状态文件做原子改写）。既有经验确立了"WSL 通道下路径统一改写 /mnt/c"的契约；按该契约把独立脚本（`finalize.py` 类收尾脚本）的内部路径也写成 `/mnt/c/...` 后执行，脚本启动即报 FileNotFoundError，且同一会话内写在命令文件里的其他 python 调用（内部路径同为 /mnt/c）却全部成功——两种结果并存，通道归属难以直觉判断。

## Key Signals

- **traceback 路径形态（决定性指纹）**：失败脚本的报错呈现 `File "C:\\Users\\...\\finalize.py", line N` 的 Windows 反斜杠形态——执行该脚本的解释器是 **Windows Python**，而非 WSL Python。
- 报错主体是 `io.open('/mnt/c/...')` → `FileNotFoundError`——Windows Python 不解析 WSL 挂载路径，`/mnt/c` 对它只是不存在的相对/无效路径。
- **对照信号**：同一会话中，写在 `_wiki_cmd.sh` 命令文件内执行的 python 调用（脚本安装路径、产物路径全部 `/mnt/c/...`）全部 success——该通道的解释器认 `/mnt/c`，即 WSL Python。
- 环境事实：`bash --version` 报 5.3.9 (x86_64-pc-linux-gnu)（WSL）与 `python --version` 报 3.11.9（Windows 安装）并存，两个运行时都在。

## Essence

同一台机器上存在两个 Python 运行时，**解释器身份随调用通道变化**：① 写入命令文件（.sh）后整批执行的 `python` → WSL bash 子进程内的解释器 → 认 `/mnt/c/`，不认 `C:/`；② 直调 `python <脚本>` 短命令（不经命令文件）→ 经 WSL interop/原生解析落到 Windows Python → 认 `C:/`，不认 `/mnt/c/`。路径格式必须**跟解释器走**，而不是跟"bash 是 WSL"这个通道标签走——把 /mnt/c 契约无差别套用到所有脚本内部路径，恰好在 Windows Python 通道上踩出反向坑。判定指纹就在 traceback 的 `File "..."` 路径形态里。

## Approach

1. **失败先读 traceback 形态**：`File "C:\..."`（反斜杠盘符）→ Windows Python；`File "/mnt/c/..."`（POSIX 挂载形态）→ WSL Python。这一步 5 秒完成，先于任何"文件是否存在"的排查。
2. **脚本内部路径按解释器选形态**：判定为 Windows Python → 内部路径改写 `C:/Users/...`（正斜杠，Python 在 Windows 下两种斜杠都接受）；判定为 WSL Python → 保持 `/mnt/c/...`。
3. **可移植兜底（可选）**：收尾类独立脚本内部用双形态探测——对关键路径先 `os.path.exists` 依次试两种形态取存在者，或按 `sys.platform` 分支拼路径；一次编写，两个解释器通吃。
4. **保持执行结构不变**：只改脚本内的路径字面量，不切换"写文件后执行"的调用结构，也不重装/重链 python——问题在路径语义层，不在运行时安装层。
5. **命令文件与独立脚本分治**：命令文件（.sh）内路径按 WSL 契约写 `/mnt/c`；独立 Python 脚本内部路径按其实际宿主解释器写——两类载体契约分离，不互相套用。

## Faster Next Time

- 判定表：traceback `C:\` 形态 + open('/mnt/c') 失败 → Windows Python，改 C:/；traceback `/mnt/c` 形态 + open('C:/') 失败（或报"工作目录 + C:/..." 拼接串）→ WSL Python，改 /mnt/c（见相邻经验）；报错与路径无关 → 先查参数契约与文件真实存在性。
- 首查动作：任何 Python 脚本 FileNotFoundError，第一眼看 traceback 的路径分隔符形态，再决定改哪侧路径——省掉"找文件→确认存在→再怀疑解释器"的弯路。
- ROI：一次形态判定 + 一次路径改写即可收尾；走错方向（去找文件、重装解释器、整通道切换）的代价是多轮无效排查。
- 反模式：见"/mnt/c 经验"就全量套用到独立脚本内部路径；把 FileNotFoundError 归因于"文件没生成"而发起产物重跑；为统一格式把命令文件内已成功的 /mnt/c 路径反向改坏。

## Applicability Boundaries

- 适用：Windows 宿主 + WSL interop 双解释器并存的环境，凡"命令文件内执行"与"直调短命令"两条通道混用的流程（收尾脚本、校验脚本、临时工具脚本通用）。
- 不适用：纯 WSL 或纯 Windows 单解释器环境（只有一种路径形态，无判定问题）；python 命令在两个通道被显式指向同一解释器的配置（如 PATH 统一接管后，此时以实际解析结果为准，判定指纹依然适用）。
- 与相邻经验分工：2026-11-08-wsl-bash-mount-c-path-contract 与 2026-11-09-wsl-bash-drive-letter-path-relativized 管"WSL Python 通道下 C:/ 失效（拼接指纹/全量改写）"；2026-11-08-wsl-bash-channel-mismatch-ps1-fallback 管"WSL 通道整体吞命令时的 ps1 降级"；本条管反向面——"Windows Python 通道下 /mnt/c 失效"，四者共同构成双运行时路径判定矩阵，按 traceback 形态选条目。

## Evidence or Examples

- 源会话 ses_e39bfec85ffeYWVqiFQx41gRI4（docgen-apply 主 Agent，Date 项目 Wiki 增量更新收尾阶段）。
- 失败实测（两次同因）：finalize_progress.py 内部路径写 `/mnt/c/...`，执行报 `File "C:\\Users\\Administrator\\Desktop\\Date\\.codeartsdoer\\temp\\finalize_progress.py", line 5 ... FileNotFoundError: [Errno 2] No such file or directory: '/mnt/c/.../progress.json'`——traceback 的 `C:\` 形态证明宿主是 Windows Python。
- 修复实测：脚本内路径改 `C:/Users/...` 正斜杠形态后一次成功，输出 `{"update_plan_cleared": true, "final_status": "completed"}`，收尾闭环。
- 对照实测：同会话 _wiki_cmd.sh 内 extract_symbols/reverse_lookup/build_index 等 python 调用，路径全为 `/mnt/c/...`，全部 success——命令文件通道解释器认 /mnt/c（WSL Python），与本坑通道形成同机双形态并存的确证。