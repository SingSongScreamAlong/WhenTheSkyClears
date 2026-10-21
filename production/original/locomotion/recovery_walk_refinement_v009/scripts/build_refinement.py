"""Isolated editable planar performance; source paint/geometry is reused.
Source poses 1..72 retained apart from a design-preserving head simplification.
New late world-space foot contacts and root curve deliberately supersede v007.
"""
import bpy,math,json,csv,runpy
from pathlib import Path
from mathutils import Matrix,Vector
P=Path(__file__).resolve().parents[1];R=P.parents[1]
for folder in ['evidence','native','previews']:(P/folder).mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'locomotion/supported_recovery_v007/native/WTSC_Supported_Recovery_v007.blend'),load_ui=False)
S=bpy.context.scene;root=next(o for o in S.objects if o.get('motion_revision')=='v007_drawn_pose_corrections');pair=root.users_collection[0]
rigs={o['character']:o for o in root.children_recursive if o.type=='ARMATURE'}
rest={w:{b.name:b.matrix_local.copy() for b in rig.data.bones} for w,rig in rigs.items()}
distance=next(o for o in root.children if o.get('loco_role')=='DISTANCE_CURVE')
base={w:{} for w in rigs};draw={};D=[]
for w,rig in rigs.items():
 for ob in rig.children:
  if ob.type=='MESH' and ob.get('v007_role') in ['drawn_leg','drawn_arm','drawn_cuff']:
   draw[ob.name]={f:[v.co.copy() for v in ob.data.shape_keys.key_blocks[f'POSE_{f:03d}'].data] for f in range(1,121)}
for f in range(1,121):
 S.frame_set(f);bpy.context.view_layer.update();D.append(distance.location.x)
 for w,rig in rigs.items():base[w][f]={p.name:p.matrix.copy() for p in rig.pose.bones}
def sm(a,b,t):
 u=max(0,min(1,(t-a)/(b-a)));return u*u*(3-2*u)
def cv(keys,t):
 if t<=keys[0][0]:return keys[0][1]
 for (a,x),(b,y) in zip(keys,keys[1:]):
  if t<=b:return x+(y-x)*sm(a,b,t)
 return keys[-1][1]
def around(p,a):return Matrix.Translation(p)@Matrix.Rotation(a,4,'Y')@Matrix.Translation(-p)
def extra(f):
 if f<=88:return 0.
 if f<102:return .012*(f-88)**2/28
 return .084+.012*(f-102)
ND=[D[f-1]+extra(f) for f in range(1,121)]
def linear(action):
 for l in action.layers:
  for st in l.strips:
   for bag in st.channelbags:
    for fc in bag.fcurves:
     for k in fc.keyframe_points:k.interpolation='LINEAR'
def clear(id):
 if id.animation_data:
  id.animation_data.action=None
  for t in list(id.animation_data.nla_tracks):id.animation_data.nla_tracks.remove(t)
def stash(id,action,label):
 linear(action);slot=id.animation_data.action_slot;id.animation_data.action=None;track=id.animation_data.nla_tracks.new();track.name=label;st=track.strips.new(action.name,1,action);st.action_slot=slot;st.action_frame_start=1;st.action_frame_end=120;st.frame_end=120;st.extrapolation='HOLD';action.use_fake_user=True
def segment(w,n,A,B):
 rb=rigs[w].data.bones[n];v=rb.tail_local-rb.head_local;d=B-A
 a=math.atan2(d.x,d.z)-math.atan2(v.x,v.z)
 return Matrix.Translation(A)@Matrix.Rotation(a,4,'Y')@Matrix.Translation(-rb.head_local)@rest[w][n]
def solve_arm(w,p,side,W,direction):
 A=p['upper_arm_'+side].translation.copy();A.y=0;W=W.copy();W.y=0
 L1=rigs[w].data.bones['upper_arm_'+side].length;L2=rigs[w].data.bones['forearm_'+side].length
 d=W-A;dd=min(max(d.length,abs(L1-L2)+.003),.987*(L1+L2));u=d.normalized();W=A+u*dd
 a=(L1*L1-L2*L2+dd*dd)/(2*dd);h=math.sqrt(max(0,L1*L1-a*a));n=Vector((-u.z,0,u.x));E=min([A+u*a+n*h,A+u*a-n*h],key=lambda v:v.z+.08*abs(v.x-A.x))
 p['upper_arm_'+side]=segment(w,'upper_arm_'+side,A,E);p['forearm_'+side]=segment(w,'forearm_'+side,E,W);p['hand_'+side]=segment(w,'hand_'+side,W,W+direction.normalized()*.06)
