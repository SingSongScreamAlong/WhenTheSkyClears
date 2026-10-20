import bpy,sys,json
from pathlib import Path
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Recovery_Walk_v009.blend'),load_ui=False);s=bpy.context.scene
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=16;s.render.threads_mode='FIXED';s.render.threads=2
s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100
folder=P/'previews/neutral';folder.mkdir(exist_ok=True)
frames=range(1,121) if '--all' in sys.argv else [37,44,45,73,81,86,94,99,102,108,112,116,120]
for f in frames:
 path=folder/f'{f:04d}.png'
 if path.exists() and '--force' not in sys.argv:continue
 s.frame_set(f);s.render.filepath=str(path);bpy.ops.render.render(write_still=True);print('PROOF_FRAME',f,flush=True)
print('NEUTRAL_PROOF_DONE',flush=True)
