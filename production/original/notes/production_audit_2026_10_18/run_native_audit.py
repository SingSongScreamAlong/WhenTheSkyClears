import json
import subprocess
import time
from pathlib import Path
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
BLENDER = Path(r'WTSC_LOCAL_USER\AppData\Local\Programs\Blender\blender-5.2.2-windows-x64\blender.exe')
sources = {
    'full_v040': 'shots/world/WTSC_Painted_World_Full_Trailer_Editable_v040.blend',
    'world_v058': 'work/world_minimum_v058/WTSC_World_Development_v058_Packed.blend',
    'recovery_v059': 'work/production_review_v059/WTSC_Production_Benchmark_v059.blend',
    'color_v063': 'work/color_arc_v063/native/WTSC_Shared_Color_To_Charcoal_v063.blend',
    'face_hand_v050': 'locomotion/face_hand_finish_v050/native/WTSC_Face_Hand_Finish_v050.blend',
    'coat_v051': 'locomotion/coat_fluidity_v051/native/WTSC_Controlled_Fluid_Coat_v051.blend',
    'impact_v015d': 'effects/main_impact_v015/native/WTSC_Painted_Main_Impact_Append_v015d.blend',
}
results = []
for label, rel in sources.items():
    source = ROOT / rel
    if not source.exists():
        results.append({'label': label, 'source': rel, 'status': 'missing_selected_path'})
        print('MISSING', label, flush=True)
        continue
    start = time.monotonic()
    try:
        with (OUT / f'native_{label}.log').open('w', encoding='utf-8') as stream:
            done = subprocess.run([str(BLENDER), '--background', '--factory-startup', '--disable-autoexec',
                                   '--threads', '2', '--python', str(OUT / 'audit_native.py'), '--',
                                   str(source), str(OUT / f'native_{label}.json')],
                                  cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT,
                                  timeout=120, creationflags=subprocess.CREATE_NO_WINDOW)
        results.append({'label': label, 'source': rel, 'returncode': done.returncode,
                        'json_written': (OUT / f'native_{label}.json').exists(),
                        'seconds': round(time.monotonic() - start, 3)})
    except subprocess.TimeoutExpired:
        results.append({'label': label, 'source': rel, 'status': 'timeout', 'seconds': 120})
    (OUT / 'native_runs.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
    print(json.dumps(results[-1]), flush=True)
