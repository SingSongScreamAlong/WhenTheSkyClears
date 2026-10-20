"""Build a labelled review sheet and a decoded native mill recording."""
from pathlib import Path
import hashlib
import json
import subprocess
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

P = Path(__file__).resolve().parents[1]
E = P / "evidence/v041"
F = E / "release_final"
capture = F / "capture"
shots = [
    ("01_mill_gardens", "Village / stone floodbanks"),
    ("04_signal_yard", "Camp / freight and signal yard"),
    ("05_school_gallery", "School / ruined gallery"),
    ("06_living_terraces", "Ash road / abandoned terraces"),
    ("03_canal_upper_route", "Canal / dry upper crossing"),
    ("08_interactive_mill_bridge", "Mill / bridge and foreground rail"),
    ("09_interactive_wheel_approach", "Mill / wheel, bearing and chain"),
    ("10_canal_pump_work", "Shared pump / held work"),
    ("12_supplies_close_study", "Supplies / staged close view"),
]
board = Image.new("RGB", (1980, 1320), "#14201e")
draw = ImageDraw.Draw(board)
font_path = P / "assets/fonts/interface.ttf"
font = ImageFont.truetype(str(font_path), 19)
title = ImageFont.truetype(str(font_path), 26)
draw.text((24, 22), "WHEN THE SKY CLEARS / WORLD REFINEMENT / 0.4.1", fill="#e4dfcb", font=title)
draw.text((24, 60), "Actual native 3840 x 2160 captures. Staged views; navigation and survival tested separately.", fill="#bbc5ba", font=font)
for index, (name, label) in enumerate(shots):
    image = Image.open(capture / (name + ".png")).convert("RGB")
    image.thumbnail((640, 360), Image.Resampling.LANCZOS)
    x, y = 20 + index % 3 * 660, 110 + index // 3 * 400
    board.paste(image, (x, y))
    draw.text((x + 3, y + 369), label, fill="#ced3c6", font=font)
board.save(E / "V041_PLAYABLE_REVIEW.jpg", quality=93)

folder = F / "mill-playthrough"
report = json.loads((folder / "mill_checks.json").read_text(encoding="utf-8"))
movie_data = report.get("recording", {})
assert report["all_passed"] and movie_data["enabled"] and movie_data["fps"] == 30
call = json.loads((folder / "invocation.json").read_text(encoding="utf-8"))
identity = json.loads((E / "EXPORT_IDENTITY.json").read_text(encoding="utf-8"))
assert call["exit_code"] == 0 and not call["engine_errors"] and call["exe_sha256"] == identity["sha256"]
frames = int(movie_data["frames"])
sequence = folder / "motion_frames"
assert frames > 0 and all((sequence / f"{i:05d}.jpg").is_file() for i in range(frames))
output = E / "WTSC_Mill_Playthrough_v041.mp4"
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
command = [ffmpeg, "-y", "-framerate", "30", "-i", str(sequence / "%05d.jpg"),
           "-frames:v", str(frames), "-c:v", "libx264", "-crf", "19",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", str(output)]
result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
assert result.returncode == 0, result.stderr[-2000:]
decoded = subprocess.run([ffmpeg, "-v", "error", "-i", str(output), "-f", "null", "-"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace")
assert decoded.returncode == 0 and not decoded.stderr.strip(), decoded.stderr
actual_frames, seconds = imageio_ffmpeg.count_frames_and_secs(str(output))
assert actual_frames == frames
validation = {"file": output.name, "frames": frames, "seconds": seconds, "fps": 30,
              "audio": False, "decode_passed": True,
              "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
              "native_invocation_sha256": hashlib.sha256((folder / "invocation.json").read_bytes()).hexdigest(),
              "method": "Exact recorded native frame range; full FFmpeg decode and frame-count check. The fixture places both children before the mill; subsequent safe traversal uses native Input and physics."}
(E / "mill_movie_validation.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
print(json.dumps(validation))
