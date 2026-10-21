import bpy,sys
from pathlib import Path
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Unpainted_Motion_Rebuild_v012.blend'),load_ui=False);s=bpy.context.scene
modes=['INSPECTION','SHOT_SIZE'] if '--both' in sys.argv else ['SHOT_SIZE' if '--shot' in sys.argv else 'INSPECTION'];s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG'
frames=range(1,145) if '--all' in sys.argv else [1,13,20,22,23,24,25,26,27,28,29,30,32,34,36,38,40,42,44,48,53,58,64,66,70,74,78,83,86,90,94,98,102,106,109,113,117,121,124,128,132,136,139,144]
for mode in modes:
 s.camera=bpy.data.objects['TEST | '+mode];folder=P/'previews'/mode;folder.mkdir(exist_ok=True)
 for f in frames:
  path=folder/f'{f:04d}.png'
  if path.exists() and '--force' not in sys.argv:continue
  s.frame_set(f);s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
 print('V012_TEST_RENDER_DONE',mode,flush=True)
