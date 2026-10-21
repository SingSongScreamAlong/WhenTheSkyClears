import bpy,sys
from pathlib import Path
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Unpainted_Motion_Rebuild_v011.blend'),load_ui=False);s=bpy.context.scene
modes=['INSPECTION','SHOT_SIZE'] if '--both' in sys.argv else ['SHOT_SIZE' if '--shot' in sys.argv else 'INSPECTION'];s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG'
frames=range(1,145) if '--all' in sys.argv else [1,13,23,24,27,30,35,40,44,48,56,64,66,72,78,82,94,109,124,139,144]
for mode in modes:
 s.camera=bpy.data.objects['TEST | '+mode];folder=P/'previews'/mode;folder.mkdir(exist_ok=True)
 for f in frames:
  path=folder/f'{f:04d}.png'
  if path.exists() and '--force' not in sys.argv:continue
  s.frame_set(f);s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
 print('V011_TEST_RENDER_DONE',mode,flush=True)
