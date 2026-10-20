import bpy,sys,json,hashlib,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];R=P.parents[1];sys.path.insert(0,str(P/'scripts'));import motion_design as M
bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Unpainted_Motion_Rebuild_v012.blend'),load_ui=False);s=bpy.context.scene;rigs={o['character']:o for o in s.objects if o.type=='ARMATURE'};boots={(w,side):next(o for o in rig.children if o.get('foot_side')==side) for w,rig in rigs.items() for side in ['near','far']}
joint_error=0;floor_min=1.;segment_error=0;surface_center_error=0;rows=[];flat_groups={};com_support={}
for f in range(1,145):
 s.frame_set(f);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();row={'frame':f,'characters':{}}
 for w,rig in rigs.items():
  target=M.sample(w,f);row['characters'][w]={'hip_z':target['hip_z'],'root_x':target['root_x'],'com_proxy':list(target['com_proxy']),'feet':{}}
  for name,(A,B) in target['segments'].items():
   pb=rig.pose.bones[name];joint_error=max(joint_error,(rig.matrix_world@pb.head-A).length,(rig.matrix_world@pb.tail-B).length);segment_error=max(segment_error,abs((pb.tail-pb.head).length-rig.data.bones[name].length))
  for side in ['near','far']:
   ob=boots[w,side];ev=ob.evaluated_get(dg);me=ev.to_mesh();pts=[ev.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear();floor_min=min(floor_min,min(p.z for p in pts));ft=target['feet'][side];data={'state':ft['state'],'min_z':min(p.z for p in pts),'min_x':min(p.x for p in pts),'max_x':max(p.x for p in pts)};row['characters'][w]['feet'][side]=data
   if ft['state']=='flat' and abs(ft['angle'])<1e-7:flat_groups.setdefault((w,side,round(ft['x'],6)),[]).append((f,pts))
  for ob in rig.children:
   if ob.type!='MESH' or not ob.vertex_groups:continue
   bone=ob.vertex_groups[0].name
   if bone=='pelvis' or ob.get('foot_side') or 'cue' in ob.name or ob.get('attachment_role'):continue
   ev=ob.evaluated_get(dg);me=ev.to_mesh();center=sum((ev.matrix_world@v.co for v in me.vertices),Vector())/len(me.vertices);ev.to_mesh_clear();pb=rig.pose.bones[bone];expected=rig.matrix_world@((pb.head+pb.tail)*.5);surface_center_error=max(surface_center_error,(center-expected).length)
  if f in [24,30,40,44,56,60,66,78]:
   supports=[]
   for side,ft in target['feet'].items():
    if ft['state']=='flat':supports.append([ft['heel'].x,ft['toe'].x])
    elif ft['state'].startswith('toe'):supports.append([ft['toe'].x,ft['toe'].x])
    elif ft['state']=='heel':supports.append([ft['heel'].x,ft['heel'].x])
   com_support[w+'_'+str(f)]={'com_proxy_x':target['com_proxy'].x,'support_x_ranges':supports,'interpretation':'Geometric authored mass proxy only; moving CoM may be outside static support during the intentional fall. No force/dynamics pass.'}
 rows.append(row)
flat_drift=0;flat_pairs=0
for group in flat_groups.values():
 prev=None
 for f,pts in group:
  if prev is not None and f==prev[0]+1:flat_drift=max(flat_drift,max((a-b).length for a,b in zip(prev[1],pts)));flat_pairs+=1
  prev=(f,pts)
assert joint_error<1e-5 and surface_center_error<1e-5,(joint_error,surface_center_error);assert segment_error<1e-5,segment_error;assert floor_min>-.002,floor_min;assert flat_drift<1e-5,flat_drift
protected=json.loads((P/'evidence/protected_inputs.json').read_text());preserved={n:hashlib.sha256((R/n).read_bytes()).hexdigest()==sha for n,sha in protected.items()};assert all(preserved.values())
report={'cold_reopened':True,'version':bpy.app.version_string,'frames':144,'evaluated_joint_target_error_m':joint_error,'bound_proxy_mesh_center_error_m':surface_center_error,'native_segment_length_error_m':segment_error,'floor_min_z_m':floor_min,'adjacent_flat_stance_vertex_drift_m':flat_drift,'flat_adjacent_pairs':flat_pairs,'flat_definition':'State flat AND foot rotation angle below1e-7rad. Toe/heel roll is deliberately excluded; it changes vertices while contact pivot stays fixed.','support_and_mass_samples':com_support,'protected_sources_preserved':preserved,'scope':'Technical integrity and authored support data only. Does not establish convincing motion or artistic acceptance.'}
(P/'evidence/native_validation.json').write_text(json.dumps(report,indent=2));(P/'evidence/contact_samples.json').write_text(json.dumps(rows,indent=2));print('V012_NATIVE_VALIDATED',json.dumps({k:v for k,v in report.items() if k!='support_and_mass_samples'}),flush=True)
