import bpy,sys
from pathlib import Path
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'scripts'));import story_poses as M
bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Whole_Pose_Blocking_v013.blend'),load_ui=False);s=bpy.context.scene;s.render.image_settings.file_format='PNG'
frames=range(1,73) if '--all' in sys.argv else M.KEYS
for mode in ['INSPECTION','SHOT_SIZE']:
 s.camera=bpy.data.objects['TEST | '+mode];folder=P/'previews'/mode;folder.mkdir(exist_ok=True)
 for f in frames:
  path=folder/f'{f:04d}.png'
  if path.exists() and '--force' not in sys.argv:continue
  s.frame_set(f);s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
 print('V013_BLOCKING_RENDERED',mode,flush=True)
