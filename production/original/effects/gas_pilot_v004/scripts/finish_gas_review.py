import json, subprocess, re, hashlib, os
from pathlib import Path
from PIL import Image

P = Path(__file__).resolve().parents[1]
F = Path(r'WTSC_LOCAL_USER\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe')
raw = P / 'previews/proof_frames'
files = {int(file.stem): file for file in raw.glob('*.png')}
assert set(files) == set(range(-23, 97)), (len(files), min(files), max(files))
aligned = P / 'previews/matched_global'
aligned.mkdir(exist_ok=True)
for local, file in files.items():
    with Image.open(file) as image:
        image.load()
        assert image.size == (1920, 1080)
    dest = aligned / f'{local + 1823:04}.png'
    if not dest.exists():
        os.link(file, dest)
    assert os.path.samefile(file, dest)
reference = P.parent / 'benchmark_v003/previews/motion_frames'
assert len(list(reference.glob('*.png'))) == 120

def run(arguments, log_name):
    result = subprocess.run([str(F), '-hide_banner', '-nostdin', '-y', *arguments], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    (P / 'evidence' / log_name).write_text(result.stderr)
    assert result.returncode == 0, result.stderr
    return result

codec = ['-frames:v', '120', '-an', '-c:v', 'libx264', '-crf', '17', '-preset', 'fast', '-threads', '2', '-pix_fmt', 'yuv420p', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-movflags', '+faststart']
proof = P / 'WTSC_Gas_Particles_75-80s_v004.mp4'
comparison = P / 'WTSC_Compare_LEFT-v003_RIGHT-Gas-v004.mp4'
run(['-framerate', '24', '-start_number', '1800', '-i', str(aligned / '%04d.png'), *codec, str(proof)], 'encode_proof.log')
run(['-framerate', '24', '-start_number', '1800', '-i', str(reference / '%04d.png'), '-framerate', '24', '-start_number', '1800', '-i', str(aligned / '%04d.png'), '-filter_complex', '[0:v][1:v]hstack=inputs=2[v]', '-map', '[v]', *codec, str(comparison)], 'encode_comparison.log')
outputs = []
for file, pixels in [(proof, [1920, 1080]), (comparison, [3840, 1080])]:
    assert file.stat().st_size < 20_000_000
    result = run(['-v', 'error', '-i', str(file), '-progress', 'pipe:1', '-f', 'null', 'NUL'], file.stem + '_decode.log')
    counts = re.findall(r'^frame=(\d+)', result.stdout, re.M)
    assert counts and int(counts[-1]) == 120
    outputs.append({'file': file.name, 'bytes': file.stat().st_size, 'sha256': hashlib.sha256(file.read_bytes()).hexdigest(), 'pixels': pixels, 'frames': 120, 'fps': 24, 'seconds': 5, 'full_decode': True})
audit = P / 'previews/decoded_audit'
audit.mkdir(exist_ok=True)
frames = [1825, 1830, 1847, 1860, 1883, 1919]
selector = "select='" + '+'.join(f'eq(n,{frame - 1800})' for frame in frames) + "'"
run(['-v', 'error', '-i', str(proof), '-vf', selector, '-fps_mode', 'passthrough', str(audit / '%02d.png')], 'extract_audit.log')
(P / 'evidence/decoded_audit_map.json').write_text(json.dumps([{'image': f'{i + 1:02d}.png', 'production_frame': frame, 'gas_local_frame': frame - 1823} for i, frame in enumerate(frames)], indent=2))
run(['-i', str(reference / '1883.png'), '-i', str(aligned / '1883.png'), '-filter_complex', '[0:v][1:v]hstack=inputs=2[v]', '-map', '[v]', '-frames:v', '1', str(P / 'previews/Compare_LEFT-v003_RIGHT-Gas_v004_frame1883.png')], 'comparison_still.log')
v3 = P.parent / 'benchmark_v003/native/WTSC_Evolving_Eruption_Collection_v003.blend'
v3_sha = hashlib.sha256(v3.read_bytes()).hexdigest()
assert v3_sha == 'd089770cccee18b786692d76113b80fbf8514d8034bab4eaae17d6b5f9bd1868'
report = {'outputs': outputs, 'all120_new_pngs_decoded': True, 'all_frames_actual_new_gpu_renders': True, 'partial_CPU_frames_excluded': True, 'same_camera_and_framing_as_v003': True, 'timeline': {'new_local_range': [-23, 96], 'production_range': [1800, 1919], 'local_ignition': 1, 'production_ignition': 1824, 'gas_cache_local_range': [1, 120]}, 'v003_source_unchanged_sha256': v3_sha, 'renderer': json.loads((P / 'evidence/render_motion.json').read_text()), 'render_resources': json.loads((P / 'evidence/render_resources.json').read_text()), 'status': 'Coarse technique proof. Gas viability is not cinematic acceptance or production integration.'}
(P / 'evidence/media_validation.json').write_text(json.dumps(report, indent=2))
print('GAS_REVIEW_MEDIA_COMPLETE', json.dumps({k: v for k, v in report.items() if k != 'render_resources'}), flush=True)
