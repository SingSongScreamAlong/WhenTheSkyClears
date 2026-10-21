import bpy,sys,json
from pathlib import Path
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'scripts'));import motion_design as M
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
with bpy.data.libraries.load(str(P/'native/WTSC_Unpainted_Motion_Rebuild_v012.blend'),link=False) as (av,loaded):loaded.collections=['WTSC_UNPAINTED_MOTION_REBUILD_v012']
s.collection.children.link(loaded.collections[0]);assert not any(o.type in ['CAMERA','LIGHT'] for o in loaded.collections[0].all_objects);rigs={o['character']:o for o in loaded.collections[0].all_objects if o.type=='ARMATURE'};err=0
for f in [1,24,40,44,66,94,144]:
 s.frame_set(f);bpy.context.view_layer.update()
 for w,rig in rigs.items():
  row=M.sample(w,f)
  for name,(A,B) in row['segments'].items():pb=rig.pose.bones[name];err=max(err,(rig.matrix_world@pb.head-A).length,(rig.matrix_world@pb.tail-B).length)
assert err<1e-5,err
s.frame_start=1;s.frame_end=144;s.render.fps=24;s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_v012_Fresh_Append_Test.blend'),compress=True);report={'fresh_empty_scene_append':True,'objects':len(loaded.collections[0].all_objects),'native_armatures':len(rigs),'camera_light_count':0,'sample_joint_world_error_m':err,'external_images':len(bpy.data.images)};(P/'evidence/append_validation.json').write_text(json.dumps(report,indent=2));print('V012_FRESH_APPEND_PASSED',json.dumps(report),flush=True)
