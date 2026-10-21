import bpy,json,hashlib,math
from pathlib import Path
O=Path(__file__).resolve().parents[1];B=json.loads((O/'evidence/BUILD.json').read_text());P=Path(B['native']);H=hashlib.sha256(P.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(P),load_ui=False,use_scripts=False);S=bpy.data.scenes[B['world_scene']];bpy.context.window.scene=S
R={w:bpy.data.objects['V044 '+w+' | estimated joint centres'] for w in ['BOY','GIRL']};root=bpy.data.objects['V047 | shared travel | steady .73125mps'];stage=root.parent;z0=stage.matrix_world.translation.z;y0=stage.matrix_world.translation.y;slope=(3-z0)/(16+y0)
metrics={'max_joint_gap_m':0.,'max_leg_length_error_m':0.,'min_sole_clearance_m':1.,'max_hip_target_error_m':0.,'packed_art_unchanged':True};supports={};sample=[]
for row in B['rows']:
 g=row['frame'];S.frame_set(math.floor(g),subframe=g-math.floor(g));bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
 for who,r in R.items():
  e=r.evaluated_get(dg);bones=e.pose.bones;expected=row['children'][who]
  metrics['max_hip_target_error_m']=max(metrics['max_hip_target_error_m'],(bones['pelvis'].head-__import__('mathutils').Vector(expected['hip'])).length)
  for side in ['near','far']:
   for a,b in [('thigh_'+side,'shin_'+side),('shin_'+side,'foot_'+side),('upper_arm_'+side,'forearm_'+side),('forearm_'+side,'hand_'+side)]:metrics['max_joint_gap_m']=max(metrics['max_joint_gap_m'],(bones[a].tail-bones[b].head).length)
   for n in ['thigh_'+side,'shin_'+side]:metrics['max_leg_length_error_m']=max(metrics['max_leg_length_error_m'],abs((bones[n].tail-bones[n].head).length-r.data.bones[n].length))
   boot=next(o for o in S.objects if o.parent==r and o.get('proportion_role')=='boot' and o.name.endswith(side) and not o.hide_render)
   ev=boot.evaluated_get(dg);ps=[ev.matrix_world@v.co for v in ev.data.vertices];clearance=min(p.z-(3-slope*(p.y+16)) for p in ps);metrics['min_sole_clearance_m']=min(metrics['min_sole_clearance_m'],clearance)
   fm=expected['feet'][side]
   if fm['stance'] and 3.5<fm['phase']<13:
    key=who+'_'+side+'_'+str(fm['contact_start']);ids=fm['support_indices'];x=sum(ps[i].x for i in ids)/len(ids);supports.setdefault(key,[]).append(x)
  if g in [937,957,966,979,990,1016,1056]:sample.append({'frame':g,'who':who,'hip':list(bones['pelvis'].head),'head_direction':list(bones['head'].tail-bones['head'].head),'wrist':list(e.matrix_world@bones['hand_near'].head)})
metrics['max_flat_stance_world_sliding_m']=max((max(v)-min(v) for v in supports.values()),default=0)
for im in bpy.data.images:
 if im.name in B['artwork_hashes']:metrics['packed_art_unchanged'] &= bool(im.packed_file and hashlib.sha256(im.packed_file.data).hexdigest()==B['artwork_hashes'][im.name])
metrics['source_unchanged']=hashlib.sha256(Path(B['source']).read_bytes()).hexdigest()==B['source_sha256'];metrics['candidate_unchanged']=hashlib.sha256(P.read_bytes()).hexdigest()==H
checks={'joints':metrics['max_joint_gap_m']<.00002,'leg_lengths':metrics['max_leg_length_error_m']<.00002,'hip_targets':metrics['max_hip_target_error_m']<.00002,'ground':metrics['min_sole_clearance_m']>-.003,'planted_flat_support':metrics['max_flat_stance_world_sliding_m']<.001,'original_paint':metrics['packed_art_unchanged'],'source_preservation':metrics['source_unchanged'],'candidate_preservation':metrics['candidate_unchanged']}
out={'metrics':metrics,'checks':checks,'samples':sample,'passed':all(checks.values()),'limit':'Technical checks do not establish convincing acting or artistic acceptance.'}
(O/'evidence/COLD_VALIDATION.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
if not out['passed']:raise RuntimeError('Candidate mechanical checks failed')
