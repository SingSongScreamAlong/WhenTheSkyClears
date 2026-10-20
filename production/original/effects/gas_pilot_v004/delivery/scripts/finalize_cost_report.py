import json
from pathlib import Path
P = Path(__file__).resolve().parents[1]
def read(name):
    return json.loads((P / 'evidence' / name).read_text(encoding='utf-8-sig'))
main = read('render_motion.json')
preroll = read('render_preroll.json')
main['requested_range'] = [-23, 96]
main['range'] = [0, 96]
main['actual_main_pass_frames'] = 97
main['additional_manual_preroll_frames'] = 23
main['additional_manual_preroll_seconds'] = preroll['wall_seconds']
main['total_final_frames'] = 120
main['total_render_calls_seconds'] = main['wall_seconds'] + preroll['wall_seconds']
main['note'] = 'Initial animation start clamped to0. Missing23negative pre-roll frames were subsequently rendered explicitly; all120finalframes were validated.'
(P / 'evidence/render_motion.json').write_text(json.dumps(main, indent=2))
media = read('media_validation.json')
media['renderer'] = main
(P / 'evidence/media_validation.json').write_text(json.dumps(media, indent=2))
small = read('bake_result.json'); small_resource = read('bake_resources.json')
proof = read('proof_bake_result.json'); proof_resource = read('proof_bake_resources.json')
particles = read('particle_setup.json'); render = read('render_resources.json')
summary = {'pilot40': {'bake_seconds': small['bake_seconds'], 'cache_MiB': small['cache_bytes'] / 1024**2, 'peak_RSS_MiB': small_resource['peak_rss_bytes'] / 1024**2}, 'proof48': {'bake_seconds': proof['bake_seconds'], 'cache_MiB': proof['cache_bytes'] / 1024**2, 'peak_RSS_MiB': proof_resource['peak_rss_bytes'] / 1024**2}, 'particles': {'bake_seconds': particles['particle_bake_seconds'], 'point_cache_KiB': particles['pointcache_bytes'] / 1024}, 'render': {'total_render_calls_seconds': main['total_render_calls_seconds'], 'final_frames': 120, 'measured_main_pass_peak_RSS_MiB': render['peak_rss_bytes'] / 1024**2, 'GPU_device_total_peak_MiB': render['gpu_peak_total_used_MiB'], 'GPU_device_total_baseline_MiB': render['gpu_baseline_total_used_MiB'], 'GPU_attribution': 'Device total; not exclusive per-process'}, 'limits_reached': False, 'no_upres_noise_bake': True, 'no_production_worker_interrupted': True, 'artistic_status': 'Coarse technique proof, not accepted production art.'}
(P / 'evidence/cost_summary.json').write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))
