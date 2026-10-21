"""Encode a labeled 12-frame editorial review, one native pose per plate phase.

The 3 fps pace is an invented review interval, not Muybridge exposure timing.
This script never duplicates, interpolates, generates or retimes any drawing.
"""

import hashlib
import json
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

root=Path(__file__).resolve().parents[1]
frames=root / "playback_frames"
frames.mkdir(exist_ok=True)
font_path=Path(r"C:\Windows\Fonts\arial.ttf")
large=ImageFont.truetype(str(font_path),25) if font_path.exists() else ImageFont.load_default()
medium=ImageFont.truetype(str(font_path),18) if font_path.exists() else ImageFont.load_default()
small=ImageFont.truetype(str(font_path),15) if font_path.exists() else ImageFont.load_default()
frame_hashes={}
for phase in range(1,13):
    source=Image.open(root / "reference" / f"phase{phase:02d}_source_crop.png").convert("RGB")
    native=Image.open(root / "previews" / f"phase{phase:02d}_native_rgba_v064.png").convert("RGBA")
    if source.size!=(310,588) or native.size!=(620,1176):
        raise RuntimeError(f"Wrong source/native sizes for phase {phase}")
    source_2x=source.resize(native.size,Image.Resampling.LANCZOS)
    layer=Image.new("RGBA",native.size,(8,238,231,0))
    layer.putalpha(native.getchannel("A").point(lambda value:round(value*0.72)))
    overlay=Image.alpha_composite(source_2x.convert("RGBA"),layer).convert("RGB").resize((310,588),Image.Resampling.LANCZOS)
    paper=Image.new("RGBA",native.size,(239,235,224,255))
    isolated=Image.alpha_composite(paper,native).convert("RGB").resize((310,588),Image.Resampling.LANCZOS)
    canvas=Image.new("RGB",(1280,720),(236,231,219))
    draw=ImageDraw.Draw(canvas)
    draw.text((52,13),"MUYBRIDGE SOURCE-MOTION STUDY",font=large,fill=(32,31,28))
    draw.text((1007,18),f"PHASE {phase:02d} / 12",font=medium,fill=(32,31,28))
    for x,panel,label in ((85,source,"ORIGINAL PHOTO"),(485,overlay,"SOURCE + NATIVE GP"),(885,isolated,"EDITABLE GP RENDER")):
        draw.text((x,53),label,font=medium,fill=(48,45,39))
        canvas.paste(panel,(x,79))
        draw.rectangle((x-1,78,x+310,668),outline=(95,91,82),width=1)
    draw.text((52,684),"EDITORIAL PLAYBACK: 3 FPS | ONE AUTHORED POSE PER PHASE | ORIGINAL EXPOSURE TIMING UNKNOWN",font=small,fill=(56,52,45))
    out=frames / f"phase{phase:02d}.png"
    canvas.save(out,optimize=True)
    frame_hashes[f"phase{phase:02d}"]=hashlib.sha256(out.read_bytes()).hexdigest()

ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
output=root / "previews" / "Muybridge_12_Source_Phases_Editorial_3fps_v064.mp4"
command=[ffmpeg,"-y","-framerate","3","-start_number","1","-i",str(frames / "phase%02d.png"),"-frames:v","12","-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p","-r","3","-movflags","+faststart","-an",str(output)]
result=subprocess.run(command,capture_output=True,text=True)
(root / "evidence" / "EDITORIAL_FFMPEG_STDERR_v064.txt").write_text(result.stderr,encoding="utf-8")
if result.returncode!=0 or not output.exists():
    raise RuntimeError(f"Editorial encode failed with exit {result.returncode}")
report={
    "file":str(output),
    "file_size_bytes":output.stat().st_size,
    "sha256":hashlib.sha256(output.read_bytes()).hexdigest(),
    "editorial_fps":3,
    "authored_pose_count":12,
    "presented_frame_count":12,
    "expected_duration_seconds":4.0,
    "hold_frames_or_duplicates_added":False,
    "source_exposure_timing_known":False,
    "continuous_motion_verified":False,
    "music_or_audio":False,
    "frame_sha256":frame_hashes,
    "ffmpeg_executable":ffmpeg,
    "ffmpeg_exit_code":result.returncode,
}
(root / "evidence" / "EDITORIAL_PLAYBACK_v064.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps({k:v for k,v in report.items() if k not in ("frame_sha256","ffmpeg_executable")}))
