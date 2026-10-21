"""Cold-open tests and actual pose renders. No native save."""
import bpy,math,json,hashlib,ast
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];FILE=P/'native/WTSC_Age10_Walk_Retarget_Proof_v045.blend';before=hashlib.sha256(FILE.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(FILE),load_ui=False,use_scripts=False);S=bpy.data.scenes['V045 | AGE TEN | RETARGET AFTER STATIC SCALE'];bpy.context.window.scene=S
A=json.loads((P/'evidence/PREFERRED_EIGHTH_FRAME_REFERENCE.json').read_text());ROWS=A['samples'];build=json.loads((P/'evidence/RETARGET_BUILD.json').read_text());TARGET=json.loads((ROOT/'locomotion/age10_proportion_candidate_v044/evidence/STATIC_SCALE_BUILD.json').read_text())['candidate_measurements'];STRIDE=build['new_stride_m'];STEP_RATIO=build['stride_ratio'];PERIOD=31.;RIGS={w:bpy.data.objects['V044 '+w+' | estimated joint centres'] for w in ['BOY','GIRL']};ART=bpy.data.collections['V044 | age10 editable profile anatomy'];FOOT={};boots={}
for who,r in RIGS.items():
 boots[who]={s:next(o for o in ART.objects if o.parent==r and o.get('proportion_role')=='boot' and o.name.endswith(s)) for s in ['near','far']};b=boots[who]['near'];off=[p.co-Vector((0,0,TARGET[who]['estimated_ankle_joint_z_m'])) for p in b.data.vertices];z=min(p.z for p in off);FOOT[who]={'offsets':off,'heel':min(p.x for p in off if p.z<=z+.000001)}
tree=ast.parse((P/'scripts/build_retarget.py').read_text());tree.body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['D','ref','v','unit2','rot','smooth','stance','foot','ik']];exec(compile(tree,'retarget_functions_only','exec'),globals())
travel=bpy.data.objects['V045 | shared travel | new stride90percent'];records=[];maxima={'root_distance_error_m':0,'camera_follow_error_m':0,'joint_gap_m':0,'segment_length_error_m':0,'stance_floor_error_m':0,'stance_support_x_error_m':0,'sole_penetration_m':0,'knee_backward_m':0};first={};loop={}
for i in range(745):
 f=1+i/8;S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();maxima['root_distance_error_m']=max(maxima['root_distance_error_m'],abs(travel.location.x-D(f)));maxima['camera_follow_error_m']=max(maxima['camera_follow_error_m'],abs(S.camera.location.x-D(f)))
 for who,r in RIGS.items():
  e=r.evaluated_get(dg);phase=0 if who=='BOY' else 3.5;rr={'frame':f,'character':who,'hip_world':list(e.matrix_world@e.pose.bones['pelvis'].head),'feet':{}}
  for n,b in e.pose.bones.items():maxima['segment_length_error_m']=max(maxima['segment_length_error_m'],abs((b.tail-b.head).length-r.data.bones[n].length))
  for side in ['near','far']:
   th=e.pose.bones['thigh_'+side];sh=e.pose.bones['shin_'+side];fb=e.pose.bones['foot_'+side]
   for a,b in [(th.tail,sh.head),(sh.tail,fb.head),(e.pose.bones['upper_arm_'+side].tail,e.pose.bones['forearm_'+side].head),(e.pose.bones['forearm_'+side].tail,e.pose.bones['hand_'+side].head)]:maxima['joint_gap_m']=max(maxima['joint_gap_m'],(a-b).length)
   U=(sh.tail-th.head).normalized();perp=Vector((-U.z,0,U.x));bend=(th.tail-th.head).dot(perp);maxima['knee_backward_m']=max(maxima['knee_backward_m'],-bend)
   ob=boots[who][side];ev=ob.evaluated_get(dg);V=[ev.matrix_world@v.co for v in ev.data.vertices];floor=min(v.z for v in V);maxima['sole_penetration_m']=max(maxima['sole_penetration_m'],-floor);ank,theta,meta=foot(f+phase,who,side);fr={'stance':meta['stance'],'minimum_sole_z_m':floor,'ankle_world':list(e.matrix_world@fb.head)}
   if meta['stance']:
    inds=meta['support_indices'];support=sum((V[k] for k in inds),Vector())/len(inds);expected=meta['expected_support_x_plus_D']+r.location.x+D(f)-D(f+phase);err=abs(support.x-expected);maxima['stance_floor_error_m']=max(maxima['stance_floor_error_m'],abs(floor));maxima['stance_support_x_error_m']=max(maxima['stance_support_x_error_m'],err);fr.update({'support_x_m':support.x,'expected_support_x_m':expected,'support_x_error_m':err,'support_indices':inds})
   rr['feet'][side]=fr
  if i==0:first[who]={n:[list(row) for row in b.matrix] for n,b in e.pose.bones.items()}
  if i==248:loop[who]=max(abs(b.matrix[j][k]-first[who][n][j][k]) for n,b in e.pose.bones.items() for j in range(4) for k in range(4))
  records.append(rr)
limits={'root_distance_error_m':.000002,'camera_follow_error_m':.000002,'joint_gap_m':.0005,'segment_length_error_m':.000002,'stance_floor_error_m':.0005,'stance_support_x_error_m':.001,'sole_penetration_m':.0005,'knee_backward_m':.000001};passed={n:maxima[n]<=val for n,val in limits.items()};report={'native_sha256':before,'samples':745,'frame_range':[1,94],'sample_step_frames':.125,'fps':30,'new_stride_m':STRIDE,'maxima':maxima,'limits':limits,'checks_pass':passed,'loop_matrix_error_local':loop,'records':records,'technical_only':'Passing geometric tests does not establish convincing movement, visible cloth/paint continuity or acting.'};(P/'evidence/COLD_CONTACT_VALIDATION.json').write_text(json.dumps(report,indent=2));print('COLD_CONTACT_METRICS',json.dumps({'maxima':maxima,'pass':passed,'loop':loop}),flush=True)
S.render.resolution_x=1280;S.render.resolution_y=720;S.render.resolution_percentage=100;S.render.threads_mode='FIXED';S.render.threads=2;S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB';S.render.dither_intensity=0
for f in [1,9,17,25]:S.frame_set(f);S.render.filepath=str(P/'previews'/f'PROOF_{f:04d}.png');bpy.ops.render.render(write_still=True,scene=S.name)
after=hashlib.sha256(FILE.read_bytes()).hexdigest();assert before==after;print('CONTACT_PROOF_COMPLETE_NATIVE_UNCHANGED',flush=True)
