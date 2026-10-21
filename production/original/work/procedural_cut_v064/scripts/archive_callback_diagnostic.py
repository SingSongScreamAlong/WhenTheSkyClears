from pathlib import Path
import shutil,json,time
O=Path(r'WTSC_LOCAL_WORKSPACE\work\procedural_cut_v064')
dst=O/'evidence/diagnostic_animation_callback'
dst.mkdir(exist_ok=False)
for f in (O/'evidence').glob('world_*.log'):shutil.move(str(f),str(dst/f.name))
for f in ['render_full_world.log','RENDER_STATUS.json']:
 p=O/'evidence'/f
 if p.exists():shutil.move(str(p),str(dst/f))
frames=O/'previews/world_frames'
shutil.move(str(frames),str(O/'previews/diagnostic_animation_callback_frames'));frames.mkdir()
(dst/'REASON.json').write_text(json.dumps(dict(reason='Animation callback read original saved datablock properties instead of evaluated render values; exported opening image was full-color correctly. Batch stopped after failed verification. Corrected explicit frame_set/render loop retains native procedural drivers and checks each actual frame.',preserved_frames=len(list((O/'previews/diagnostic_animation_callback_frames').glob('*.png')))),indent=2))
print('V064_DIAGNOSTIC_BATCH_ARCHIVED')
