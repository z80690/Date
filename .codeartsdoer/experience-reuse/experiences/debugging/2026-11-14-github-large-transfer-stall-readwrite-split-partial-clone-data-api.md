---
id: 2026-11-14-github-large-transfer-stall-readwrite-split-partial-clone-data-api
title: GitHub 大传输卡死三级降级链：读写分流分型诊断 → partial clone 只拉树 → Git Data API 远端建提交
category: debugging
nature: technique
created_at: 2026-11-14T18:44:44
updated_at: 2026-11-14T18:44:44
tags: [github, 传输卡死, partial-clone, git-data-api, 降级链]
keywords: [github 卡死, 读写分流诊断, ls-remote 秒通, clone 卡死 pack 0 字节, partial clone blob:none, Git Data API blobs trees commits, credential fill, 远端建提交, 同通道重试纪律, 传输停滞分型]
problem_patterns:
  - git clone 对含大文件的仓库长时间无进展（pack 文件 0 字节），ls-remote 却秒回，误判为凭据或整体网络故障反复重试同一通道
  - 需要把修复提交落到远端仓库，但本地对象写持续挂死，任务整体卡死不知还有哪条路可走
  - 对卡死通道反复同命令重试，每次超时转后台且输出零增量，白白消耗等待轮次
source_sessions: [ses_e2663e19effewWyExkRIOfefi6]
project: Date
severity: high
quality_score: 90
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [debugging/2026-11-06-github-api-vs-git-protocol-channel-split, debugging/2026-11-14-partial-clone-blobless-auto-maintenance-write-stall, build-env/2026-11-12-git-url-config-noproxy-silent-proxy-override, debugging/2026-11-14-git-init-soft-reset-empty-index-empty-tree-commit-hazard]
---

# GitHub 大传输卡死三级降级链：读写分流分型诊断 → partial clone 只拉树 → Git Data API 远端建提交

## Scenario

受限网络环境下需要对 GitHub 仓库执行"读取基线 + 写入修复提交"的完整操作。clone 等大传输操作卡死，同通道重试无增量信息；若不能落提交，修复链路整体中断。

## Key Signals

- **读写分流分型**（决定性）：元数据操作（`git ls-remote`、REST API 元数据查询）秒级返回，而对象传输与写入（clone、pack 接收、add/commit/write-tree）90s+ 无进展、后台输出文件 0 字节——这是传输通道问题，不是凭据问题也不是权限问题。
- clone 卡死的物理证据：仓库目录内 `tmp_pack_*` 文件 0 字节且长时间不增长。
- partial fetch 成功对照：`--filter=blob:none --depth 1` 的 fetch 秒级完成（fetch_exit=0）——通道只对大 blob 传输失效。
- 凭据可用性信号：`git credential fill` 能返回已缓存的账号与 token——本地写即使全灭，远端 API 通道有凭据可用。

## Essence

GitHub 通道在受限网络下呈现"元数据通、对象传输卡"的分化形态。降级链的核心逻辑是把每次动作的传输量逐级压到通道能承载的量级：① 读写分流诊断定型（元数据秒回 = 通道可用，只卡大传输）；② partial clone 把读取量从几百 MB 压到几百 KB（只拉 commit+tree，blob 按需留空）；③ 本地对象写也依赖隐式大传输（见 gc 陷阱）时，直接绕开本地对象库，用 GitHub Git Data API 在远端构建提交——blob→tree→commit→update ref 全部是 KB 级 JSON 请求。

## Approach

1. 同命令卡死 2 次后停止重试，先做读写分流测试：`git ls-remote <url>` 若秒回即分型成立，进入降级链；
2. **第②级（partial clone）**：`git init` → `git remote add origin <url>` → `git fetch --filter=blob:none --depth 1 origin <branch>`（只拉 commit+tree）→ `git reset --mixed FETCH_HEAD` 回填索引（**禁用 --soft**，见空索引事故篇）；
3. **第③级（远端建提交）**：写操作仍卡死时，`git credential fill`（stdin=`protocol=https\nhost=github.com\n\n`）提取本机凭据管理器的 token；
4. REST 序列（单 commit 多文件）：`GET /git/ref/heads/<branch>` 取基线 sha → `GET /git/commits/{sha}` 取 base tree → `POST /git/blobs`（content=base64, encoding=base64，每文件一次）→ `POST /git/trees`（base_tree + entries）→ `POST /git/commits`（tree + parents）→ `PATCH /git/refs/heads/<branch>` 前移引用；
5. token 只在脚本内流转，不落盘不打印；完成后清理临时仓库目录与脚本。

## Faster Next Time

- 判定顺序固定：同通道 2 次卡死 → 读写分流测试 → 分型成立即降级，禁止第 3 次同命令重试；
- "向部署平台连接的远端仓落修复"类任务，可跳过 clone 直接走 API 建提交——远端只需要最终树，不需要本地工作副本；
- ls-remote 秒回即可确认 SSH/API 元数据通道健康，这一信号同时用于排除"整体断网"误判。

## Applicability Boundaries

- 适用：GitHub（支持 filter 协议与 Git Data API）；本机凭据管理器已缓存有效凭据（无凭据时需用户侧授权获取）；
- 不适用：非 GitHub 平台（API 形态不同）；匿名场景（Git Data API 需认证，且有限流配额）；需要本地跑通源码的任务（partial clone 无 blob，构建会缺文件，须另取 blob 或转 release 产物路线）；
- 降级链第②③级为 2026-11-14 单窗口实证，通道分化形态随网络策略可能变化，复用前先做一次读写分流测试。

## Evidence or Examples

- 来源会话：ses_e2663e19effewWyExkRIOfefi6（2026-11-14）。
- 卡死实证：SSH clone my-date 快照仓转后台 15s+，`tmp_pack_0D5pv2` 0 字节；同窗口 `ls-remote` 秒回（HEAD=645ef8a）——读写分化成立。
- partial clone 实证：`fetch --filter=blob:none --depth 1` 秒级完成（fetch_exit=0），目录列表即见快照全部 14 个顶层条目。
- 远端建提交实证：credential fill 返回 username=z80690 + token（不落盘）；API 序列一次成功：blob ×4 ok → tree ok（6bd5b3156f）→ commit ok（f34fe22825）→ ref updated → main=f34fe22825。
- 验证闭环：`ls-remote` 复查两仓各自 HEAD（Date=baddcd0、my-date=f34fe228），确认修复各归其位。