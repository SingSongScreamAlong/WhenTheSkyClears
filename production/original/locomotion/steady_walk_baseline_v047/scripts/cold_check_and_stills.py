import bpy,math,json,hashlib,ast,csv
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];FILE=P/'native/WTSC_Steady_Ordinary_Walk_v047.blend';before=hashlib.sha256(FILE.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(FILE),load_ui=False,use_scripts=False);S=bpy.data.scenes['V047 | STEADY ORDINARY WALK | no stumble baseline'];bpy.context.window.scene=S
build=json.loads((P/'evidence/STEADY_WALK_BUILD.json').read_text());TARGET=json.loads((ROOT/'locomotion/age10_proportion_candidate_v044/evidence/STATIC_SCALE_BUILD.json').read_text())['candidate_measurements'];RIGS={w:bpy.data.objects['V044 '+w+' | estimated joint centres'] for w in ['BOY','GIRL']};ART=bpy.data.collections['V044 | age10 editable profile anatomy'];C=bpy.data.collections['V046 | restored original painted wardrobe'];PERIOD=32.;STRIDE=.78;STANCE=18.8;PHASE={'BOY':0.,'GIRL':2.};FOOT={};boots={}
for who,r in RIGS.items():
 boots[who]={s:next(o for o in ART.objects if o.parent==r and o.get('proportion_role')=='boot' and o.name.endswith(s)) for s in ['near','far']};off=[Vector((p.co.x,0,p.co.z-TARGET[who]['estimated_ankle_joint_z_m'])) for p in boots[who]['near'].data.vertices];z=min(p.z for p in off);FOOT[who]={'offsets':off,'heel':min(p.x for p in off if p.z<=z+.000001)}
tree=ast.parse((P/'scripts/build_steady_walk.py').read_text());tree.body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['D','ease5','ease3','rot','angle','support_geometry','stance','foot']];exec(compile(tree,'steady_expected_contact_functions','exec'),globals())
root=bpy.data.objects['V047 | shared travel | steady .73125mps'];maxima={'root_distance_error_m':0.,'camera_follow_error_m':0.,'joint_gap_m':0.,'segment_length_error_m':0.,'sole_penetration_m':0.,'stance_floor_error_m':0.,'stance_support_x_error_m':0.,'knee_backward_m':0.};records={w:[] for w in RIGS};first={};loop={}
for i in range(1025):
 f=1+i/8;S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();maxima['root_distance_error_m']=max(maxima['root_distance_error_m'],abs(root.location.x-D(f)));maxima['camera_follow_error_m']=max(maxima['camera_follow_error_m'],abs(S.camera.location.x-D(f)))
 for who,r in RIGS.items():
  e=r.evaluated_get(dg);hip=e.pose.bones['pelvis'].head;rr={'frame':f,'hip_x_local':hip.x,'hip_z':hip.z,'feet':{}}
  for n,b in e.pose.bones.items():maxima['segment_length_error_m']=max(maxima['segment_length_error_m'],abs((b.tail-b.head).length-r.data.bones[n].length))
  for side in ['near','far']:
   th=e.pose.bones['thigh_'+side];sh=e.pose.bones['shin_'+side];fb=e.pose.bones['foot_'+side]
   for a,b in [(th.tail,sh.head),(sh.tail,fb.head),(e.pose.bones['upper_arm_'+side].tail,e.pose.bones['forearm_'+side].head),(e.pose.bones['forearm_'+side].tail,e.pose.bones['hand_'+side].head)]:maxima['joint_gap_m']=max(maxima['joint_gap_m'],(a-b).length)
   U=(sh.tail-th.head).normalized();maxima['knee_backward_m']=max(maxima['knee_backward_m'],-(th.tail-th.head).dot(Vector((-U.z,0,U.x))))
   ob=boots[who][side];ev=ob.evaluated_get(dg);V=[ev.matrix_world@p.co for p in ev.data.vertices];bottom=min(p.z for p in V);maxima['sole_penetration_m']=max(maxima['sole_penetration_m'],-bottom);_,_,meta=foot(f+PHASE[who],who,side);q={'stance':meta['stance'],'minimum_sole_z_m':bottom}
   if meta['stance']:
    support=sum((V[k] for k in meta['support_indices']),Vector())/len(meta['support_indices']);expect=meta['expected_support_x_plus_D']+r.location.x+D(f)-D(f+PHASE[who]);err=abs(support.x-expect);maxima['stance_floor_error_m']=max(maxima['stance_floor_error_m'],abs(bottom));maxima['stance_support_x_error_m']=max(maxima['stance_support_x_error_m'],err);q['support_x_error_m']=err
   rr['feet'][side]=q
  if i==0:first[who]={n:b.matrix.copy() for n,b in e.pose.bones.items()}
  if i==256:loop[who]=max(abs(b.matrix[j][k]-first[who][n][j][k]) for n,b in e.pose.bones.items() for j in range(4) for k in range(4))
  records[who].append(rr)
