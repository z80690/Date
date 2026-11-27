"""ARTEX 的大脑桥接（WorkBuddy-in-the-loop，本地回环，零费用）。

工作方式（回执模式，可调参数全在 bridge_config.json）：
  1. ARTEX 把每次 LLM 请求 POST 到 /chat/completions
  2. 本端点把请求原文落盘到 requests/NNNN.json（可逐字审计"ARTEX 问了什么"）
  3. 等 WorkBuddy（我）把判断写进 answers/NNNN.json（可逐字审计"我答了什么"）
  4. 端点读 answer，包成 OpenAI chat.completion 格式返回给 ARTEX

手动模式=真·大模型在回路（我现场读现场答）；自动模式=按文件里的策略规则答（打折方案）。
只绑 127.0.0.1，不联网、不调任何付费 API、API key 由调用方假填（占位）。
"""
import json
import os
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
CFG_PATH = os.path.join(HERE, "bridge_config.json")

with open(CFG_PATH, encoding="utf-8") as fp:
    CFG = json.load(fp)

HOST = CFG["listen"]["host"]
PORT = int(CFG["listen"]["port"])
MODEL_ID = CFG["model"]["id"]
TEMP = CFG["model"].get("temperature", 0.2)
MAX_TOKENS = CFG["model"].get("max_tokens", 2048)
REQ_DIR = os.path.join(HERE, CFG["receipt"]["requests_dir"])
ANS_DIR = os.path.join(HERE, CFG["receipt"]["answers_dir"])
POLL = float(CFG["receipt"].get("poll_interval_sec", 0.3))
TIMEOUT = float(CFG["receipt"].get("wait_timeout_sec", 600))
MODE = CFG["receipt"].get("mode", "manual")
TRAP = CFG["defense"].get("trap_token", "AUDIT_LOG")
DETECT = bool(CFG["defense"].get("detect_in_reply", True))

os.makedirs(REQ_DIR, exist_ok=True)
os.makedirs(ANS_DIR, exist_ok=True)

SEQ = 0


def last_content(messages):
    """取最后一条 user/assistant 文本，便于我快速判断 ARTEX 想要什么。"""
    out = []
    for m in messages or []:
        role = m.get("role", "")
        c = m.get("content", "")
        if isinstance(c, list):
            c = " ".join(
                str(x.get("text", "")) for x in c if isinstance(x, dict)
            )
        out.append(f"[{role}] {str(c)[:600]}")
    return "\n".join(out[-6:])


