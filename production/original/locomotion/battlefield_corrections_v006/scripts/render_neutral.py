import bpy,json,sys
from pathlib import Path
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Battlefield_Drawn_Corrections_v006.blend'),load_ui=False)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=2;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100
folder=P/'previews/neutral';folder.mkdir(exist_ok=True)
frames=range(1,121) if '--all' in sys.argv else [1,37,47,58,81,101,120]
for f in frames:
    path=folder/f'{f:04d}.png'
    if path.exists():continue
    s.frame_set(f);s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
print('V006_NEUTRAL_RENDER_DONE',flush=True)
