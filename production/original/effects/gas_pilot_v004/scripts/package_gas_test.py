import json, hashlib, zipfile, shutil
from pathlib import Path
P = Path(__file__).resolve().parents[1]
stage = P / 'delivery'
for name in ['TECHNIQUE_TEST_README.txt']:
    shutil.copy2(P / name, stage / name)
evidence = ['installed_gas_probe.json', 'pilot_config.json', 'bake_result.json', 'bake_resources.json', 'proof_config.json', 'proof_bake_result.json', 'proof_bake_resources.json', 'particle_setup.json', 'proof_scene_validation.json', 'portable_native_validation.json', 'render_keys.json', 'render_resources.json', 'render_motion.json', 'render_preroll.json', 'media_validation.json', 'visual_assessment.json', 'cpu_to_gpu_swap.json', 'cost_summary.json']
(stage / 'evidence').mkdir(exist_ok=True)
for name in evidence:
    shutil.copy2(P / 'evidence' / name, stage / 'evidence' / name)
(stage / 'scripts').mkdir(exist_ok=True)
for file in (P / 'scripts').glob('*.py'):
    shutil.copy2(file, stage / 'scripts' / file.name)
members = [stage / 'native/WTSC_Gas_Particles_Proof_48r_120f_v004.blend']
members += [file for file in (stage / 'native/blendcache_WTSC_Gas_Particles_Proof_48r_120f_v004').rglob('*') if file.is_file()]
members += [file for file in (stage / 'cache/proof_48r_120f').rglob('*') if file.is_file()]
members += [file for folder in ['evidence', 'scripts'] for file in (stage / folder).rglob('*') if file.is_file()]
members += [stage / 'TECHNIQUE_TEST_README.txt']
manifest = {'status': 'Coarse technique test only; not accepted production art.', 'files': []}
for file in members:
    data = file.read_bytes()
    manifest['files'].append({'path': file.relative_to(stage).as_posix(), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
(stage / 'MANIFEST.json').write_text(json.dumps(manifest, indent=2))
target = P / 'WTSC_Gas_Particles_Technique_Source_v004.zip'
with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
    for file in members + [stage / 'MANIFEST.json']:
        archive.write(file, arcname=file.relative_to(stage).as_posix())
with zipfile.ZipFile(target) as archive:
    assert archive.testzip() is None
report = {'file': target.name, 'bytes': target.stat().st_size, 'sha256': hashlib.sha256(target.read_bytes()).hexdigest(), 'members': len(members) + 1, 'crc_test': 'passed', 'cache_included': True, 'native_relative_cache_loading': 'validated at density60 and particles12', 'excluded': 'Pilot40cache, partialCPUframes, rawGPUimages, production source files, backup blends and unrelated private files.'}
(P / 'evidence/package_validation.json').write_text(json.dumps(report, indent=2))
print('GAS_SOURCE_PACKAGED', json.dumps(report), flush=True)
