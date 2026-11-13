"""P003 IF-9 verdict over the already-captured round-08 pcap (no re-drill)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from adapter import verdict  # noqa: E402

ROUND_NO = 8
PCAP = r"C:\Users\Administrator\Desktop\Date\temp\p003_drill\round-08\round-08.pcapng"
TSHARK = r"C:\Program Files\Wireshark\tshark.exe"

counts = verdict.collect_evidence(ROUND_NO, PCAP, tshark_path=TSHARK, audit_available=True)
for key in (
    "j1_plaintext_hits",
    "j2_public_ip_hits",
    "j3_abnormal_outbound",
    "j4_disguise_valid",
    "j5_log_clean_hits",
):
    print(f"{key} = {counts[key]}")
for item in counts["per_item_evidence"]:
    print(f"  evidence | {item}")
report = verdict.verdict_from_counts(ROUND_NO, counts)
print(f"CONCLUSION = {report['conclusion']}")
print(f"REASON     = {report['reason']}")