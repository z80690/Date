import re, io

src = r"D:\refs\PentAGI\.env.example"
dst = r"D:\refs\PentAGI\.env"
text = io.open(src, encoding="utf-8", errors="replace").read()

overrides = {
    "SERVER_HOST": "127.0.0.1",
    "SERVER_PORT": "8443",
    "LLM_SERVER_URL": "http://127.0.0.1:7810/v1",
    "LLM_SERVER_KEY": "placeholder-not-a-real-key",
    "LLM_SERVER_MODEL": "placeholder",
    "LLM_SERVER_PROVIDER": "openai_compatible",
    "PROXY_URL": "",
}
# wipe cloud model keys and search providers (R1/R2: kill egress surface)
wipe_keys = ["OPEN_AI_KEY", "OPEN_AI_ORG_ID", "OPEN_AI_API_TYPE", "OPEN_AI_BASE_URL", "ANTHROPIC_API_KEY",
             "GEMINI_API_KEY", "GIGACHAT_CREDENTIALS", "OPENROUTER_API_KEY", "DEEPSEEK_API_KEY", "OLLAMA_HOST",
             "TAVILY_API_KEY", "FIRECRAWL_API_KEY", "TRIVERSAAL_API_KEY", "PERPLEXITY_API_KEY",
             "GOOGLE_API_KEY", "GOOGLE_CX", "SPOTIOS_API_KEY", "SEARXNG_URL", "GRAPHITI_URL", "UPDATE_CHECK_URL"]

lines = text.splitlines()
seen = set()
out = []
for ln in lines:
    m = re.match(r"^([A-Z0-9_]+)=", ln)
    if m:
        k = m.group(1)
        seen.add(k)
        if k in overrides:
            out.append("%s=%s" % (k, overrides[k]))
        elif k in wipe_keys:
            out.append("%s=" % k)
        else:
            out.append(ln)
    else:
        out.append(ln)
for k, v in overrides.items():
    if k not in seen:
        out.append("%s=%s" % (k, v))

io.open(dst, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
print("WROTE", dst)