def solve_leg(w,p,side,H,A):
 L1=rigs[w].data.bones['thigh_'+side].length;L2=rigs[w].data.bones['shin_'+side].length;v=A-H;v.y=0;dd=min(v.length,(L1+L2)*.997);u=v.normalized();a=(L1*L1-L2*L2+dd*dd)/(2*dd);h=math.sqrt(max(0,L1*L1-a*a));n=Vector((-u.z,0,u.x));K=H+u*a+n*h
 p['thigh_'+side]=segment(w,'thigh_'+side,H,K);p['shin_'+side]=segment(w,'shin_'+side,K,A)
bootpoints={};pivots={}
for w,rig in rigs.items():
 for side in ['near','far']:
  ob=next(o for o in rig.children if o.get('v007_role')=='support_boot' and o.name.endswith(side));B=base[w][81]['foot_'+side]
  pts=[B@rest[w]['foot_'+side].inverted()@v.co for v in ob.data.shape_keys.key_blocks['POSE_081'].data]
  floor=min(p.z for p in pts);sole=[p for p in pts if p.z<floor+.004]
  toe=max(sole,key=lambda p:p.x).copy();heel=min(sole,key=lambda p:p.x).copy();toe.z=floor;heel.z=floor
  bootpoints[w,side]=pts;pivots[w,side]=(toe,heel)
events={('GIRL','near'):(86,102,.30,.070),('GIRL','far'):(110,128,.53,.062),('BOY','near'):(99,116,.32,.078),('BOY','far'):(124,142,.53,.070)}
def foot_pose(w,side,f):
 B=base[w][81]['foot_'+side].copy();start,end,step,height=events[w,side];u=max(0,min(1,(f-start)/(end-start)));toe,heel=pivots[w,side]
 if f<start:
  angle=.21*sm(start-4,start,f);pivot=toe;dx=0.;lift=0
 elif f<=end:
  angle=cv([(0,.21),(.35,.03),(.7,-.16),(1,-.075)],u);pivot=toe.lerp(heel,sm(.2,.8,u));dx=step*sm(0,1,u);lift=height*math.sin(math.pi*u)**1.25
 else:angle=-.075*(1-sm(end,end+3,f));pivot=heel;dx=step;lift=0
 M=Matrix.Translation(Vector((dx-extra(f),0,lift)))@around(pivot,angle)@B
 return M
poses={w:{} for w in rigs};contacts=[]
for w,rig in rigs.items():
 for f in range(1,121):
  # Faster recovery opens time for actual stepping; original fall/catch preserved.
  t=min(120,round(81+1.65*(f-81))) if f>81 else f
  p={n:m.copy() for n,m in base[w][t].items()}
  if f>72:
   blend=sm(72,81,f);hip=p['pelvis'].translation.copy()
   if w=='BOY':
    target=Vector((cv([(72,.063),(81,.073),(91,.105),(99,.095),(108,.060),(116,.035),(120,.045)],f),0,cv([(72,.451),(81,.431),(88,.440),(96,.505),(105,.548),(110,.555),(116,.539),(120,.548)],f)))
   else:
    target=Vector((cv([(72,-.021),(81,.010),(86,.055),(94,.092),(102,.137),(110,.143),(116,.098),(120,.062)],f),0,cv([(72,.49),(81,.516),(88,.535),(96,.555),(103,.553),(110,.566),(116,.557),(120,.545)],f)))
   off=(target-hip)*blend
   for n in p:
    if not n.startswith(('foot_','thigh_','shin_')):p[n]=Matrix.Translation(off)@p[n]
   hip=p['pelvis'].translation.copy()
   for side in ['near','far']:
    M=foot_pose(w,side,f);p['foot_'+side]=base[w][f]['foot_'+side].lerp(M,blend)
    H=hip+Vector((.012 if side=='near' else -.012,0,0));solve_leg(w,p,side,H,p['foot_'+side].translation)
  # Keep original right profile and braid for every exposure. Rotation is only in XZ.
  if w=='GIRL' and f>=39:
   a=cv([(39,0),(52,.065),(73,.09),(89,.035),(106,.015),(120,.04)],f)
   current=p['head'];desired=around(current.translation,a)@base[w][37]['head'];desired.translation=current.translation
   delta=desired@current.inverted();p['head']=desired
   if 'braid' in p:p['braid']=delta@p['braid']
  if f>=70:
   b=sm(70,80,f);hip=p['pelvis'].translation.copy()
   for side in ['near','far']:
    W=p['hand_'+side].translation.copy();direction=Vector((.15,0,-1))
    if (w,side) in [('GIRL','near'),('BOY','far')]:
     offer=sm(76,96,f)*(1-sm(103,114,f));reach=Vector((-.256 if w=='GIRL' else .416,0,cv([(70,.79),(96,.82),(103,.85),(114,.80)],f)))
     hanging=hip+Vector((.035 if side=='near' else .115,0,.04 if w=='BOY' else -.015))
     target=hanging.lerp(reach,offer);direction=Vector((-1 if w=='GIRL' else 1,0,0)).lerp(Vector((.12,0,-1)),sm(103,114,f))
    elif w=='BOY' and side=='near':
     brace=1-sm(95,109,f);target=(hip+Vector((.04,0,.015))).lerp(p['shin_far'].translation+Vector((.015,0,.17)),brace)
    else:target=hip+Vector((.065+.032*math.sin((f-94)*math.pi/20),0,-.025));direction=Vector((.2,0,-1))
    solve_arm(w,p,side,W.lerp(target,b),direction)
  poses[w][f]=p
 clear(rig);rig.animation_data.action=bpy.data.actions.new('V009_'+w+'__RECOVERY_TO_WALK_120F')
 for f,p in poses[w].items():
  for n,m in p.items():
   pb=rig.pose.bones[n];pb.rotation_mode='QUATERNION';pb.matrix=m
   for field in ['location','rotation_quaternion','scale']:pb.keyframe_insert(field,frame=f,group=n)
 stash(rig,rig.animation_data.action,'V009 authored weight and restart')