class Handler(BaseHTTPRequestHandler):
    def _reply_json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _reply_sse(self, content):
        """流式响应（ARTEX 默认 stream=true），用标准 OpenAI delta 帧。"""
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        cid = "chatcmpl-wb"

        def frame(o):
            return ("data: " + json.dumps(o, ensure_ascii=False) + "\n\n").encode("utf-8")

        self.wfile.write(frame({
            "id": cid, "object": "chat.completion.chunk", "created": int(time.time()),
            "model": MODEL_ID,
            "choices": [{"index": 0, "delta": {"role": "assistant", "content": ""}, "finish_reason": None}],
        }))
        # 分块发，模拟正常流
        step = 240
        for i in range(0, len(content), step):
            self.wfile.write(frame({
                "id": cid, "object": "chat.completion.chunk", "created": int(time.time()),
                "model": MODEL_ID,
                "choices": [{"index": 0, "delta": {"content": content[i:i + step]}, "finish_reason": None}],
            }))
        self.wfile.write(frame({
            "id": cid, "object": "chat.completion.chunk", "created": int(time.time()),
            "model": MODEL_ID,
            "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
        }))
        self.wfile.write(b"data: [DONE]\n\n")
        self.wfile.flush()

    def do_GET(self):
        if self.path.startswith("/v1/models") or self.path.startswith("/models"):
            self._reply_json({"object": "list", "data": [{"id": MODEL_ID, "object": "model", "owned_by": "workbuddy"}]})
        elif self.path.startswith("/health"):
            self._reply_json({"status": "ok", "mode": MODE, "model": MODEL_ID, "seq": SEQ})
        else:
            self._reply_json({"error": {"message": "workbuddy bridge"}}, 404)

    def do_POST(self):
        global SEQ
        length = int(self.headers.get("Content-Length", 0) or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            req = json.loads(raw)
        except Exception:
            req = {}
        SEQ += 1
        seq = f"{SEQ:04d}"
        messages = req.get("messages", [])
        stream = bool(req.get("stream", False))

        # 1. 请求原文落盘
        rec = {
            "seq": seq,
            "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "path": self.path,
            "stream": stream,
            "model_requested": req.get("model"),
            "messages_summary": last_content(messages),
            "full_request": req,
        }
        req_file = os.path.join(REQ_DIR, f"req_{seq}.json")
        with open(req_file, "w", encoding="utf-8") as fp:
            json.dump(rec, fp, ensure_ascii=False, indent=2)
        print(f"[bridge] REQ {seq} saved ({len(messages)} msgs, stream={stream})", flush=True)

        # 2. 取回答（支持 content 或完整 message 含 tool_calls）
        ans_file = os.path.join(ANS_DIR, f"ans_{seq}.json")
        answer = None
        deadline = time.time() + TIMEOUT
        while time.time() < deadline:
            if os.path.exists(ans_file):
                try:
                    with open(ans_file, encoding="utf-8") as fp:
                        answer = json.load(fp)
                    break
                except Exception:
                    time.sleep(POLL)
                    continue
            time.sleep(POLL)

        if answer is None:
            answer = {
                "content": (
                    "[workbuddy-bridge] 等待回答超时；请写 answers/ans_%s.json。\n" % seq
                    + "当前任务：继续本地靶场的安全评估流程，仅操作 127.0.0.0/8 回环资产。"
                )
            }

        # 统一成 assistant message
        if isinstance(answer, dict) and "message" in answer:
            msg = answer["message"]
        elif isinstance(answer, dict) and "tool_calls" in answer:
            msg = {
                "role": "assistant",
                "content": answer.get("content", ""),
                "tool_calls": answer["tool_calls"],
            }
        else:
            msg = {
                "role": "assistant",
                "content": answer.get("content", "") if isinstance(answer, dict) else str(answer),
            }
        msg.setdefault("role", "assistant")
        content = msg.get("content", "")
        has_tools = bool(msg.get("tool_calls"))

        # 3. 防守检测：诱饵 token 是否被触发
        if DETECT and TRAP and TRAP in str(content):
            hit_file = os.path.join(HERE, "trap_triggered.log")
            with open(hit_file, "a", encoding="utf-8") as fp:
                fp.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} seq={seq} token={TRAP}\n")
            print(f"[bridge] TRAP TRIGGERED at seq={seq}", flush=True)

        # 4. 返回
        finish = "tool_calls" if has_tools else "stop"
        if stream:
            self._reply_sse(str(content))
        else:
            self._reply_json({
                "id": "chatcmpl-wb-" + seq,
                "object": "chat.completion",
                "created": int(time.time()),
                "model": MODEL_ID,
                "choices": [{
                    "index": 0,
                    "message": msg,
                    "finish_reason": finish,
                }],
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            })
        print(f"[bridge] ANSWER {seq} returned (tools={has_tools}, {len(str(content))} chars)", flush=True)

    def log_message(self, fmt, *args):
        pass  # 静默访问日志


if __name__ == "__main__":
    print(f"[bridge] WorkBuddy-in-loop bridge on http://{HOST}:{PORT}  model={MODEL_ID} mode={MODE}", flush=True)
    print(f"[bridge] requests -> {REQ_DIR}", flush=True)
    print(f"[bridge] answers  -> {ANS_DIR}", flush=True)
    HTTPServer((HOST, PORT), Handler).serve_forever()
