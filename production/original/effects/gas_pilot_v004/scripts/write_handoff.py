import json
from pathlib import Path
P = Path(__file__).resolve().parents[1]
def read(name):
    return json.loads((P / 'evidence' / name).read_text(encoding='utf-8-sig'))
items = read('library_media_receipt.json')['items'] + read('library_images_receipt.json')['items']
report = {
    'task_status': 'Completed bounded gas/particle feasibility test and actual matched five-second review media.',
    'technical_conclusion': 'Native GAS/OpenVDB and sparse Newtonian particle simulation work in installed Blender5.2.2 within small measured resource limits.',
    'artistic_conclusion': 'Not accepted. Coarse gas is soft and fog-like with less painted detail than v003. Keep v003 as the existing integration candidate; do not substitute this gas test as approved final art.',
    'actual_media': read('media_validation.json')['outputs'],
    'native_portable': read('portable_native_validation.json'),
    'native_portable_absolute_path': str(P / 'delivery/native/WTSC_Gas_Particles_Proof_48r_120f_v004.blend'),
    'original_render_scene_absolute_path': str(P / 'native/WTSC_Gas_Particles_Proof_48r_120f_v004.blend'),
    'source_archive': read('package_validation.json'),
    'measured_cost': read('cost_summary.json'),
    'library': [{'file_name': item.get('file_name'), 'library_file_id': item.get('library_file_id'), 'file_id': item.get('file_id'), 'status': item.get('status'), 'local_path': item.get('local_path')} for item in items],
    'timing': {'fps': 24, 'review_production_frames': [1800, 1919], 'production_ignition': 1824, 'cache_local_ignition': 1, 'gas_cache_range': [1, 120], 'mapping': 'production = local +1823', 'review_local_frames': [-23, 96], 'all120_review_frames': 'Actual fresh1080p GPU renders; negative pre-roll manually stepped because Scene.frame_start clamps to0.'},
    'particle_method': '12native NEWTON debris particles and6native NEWTON embers, short births/lives, disk caches, transparent isolated test collider. Actual18live particles verified at local12 in portable copy.',
    'physical_domain': {'metres': [4.2, 2.8, 4.0], 'grid': [48, 32, 46], 'source_world_metres': [109.1, 10, -0.7048803], 'noise_upres_bake': False, 'material_finish': 'Mild16percent3D density noise wash, not simulated fine detail. Native volume emission and blackbody zero.'},
    'ownership': 'No main production edits. Preview-only local shading lights and test collider remain in the separate proof. Production owns lighting/contact/live occlusion and actual integration.',
    'preservation': {'v003_collection_sha256_unchanged': read('media_validation.json')['v003_source_unchanged_sha256'], 'v001': 'Rejected and excluded', 'owned_render_jobs': 'Finished; CPU preview was stopped only by verified owned PID50160;27partial CPU frames preserved and excluded from final.'},
    'tests_actually_completed': ['Native solver/flow RNA and actual bake execution', '72frame40division and120frame48division supervised caches; no caps hit', 'Native particle baking and position samples', 'Relative portable gas cache read at60 and18live particles at12', 'All120new PNGs loaded; both120frame MP4s fully decoded', 'Representative native-size GPU/exported frames inspected', 'ZIP CRC check passed', 'Protected v003 source hash unchanged'],
    'remaining_limits': ['No cinematic artistic acceptance', 'Coarse smooth/foggy volume lacks fine painterly billows; broad late cloud and small-domain edges require review', 'Held original camera/children/scenery; no current production stumble, moving camera, live occlusion/contact or4K validation', 'Native test uses local cache timeline and is not a tested direct global-timeline Append asset', 'No real-time full-video playback audit', 'No transparent animation export in this revision'],
    'delivery_notes': 'Extract entire source archive, preserve native blend basename and matching blendcache folder. Gas path is relative. All image dependencies are packed. Library saves succeeded; unsupported Windows xattrs are retained in receipt JSON rather than local filesystem metadata.',
    'remaining_blockers': 'No technical blocker to reviewing this feasibility evidence. Artistic quality and production cache/timeline integration remain unaccepted.'
}
assert all(item['status'] == 'succeeded' for item in report['library'])
(P / 'evidence/HANDOFF_v004.json').write_text(json.dumps(report, indent=2))
print('HANDOFF_READY', len(items), 'Library results; native', report['native_portable']['sha256'])