def norm(v):
 v=Vector((-v.z,0,v.x));return v.normalized() if v.length>1e-7 else Vector((1,0,0))
def qbez(a,b,c,t):return (1-t)**2*a+2*(1-t)*t*b+t*t*c
def cbez(a,b,c,d,t):return (1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d
def put(ob,f,pts):
 key=ob.data.shape_keys.key_blocks[f'POSE_{f:03d}'];key.data.foreach_set('co',[c for p in pts for c in p])
for w,rig in rigs.items():
 for side in ['near','far']:
  leg=next(o for o in rig.children if o.get('v007_role')=='drawn_leg' and o.name.endswith(side));sleeve=next(o for o in rig.children if o.get('v007_role')=='drawn_arm' and 'sleeve' in o.name and o.name.endswith(side));skin=next(o for o in rig.children if o.get('v007_role')=='drawn_arm' and 'skin' in o.name and o.name.endswith(side));cuff=next(o for o in rig.children if o.get('v007_role')=='drawn_cuff' and o.name.endswith(side))
  for f in range(73,121):
   p=poses[w][f];b=sm(72,81,f);old=draw[leg.name][f];oldE=(old[-2]+old[-1])*.5;E=p['foot_'+side]@base[w][f]['foot_'+side].inverted()@oldE;H=p['thigh_'+side].translation;K=p['shin_'+side].translation
   t1=(K-H).normalized();t2=(E-K).normalized();r=min(.065,(K-H).length*.3,(E-K).length*.3);B=K-t1*r;C=K+t2*r;centers=[]
   for i in range(33):
    t=i/32
    centers.append(H.lerp(B,t/.35) if t<.35 else qbez(B,K,C,(t-.35)/.3) if t<.65 else C.lerp(E,(t-.65)/.35))
   pts=[]
   for i,A in enumerate(centers):
    n=norm(centers[min(32,i+1)]-centers[max(0,i-1)]);width=(old[2*i+1]-old[2*i]).length*.5
    if i>=30:
     axis=(p['foot_'+side]@base[w][f]['foot_'+side].inverted()).to_3x3()@(old[-1]-old[-2]);axis.normalize()
     if axis.dot(n)<0:axis=-axis
     n=n.lerp(axis,sm(29,32,i)).normalized()
    for j,sign in enumerate([-1,1]):
     v=A+n*width*sign;v.y=old[2*i+j].y;pts.append(old[2*i+j].lerp(v,b))
   put(leg,f,pts)
   A=p['upper_arm_'+side].translation;E=p['forearm_'+side].translation;W=p['hand_'+side].translation;tangent=(W-A).normalized();newSleeve=[]
   for ob,aa,bb,c1,c2 in [(sleeve,A,E,A+(E-A)*.32,E-tangent*(E-A).length*.23),(skin,E,W,E+tangent*(W-E).length*.26,W-(W-E)*.24)]:
    old=draw[ob.name][f];pts=[]
    for i in range(19):
     t=i/18;point=cbez(aa,c1,c2,bb,t);v=3*(1-t)**2*(c1-aa)+6*(1-t)*t*(c2-c1)+3*t*t*(bb-c2);n=norm(v);width=(old[2*i+1]-old[2*i]).length*.5
     for j,sign in enumerate([-1,1]):
      q=point+n*width*sign;q.y=old[2*i+j].y;pts.append(old[2*i+j].lerp(q,b))
    put(ob,f,pts)
    if ob==sleeve:newSleeve=pts
   put(cuff,f,[Vector((v.x,v.y-.001,v.z)) for v in newSleeve[-8:]])
# No passing-disc or reflected head exposure. Existing source head includes braid.
girl=rigs['GIRL'];sourcehead=next(o for o in girl.children if 'original head and attached braid' in o.name)
for ob in girl.children:
 if ob.get('v007_head_exposure'):
  clear(ob);ob.hide_render=ob!=sourcehead;ob.hide_viewport=ob!=sourcehead;ob['v009_head_choice']='Original right profile retained; downward nod; no out-of-plane rotation or missing turnaround'
  if ob!=sourcehead:ob['v009_excluded_study']=True
sourcehead.hide_render=False;sourcehead.hide_viewport=False
clear(distance)
for f,d in enumerate(ND,1):distance.location.x=d;distance.keyframe_insert('location',index=0,frame=f)
distance.animation_data.action.name='V009_ROOT__EXPLICIT_TRAVEL_120F';stash(distance,distance.animation_data.action,'V009 travel contract')
pair.name='WTSC_RECOVERY_WALK_PAIR_v009';root['motion_revision']='v009_recovery_walk';root['loco_pack']='WTSC_RECOVERY_WALK_v009';root['travel_total_m']=ND[-1];root['review_status']='Isolated recovery-to-walk motion proof. Artistic assessment required. New root/foot contract.'
for w,rig in rigs.items():rig['motion_status']='v009 distinct weight transfer and restart; original paint/proportions'
for ob in pair.all_objects:
 if ob.type=='CURVE':ob.hide_render=True;ob.hide_viewport=True
cfg=runpy.run_path(str(P/'scripts/configure_v009.py'))['configure_v009'];cfg(start=1,root_motion=False,root=root)
for t in list(bpy.data.texts):bpy.data.texts.remove(t)
text=bpy.data.texts.new('configure_v009.py');text.write((P/'scripts/configure_v009.py').read_text())
S.name='V009 | recovery to walking | isolated proof';S.frame_start=1;S.frame_end=120
for name,label in [('LOCO | title','WHEN THE SKY CLEARS / v009 MOTION PROOF'),('LOCO | clip label','DISTINCT RECOVERY / RESTART STEP / SOURCE PAINT')]:
 if name in S.objects:S.objects[name].data.body=label
for o in S.objects:
 if o.type=='FONT' and 'VARIABLE DISTANCE' in o.data.body:o.data.body='NATIVE PAINTED 2D / REVIEW BEFORE INTEGRATION / NEW TRAVEL 0.861667m'
S.render.threads_mode='FIXED';S.render.threads=2;S.render.resolution_x=960;S.render.resolution_y=540;S.render.resolution_percentage=100
S.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Recovery_Walk_v009.blend'),compress=True)
with (P/'evidence/travel_curve_v009.csv').open('w',newline='') as out:
 writer=csv.writer(out);writer.writerow(['local_frame','global_frame','time_seconds','distance_m','delta_vs_v046_m'])
 for f in range(1,121):writer.writerow([f,1800+f,75+(f-1)/24,ND[f-1],extra(f)])
report={'native':str(P/'native/WTSC_Recovery_Walk_v009.blend'),'fps':24,'frames':120,'total_travel_m':ND[-1],'extra_travel_m':extra(120),'travel_formula':'D009(f)=D007(f)+e(f). e=0 for f<=88; .012*(f-88)^2/28 for88<f<102; .084+.012*(f-102) thereafter. Native distance Action linearly interpolates integer samples.','steps':{w+'_'+s:{'toeoff':a,'heel_strike':b,'delta_m':x,'clearance_m':z} for (w,s),(a,b,x,z) in events.items()},'head_choice':'Hold original painted right profile and attached braid; XZ nod only. Removes disc and avoids rejected v008/head art. Girl attends through lowered gaze, counterbalance and offered/releasing arm. No literal look back claimed.','hands':'Light steadying cue, feet carry weight; no load-bearing clasp claim. Release103..114.','limits':'Source early stumble retained; native planar limbs still have cutout limits. End boundary is moving with second girl step airborne and boy trailing heel preparing. Continuation must preserve state/velocity.'}
(P/'evidence/authored_pose_targets.json').write_text(json.dumps({w:{str(f):{n:[list(v) for v in m] for n,m in poses[w][f].items()} for f in [81,86,94,99,102,108,112,116,120]} for w in rigs},indent=2))
(P/'evidence/build_report.json').write_text(json.dumps(report,indent=2));print('V009_NATIVE_BUILT',json.dumps(report),flush=True)
