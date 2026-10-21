import bpy,json,runpy,math
from pathlib import Path
from mathutils import Vector
import numpy as np
P=Path(__file__).resolve().parents[1];R=P.parents[1];cfg=runpy.run_path(str(P/'scripts/configure_v007.py'))['configure_v007'];src=json.loads((R/'locomotion/performance_v003/art/native_overlap_sources.json').read_text())
base=R/'locomotion/battlefield_proof_v005/native/WTSC_Battlefield_Weary_Stumble_5s_v005.blend';bpy.ops.wm.open_mainfile(filepath=str(base),load_ui=False);s=bpy.context.scene;root=next(o for o in s.objects if o.get('loco_pack')=='WTSC_BATTLEFIELD_WEARY_v005');runpy.run_path(str(R/'locomotion/battlefield_proof_v005/scripts/configure_battlefield.py'))['configure_battlefield'](start=1801,root_motion=True,root=root)
rigs={o['character']:o for o in root.children_recursive if o.type=='ARMATURE'};reference={};restboots={}
for who,r in rigs.items():
 for side in ['near','far']:
  ob=next(o for o in r.children if 'rigid original boot '+side in o.name);restboots[who,side]=[v.co.copy() for v in ob.data.vertices]
for f in range(1,121):
 s.frame_set(1800+f);bpy.context.view_layer.update();row={}
 for who,r in rigs.items():
  for side in ['near','far']:
   bn='foot_'+side;M=r.matrix_world@r.pose.bones[bn].matrix;D=M@r.data.bones[bn].matrix_local.inverted();points=[D@p for p in restboots[who,side]];z=min(p.z for p in points);bottom=[p for p in points if p.z<=z+.004]
   row[who,side]={'matrix':M.copy(),'points':points,'extrema':[sum(p.x for p in bottom)/len(bottom),sum(p.y for p in bottom)/len(bottom),z]}
 reference[f]=row
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
with bpy.data.libraries.load(str(P/'native/WTSC_Supported_Recovery_v007.blend'),link=False) as (available,loaded):loaded.collections=['WTSC_BATTLEFIELD_DRAWN_PAIR_v007']
s.collection.children.link(loaded.collections[0]);root=next(o for o in s.objects if o.get('motion_revision')=='v007_drawn_pose_corrections');cfg(start=1801,root_motion=True,root=root);rigs={o['character']:o for o in root.children_recursive if o.type=='ARMATURE'};travel=next(o for o in root.children if 'TRAVEL' in o.name);distance=next(o for o in root.children if o.get('loco_role')=='DISTANCE_CURVE');s.render.fps=24;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;s.render.engine='BLENDER_EEVEE';boots={}
for who,r in rigs.items():
 for side in ['near','far']:boots[who,side]=next(o for o in r.children if o.get('v007_role')=='support_boot' and side in o.name)
