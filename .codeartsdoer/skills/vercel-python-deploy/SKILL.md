---
name: vercel-python-deploy
description: Python 项目部署到 Vercel 的完整契约与故障排查：api/index.py 暴露 app WSGI 变量的入口约定、vercel.json builds 显式入口配置（防 temp/mock 脚本被误认为入口候选）、.vercelignore 屏蔽非部署目录、本地 WSGI 冒烟测试、以 GitHub commit status API 为权威部署状态验证（勿猜 *.vercel.app 域名）、vercel.app 域名国内直连被墙（HTTP=000）的访问路径、修复必须推到部署平台实际连接的仓库。凡涉及 Vercel 部署失败（PYTHON_ENTRYPOINT_NOT_FOUND 等）、部署 Python/Web 服务到 Vercel、确认部署是否成功、vercel.app 打不开/HTTP 000、构建日志报找不到 Python 入口点、部署仓库与本地仓库不一致排查时使用。
---

# Vercel Python 部署契约与排查

## 1. 部署失败第一查：修复是否推到了部署平台实际连接的仓库

本地 origin 与 Vercel 连接的仓库可能不同（用户手动上传快照建仓 vs 本地完整历史仓）。

- 以 Vercel 构建日志第一行"克隆 github.com/{owner}/{repo} (提交：{sha})"为部署目标真身（截图 OCR 仓库名可能误读，如 z2006900≠z80690，以 `git ls-remote` 实测 HEAD 比对日志提交号为准）
- 修复必须落到该仓库，推到本地 origin 无效

## 2. 入口契约（PYTHON_ENTRYPOINT_NOT_FOUND 两大成因）

1. 部署仓库无 `api/index.py`（Vercel 约定默认入口位置）
2. 仓库里没有入口但存在多个含 handler 变量的 .py（如 temp/ 下演练 mock），Vercel 扫描全仓把它们列为候选并报错

**入口文件要求**：`api/index.py` 暴露名为 `app` 的 WSGI callable；仅用标准库则无需 requirements.txt。最小可用模式（已实测 200）：

```python
import json
class RequestHandler:
    def __call__(self, environ, start_response):
        payload = json.dumps({"status": "ok"}).encode("utf-8")
        start_response("200 OK", [("Content-Type", "application/json; charset=utf-8"),
                                  ("Content-Length", str(len(payload)))])
        return [payload]
app = RequestHandler()
```

**构建配置**（vercel.json）——builds 显式指定 src 后 Vercel 不再扫描仓库其他 .py 作为候选：

```json
{
  "builds": [{"src": "api/index.py", "use": "@vercel/python"}],
  "rewrites": [{"source": "/(.*)", "destination": "api/index.py"}]
}
```

**红线**：构建日志建议的 `[tool.vercel] entrypoint = "temp.mock_llm_server: Handler"` 不可照做——那是本地演练 mock（绑定 127.0.0.1），部署后不可用。

## 3. .vercelignore（缩小构建上下文+屏蔽候选扫描）

```
temp/
DVWA/
workspace/
notes/
tests/
.codeartsdoer/
.workbuddy/
.obsidian/
.pytest_cache/
.ruff_cache/
.env
```

`.env` 必含敏感凭据，绝不进 Vercel 构建上下文。

## 4. 本地冒烟（不起服务器）

```powershell
python -c "import sys; sys.path.insert(0,'api'); from index import app; env={'PATH_INFO':'/','REQUEST_METHOD':'GET'}; out=[]; app(env, lambda s,h: out.append((s,h))); print(out[0][0])"
```

期望输出 `200 OK`。

## 5. 部署状态权威验证：GitHub commit status API

push 后约 30-90 秒，Vercel GitHub App 会向部署 commit 回写状态。比猜 *.vercel.app 域名可靠：

```
GET https://api.github.com/repos/{owner}/{repo}/commits/{sha}/status
Authorization: Bearer <token from "git credential fill">
```

`state: success` + `context: Vercel` 即部署成功，`target_url` 为控制台链接。凭据来源：`git credential fill`（stdin=`protocol=https\nhost=github.com\n\n`）读取 GCM 缓存，token 不落盘不打印。

## 6. vercel.app 域名国内直连被墙

`https://<project>.vercel.app` 直连 HTTP=000（DNS 污染），平台 webfetch 同样 socket closed。部署 success 但域名不通≠部署失败。访问路径：本机代理（DevSidecar `127.0.0.1:31181` / tor `9050`，启动与否先 Test-NetConnection 核实）或 Vercel Settings→Domains 绑自定义域名（CNAME 解析可国内直连）。

## 7. 本机大传输被墙时的修复通道

SSH 元数据通但 blob 大传输卡死时，走 partial clone 或 GitHub Git Data API 远端建提交，详见 windows-git-powershell-quirks 技能"GitHub 大传输三级降级链"。
