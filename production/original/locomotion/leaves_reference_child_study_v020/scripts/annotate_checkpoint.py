import bpy
from pathlib import Path
P=Path(__file__).resolve().parents[1]
# The cached source native was created by this study; trim only factory defaults.
path=P/'native/Leaves_Walk_Source_Inspection_v020.blend';bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
for name in ['Cube','Light','Camera']:
 o=bpy.data.objects.get(name)
 if o:bpy.data.objects.remove(o,do_unlink=True)
S=bpy.context.scene;S.render.fps=30;S.frame_start=2;S.frame_end=33;S.frame_set(2);S['source_status']='Original user-supplied52bone FBX action,30fps keys2..33. Cached import only; no child animation.';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
path=P/'native/WTSC_Leaves_Reference_Child_Eight_Poses_v020.blend';bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);S=bpy.context.scene
for filename in ['V020_REFERENCE_TO_CHILD_REPORT.txt','V020_IMPORT_AND_SOURCE_TIME_GUIDE.txt','V020_CORRECTIVES_NOT_STARTED.csv']:
 t=bpy.data.texts.get(filename) or bpy.data.texts.new(filename);t.clear();t.write((P/filename).read_text())
for filename in ['build_study.py','source_match.py']:
 t=bpy.data.texts.get('V020 '+filename) or bpy.data.texts.new('V020 '+filename);t.clear();t.write((P/'scripts'/filename).read_text())
def hide_preview(lc):
 if lc.name in ['V020 | source skeleton render','V020 | child native skeleton render']:lc.hide_viewport=True
 for child in lc.children:hide_preview(child)
for vl in S.view_layers:hide_preview(vl.layer_collection)
bpy.data.objects['V020 | SOURCE52 | exact FBX sampled poses'].hide_set(True);S.camera=bpy.data.objects['V020 | CHILD | CLOSE'];S.frame_set(1);S['V020_stop']='Review only. Matching partial and art unpassed. No world/production integration. No broad child in-between pass.';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
print('V020_CHECKPOINT_ANNOTATED_NO_ANIMATION_EDITS')
