"""Package actual v063 palette-only renders; does not edit native art or scenes."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import hashlib, json, re, subprocess
import numpy as np
import imageio_ffmpeg

O = Path(r'WTSC_LOCAL_WORKSPACE\work\color_arc_v063')
P = O / 'previews'
E = O / 'evidence'
FPS = 12
COUNT = 60
CANVAS = (1280, 816)
HEADER = 96
LIMITS = (
    'Palette-only comparison. The identical pose, camera and forest are held at '
    'scene frame 981. The full represented trailer palette progression from 0 to '
    '100 seconds is compressed to five seconds at 12 fps. This is not a new story '
    'animation, a trailer edit or soundtrack timing proof. Movie is deliberately mute.'
)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def font(size):
    for path in [
        Path(r'C:\Windows\Fonts\segoeui.ttf'),
        Path(r'C:\Windows\Fonts\arial.ttf'),
    ]:
        if path.is_file():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()

def run(args):
    r = subprocess.run([str(x) for x in args], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError('Command failed:\n' + ' '.join(map(str, args)) + '\n' + r.stderr[-5000:])
    return r

def main():
    metadata = json.loads((E / 'COLOR_ARC_RENDER.json').read_text())
    rows = metadata['rows']
    assert len(rows) == COUNT, len(rows)
    assert metadata['native_unchanged'] is True
    native = O / 'native/WTSC_Shared_Color_To_Charcoal_v063.blend'
    assert sha(native) == metadata['native_sha256']
    source_hashes = []
    labels_dir = P / 'color_arc_labelled_frames'
    labels_dir.mkdir(exist_ok=True)
    title_font, sub_font = font(27), font(22)
    for i, row in enumerate(rows, 1):
        assert row['review_frame'] == i, row
        assert row['scene_pose_frame'] == 981, row
        src = P / 'arc_frames' / ('%04d.png' % i)
        h = sha(src)
        assert h == row['sha256'], (src.name, h)
        source_hashes.append({'frame': i, 'sha256': h})
        im = Image.open(src).convert('RGB')
        assert im.size == (1280, 720), (src.name, im.size)
        frame = Image.new('RGB', CANVAS, (19, 21, 25))
        frame.paste(im, (0, HEADER))
        draw = ImageDraw.Draw(frame)
        draw.text((22, 10), 'Color arc study | same pose for comparison',
                  font=title_font, fill=(242, 242, 239))
        t = float(row['represented_trailer_seconds'])
        p = float(row['progress'])
        text = 'Represented trailer time: %.1f / 100 s   |   Charcoal transition: %.1f%%   |   Mute palette study' % (t, p * 100)
        draw.text((22, 54), text, font=sub_font, fill=(191, 197, 198))
        frame.save(labels_dir / ('%04d.png' % i))
    assert abs(float(rows[0]['represented_trailer_seconds'])) < 1e-8
    assert abs(float(rows[-1]['represented_trailer_seconds']) - 100) < 1e-8

    # This board uses only native render crops; labels occupy a separate margin.
    states = [
        ('Full_Color_v063.png', 'Start | both in full color'),
        ('Midpoint_v063.png', 'Midpoint | shared transition'),
        ('Charcoal_v063.png', 'Ending | both in charcoal'),
    ]
    board = Image.new('RGB', (1260, 530), (19, 21, 25))
    bd = ImageDraw.Draw(board)
    bd.text((18, 12), 'Color arc study | identical pose and forest', font=font(27), fill=(242, 242, 239))
    endpoint_hashes = []
    for i, (name, label) in enumerate(states):
        src = P / name
        im = Image.open(src).convert('RGB')
        assert im.size == (1920, 1080), (name, im.size)
        crop = im.crop((700, 240, 1260, 820))
        crop = crop.resize((420, 435), Image.Resampling.LANCZOS)
        board.paste(crop, (420 * i, 85))
        bd.text((420 * i + 12, 53), label, font=font(21), fill=(220, 222, 216))
        endpoint_hashes.append({'file': name, 'sha256': sha(src), 'dimensions': list(im.size)})
    board_path = P / 'Color_Arc_Start_Middle_End_v063.jpg'
    board.save(board_path, quality=95, subsampling=0)

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    movie = P / 'WTSC_Both_Children_Color_Arc_v063.mp4'
    run([ffmpeg, '-y', '-hide_banner', '-loglevel', 'error',
         '-framerate', str(FPS), '-start_number', '1',
         '-i', labels_dir / '%04d.png', '-frames:v', str(COUNT),
         '-an', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
         '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
         '-video_track_timescale', '12288', movie])
    decoded = P / 'color_arc_decoded_frames'
    decoded.mkdir(exist_ok=True)
    for old in decoded.glob('*.png'):
        old.unlink()
    # Decode the actual deliverable, not source placeholders.
    run([ffmpeg, '-y', '-hide_banner', '-loglevel', 'error',
         '-i', movie, '-map', '0:v:0', '-fps_mode', 'passthrough',
         '-start_number', '1', decoded / '%04d.png'])
    decoded_paths = sorted(decoded.glob('*.png'))
    assert len(decoded_paths) == COUNT, len(decoded_paths)
    differences = []
    for i, path in enumerate(decoded_paths, 1):
        got = np.asarray(Image.open(path).convert('RGB'), dtype=np.int16)
        want = np.asarray(Image.open(labels_dir / ('%04d.png' % i)).convert('RGB'), dtype=np.int16)
        assert got.shape == want.shape == (816, 1280, 3), (i, got.shape, want.shape)
        error = float(np.abs(got - want).mean())
        assert error < 8.0, (i, error)
        differences.append(error)
    timing = run([ffmpeg, '-hide_banner', '-i', movie,
                  '-map', '0:v:0', '-vf', 'showinfo', '-an', '-f', 'null', '-'])
    samples = re.findall(r'n:\s*(\d+)\s+pts:\s*(-?\d+)\s+pts_time:([-\d.]+)', timing.stderr)
    assert len(samples) == COUNT, (len(samples), timing.stderr[-3000:])
    pts_errors = []
    for i, sample in enumerate(samples):
        n, pts, t = sample
        assert int(n) == i, (i, sample)
        error = abs(float(t) - i / FPS)
        assert error < 0.00005, (i, t, error)
        pts_errors.append(error)
    assert 'Audio:' not in timing.stderr, 'Movie unexpectedly contains audio'
    duration_match = re.search(r'Duration:\s*(\d+):(\d+):([\d.]+)', timing.stderr)
    assert duration_match, timing.stderr[:1000]
    hh, mm, ss = duration_match.groups()
    duration = int(hh) * 3600 + int(mm) * 60 + float(ss)
    assert abs(duration - 5.0) < 0.011, duration
    assert sha(native) == metadata['native_sha256']

    report = {
        'native_sha256': metadata['native_sha256'],
        'native_unchanged': True,
        'movie': str(movie),
        'movie_sha256': sha(movie),
        'movie_bytes': movie.stat().st_size,
        'board': str(board_path),
        'board_sha256': sha(board_path),
        'endpoint_sources': endpoint_hashes,
        'source_frame_hashes_verified': source_hashes,
        'frames_encoded_and_decoded': COUNT,
        'fps': FPS,
        'duration_seconds': duration,
        'represented_trailer_seconds': [0, 100],
        'scene_pose_frame_held': 981,
        'frame_dimensions_with_separate_header': list(CANVAS),
        'header_height_pixels': HEADER,
        'source_image_dimensions': [1280, 720],
        'all_frame_pts_max_error_seconds': max(pts_errors),
        'all_frame_rgb_mean_abs_error_max': max(differences),
        'all_frame_rgb_mean_abs_error_average': float(np.mean(differences)),
        'has_audio': False,
        'review_limits': LIMITS,
        'board_crop_from_native_endpoints': [700, 240, 1260, 820],
        'source_art_pixel_edits': False,
    }
    (E / 'COLOR_REVIEW_ENCODE.json').write_text(json.dumps(report, indent=2) + '\n')
    print('V063_COLOR_REVIEW_PACKAGE_COMPLETE', flush=True)
    print(json.dumps({k: report[k] for k in [
        'movie', 'movie_sha256', 'movie_bytes', 'board', 'board_sha256',
        'frames_encoded_and_decoded', 'duration_seconds',
        'all_frame_pts_max_error_seconds', 'all_frame_rgb_mean_abs_error_max',
    ]}, indent=2), flush=True)

if __name__ == '__main__':
    main()
