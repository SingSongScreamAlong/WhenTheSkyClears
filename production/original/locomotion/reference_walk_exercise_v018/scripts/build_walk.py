import bpy,sys,math,json
from pathlib import Path
from mathutils import Matrix,Vector
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'scripts'));import walk_common as W
S,rig,T,col,recipes=W.setup();times={1+i*.0625 for i in range(769)}
for side in ['near','far']:
 for C in range(1 if side=='near' else -11,50,24):
  for q in [0,3,9,14,24]+[r['from_phase'] for r in recipes[side]['contacts']]:
   if 1<=C+q<=49:times.add(C+q)
times=sorted(times);feet={}
colors={'near':W.material('V018 near contact teal',(.14,.40,.35)),'far':W.material('V018 far contact ochre',(.57,.30,.14))}
for side in ['near','far']:
 roots=[];goals=[];marks=[];flat=Matrix(recipes[side]['flat_bone'])
 for i,c in enumerate(recipes[side]['contacts']):
  root=W.empty('BOY | '+side+' | FIXED_CONTACT_VERTEX_'+str(c['vertex']),col);goal=W.empty('BOY | '+side+' | ROLL_GOAL_'+str(i),col,root);goal.matrix_basis=Matrix.Translation(-Vector(c['point']))@flat;roots.append(root);goals.append(goal)
  bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=4,radius=.008);mark=bpy.context.object;mark.name='CONTACT '+side+' vertex '+str(c['vertex'])
  for old in list(mark.users_collection):old.objects.unlink(mark)
  col.objects.link(mark);mark.data.materials.append(colors[side]);marks.append(mark)
 swing=W.empty('BOY | '+side+' | SWING_GOAL',col);swing.rotation_mode='QUATERNION';all_goals=goals+[swing];ankle=W.api.CONTROLS['BOY','ANKLE_'+side];cts=[]
 for goal in all_goals:
  ct=ankle.constraints.new('COPY_TRANSFORMS');ct.name='V018 | world sole mode | '+goal.name;ct.target=goal;ct.owner_space='WORLD';ct.target_space='WORLD';ct.mix_mode='REPLACE';cts.append(ct)
 for f in times:
  C=W.contact_frame(f,side);q=f-C;M,info=W.state(f,side,recipes);land=W.travel(C)+W.STEP/2
  active=len(roots) if q>=14-1e-8 else max(i for i,c in enumerate(recipes[side]['contacts']) if q>=c['from_phase']-1e-8)
  for i,(root,c,mark) in enumerate(zip(roots,recipes[side]['contacts'],marks)):
   root.location=Vector(c['anchor'])+Vector((land,0,0));root.rotation_euler=(0,info['pitch'],0);root.keyframe_insert('location',frame=f);root.keyframe_insert('rotation_euler',frame=f)
   mark.location=(root.location.x,-.12,0);mark.hide_render=(i!=active);mark.keyframe_insert('location',frame=f);mark.keyframe_insert('hide_render',frame=f)
  swing.matrix_world=M;swing.keyframe_insert('location',frame=f);swing.keyframe_insert('rotation_quaternion',frame=f)
  for i,ct in enumerate(cts):ct.influence=float(i==active);ct.keyframe_insert('influence',frame=f)
 for root in roots:
  W.interpolation(root)
  for fc in W.iter_fc(root):
   if fc.data_path=='location':
    for k in fc.keyframe_points:k.interpolation='CONSTANT'
 for mark in marks:W.interpolation(mark,'CONSTANT')
 W.interpolation(swing)
 for fc in W.iter_fc(ankle):
  for k in fc.keyframe_points:k.interpolation='CONSTANT'
 feet[side]={'constraint_names':[c.name for c in cts],'goals':[g.name for g in all_goals]}
rows=[]
for f in times:
 S.frame_set(int(f),subframe=f-int(f));saved=[]
 for o in [*W.api.CONTROLS.values(),rig,T]:
  if o.animation_data and o.animation_data.action:saved.append((o,o.animation_data.action,o.animation_data.action_slot));o.animation_data.action=None
 # Ankle mode constraint actions must stay active while solving the body.
 for o,a,slot in list(saved):
  if o.get('v016_control','').startswith('ANKLE'):o.animation_data.action=a;o.animation_data.action_slot=slot;saved.remove((o,a,slot))
 W.body_pose(f,rig,T,recipes,True,False);rows.append(W.validate(f,rig,recipes))
 for o,a,slot in saved:o.animation_data.action=a;o.animation_data.action_slot=slot
 for o in W.api.CONTROLS.values():
  if o.get('v016_control','').startswith('ANKLE'):continue
  o.rotation_mode='QUATERNION'
  for field in ['location','rotation_quaternion','scale']:o.keyframe_insert(field,frame=f)
  for k in ['Reach','Brace','TorsoFollow','BraceFollow','FrontLayer']:
   if k in o:o.keyframe_insert(data_path='["'+k+'"]',frame=f)
 for b in rig.pose.bones:
  for ct in b.constraints:
   if ct.type=='IK':ct.keyframe_insert('pole_angle',frame=f)
 T.keyframe_insert('location',frame=f)
for o in [*W.api.CONTROLS.values(),rig,T]:
 if o.get('v016_control','').startswith('ANKLE'):continue
 W.interpolation(o)
S['V018_stage']='CONTINUOUS CAPABILITY STUDY; native fixed-vertex stance pivots; 24-frame translating cycle'
S['V018_travel_contract']='D(frame)=0.44*(frame-1)/24 metres along +X. Frames1,25,49 same relative pose. 24fps. Original proportions, no stretch.'
S['V018_artistic_acceptance']='UNPASSED; independent review required before further actions, painting or integration'
rig['v018_contact_modes']=json.dumps(feet);rig['v018_boot_art_edit']='NONE. Original vertices/UVs/materials/weights preserved; measured polygonal rocker only.'
for name in ['walk_common.py','rig_pose_api.py','build_walk.py']:
 t=bpy.data.texts.get(name) or bpy.data.texts.new(name);t.clear();t.write((P/'scripts'/name).read_text())
(P/'evidence/authored_sample_validation.json').write_text(json.dumps(rows,indent=2));W.ensure_placement();S.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Boy_Travelling_Walk_v018.blend'),compress=True)
bad=[(r['frame'],x) for r in rows for x in r['reach'] if not x['reachable']];print('V018_BAD_REACH',json.dumps(bad));print('V018_CONTINUOUS_NATIVE_SAVED')
