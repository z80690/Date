import json, re, sys, io, os, subprocess, time
import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
base = os.path.dirname(__file__)
FF = r"D:\soft\scoop\apps\python311\current\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v9.0.2.exe"
UA_PC = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

print("=== transcribe BV1jd4g6fECp (audio stream m4a) ===")
audio_file = os.path.join(base, "bili", "workflow_BV1jd4g6fECp.f30280.m4a")
print("audio exists:", os.path.exists(audio_file))

from faster_whisper import WhisperModel
model = WhisperModel("small", device="cpu", compute_type="int8")
segments, info = model.transcribe(
    audio_file,
    language="zh",
    vad_filter=True,
    initial_prompt="这是一个讲解单片机AI开发工作流的视频：项目资料归档、硬件接口整理、代码开发规范、调试闭环。",
)
out = [{"start": round(s.start, 1), "end": round(s.end, 1), "text": s.text.strip()} for s in segments]
with open(os.path.join(base, "bili", "wf_transcript.json"), "w", encoding="utf-8") as f:
    f.write(json.dumps({"duration": info.duration, "segments": out}, ensure_ascii=False, indent=1))
print("segments:", len(out))
for s_ in out:
    print(f"[{s_['start']:.0f}-{s_['end']:.0f}] {s_['text']}")