limits={'root_distance_error_m':.000002,'camera_follow_error_m':.000002,'joint_gap_m':.0005,'segment_length_error_m':.000002,'sole_penetration_m':.0005,'stance_floor_error_m':.0005,'stance_support_x_error_m':.001,'knee_backward_m':.000001};checks={k:maxima[k]<=v for k,v in limits.items()};assert all(checks.values()),(maxima,checks);assert max(loop.values())<1e-6,loop
# Independent geometric observation: number of pelvis height extrema in ONE
# cycle. The former extra transfer dip/rebound must not be present.
turns={}
for who,rr in records.items():
 a=rr[:257];found=[]
 for i in range(1,len(a)-1):
  dz0=a[i]['hip_z']-a[i-1]['hip_z'];dz1=a[i+1]['hip_z']-a[i]['hip_z']
  if dz0*dz1<0 and max(abs(dz0),abs(dz1))>1e-6:found.append({'frame':a[i]['frame'],'type':'minimum' if dz0<0 else 'maximum','z':a[i]['hip_z']})
 turns[who]=found
 assert len(found)<=4,found
for f in [257,321]:S.frame_set(f);assert abs(root.location.x-D(f))<2e-6
for who,r in RIGS.items():
 for b in r.data.bones:assert list(b.head_local)==build['anatomy'][who][b.name]['head'] and list(b.tail_local)==build['anatomy'][who][b.name]['tail']
report={'native_sha256':before,'native_unchanged':True,'source_v046_unchanged':hashlib.sha256(Path(build['source']).read_bytes()).hexdigest()==build['source_sha256'],'samples_per_child':1025,'frame_range':[1,129],'step_source_frames':.125,'maxima':maxima,'limits':limits,'checks_pass':checks,'local_cycle_matrix_error':loop,'hip_height_extrema_one_cycle':turns,'anatomy_preserved':True,'records':records,'technical_only':'These checks do not establish convincing weight, intent or artistic quality; actual normal-speed review remains essential.'};assert report['source_v046_unchanged'];(P/'evidence/COLD_CONTACT_VALIDATION.json').write_text(json.dumps(report,indent=2));print('V047_COLD_CONTACTS_PASS',json.dumps({'maxima':maxima,'turns':turns}),flush=True)
with (P/'evidence/TRAVEL_CURVE_v047.csv').open('w',newline='') as h:
 w=csv.writer(h);w.writerow(['source_frame_30fps','seconds_since_F1','travelling_root_m','passing_world_m','camera_follow_m'])
 for i in range(2049):f=1+i/8;w.writerow([f,(f-1)/30,D(f),-D(f),D(f)])
S.render.resolution_x=1280;S.render.resolution_y=720;S.render.resolution_percentage=100;S.render.threads_mode='FIXED';S.render.threads=2;S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB';S.render.dither_intensity=0
for f in [1,5,9,13,17,21,25,29]:S.frame_set(f);S.render.filepath=str(P/'previews'/('STEADY_%04d.png'%f));bpy.ops.render.render(write_still=True,scene=S.name)
assert hashlib.sha256(FILE.read_bytes()).hexdigest()==before;print('V047_COLD_CHECK_AND_EIGHT_POSES_COMPLETE',flush=True)
