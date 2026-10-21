import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'scripts'));import story_poses as M
native=P/'native/WTSC_Whole_Pose_Blocking_v013.blend';bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False);s=bpy.context.scene;col=bpy.data.collections['WTSC_WHOLE_POSE_BLOCKING_v013'];rigs={o['character']:o for o in col.objects if o.type=='ARMATURE'}
joint=length=meshcenter=flatdrift=0.;floor=10.;previous={};flatpairs=0;contact=[];curves={}
for who,rig in rigs.items():
 counts=set();interpolations=set()
 for layer in rig.animation_data.action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for fc in bag.fcurves:counts.add(len(fc.keyframe_points));interpolations.update(k.interpolation for k in fc.keyframe_points)
 assert counts=={len(M.POSES[who])} and interpolations=={'CONSTANT'},(who,counts,interpolations)
 curves[who]={'keys_per_channel':list(counts),'interpolation':list(interpolations),'no_recurring_gait_channels':True}
for f in range(1,73):
 s.frame_set(f);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
 for who,rig in rigs.items():
  target=M.sample(who,f)
  for name,(A,B) in target['segments'].items():
   pb=rig.pose.bones[name];joint=max(joint,(rig.matrix_world@pb.head-A).length,(rig.matrix_world@pb.tail-B).length);length=max(length,abs((pb.tail-pb.head).length-rig.data.bones[name].length))
  for side in ['near','far']:
   ob=next(o for o in rig.children if o.get('foot_side')==side);ev=ob.evaluated_get(dg);me=ev.to_mesh();pts=[ev.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear();floor=min(floor,min(p.z for p in pts));ft=target['feet'][side];k=(who,side)
   if ft['state']=='flat':
    old=previous.get(k)
    if old and old[0]==f-1 and old[1]==ft['x']:flatdrift=max(flatdrift,max((a-b).length for a,b in zip(pts,old[2])));flatpairs+=1
    previous[k]=(f,ft['x'],pts)
   else:previous.pop(k,None)
  for ob in rig.children:
   if ob.type!='MESH' or not ob.vertex_groups or ob.get('foot_side') or ob.get('attachment_role') or 'cue' in ob.name:continue
   bone=ob.vertex_groups[0].name
   if bone=='pelvis':continue
   ev=ob.evaluated_get(dg);me=ev.to_mesh();center=sum((ev.matrix_world@v.co for v in me.vertices),Vector())/len(me.vertices);ev.to_mesh_clear();pb=rig.pose.bones[bone];expected=rig.matrix_world@((pb.head+pb.tail)*.5);meshcenter=max(meshcenter,(center-expected).length)
  if f in M.KEYS:contact.append({'frame':f,'character':who,'exposed_key':target['key_frame'],'hip':list(target['joints']['pelvis']),'feet':{side:{k:list(v) if isinstance(v,Vector) else v for k,v in ft.items() if k!='matrix'} for side,ft in target['feet'].items()}})
assert joint<1e-5 and length<1e-5 and meshcenter<1e-5 and flatdrift<1e-5 and floor>-.002,(joint,length,meshcenter,flatdrift,floor)
protected=json.loads((P/'evidence/protected_inputs.json').read_text());preserved={p:hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in protected.items()};assert all(preserved.values())
girl_settled=all(M.sample('GIRL',f)['feet'][side]['state']=='flat' for f in range(27,73) for side in ['near','far']);assert girl_settled
report={'host':bpy.app.version_string,'cold_reopened':True,'all72frames_checked':True,'joint_target_error_m':joint,'segment_length_error_m':length,'bound_mesh_center_error_m':meshcenter,'flat_sole_vertex_drift_m':flatdrift,'flat_adjacent_pairs':flatpairs,'floor_min_z_m':floor,'girl_both_feet_flat27_through72':girl_settled,'native_curve_structure':curves,'sources_preserved':preserved,'scope':'Native binding/contact/stepped-exposure integrity only. Held blocking poses deliberately jump between keys; no continuous dynamics, smoothness or artistic acceptance test.'}
(P/'evidence/native_validation.json').write_text(json.dumps(report,indent=2));(P/'evidence/contact_samples.json').write_text(json.dumps(contact,indent=2))
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(native),link=False) as (_,loaded):loaded.collections=['WTSC_WHOLE_POSE_BLOCKING_v013']
bpy.context.scene.collection.children.link(loaded.collections[0]);assert len(loaded.collections[0].all_objects)==44 and not any(o.type in ['CAMERA','LIGHT'] for o in loaded.collections[0].all_objects)
rigs={o['character']:o for o in loaded.collections[0].all_objects if o.type=='ARMATURE'};err=0
for f in [1,13,19,22,27,38,43,64,72]:
 bpy.context.scene.frame_set(f);bpy.context.view_layer.update()
 for who,rig in rigs.items():
  for name,(A,B) in M.sample(who,f)['segments'].items():pb=rig.pose.bones[name];err=max(err,(rig.matrix_world@pb.head-A).length,(rig.matrix_world@pb.tail-B).length)
assert err<1e-5,err
(P/'evidence/append_validation.json').write_text(json.dumps({'fresh_empty_scene_append':True,'objects':44,'rigs':2,'camera_light_count':0,'sample_world_joint_error_m':err,'external_images':len(bpy.data.images)},indent=2));print('V013_TECHNICAL_CHECKS_PASSED',json.dumps(report),flush=True)
