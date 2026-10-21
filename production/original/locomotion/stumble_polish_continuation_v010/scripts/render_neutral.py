import bpy,sys
from pathlib import Path
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Stumble_Polish_Continuation_v010.blend'),load_ui=False);s=bpy.context.scene
s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';folder=P/'previews/neutral';folder.mkdir(exist_ok=True)
frames=range(1,169) if '--all' in sys.argv else [25,33,37,41,45,53,69,81,94,102,116,119,120,121,124,128,134,142,148,152,160,166,168]
for f in frames:
 path=folder/f'{f:04d}.png'
 if path.exists() and '--force' not in sys.argv:continue
 s.frame_set(f);s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
print('V010_NEUTRAL_RENDER_DONE',flush=True)
