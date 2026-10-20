import bpy,sys,json,math
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];sys.path.insert(0,str(P/'scripts'));import rig_pose_api as api
def points(ob):
 e=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());return [e.matrix_world@v.co for v in e.data.vertices]
def load(path):
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);r,c=api.initialize_from_scene();return bpy.context.scene,r['BOY'],c
S,r,c=load(ROOT/'locomotion/reference_walk_exercise_v018/native/WTSC_Boy_Travelling_Walk_v018.blend');times=[1+i*.25 for i in range(193)];base={};fixed=['pelvis','chest','head','thigh_near','shin_near','foot_near','thigh_far','shin_far','foot_far'];boots=[o.name for o in r.children if o.get('v007_role')=='support_boot']
for f in times:
 S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();base[f]={'bones':{n:r.pose.bones[n].matrix.copy() for n in fixed},'boots':{n:points(bpy.data.objects[n]) for n in boots},'travel':r.parent.matrix_world.copy()}
S,r,c=load(P/'native/WTSC_Boy_Arm_Readability_v019.blend');max_pose=max_boot=max_travel=0.;reach=[];rows=[]
for f in times:
 S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();max_pose=max(max_pose,max(abs(r.pose.bones[n].matrix[i][j]-base[f]['bones'][n][i][j]) for n in fixed for i in range(4) for j in range(4)));max_boot=max(max_boot,max((a-b).length for n in boots for a,b in zip(base[f]['boots'][n],points(bpy.data.objects[n]))));max_travel=max(max_travel,max(abs(r.parent.matrix_world[i][j]-base[f]['travel'][i][j]) for i in range(4) for j in range(4)));rr=api.reach_report();reach.extend(rr);rows.append({'frame':f,'reach':rr})
out={'sample_count':len(times),'purpose':'Bounded regression only; do not infer visual quality from this result.','all_native_chains_reachable':all(v['reachable'] for v in reach),'max_IK_endpoint_error_m':max(v['endpoint_error_m'] for v in reach),'frozen_body_lower_bone_matrix_max_delta':max_pose,'frozen_boot_vertices_max_delta_m':max_boot,'frozen_travel_matrix_max_delta':max_travel,'non_wrist_action_channels_identical':json.loads((P/'evidence/change_contract.json').read_text())['non_wrist_action_identity'],'status':'PASS' if max_pose<1e-7 and max_boot<1e-7 and max_travel<1e-7 and all(v['reachable'] for v in reach) else 'FAIL','artistic_status':'REJECTED OVERALL WALK; bounded arm diagnostic only'}
(P/'evidence/frozen_gait_check.json').write_text(json.dumps(out,indent=2));(P/'evidence/wrist_reach_check.json').write_text(json.dumps(rows,indent=2));print('V019_REGRESSION',json.dumps(out))
if out['status']!='PASS':raise RuntimeError('Frozen-gait regression failed')
inspection=bpy.data.objects['V018 | INSPECTION fixed ground camera'];matched=bpy.data.objects['V018 | v046 MATCHED SIZE | follows travel']
for folder,cam in [('AFTER',inspection),('MATCHED_AFTER',matched)]:
 S.camera=cam
 for f in range(1,49):
  S.frame_set(f);S.render.filepath=str(P/f'previews/{folder}/{f:04d}.png');bpy.ops.render.render(write_still=True)
print('V019_SMALL_PREVIEWS_RENDERED')
