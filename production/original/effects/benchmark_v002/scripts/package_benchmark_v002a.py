"""Package only this benchmark's original assets and isolated native deliverables."""
import json, hashlib, zipfile
from pathlib import Path
from PIL import Image

P = Path(__file__).resolve().parents[1]
members = [
    'BENCHMARK_README.txt',
    'CURRENT_STATUS_v002a.txt',
    'native/WTSC_Hero_Eruption_Collection_v002a.blend',
    'native/WTSC_FX_Append_Test_v002a.blend',
    'assets/Hero_Explosion_Paint_v002.png',
    'assets/Ground_Dust_Paint_v002.png',
    'previews/Native_Append_Test_RGBA_v002a.png',
    'scripts/append_sandbox_v002a.py',
    'scripts/render_motion_gpu_v002.py',
    'scripts/package_benchmark_v002a.py',
    'evidence/append_test_v002a.json',
    'evidence/benchmark_native_validation.json',
    'evidence/visual_audit_v002a.json',
    'evidence/media_validation.json',
    'evidence/gpu_motion_render_v002.json',
    'evidence/resume_reconciliation_20261017.json',
    'evidence/imagegen_prompts_full.json',
    'evidence/art_recipe.json',
]
manifest = {
    'status': 'One unaccepted detailed benchmark. V001 remains rejected.',
    'included': [],
    'excluded': 'Production sources, full scene copies, render caches, partial CPU frames, generated base64 transfer files and unrelated private files.',
    'render_script_note': 'The GPU render script records local provenance. It requires the separately retained project-specific motion scene and is not a standalone rebuild script.',
    'alpha_still_note': 'Single native sandbox RGBA image only; no transparent animation sequence claimed.',
}
for name in members:
    data = (P / name).read_bytes()
    manifest['included'].append({'path': name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
(P / 'evidence/package_manifest_v002a.json').write_text(json.dumps(manifest, indent=2))
target = P / 'WTSC_Eruption_Benchmark_Assets_v002a.zip'
with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for name in members:
        z.write(P / name, arcname=name)
    z.write(P / 'evidence/package_manifest_v002a.json', arcname='evidence/package_manifest_v002a.json')
with zipfile.ZipFile(target) as z:
    assert z.testzip() is None
with Image.open(P / 'previews/Native_Append_Test_RGBA_v002a.png') as im:
    im.load()
    assert im.mode == 'RGBA' and im.size == (640, 640)
    alpha = im.getchannel('A').getextrema()
    assert alpha[0] == 0 and alpha[1] > 240
report = {'path': str(target), 'bytes': target.stat().st_size, 'sha256': hashlib.sha256(target.read_bytes()).hexdigest(), 'zip_crc_test': 'passed', 'members': len(members) + 1, 'native_append_rgba_alpha_extrema': alpha, 'artistic_status': 'Unaccepted benchmark, not final integration pack.'}
(P / 'evidence/package_validation_v002a.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
