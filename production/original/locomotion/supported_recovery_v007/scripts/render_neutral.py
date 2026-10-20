import bpy,json,sys
from pathlib import Path
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Supported_Recovery_v007.blend'),load_ui=False)
s=bpy.context.scene;assert s.render.engine=='BLENDER_EEVEE';s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100
folder=P/'previews/neutral';folder.mkdir(exist_ok=True)
frames=range(1,121) if '--all' in sys.argv else [1,37,43,47,48,58,81,89,101,110,120]
for f in frames:
    path=folder/f'{f:04d}.png'
    if path.exists():continue
    s.frame_set(f);s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
print('V007_NEUTRAL_RENDER_DONE',flush=True)
