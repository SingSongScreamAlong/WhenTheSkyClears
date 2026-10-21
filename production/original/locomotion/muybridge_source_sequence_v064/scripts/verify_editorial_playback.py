"""Decode the finished MP4 to confirm its declared editorial cadence and 12 distinct frames."""

import hashlib
import json
from pathlib import Path
import imageio_ffmpeg

root=Path(__file__).resolve().parents[1]
video=root / "previews" / "Muybridge_12_Source_Phases_Editorial_3fps_v064.mp4"
reader=imageio_ffmpeg.read_frames(str(video),pix_fmt="rgb24")
meta=next(reader)
hashes=[hashlib.sha256(frame).hexdigest() for frame in reader]
report={
    "video":str(video),
    "decoded_frame_count":len(hashes),
    "distinct_decoded_frames":len(set(hashes)),
    "fps":meta.get("fps"),
    "duration_seconds":meta.get("duration"),
    "size":meta.get("size"),
    "matches_one_frame_per_phase":len(hashes)==12 and len(set(hashes))==12 and abs(meta.get("fps",0)-3)<1e-6,
}
(root / "evidence" / "EDITORIAL_PLAYBACK_DECODE_v064.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
if not report["matches_one_frame_per_phase"]:
    raise RuntimeError("Encoded playback does not match twelve distinct editorial poses")
print(json.dumps(report))
