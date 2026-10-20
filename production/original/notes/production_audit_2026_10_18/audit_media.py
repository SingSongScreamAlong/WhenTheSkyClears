import io
import json
import re
import subprocess
from pathlib import Path
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
FLAGS = subprocess.CREATE_NO_WINDOW

def run(args, timeout=120):
    return subprocess.run([FFMPEG, '-hide_banner', '-nostdin', *args], capture_output=True,
                          timeout=timeout, creationflags=FLAGS)

headers = []
for p in sorted(ROOT.rglob('*.mp4')):
    if p.is_relative_to(OUT):
        continue
    probe = run(['-i', str(p)], timeout=20)
    log = probe.stderr.decode('utf-8', errors='replace')
    duration = re.search(r'Duration:\s*([\d:.]+)', log)
    video = next((l.strip() for l in log.splitlines() if 'Video:' in l), None)
    audio = next((l.strip() for l in log.splitlines() if 'Audio:' in l), None)
    headers.append({'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size,
                    'duration': duration.group(1) if duration else None,
                    'video': video, 'audio': audio,
                    'header_readable': bool(duration and video)})
(OUT / 'media_headers.json').write_text(json.dumps(headers, indent=2), encoding='utf-8')

selected = {
    'full_v040_UHD': ('renders/world_v016/WTSC_Full_Knockout_Trailer_4K_v040.mp4', 2544),
    'world_v058': ('work/world_minimum_v058/WTSC_v058d_World_Foreground_6s_24fps.mp4', 144),
    'recovery_v059': ('work/production_review_v059/WTSC_Recovery_Benchmark_v059_720p.mp4', 120),
    'danger_v060': ('work/trailer_development_v060/previews/WTSC_First_Danger_v060_Preview.mp4', 120),
    'danger_title_v060': ('work/trailer_development_v060/previews/WTSC_First_Danger_Title_v060_Preview.mp4', 120),
    'color_v063': ('work/color_arc_v063/previews/WTSC_Both_Children_Color_Arc_v063.mp4', 60),
    'character_v050': ('locomotion/face_hand_finish_v050/previews/WTSC_Face_Hand_Finish_v050_Actual_NormalSpeed.mp4', 257),
    'clods_v015_rough': ('effects/squat_clods_v015/previews/WTSC_Squat_Clods_SILHOUETTE_ROUGH_v015.mp4', 32),
}
results = []
for label, (rel, expected) in selected.items():
    p = ROOT / rel
    result = run(['-v', 'error', '-i', str(p), '-map', '0:v:0', '-progress', 'pipe:1', '-f', 'null', 'NUL'], timeout=180)
    counts = re.findall(r'^frame=(\d+)', result.stdout.decode(), re.M)
    frames = int(counts[-1]) if counts else None
    results.append({'label': label, 'path': rel, 'expected_frames': expected, 'decoded_frames': frames,
                    'returncode': result.returncode, 'stderr': result.stderr.decode(errors='replace')[-1500:],
                    'passed': result.returncode == 0 and frames == expected})
    (OUT / 'media_decodes.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
    print('DECODE', label, frames, results[-1]['passed'], flush=True)

font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 19)
small_font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 16)

def frame(rel, seconds):
    result = run(['-v', 'error', '-ss', str(seconds), '-i', str(ROOT / rel),
                  '-frames:v', '1', '-vf', 'scale=640:-1', '-f', 'image2pipe', '-vcodec', 'png', 'pipe:1'])
    if result.returncode or not result.stdout:
        raise RuntimeError(result.stderr.decode(errors='replace'))
    return Image.open(io.BytesIO(result.stdout)).convert('RGB')

def board(name, entries, columns=2):
    cell_w, cell_h = 640, 410
    canvas = Image.new('RGB', (columns * cell_w, ((len(entries) + columns - 1) // columns) * cell_h), '#171c23')
    draw = ImageDraw.Draw(canvas)
    for n, (label, rel, seconds) in enumerate(entries):
        x, y = n % columns * cell_w, n // columns * cell_h
        im = frame(rel, seconds)
        im.thumbnail((640, 360))
        canvas.paste(im, (x + (640 - im.width) // 2, y + 43))
        draw.text((x + 10, y + 7), label, fill='white', font=font)
    canvas.save(OUT / name, quality=92)

full = 'renders/world_v016/WTSC_Full_Knockout_Trailer_View_v040.mp4'
board('full_cut_samples.jpg', [(f'v040 full cut | {t}s', full, t) for t in [10, 20, 35, 40, 52, 67, 76, 90, 99, 103]])
board('development_samples.jpg', [
    ('v060 unmasked first-danger | local 1.8s', selected['danger_v060'][0], 1.8),
    ('v060 actual title treatment | local 1.8s', selected['danger_title_v060'][0], 1.8),
    ('v059 recovery | local 0.7s', selected['recovery_v059'][0], .7),
    ('v059 recovery | local 4.5s', selected['recovery_v059'][0], 4.5),
    ('v050 face/hand finish | ordinary walk', selected['character_v050'][0], .15),
    ('v058 foreground | held-pair world proof', selected['world_v058'][0], .7),
    ('v063 palette only | represented start', selected['color_v063'][0], 0),
    ('v063 palette only | represented charcoal end', selected['color_v063'][0], 4.85),
    ('v015 clod silhouette ROUGH | early', selected['clods_v015_rough'][0], .3),
    ('v015 clod silhouette ROUGH | late', selected['clods_v015_rough'][0], .9),
])
print(json.dumps({'media_headers': len(headers), 'bad_headers': [r['path'] for r in headers if not r['header_readable']], 'decode_passes': sum(r['passed'] for r in results)}, indent=2), flush=True)
