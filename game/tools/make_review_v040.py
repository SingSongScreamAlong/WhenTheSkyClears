"""Encode the recorded native mill and compose unchanged gameplay review images."""
from pathlib import Path
import hashlib
import json
import subprocess
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

P = Path(__file__).resolve().parents[1]
E = P / 'evidence/v040'
F = E / 'release_final/mill-playthrough'
report = json.loads((F / 'mill_checks.json').read_text(encoding='utf-8'))
recording = report['recording']
frames = [F / 'motion_frames' / f'{index:05d}.jpg' for index in range(recording['frames'])]
assert report['all_passed'] and recording['enabled']
assert recording['frames'] > 0 and all(frame.is_file() for frame in frames)
size = Image.open(frames[0]).size
assert all(Image.open(frame).size == size for frame in frames)
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
movie = E / 'WTSC_Mill_Playthrough_v040.mp4'

def run(command):
    result = subprocess.run(command, capture_output=True, text=True,
        encoding='utf-8', errors='replace', creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    assert result.returncode == 0, result.stderr[-3000:]
    return result

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

run([ffmpeg, '-y', '-framerate', str(recording['fps']), '-start_number', '0',
    '-i', str(F / 'motion_frames/%05d.jpg'), '-frames:v', str(len(frames)),
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p',
    '-movflags', '+faststart', str(movie)])
decoded = run([ffmpeg, '-v', 'error', '-i', str(movie), '-f', 'null', '-',
    '-progress', 'pipe:1', '-nostats'])
count = max(int(line.split('=')[1]) for line in decoded.stdout.splitlines() if line.startswith('frame='))
assert count == len(frames) and 'progress=end' in decoded.stdout
invocation_path = F / 'invocation.json'
invocation = json.loads(invocation_path.read_text(encoding='utf-8'))
validation = dict(file=movie.name, bytes=movie.stat().st_size, sha256=sha(movie),
    size=size, fps=recording['fps'], decoded_frames=count, duration_seconds=count/recording['fps'],
    source_exe_sha256=invocation['exe_sha256'], source_invocation_sha256=sha(invocation_path),
    scope=recording['scope'], silent=True, decode_complete=True)
(E / 'mill_movie_validation.json').write_text(json.dumps(validation, indent=2), encoding='utf-8')

font = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 24)
small = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 18)
captures = E / 'release_final/capture-v040'
shots = [
    ('08_interactive_mill_bridge.png', 'Bridge / foreground fence'),
    ('09_interactive_wheel_approach.png', 'Climb / breakaway wheel'),
    ('07_character_close_study.png', 'Painted character materials - staged close view'),
    ('01_mill_gardens.png', 'Village / mill gardens'),
    ('02_canal_lower_route.png', 'Canal / wet lower route'),
    ('03_canal_upper_route.png', 'Canal / paid raised crossing'),
    ('04_signal_yard.png', 'Camp / signal yard'),
    ('05_school_gallery.png', 'School / broken gallery'),
    ('06_living_terraces.png', 'Ash road / living terraces'),
]
board = Image.new('RGB', (1980, 1320), (19, 28, 29))
draw = ImageDraw.Draw(board)
draw.text((25, 18), 'WHEN THE SKY CLEARS / WORLD AND MATERIAL PASS / 0.4.0', font=font, fill=(232, 228, 207))
draw.text((25, 54), 'Actual native 3840 x 2160 captures. Selected scene placements; movement is verified separately.', font=small, fill=(173, 192, 184))
for index, (name, label) in enumerate(shots):
    source = captures / name
    with Image.open(source) as image:
        assert image.size == (3840, 2160)
        tile = image.convert('RGB').resize((640, 360), Image.Resampling.LANCZOS)
    x = 20 + index % 3 * 660
    y = 100 + index // 3 * 400
    board.paste(tile, (x, y))
    draw.text((x+5, y+367), label, font=small, fill=(211, 214, 191))
board.save(E / 'V040_PLAYABLE_REVIEW.jpg', quality=94)

comparison = Image.new('RGB', (2560, 1530), (19, 28, 29))
draw = ImageDraw.Draw(comparison)
before = E / 'pre_art_readability/capture-v040/08_interactive_mill_bridge.png'
after = captures / '08_interactive_mill_bridge.png'
for index, (source, label) in enumerate([(before, 'Before: darkened source paint'), (after, 'After: visible skin, cloth, timber and earth')]):
    with Image.open(source) as image:
        tile = image.convert('RGB').resize((1280, 720), Image.Resampling.LANCZOS)
    x = index * 1280
    comparison.paste(tile, (x, 60))
    draw.text((x+24, 20), label, font=font, fill=(232, 228, 207))
    close = (before.parent if index == 0 else captures) / '07_character_close_study.png'
    with Image.open(close) as image:
        tile = image.convert('RGB').resize((1280, 720), Image.Resampling.LANCZOS)
    comparison.paste(tile, (x, 790))
comparison.save(E / 'ART_READABILITY_BEFORE_AFTER.jpg', quality=95)
print(json.dumps(validation))
