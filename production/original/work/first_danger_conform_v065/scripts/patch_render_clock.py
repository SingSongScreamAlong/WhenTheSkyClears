"""Make global palette scene time explicit across nested render/Scene-strip graphs."""
import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'work/first_danger_conform_v065'
S=O/'native/WTSC_First_Danger_Conformed_v065.blend';N=O/'native/WTSC_First_Danger_Conformed_v065b.blend'
assert not N.exists()
bpy.ops.wm.open_mainfile(filepath=str(S),load_ui=False,use_scripts=False)
w=bpy.data.scenes['WTSC_FIRST_DANGER_WORLD_v065'];ctrl=bpy.data.objects['V065 | both children | global full-cut color time']
f=next(f for f in ctrl.animation_data.drivers if f.data_path=='["charcoal_progress"]');dr=f.driver
v=dr.variables.new();v.name='global_frame';v.type='SINGLE_PROP';v.targets[0].id_type='SCENE';v.targets[0].id=w;v.targets[0].data_path='frame_current_final'
dr.expression=dr.expression.replace('frame-1','global_frame-1')
for name in ['WTSC_FIRST_DANGER_TITLE_v065','WTSC_FIRST_DANGER_UNMASKED_EDIT_v065','WTSC_FIRST_DANGER_REVIEW_MASTER_v065']:
 s=bpy.data.scenes[name]
 if ctrl.name not in s.objects:s.collection.objects.link(ctrl)
 s.frame_set(981)
bpy.context.window.scene=w;w.frame_set(981);bpy.context.view_layer.update()
ctrl['V065_explicit_clock']='Scene.frame_current_final from the world, shared across every delivery scene; nested renders cannot keep a stale implicit driver frame.'
bpy.ops.wm.save_as_mainfile(filepath=str(N),compress=True)
build=json.loads((O/'evidence/BUILD.json').read_text());build['previous_draft']=str(S);build['previous_draft_sha256']=hashlib.sha256(S.read_bytes()).hexdigest();build['native']=str(N);build['native_sha256']=hashlib.sha256(N.read_bytes()).hexdigest();build['clock_correction']={'explicit_scene_clock':w.name+'.frame_current_final','driver':dr.expression,'controller_linked_to_all_delivery_scenes':True}
(O/'evidence/BUILD.json').write_text(json.dumps(build,indent=2));print('V065B_CLOCK_PATCH_SAVED',flush=True)
