import json, os
from faster_whisper import WhisperModel

base = os.path.dirname(__file__)
model = WhisperModel("small", device="cpu", compute_type="int8")
segments, info = model.transcribe(
    os.path.join(base, "audio.wav"),
    language="zh",
    vad_filter=True,
    initial_prompt="这是一个关于 ESP32-S3 开发板、AI 对话、语音合成的科技视频。",
)
out = [{"start": round(s.start, 1), "end": round(s.end, 1), "text": s.text.strip()} for s in segments]
with open(os.path.join(base, "transcript_utf8.json"), "w", encoding="utf-8") as f:
    f.write(json.dumps({"language": info.language, "duration": info.duration, "segments": out}, ensure_ascii=False, indent=1))