assert len(bpy.data.actions)==33
errors={'foot_world_matrix':0,'protected_sole_curve_points':0,'sole_extrema':0,'sole_min_Z':0,'sole_slice_centroid_X':0,'sole_slice_centroid_Y':0,'all_shoe_vertices_outside_correction':0,'root_distance':0};hands=[];poses={};exposures=[];sole_rows=[]
sole_ids={}
for (who,side),points in restboots.items():sole_ids[who,side]=[min(range(len(points)),key=lambda i:(points[i].x-x)**2+(points[i].z-z)**2) for x,z in src['feet'][who+'_'+side]['lower_hull']]
head_source=next(o for o in rigs['GIRL'].children if 'original head and attached braid' in o.name);head_turn=next(o for o in rigs['GIRL'].children if o.get('v007_role')=='look_back_original_paint');head_back=next(o for o in rigs['GIRL'].children if 'passing back-view drawing' in o.name)
def evaluated_points(ob):
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();pts=[ev.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear();return pts
for f in range(1,121):
 s.frame_set(1800+f);bpy.context.view_layer.update();errors['root_distance']=max(errors['root_distance'],abs(travel.location.x-distance.location.x))
 for who,r in rigs.items():
  for side in ['near','far']:
   a=reference[f][who,side];M=r.matrix_world@r.pose.bones['foot_'+side].matrix;errors['foot_world_matrix']=max(errors['foot_world_matrix'],max(abs(M[i][j]-a['matrix'][i][j]) for i in range(4) for j in range(4)));pts=evaluated_points(boots[who,side]);z=min(p.z for p in pts);bottom=[p for p in pts if p.z<=z+.004];extrema=[sum(p.x for p in bottom)/len(bottom),sum(p.y for p in bottom)/len(bottom),z];diff=[abs(x-y) for x,y in zip(extrema,a['extrema'])];errors['sole_extrema']=max(errors['sole_extrema'],max(diff));errors['sole_min_Z']=max(errors['sole_min_Z'],diff[2]);errors['sole_slice_centroid_X']=max(errors['sole_slice_centroid_X'],diff[0]);errors['sole_slice_centroid_Y']=max(errors['sole_slice_centroid_Y'],diff[1]);sole_rows.append({'frame':f,'who':who,'side':side,'slice_centroid_delta_XYZ_m':diff})
   if f<=28 or f>=72:errors['all_shoe_vertices_outside_correction']=max(errors['all_shoe_vertices_outside_correction'],max((p-q).length for p,q in zip(pts,a['points'])))
   errors['protected_sole_curve_points']=max(errors['protected_sole_curve_points'],max((pts[i]-a['points'][i]).length for i in sole_ids[who,side]))
 if f in [1,43,44,45,46,89,101,120]:
  active=[o.name for o in [head_source,head_back,head_turn] if not o.hide_render];assert len(active)==1,(f,active);exposures.append({'frame':f,'visible':active[0]});poses[f]=distance.location.x
 if f>=101:
  boy=next(o for o in rigs['BOY'].children if o.get('v007_role')=='drawn_hand' and 'far' in o.name);girl=next(o for o in rigs['GIRL'].children if o.get('v007_role')=='drawn_hand' and 'near' in o.name);a=np.array([[p.x,p.z] for p in evaluated_points(boy)]);b=np.array([[p.x,p.z] for p in evaluated_points(girl)]);nearest=float(np.sqrt(((a[:,None,:]-b[None,:,:])**2).sum(axis=2).min()));gap=float(b[:,0].min()-a[:,0].max());hands.append({'frame':f,'nearest_drawn_hand_vertex_distance_XZ_m':nearest,'finger_extent_gap_X_m':gap})
(P/'evidence/sole_diagnostic.json').write_text(json.dumps({'errors':errors,'worst_slice_samples':sorted(sole_rows,key=lambda r:max(r['slice_centroid_delta_XYZ_m']),reverse=True)[:12]},indent=2))
assert max(errors[k] for k in ['foot_world_matrix','protected_sole_curve_points','sole_min_Z','all_shoe_vertices_outside_correction','root_distance'])<.00003,errors
assert errors['sole_slice_centroid_X']<.004 and errors['sole_slice_centroid_Y']<.00003,errors
assert max(abs(r['finger_extent_gap_X_m']) for r in hands)<.01,hands
cfg(start=201,duration_scale=2,root_motion=True,root=root);retime=[]
for f,d in poses.items():
 s.frame_set(201+(f-1)*2);bpy.context.view_layer.update();retime.append(abs(distance.location.x-d));active=[o.name for o in [head_source,head_back,head_turn] if not o.hide_render];expected=next(row['visible'] for row in exposures if row['frame']==f);assert active==[expected],(f,active,expected)
assert max(retime)<1e-6
cfg(start=1801,root_motion=False,root=root);s.frame_set(1901);bpy.context.view_layer.update();assert abs(travel.location.x)<1e-6
report={'fresh_factory_append':True,'blender':bpy.app.version_string,'engine':'BLENDER_EEVEE','collection':loaded.collections[0].name,'actions':len(bpy.data.actions),'native_shape_key_datablocks':len(bpy.data.shape_keys),'native_bezier_guides':sum(o.type=='CURVE' for o in loaded.collections[0].all_objects),'packed_images':[i.name for i in bpy.data.images if i.packed_file],'all120frame_errors_vs_v005_original':errors,'head_exposures':exposures,'retime2_distance_error_m':max(retime),'retime2_head_exposure_pass':True,'in_place_control_pass':True,'paired_support_hand_geometry':hands,'hand_contact_limit':'Projected2D drawn contact, not a physics or grip constraint. Pair spacing must remain0.8m. Native arm IK poses are sampled without bone stretch.','units':'metres','fps':24,'plane':'XZ'}
s.frame_start=1801;s.frame_end=1920;bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_v007_Fresh_Append_Test.blend'),compress=True);(P/'evidence/native_validation.json').write_text(json.dumps(report,indent=2));print('V007_APPEND_CONTACT_RETIME_PASS',json.dumps({k:v for k,v in report.items() if k!='paired_support_hand_geometry'}),flush=True)
