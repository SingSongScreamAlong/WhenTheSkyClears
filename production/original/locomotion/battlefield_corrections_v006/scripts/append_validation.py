import bpy,json,runpy,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];R=P.parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
with bpy.data.libraries.load(str(P/'native/WTSC_Battlefield_Drawn_Corrections_v006.blend'),link=False) as (available,loaded):loaded.collections=['WTSC_BATTLEFIELD_DRAWN_PAIR_v006']
s.collection.children.link(loaded.collections[0]);root=next(o for o in s.objects if o.get('motion_revision')=='v006_drawn_pose_corrections');cfg=runpy.run_path(str(P/'scripts/configure_v006.py'))['configure_v006']
cfg(start=1801,root_motion=True,root=root);s.render.fps=24;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
assert len(bpy.data.actions)==29,len(bpy.data.actions)
rigs=[o for o in root.children_recursive if o.type=='ARMATURE'];assert len(rigs)==2
distance=next(o for o in root.children if o.get('loco_role')=='DISTANCE_CURVE');travel=next(o for o in root.children if 'TRAVEL' in o.name)
checks=[];reference={}
for f in [1,4,25,37,47,58,81,101,120]:
 s.frame_set(1800+f);bpy.context.view_layer.update();d=distance.location.x;assert abs(travel.location.x-d)<1e-6
 hands=[o for o in root.children_recursive if o.get('v006_role')=='drawn_hand'];keyerror=max(abs(sum(k.value for k in ob.data.shape_keys.key_blocks[1:])-1) for ob in hands);assert keyerror<1e-5
 reference[f]=d;checks.append({'global_frame':1800+f,'distance_m':d,'one_hot_drawing_weight_error':keyerror})
cfg(start=201,duration_scale=2,root_motion=True,root=root);retime=[]
for f,d in reference.items():
 t=201+(f-1)*2;s.frame_set(t);bpy.context.view_layer.update();retime.append(abs(distance.location.x-d))
assert max(retime)<1e-6
cfg(start=1801,root_motion=False,root=root);s.frame_set(1901);bpy.context.view_layer.update();assert abs(travel.location.x)<1e-6
report={'fresh_factory_append':True,'blender':bpy.app.version_string,'collection':loaded.collections[0].name,'actions':len(bpy.data.actions),'native_shape_key_datablocks':len(bpy.data.shape_keys),'native_bezier_guides':sum(o.type=='CURVE' for o in loaded.collections[0].all_objects),'packed_images':[i.name for i in bpy.data.images if i.packed_file],'checks':checks,'time_scale_2_distance_max_error_m':max(retime),'in_place_control_pass':True,'units':'metres','fps':24,'plane':'XZ','render_preview_settings':'CPU Cycles,2threads,2samples,960x540'}
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_v006_Fresh_Append_Test.blend'),compress=True)
(P/'evidence/append_validation.json').write_text(json.dumps(report,indent=2));print('V006_APPEND_AND_RETIME_PASS',json.dumps(report),flush=True)
