"""Encode and fully decode a native motion review; assemble a labeled contact sheet."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('capture', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()
report = json.loads((args.capture/'motion_review.json').read_text())
frames = sorted((args.capture/'motion_frames').glob('*.jpg'))
assert len(frames) == report['frames'], (len(frames), report['frames'])
size = Image.open(frames[0]).size
assert all(Image.open(frame).size == size for frame in frames)
args.output.parent.mkdir(parents=True, exist_ok=True)
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
flags = dict(capture_output=True, text=True, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
encoded = subprocess.run([ffmpeg, '-y', '-framerate', str(report['fps']), '-i',
    str(args.capture/'motion_frames/%04d.jpg'), '-c:v', 'libx264', '-preset', 'medium',
    '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(args.output)], **flags)
assert encoded.returncode == 0, encoded.stderr
decoded = subprocess.run([ffmpeg, '-v', 'error', '-i', str(args.output), '-f', 'null', '-',
                          '-progress', 'pipe:1', '-nostats'], **flags)
decoded_count = max(int(line.split('=')[1]) for line in decoded.stdout.splitlines() if line.startswith('frame='))
assert decoded.returncode == 0 and not decoded.stderr.strip() and decoded_count == len(frames)
metadata = dict(file=args.output.name, decoded_frames=decoded_count, fps=report['fps'],
                duration_seconds=decoded_count/report['fps'], size=list(size),
                bytes=args.output.stat().st_size, sha256=hashlib.sha256(args.output.read_bytes()).hexdigest(),
                audio='silent', scope=report.get('scope', report.get('scene')))
args.output.with_suffix('.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
board = Image.new('RGB', (1440, 980), (15, 24, 27))
draw = ImageDraw.Draw(board)
try:
    font = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 22)
except OSError:
    font = ImageFont.load_default()
labels = [(60, 'Walk'), (125, 'Brake and turn'), (215, 'Crouch'),
          (285, 'Run'), (345, 'Jump'), (435, 'Shared work')]
for index, (number, label) in enumerate(labels):
    if number >= len(frames): continue
    frame = Image.open(frames[number]).convert('RGB')
    frame.thumbnail((710, 400))
    x, y = (index%2)*720, 54+(index//2)*300
    # This is a crop of the unaltered game frame, to make the actual poses legible.
    frame = Image.open(frames[number]).convert('RGB').crop((80, 260, 1080, 680))
    frame.thumbnail((710, 260))
    board.paste(frame, (x, y))
    draw.text((x+12, y+262), label, fill=(211, 219, 205), font=font)
draw.text((15, 12), 'WHEN THE SKY CLEARS / CHARACTER MOVEMENT REVIEW / 30 FPS', fill=(211, 219, 205), font=font)
draw.text((15, 954), 'Staged character study. Native game renderer and controllers. Campaign tested separately.', fill=(148, 170, 168), font=font)
board.save(args.output.with_suffix('.jpg'), quality=94)
print(json.dumps(metadata))
