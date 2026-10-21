"""Package fresh v064 native world frames into the unchanged 106-second title cut.

No Blender invocation, frame synthesis, interpolation, old-world reuse or native edits.
Run only after root confirms all 2,400 fresh world PNGs are complete.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import argparse, hashlib, json, math, os, re, shutil, subprocess, time
import numpy as np
import imageio_ffmpeg

R = Path(r'WTSC_LOCAL_WORKSPACE')
O = R / 'work/procedural_cut_v064'
P, E = O / 'previews', O / 'evidence'
NATIVE = O / 'native/WTSC_Procedural_Full_Trailer_v064.blend'
FRAMES = P / 'world_frames'
MASK_DIR = R / 'renders/world_v016/full_parts_v037'
MASK_LIST = MASK_DIR / 'mask_concat.txt'
CREDITS = MASK_DIR / 'credits_6s.mp4'
WAV = R / 'edit/When_The_Sky_Clears_Trailer_Music_100s.wav'
FPS, WORLD_COUNT, CREDIT_COUNT, TOTAL_COUNT = 24, 2400, 144, 2544
VIDEO_RATE, AUDIO_RATE = '1250k', '128k'
SIZE_LIMIT = 20_000_000
F = imageio_ffmpeg.get_ffmpeg_exe()
EXPECTED_CACHED = {
    'mask_01.mp4': '993ffe6581c6013d0de9fcaeb6748709c3d66e25fc188d0cb1db5ade4bfd9fc5',
    'mask_02.mp4': '9048a000f0681c028b93f9c591b1a9fc73609642ee3bea6229f3648f53ad8c09',
    'mask_03.mp4': '0b9bce120eb65a92561895f9ba91d1abc6ff537b2dfdcb29bd85f08f7d3891d7',
    'mask_04.mp4': '6f0d72de05cdc806aefbf4c6455ebaca0b6622078494bab6eeba191a86851c59',
    'credits_6s.mp4': '70734a04196b82ff7d49066fb11492655fe441047d8f86e0bd00bbb80a1c4d8a',
}
EXPECTED_WAV = '0694b2f40f56df5bbadaa23e1c92ac6a048507a8920cebf5b060fc7493368114'
SAMPLE_INDICES = [0, 432, 840, 936, 1055, 1200, 1608, 1920, 2160, 2303, 2399]

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def status(phase, **kwargs):
    data = {'phase': phase, 'utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), **kwargs}
    (E / 'PACKAGE_STATUS_v064.json').write_text(json.dumps(data, indent=2) + '\n')
    print('V064_PACKAGE_STATUS', json.dumps(data), flush=True)

def command(args, log):
    with Path(log).open('w', encoding='utf8') as stream:
        r = subprocess.run([F, '-nostdin', '-hide_banner'] + [str(x) for x in args],
                           stdout=stream, stderr=subprocess.STDOUT)
    if r.returncode:
        raise RuntimeError(str(log) + '\n' + Path(log).read_text(errors='replace')[-6000:])
    return Path(log).read_text(errors='replace')

def checked_capture(args):
    r = subprocess.run([F, '-nostdin', '-hide_banner'] + [str(x) for x in args],
                       capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr[-6000:])
    return r.stderr

def fresh_input():
    return ['-framerate', str(FPS), '-start_number', '1', '-i', FRAMES / '%04d.png']

def common_video():
    return ['-c:v', 'libx264', '-preset', 'medium', '-b:v', VIDEO_RATE,
            '-maxrate', '1500k', '-bufsize', '3000k', '-threads', '4',
            '-pix_fmt', 'yuv420p', '-fps_mode', 'passthrough',
            '-video_track_timescale', '24000',
            '-color_primaries', 'bt709', '-color_trc', 'bt709',
            '-colorspace', 'bt709', '-color_range', 'tv']

def title_graph():
    return (
        '[0:v]trim=end_frame=2400,setpts=N/(24*TB),format=gbrp[w];'
        '[1:v]trim=end_frame=2400,setpts=N/(24*TB),'
        'scale=1280:720:flags=lanczos,format=gbrp[m];'
        '[w][m]blend=all_mode=multiply:shortest=1,setsar=1[p];'
        '[2:v]trim=end_frame=144,setpts=N/(24*TB),'
        'scale=1280:720:flags=lanczos,format=gbrp,setsar=1[c];'
        '[p][c]concat=n=2:v=1:a=0,'
        'scale=iw:ih:out_color_matrix=bt709:out_range=tv,format=yuv420p[v]'
    )

def two_pass_title(attempt):
    movie = attempt / 'WTSC_Procedural_Full_Knockout_v064.mp4'
    inputs = fresh_input() + ['-f', 'concat', '-safe', '0', '-i', MASK_LIST, '-i', CREDITS]
    graph = ['-filter_complex_threads', '2', '-filter_complex', title_graph(), '-map', '[v]']
    for pass_number in [1, 2]:
        status('encoding native title cut', pass_number=pass_number, frames=TOTAL_COUNT)
        args = inputs + ([] if pass_number == 1 else ['-i', WAV]) + graph + common_video()
        args += ['-pass', str(pass_number), '-passlogfile', attempt / 'title_2pass',
                 '-frames:v', str(TOTAL_COUNT)]
        if pass_number == 1:
            args += ['-an', '-f', 'null', os.devnull]
        else:
            args += ['-map', '3:a:0',
                     '-af', 'afade=t=out:st=90:d=10,apad=whole_dur=106,atrim=duration=106,asetpts=N/SR/TB',
                     '-c:a', 'aac', '-b:a', AUDIO_RATE, '-ar', '48000', '-ac', '2',
                     '-t', '106', '-movflags', '+faststart', '-y', movie]
        log = command(args + ['-progress', 'pipe:1', '-nostats'], attempt / ('title_pass%d.log' % pass_number))
        assert max([int(x) for x in re.findall(r'^dup_frames=(\d+)', log, re.M)] or [0]) == 0
        assert max([int(x) for x in re.findall(r'^drop_frames=(\d+)', log, re.M)] or [0]) == 0
    return movie

def two_pass_world(attempt):
    movie = attempt / 'WTSC_Procedural_Unmasked_World_v064.mp4'
    vf = 'trim=end_frame=2400,setpts=N/(24*TB),setsar=1,scale=iw:ih:out_color_matrix=bt709:out_range=tv,format=yuv420p'
    for pass_number in [1, 2]:
        status('encoding readable unmasked world', pass_number=pass_number, frames=WORLD_COUNT)
        args = fresh_input() + ['-vf', vf, '-map', '0:v:0', '-an'] + common_video()
        args += ['-pass', str(pass_number), '-passlogfile', attempt / 'world_2pass',
                 '-frames:v', str(WORLD_COUNT)]
        args += ['-f', 'null', os.devnull] if pass_number == 1 else ['-movflags', '+faststart', '-y', movie]
        log = command(args + ['-progress', 'pipe:1', '-nostats'], attempt / ('world_pass%d.log' % pass_number))
        assert max([int(x) for x in re.findall(r'^dup_frames=(\d+)', log, re.M)] or [0]) == 0
        assert max([int(x) for x in re.findall(r'^drop_frames=(\d+)', log, re.M)] or [0]) == 0
    return movie

def verify_clock(movie, count, seconds, expect_audio, attempt, label):
    text = command(['-i', movie, '-map', '0:v:0', '-vf', 'showinfo',
                    '-an', '-f', 'null', os.devnull], attempt / (label + '_full_decode.log'))
    samples = re.findall(r'n:\s*(\d+)\s+pts:\s*(-?\d+)\s+pts_time:([-\d.]+)', text)
    assert len(samples) == count, (label, len(samples), count)
    sizes = re.findall(r'n:\s*\d+[^\r\n]*\bs:(\d+)x(\d+)', text)
    assert len(sizes) == count and set(sizes) == {('1280', '720')}, (label, set(sizes), len(sizes))
    base_match = re.search(r'config in time_base:\s*(\d+)/(\d+)', text)
    assert base_match, (label, 'missing decoder time base')
    time_base = int(base_match.group(1)) / int(base_match.group(2))
    errors = []
    for i, (number, pts, stamp) in enumerate(samples):
        assert int(number) == i, (label, i, number)
        # Integer PTS avoids showinfo's six-significant-digit display rounding after 100 s.
        error = abs(int(pts) * time_base - i / FPS)
        assert error < 1e-8, (label, i, pts, stamp, error)
        errors.append(error)
    match = re.search(r'Duration:\s*(\d+):(\d+):([\d.]+)', text)
    assert match, label
    hh, mm, ss = match.groups()
    duration = 3600 * int(hh) + 60 * int(mm) + float(ss)
    assert abs(duration - seconds) < .011, (label, duration)
    assert ('Audio:' in text) is expect_audio, (label, 'audio stream mismatch')
    assert movie.stat().st_size < SIZE_LIMIT, (label, movie.stat().st_size)
    return {'decoded_frames': count, 'duration_seconds': duration,
            'fps': FPS, 'resolution': [1280, 720], 'all_pts_max_error_seconds': max(errors),
            'has_audio': expect_audio, 'bytes': movie.stat().st_size,
            'sha256': sha(movie), 'under_20000000_bytes': True}

def extract_selected(inputs, indices, outdir, extra_before_select=''):
    outdir.mkdir()
    expression = '+'.join('eq(n,%d)' % i for i in indices)
    vf = extra_before_select + (',' if extra_before_select else '') + "select='" + expression + "'"
    checked_capture(inputs + ['-map', '0:v:0', '-vf', vf, '-an',
                              '-fps_mode', 'passthrough', '-start_number', '1',
                              outdir / '%04d.png'])
    paths = sorted(outdir.glob('*.png'))
    assert len(paths) == len(indices), (outdir, len(paths), len(indices))
    return paths

def rgb(path):
    return np.asarray(Image.open(path).convert('RGB'), dtype=np.float32)

def verify_picture(movie, attempt, world_movie=None):
    actual = extract_selected(['-i', movie], SAMPLE_INDICES + [2400, 2543], attempt / 'title_decoded_samples')
    masks = extract_selected(['-f', 'concat', '-safe', '0', '-i', MASK_LIST],
                             SAMPLE_INDICES, attempt / 'native_mask_samples',
                             'scale=1280:720:flags=lanczos,format=rgb24')
    comparisons = []
    for i, index in enumerate(SAMPLE_INDICES):
        world = rgb(FRAMES / ('%04d.png' % (index + 1)))
        mask = rgb(masks[i])
        expected = world * mask / 255
        got = rgb(actual[i])
        error = float(np.abs(expected - got).mean())
        inside = mask.max(axis=2) > 32
        inside_error = float(np.abs(expected - got)[inside].mean()) if inside.any() else 0.0
        # Exclude native alpha's immediate edge before measuring black outside the letters.
        expanded = Image.fromarray(mask.max(axis=2).astype(np.uint8)).filter(ImageFilter.MaxFilter(9))
        outside = np.asarray(expanded) == 0
        outside_error = float(np.abs(got[outside]).mean()) if outside.any() else 0.0
        assert error < 8, (index, error)
        assert inside_error < 14, (index, inside_error)
        assert outside_error < 1.5, (index, outside_error)
        comparisons.append({'global_frame': index + 1, 'rgb_mae': error,
                            'inside_letters_rgb_mae': inside_error,
                            'outside_expanded_letters_rgb_mean': outside_error})
    credit_refs = extract_selected(['-i', CREDITS], [0, 143], attempt / 'original_credit_samples',
                                   'scale=1280:720:flags=lanczos,format=rgb24')
    credit_errors = []
    for got_path, expected_path in zip(actual[-2:], credit_refs):
        error = float(np.abs(rgb(got_path) - rgb(expected_path)).mean())
        assert error < 8, error
        credit_errors.append(error)
    world_errors = []
    if world_movie is not None:
        decoded_world = extract_selected(['-i', world_movie], SAMPLE_INDICES, attempt / 'world_decoded_samples')
        for i, index in enumerate(SAMPLE_INDICES):
            error = float(np.abs(rgb(decoded_world[i]) - rgb(FRAMES / ('%04d.png' % (index + 1)))) .mean())
            assert error < 8, (index, error)
            world_errors.append({'frame': index + 1, 'rgb_mae': error})
    return {'actual_title_vs_native_world_times_native_alpha': comparisons,
            'first_last_credits_rgb_mae': credit_errors,
            'unmasked_vs_fresh_native_samples': world_errors}

def verify_audio(movie, attempt):
    status('verifying original audio, single fade and silent credits')
    decoded, source = attempt / 'decoded_audio.f32', attempt / 'original_audio.f32'
    for input_path, target in [(movie, decoded), (WAV, source)]:
        checked_capture(['-i', input_path, '-map', '0:a:0', '-vn',
                         '-af', 'apad=whole_dur=106,atrim=duration=106',
                         '-ac', '2', '-ar', '48000', '-f', 'f32le', target])
    got = np.fromfile(decoded, dtype='<f4').reshape(-1, 2).astype(np.float64)
    original = np.fromfile(source, dtype='<f4').reshape(-1, 2).astype(np.float64)
    assert got.shape == original.shape == (106 * 48000, 2), (got.shape, original.shape)
    t = np.arange(len(original), dtype=np.float64) / 48000
    gain = np.ones(len(original), dtype=np.float64)
    gain[t >= 90] = np.clip((100 - t[t >= 90]) / 10, 0, 1)
    expected = original * gain[:, None]
    correlation = float(np.corrcoef(got[:90 * 48000].ravel(), original[:90 * 48000].ravel())[0, 1])
    assert correlation > .98, correlation
    fade_gain_samples = []
    for center in [90.5, 92, 95, 98, 99.5]:
        lo, hi = int((center - .20) * 48000), int((center + .20) * 48000)
        x, y, want = original[lo:hi].ravel(), got[lo:hi].ravel(), expected[lo:hi].ravel()
        denominator = float(np.dot(x, x))
        if denominator > 1e-9:
            measured_gain = float(np.dot(x, y) / denominator)
            expected_gain = float(np.dot(x, want) / denominator)
            assert abs(measured_gain - expected_gain) < .04, (center, measured_gain, expected_gain)
            fade_gain_samples.append({'seconds': center, 'measured_gain': measured_gain,
                                      'single_linear_fade_expected_gain': expected_gain})
    silent = got[100 * 48000:]
    silence_rms = float(np.sqrt(np.mean(silent ** 2)))
    silence_peak = float(np.abs(silent).max())
    assert silence_rms < .0001 and silence_peak < .001, (silence_rms, silence_peak)
    normalized_error = float(np.sqrt(np.mean((got - expected) ** 2)) / max(np.sqrt(np.mean(expected ** 2)), 1e-12))
    assert normalized_error < .20, normalized_error
    decoded.unlink()
    source.unlink()
    return {'original_wav_sha256': sha(WAV), 'sample_rate': 48000, 'channels': 2,
            'checked_duration_seconds': 106, 'zero_lag_correlation_before_fade': correlation,
            'single_90_to_100s_fade_gain_checks': fade_gain_samples,
            'silent_100_to_106s_rms': silence_rms, 'silent_100_to_106s_peak': silence_peak,
            'normalized_error_vs_original_with_one_fade': normalized_error,
            'start_seconds': 0, 'fade_count': 1, 'fade_seconds': [90, 100]}

def make_board(attempt):
    try:
        font = ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf', 17)
    except OSError:
        font = ImageFont.load_default()
    indices = [0, 432, 840, 1200, 1608, 1920, 2160, 2399]
    board = Image.new('RGB', (1280, 422), (18, 20, 23))
    draw = ImageDraw.Draw(board)
    for n, index in enumerate(indices):
        x, y = (n % 4) * 320, (n // 4) * 211
        with Image.open(FRAMES / ('%04d.png' % (index + 1))) as image:
            board.paste(image.convert('RGB').resize((320, 180), Image.Resampling.LANCZOS), (x, y + 31))
        draw.text((x + 10, y + 6), 'Native world | %.2f s | F%d' % (index / FPS, index + 1),
                  font=font, fill=(231, 233, 229))
    path = attempt / 'Full_Cut_World_Progression_v064.jpg'
    board.save(path, quality=94, subsampling=0)
    return path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--skip-world-review', action='store_true',
                        help='Skip the optional 100-second mute unmasked viewing copy.')
    args = parser.parse_args()
    E.mkdir(exist_ok=True)
    build = json.loads((E / 'FULL_CUT_BUILD.json').read_text())
    assert build['all_checks_pass'] is True
    assert build['unchanged_mask_and_credits_signature'] is True
    assert build['mask_reference_v040_verified'] is True
    assert Path(build['native']).resolve() == NATIVE.resolve()
    assert [build[k] for k in ['world_scene', 'picture_scene', 'master_scene']] == [
        'WTSC_PROCEDURAL_COLOR_WORLD_v064', 'WTSC_PROCEDURAL_FULL_CUT_v064', 'WTSC_PROCEDURAL_MASTER_106S_v064']
    native_hash = sha(NATIVE)
    assert native_hash == build['native_sha256'], (native_hash, build['native_sha256'])
    report_path = E / 'FULL_CUT_DELIVERY_v064.json'
    assert not report_path.exists(), 'Completed delivery already exists; preserve it.'
    finals = [P / 'WTSC_Procedural_Full_Knockout_v064.mp4', P / 'Full_Cut_World_Progression_v064.jpg']
    if not args.skip_world_review:
        finals.append(P / 'WTSC_Procedural_Unmasked_World_v064.mp4')
    assert not any(x.exists() for x in finals), 'A final output already exists; preserve it.'
    status('preflight native source, cached title/credits and all fresh world frames')
    assert sha(WAV) == EXPECTED_WAV
    cache_hashes = {}
    for name, expected in EXPECTED_CACHED.items():
        path = MASK_DIR / name
        h = sha(path)
        assert h == expected, (name, h)
        cache_hashes[name] = h
    assert MASK_LIST.read_text().splitlines() == ["file 'mask_%02d.mp4'" % i for i in range(1, 5)]
    frame_rows, adjacent_identical = [], []
    previous = None
    for index in range(1, WORLD_COUNT + 1):
        path = FRAMES / ('%04d.png' % index)
        with Image.open(path) as image:
            assert image.size == (1280, 720), (index, image.size)
        h = sha(path)
        frame_rows.append({'frame': index, 'sha256': h})
        if h == previous:
            adjacent_identical.append(index)
        previous = h
    # Identical native holds are reported, never replaced or interpolated.
    stamp = time.strftime('%Y%m%d_%H%M%S', time.gmtime())
    attempt = P / ('package_run_' + stamp)
    attempt.mkdir()
    (attempt / 'FRESH_WORLD_FRAME_HASHES.json').write_text(json.dumps(frame_rows, indent=2) + '\n')
    title = two_pass_title(attempt)
    world = None if args.skip_world_review else two_pass_world(attempt)
    status('decoding complete deliverables and checking every timestamp')
    title_check = verify_clock(title, TOTAL_COUNT, 106, True, attempt, 'title')
    world_check = None if world is None else verify_clock(world, WORLD_COUNT, 100, False, attempt, 'world')
    picture_check = verify_picture(title, attempt, world)
    audio_check = verify_audio(title, attempt)
    board = make_board(attempt)
    assert sha(NATIVE) == native_hash
    assert sha(WAV) == EXPECTED_WAV
    for name, h in cache_hashes.items():
        assert sha(MASK_DIR / name) == h
    delivery_paths = []
    for src in [title, board] + ([] if world is None else [world]):
        target = P / src.name
        assert not target.exists()
        shutil.copy2(src, target)
        assert sha(target) == sha(src)
        delivery_paths.append(str(target))
    title_check['path'] = str(P / title.name)
    if world_check is not None:
        world_check['path'] = str(P / world.name)
    report = {
        'native': str(NATIVE), 'native_sha256': native_hash, 'native_unchanged': True,
        'build_evidence': str(E / 'FULL_CUT_BUILD.json'),
        'world_scene': 'WTSC_PROCEDURAL_COLOR_WORLD_v064',
        'picture_scene': 'WTSC_PROCEDURAL_FULL_CUT_v064',
        'master_scene': 'WTSC_PROCEDURAL_MASTER_106S_v064',
        'world_source': 'All 2400 freshly rendered native PNGs; supplied title-matched glare is not reapplied.',
        'world_frame_pattern': str(FRAMES / '%04d.png'),
        'world_frame_hash_manifest': str(attempt / 'FRESH_WORLD_FRAME_HASHES.json'),
        'source_frames': [1, 2400], 'source_resolution': [1280, 720],
        'source_adjacent_identical_native_frames_reported_not_repaired': adjacent_identical,
        'cached_mask_and_credit_hashes': cache_hashes,
        'unchanged_mask_and_credits_signature': True,
        'cached_old_world_used': False, 'frame_interpolation': False,
        'video_target_bitrate': VIDEO_RATE, 'audio_target_bitrate': AUDIO_RATE,
        'encoder': 'libx264 two-pass medium / yuv420p / bt709',
        'native_glare_already_in_world_frames': True,
        'duplicate_or_dropped_frames_added_by_packager': False,
        'primary': title_check, 'unmasked_mute_world_review': world_check,
        'picture_verification': picture_check, 'audio_verification': audio_check,
        'deliveries': delivery_paths, 'run_evidence_directory': str(attempt),
        'board_sha256': sha(P / board.name),
        'limits': 'Procedural development cut. Completion of this export does not establish final character acting, shot finish or Arcane-level production quality.',
    }
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    status('complete', primary=str(P / title.name), optional_world=None if world is None else str(P / world.name),
           total_frames=TOTAL_COUNT, seconds=106, report=str(report_path))
    print('V064_FULL_CUT_PACKAGE_COMPLETE', flush=True)

if __name__ == '__main__':
    main()
