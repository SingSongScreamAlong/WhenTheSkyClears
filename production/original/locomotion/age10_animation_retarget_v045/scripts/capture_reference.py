import bpy,json,hashlib,math
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1]
for n in ['native','evidence','previews']:(P/n).mkdir(exist_ok=True)
source=ROOT/'locomotion/age10_proportion_candidate_v044/native/WTSC_Age10_Static_Proportion_Candidate_v044.blend';before=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);S=next(s for s in bpy.data.scenes if s.name.startswith('REFERENCE | liked v041'));bpy.context.window.scene=S;R=S.objects['LOCO_BOY | RIG'];rows=[]
for i in range(249):
 f=1+i/8;S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();er=R.evaluated_get(dg);origin=er.matrix_world.translation.copy();row={'frame':f,'bones':{},'boots':{}}
 for n in ['pelvis','chest','head','upper_arm_near','forearm_near','hand_near','upper_arm_far','forearm_far','hand_far']:
  b=er.pose.bones[n];row['bones'][n]={'head':list(er.matrix_world@b.head-origin),'tail':list(er.matrix_world@b.tail-origin)}
 for side in ['near','far']:
  o=S.objects[f'V033 | {side} | canonical painted shoe'];e=o.evaluated_get(dg);V=[e.matrix_world@v.co-origin for v in e.data.vertices];z=min(v.z for v in V);row['boots'][side]={'origin':list(e.matrix_world.translation-origin),'angle_xz':math.atan2(e.matrix_world[2][0],e.matrix_world[0][0]),'min_z':z,'support_x_min':min(v.x for v in V if v.z<=z+.001),'support_x_max':max(v.x for v in V if v.z<=z+.001)}
 rows.append(row)
after=hashlib.sha256(source.read_bytes()).hexdigest();assert before==after;out={'source':str(source),'source_sha256':before,'source_preserved':True,'reference':'Liked v041/v028 preferred boy timing and gesture; these are evaluated numeric references, not already-retargeted animation.','fps':30,'period_frames':31,'old_stride_m':.9524437384576381,'samples':rows};(P/'evidence/PREFERRED_EIGHTH_FRAME_REFERENCE.json').write_text(json.dumps(out,indent=2));print(json.dumps({'hip_z_range':[min(r['bones']['pelvis']['head'][2] for r in rows),max(r['bones']['pelvis']['head'][2] for r in rows)],'hip_x_range':[min(r['bones']['pelvis']['head'][0] for r in rows),max(r['bones']['pelvis']['head'][0] for r in rows)],'boots':{s:{'angle_degrees':[math.degrees(min(r['boots'][s]['angle_xz'] for r in rows)),math.degrees(max(r['boots'][s]['angle_xz'] for r in rows))],'min_z_range':[min(r['boots'][s]['min_z'] for r in rows),max(r['boots'][s]['min_z'] for r in rows)]} for s in ['near','far']}}),flush=True)
