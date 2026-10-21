import bpy,sys
from pathlib import Path
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_v009_Matched_Review_Copy.blend'),load_ui=False);s=bpy.context.scene
s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.use_sequencer=False
folder=P/'previews/matched';folder.mkdir(exist_ok=True)
frames=range(1,121) if '--all' in sys.argv else [44,45,81,86,94,99,102,108,112,116,120]
for f in frames:
 path=folder/f'{f:04d}.png'
 if path.exists() and '--force' not in sys.argv:continue
 s.frame_set(f+1800);s.render.filepath=str(path);bpy.ops.render.render(write_still=True);print('MATCHED_FRAME',f,flush=True)
print('MATCHED_REVIEW_DONE',flush=True)
