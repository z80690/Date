import json, os
from faster_whisper import WhisperModel

base = os.path.dirname(__file__)
model = WhisperModel("small", device="cpu", compute_type="int8")
segments, info = model.transcribe(
    os.path.join(base, "audio.wav"),
    language="zh",
    vad_filter=True,
    initial_prompt="这是一个关于单片机嵌入式开发、AI编程辅助、6个单片机项目实战经验分享的视频。",
)
out = [{"start": round(s.start, 1), "end": round(s.end, 1), "text": s.text.strip()} for s in segments]
with open(os.path.join(base, "transcript_utf8.json"), "w", encoding="utf-8") as f:
    f.write(json.dumps({"language": info.language, "duration": info.duration, "segments": out}, ensure_ascii=False, indent=1))
print("segments:", len(out))