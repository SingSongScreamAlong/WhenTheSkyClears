import bpy,math,json,csv,ast,runpy,hashlib
from pathlib import Path
from mathutils import Matrix,Vector,Quaternion
P=Path(__file__).resolve().parents[1];R=P.parents[1];V9=R/'locomotion/recovery_walk_refinement_v009';N=168
for folder in ['native','evidence','previews']:(P/folder).mkdir(exist_ok=True)
protected=['locomotion/recovery_walk_refinement_v009/native/WTSC_Recovery_Walk_v009.blend','locomotion/recovery_walk_refinement_v009/native/WTSC_v009_Matched_Review_Copy.blend','locomotion/recovery_walk_refinement_v009/WTSC_v009_Matched_Recovery_Walk_75_80.mp4','shots/world/WTSC_Open_Battlefield_Supported_Trial_v046.blend','locomotion/supported_recovery_v007/native/WTSC_Supported_Recovery_v007.blend','shots/world/WTSC_Open_Battlefield_Art_Study_v045c.blend']
(P/'evidence/protected_inputs.json').write_text(json.dumps({n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in protected},indent=2))
bpy.ops.wm.open_mainfile(filepath=str(V9/'native/WTSC_Recovery_Walk_v009.blend'),load_ui=False);S=bpy.context.scene
root=next(o for o in S.objects if o.get('motion_revision')=='v009_recovery_walk');pair=root.users_collection[0];rigs={o['character']:o for o in root.children_recursive if o.type=='ARMATURE'};rest={w:{b.name:b.matrix_local.copy() for b in rig.data.bones} for w,rig in rigs.items()};distance=next(o for o in root.children if o.get('loco_role')=='DISTANCE_CURVE')
# Reuse the retained native planar construction helpers without executing its builder.
tree=ast.parse((V9/'scripts/build_refinement.py').read_text());tree.body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['sm','cv','around','linear','clear','segment','solve_arm','solve_leg','norm','qbez','cbez']];exec(compile(tree,'retained_v009_geometry_helpers','exec'),globals())
base={w:{} for w in rigs};draw={};values={};oldD=[]
for ob in pair.all_objects:
 if ob.type=='MESH' and ob.data.shape_keys:
  sk=ob.data.shape_keys
  if 'POSE_001' in sk.key_blocks:draw[ob.name]={f:[v.co.copy() for v in sk.key_blocks[f'POSE_{f:03d}'].data] for f in range(1,121)}
  else:values[ob.name]={}
for f in range(1,121):
 S.frame_set(f);bpy.context.view_layer.update();oldD.append(distance.location.x)
 for w,rig in rigs.items():base[w][f]={b.name:b.matrix.copy() for b in rig.pose.bones}
 for name in values:values[name][f]={k.name:k.value for k in bpy.data.objects[name].data.shape_keys.key_blocks if k.name!='Basis'}
contractD=[float(row['distance_m']) for row in csv.DictReader((V9/'evidence/travel_curve_v009.csv').open())]
ND=contractD+[contractD[-1]+.012*(f-120) for f in range(121,N+1)]
def stash(id,action,label):
 linear(action);slot=id.animation_data.action_slot;id.animation_data.action=None;tr=id.animation_data.nla_tracks.new();tr.name=label;st=tr.strips.new(action.name,1,action);st.action_slot=slot;st.action_frame_start=1;st.action_frame_end=N;st.frame_end=N;st.extrapolation='HOLD';action.use_fake_user=True
def hcurve(keys,f,initial_velocity=0.):
 if f<=keys[0][0]:return keys[0][1]
 for i,((a,x),(b,y)) in enumerate(zip(keys,keys[1:])):
  if f<=b:
   m0=initial_velocity if i==0 else (y-keys[i-1][1])/(b-keys[i-1][0]);m1=0 if i+2==len(keys) else (keys[i+2][1]-x)/(keys[i+2][0]-a);t=(f-a)/(b-a);d=b-a
   return (2*t**3-3*t*t+1)*x+(t**3-2*t*t+t)*d*m0+(-2*t**3+3*t*t)*y+(t**3-t*t)*d*m1
 return keys[-1][1]
def inertia(Mprev,Mend,target,dt):
 # Short authored continuation of prior local velocity; converges within eight frames.
 a=Mend.copy();a.translation+=(Mend.translation-Mprev.translation)*dt
 q0=Mprev.to_quaternion();q1=Mend.to_quaternion();dq=q1@q0.inverted();axis,angle=dq.to_axis_angle();q=Quaternion(axis,angle*dt)@q1;a=Matrix.LocRotScale(a.translation,q,Mend.to_scale())
 return a.lerp(target,sm(120,128,120+dt))
pivots={}
for w,rig in rigs.items():
 for side in ['near','far']:
  ob=next(o for o in rig.children if o.get('v007_role')=='support_boot' and o.name.endswith(side));B=base[w][81]['foot_'+side];pts=[B@rest[w]['foot_'+side].inverted()@p for p in draw[ob.name][81]];floor=min(p.z for p in pts);sole=[p for p in pts if p.z<floor+.004];toe=max(sole,key=lambda p:p.x).copy();heel=min(sole,key=lambda p:p.x).copy();toe.z=floor;heel.z=floor;pivots[w,side]=(toe,heel)
events={('GIRL','near'):[(86,102,.30,.070),(134,152,.876,.062)],('GIRL','far'):[(110,128,.53,.062),(158,176,1.106,.059)],('BOY','near'):[(99,116,.32,.078),(148,166,.896,.066)],('BOY','far'):[(124,142,.53,.070),(172,190,1.106,.064)]}
def foot(w,side,f):
 B=base[w][81]['foot_'+side];toe,heel=pivots[w,side];previous=0
 for start,end,target,height in events[w,side]:
  if f<=end:
   if f<start:angle=.21*sm(start-4,start,f);pivot=toe;dx=previous;lift=0
   else:
    u=(f-start)/(end-start);angle=cv([(0,.21),(.35,.03),(.7,-.16),(1,-.075)],u);pivot=toe.lerp(heel,sm(.2,.8,u));dx=previous+(target-previous)*sm(0,1,u);lift=height*math.sin(math.pi*u)**1.25
   break
  previous=target
  # If between contact flattening and next toe roll, use the completed step.
  nextstart=next((a for a,b,_,_ in events[w,side] if a>start),None)
  if nextstart is None or f<nextstart-4:
   angle=-.075*(1-sm(end,end+3,f));pivot=heel;dx=target;lift=0;break
 else:angle=0;pivot=heel;dx=previous;lift=0
 return Matrix.Translation(Vector((dx-(ND[f-1]-oldD[80]),0,lift)))@around(pivot,angle)@B
poses={w:{} for w in rigs};hipoffset={w:{} for w in rigs}
for w,rig in rigs.items():
 for f in range(1,121):
  p={n:m.copy() for n,m in base[w][f].items()};env=sm(24,31,f)*(1-sm(64,77,f));hip=p['pelvis'].translation.copy()
  if w=='BOY':
   off=Vector((cv([(24,0),(31,-.012),(39,-.015),(45,.012),(53,.008),(65,0),(77,0)],f),0,cv([(24,0),(30,.008),(38,-.012),(46,-.020),(55,.010),(65,.006),(77,0)],f)))
   tilt=cv([(24,0),(31,-.035),(37,.045),(43,.065),(51,-.025),(62,.01),(77,0)],f)
  else:
   off=Vector((cv([(24,0),(28,.012),(35,.018),(42,-.012),(49,-.018),(60,0),(77,0)],f),0,cv([(24,0),(29,.006),(36,-.008),(44,.014),(52,.012),(65,0),(77,0)],f)));tilt=cv([(24,0),(30,-.045),(36,-.025),(42,-.055),(51,.015),(62,0),(77,0)],f)
  hipoffset[w][f]=off
  if 24<f<82:
   for n in p:
    if not n.startswith(('foot_','thigh_','shin_')):p[n]=Matrix.Translation(off)@p[n]
   hip=p['pelvis'].translation.copy();rot=around(hip,tilt)
   for n in p:
    if n in ['chest','head','braid'] or n.startswith(('upper_arm_','forearm_','hand_')):p[n]=rot@p[n]
   for side in ['near','far']:
    H=base[w][f]['thigh_'+side].translation+off;K=base[w][f]['shin_'+side].translation+off*.4;A=p['foot_'+side].translation;p['thigh_'+side]=segment(w,'thigh_'+side,H,K);p['shin_'+side]=segment(w,'shin_'+side,K,A)
   for side in ['near','far']:
    W=p['hand_'+side].translation.copy();A=p['upper_arm_'+side].translation.copy();A+=Vector((-.006 if w=='BOY' else .004,0,-.006))*env;p['upper_arm_'+side].translation=A
    if w=='GIRL' and side=='near':
     guard=hip+Vector((cv([(24,.10),(31,.23),(38,.30),(45,.24),(53,.14)],f),0,cv([(24,.1),(31,.20),(38,.16),(45,.15),(53,.1)],f)))
     released=A+Vector((cv([(45,.04),(53,.035),(61,-.13),(69,-.24),(77,-.26)],f),0,cv([(45,-.34),(53,-.365),(61,-.31),(69,-.18),(77,-.08)],f)));target=guard.lerp(released,sm(43,53,f))
    elif w=='GIRL':
     balance=hip+Vector((cv([(24,-.08),(32,-.15),(39,-.19),(46,-.14),(55,-.06),(65,.01),(77,.01)],f),0,cv([(24,.1),(35,.12),(44,.08),(55,.02),(65,-.015),(77,-.015)],f)));target=balance.lerp(A+Vector((.035,0,-.365)),sm(43,53,f))
    elif side=='far':target=A+Vector((cv([(24,-.02),(32,-.05),(39,-.08),(47,-.07),(56,-.02),(66,.02),(77,.04)],f),0,cv([(24,-.36),(33,-.38),(42,-.375),(51,-.38),(65,-.39),(77,-.39)],f)))
    else:
     target=A+Vector((cv([(24,.08),(32,.11),(39,.13),(44,.10),(50,.05)],f),0,cv([(24,-.35),(32,-.36),(39,-.355),(44,-.37),(50,-.38)],f)))
    influence=env*.88
    if w=='GIRL' and side=='far':influence=max(influence,sm(45,53,f)*(1-sm(73,81,f)))
    if w=='BOY' and side=='near':influence*=1-sm(41,50,f)
    solve_arm(w,p,side,W.lerp(target,influence),Vector((.15,0,-1)))
  # Limit excessive wrist kinks, preserving the light-contact intent at94..103.
  wristweight=sm(23,32,f)*(1-sm(84,94,f)*(1-sm(103,115,f)))
  for side in ['near','far']:
   E=p['forearm_'+side].translation;W=p['hand_'+side].translation;fore=(W-E).normalized();old=p['hand_'+side].col[1].xyz.normalized();a=math.atan2(old.x,old.z)-math.atan2(fore.x,fore.z);a=(a+math.pi)%(2*math.pi)-math.pi;clamped=max(-.65,min(.65,a));wanted=Matrix.Rotation(clamped,3,'Y')@fore;direction=old.lerp(wanted,wristweight*.85).normalized();p['hand_'+side]=segment(w,'hand_'+side,W,W+direction*.06)
  poses[w][f]=p
 for f in range(121,N+1):
  end=poses[w][120];prev=poses[w][119];hip0=end['pelvis'].translation;vel=hip0-prev['pelvis'].translation
  if w=='BOY':kx=[(120,hip0.x),(126,.025),(132,-.015),(139,-.070),(142,-.055),(148,.040),(154,.020),(160,-.040),(166,-.045),(168,-.025)];kz=[(120,hip0.z),(128,.558),(138,.548),(143,.536),(151,.558),(161,.549),(166,.537),(168,.543)]
  else:kx=[(120,hip0.x),(126,.070),(132,.150),(138,.130),(144,.070),(150,.035),(156,.120),(162,.130),(168,.070)];kz=[(120,hip0.z),(127,.540),(135,.562),(145,.551),(152,.539),(160,.563),(168,.551)]
  hip=Vector((hcurve(kx,f,vel.x),0,hcurve(kz,f,vel.z)));lean=.020*math.sin((f-120)*math.pi/24);transform=Matrix.Translation(hip-hip0)@around(hip0,lean);p={n:inertia(prev[n],end[n],transform@end[n],f-120) for n in end}
  # Pelvis directly follows the smooth authored support curve.
  p['pelvis']=end['pelvis'].copy();p['pelvis'].translation=hip
  for side in ['near','far']:
   p['foot_'+side]=foot(w,side,f);H=hip+Vector((.012 if side=='near' else -.012,0,0));solve_leg(w,p,side,H,p['foot_'+side].translation)
   phase=(f-120)*math.pi/24+(0 if side=='near' else math.pi)+(0 if w=='BOY' else .6);hanging=end['hand_'+side].translation+(hip-hip0);hanging.x+=.023*math.sin(phase)*sm(120,132,f);hanging.z+=.006*math.sin(phase+.4)*sm(120,132,f);W=p['hand_'+side].translation.lerp(hanging,sm(120,130,f));solve_arm(w,p,side,W,Vector((.10+.12*math.sin(phase-.3),0,-1)))
   # Blend the wrist direction from the actual final pose, avoiding a seam snap.
   wrist=p['hand_'+side].translation;direction=end['hand_'+side].col[1].xyz.normalized().lerp(p['hand_'+side].col[1].xyz.normalized(),sm(120,130,f)).normalized();p['hand_'+side]=segment(w,'hand_'+side,wrist,wrist+direction*.06)
  poses[w][f]=p
 # Native rig curves, every sample explicit and editable.
 clear(rig);rig.animation_data.action=bpy.data.actions.new('V010_'+w+'__POLISH_AND_CONTINUE_168F')
 for f,p in poses[w].items():
  for name,m in p.items():
   pb=rig.pose.bones[name];pb.rotation_mode='QUATERNION';pb.matrix=m
   for field in ['location','rotation_quaternion','scale']:pb.keyframe_insert(field,frame=f,group=name)
 stash(rig,rig.animation_data.action,'V010 authored support continuation')
def setpts(ob,f,pts):
 sk=ob.data.shape_keys;key=sk.key_blocks.get(f'POSE_{f:03d}') or ob.shape_key_add(name=f'POSE_{f:03d}');key.data.foreach_set('co',[c for p in pts for c in p])
# Extend source native drawings. Original UVs and body/head rest geometry stay.
for ob in pair.all_objects:
 if ob.name not in draw:continue
 for f in range(121,N+1):setpts(ob,f,draw[ob.name][120])
for w,rig in rigs.items():
 for side in ['near','far']:
  leg=next(o for o in rig.children if o.get('v007_role')=='drawn_leg' and o.name.endswith(side));sleeve=next(o for o in rig.children if o.get('v007_role')=='drawn_arm' and 'sleeve' in o.name and o.name.endswith(side));skin=next(o for o in rig.children if o.get('v007_role')=='drawn_arm' and 'skin' in o.name and o.name.endswith(side));cuff=next(o for o in rig.children if o.get('v007_role')=='drawn_cuff' and o.name.endswith(side))
  for f in range(1,N+1):
   p=poses[w][f];src=min(f,120);old=draw[leg.name][src]
   if f<=120:
    off=hipoffset[w][f];pts=[q+off*(1-(i//2)/32)**1.2 for i,q in enumerate(old)];setpts(leg,f,pts)
   else:
    E=p['foot_'+side]@base[w][120]['foot_'+side].inverted()@((old[-2]+old[-1])*.5);H=p['thigh_'+side].translation;K=p['shin_'+side].translation;t1=(K-H).normalized();t2=(E-K).normalized();r=min(.065,(K-H).length*.3,(E-K).length*.3);B=K-t1*r;C=K+t2*r;centers=[]
    for i in range(33):
     t=i/32;centers.append(H.lerp(B,t/.35) if t<.35 else qbez(B,K,C,(t-.35)/.3) if t<.65 else C.lerp(E,(t-.65)/.35))
    pts=[]
    for i,A in enumerate(centers):
     n=norm(centers[min(32,i+1)]-centers[max(0,i-1)]);width=(old[2*i+1]-old[2*i]).length*.5
     if i>=30:
      axis=(p['foot_'+side]@base[w][120]['foot_'+side].inverted()).to_3x3()@(old[-1]-old[-2]);axis.normalize()
      if axis.dot(n)<0:axis=-axis
      n=n.lerp(axis,sm(29,32,i)).normalized()
     for j,sign in enumerate([-1,1]):v=A+n*width*sign;v.y=old[2*i+j].y;pts.append(v)
    setpts(leg,f,pts)
   A=p['upper_arm_'+side].translation;E=p['forearm_'+side].translation;W=p['hand_'+side].translation;tangent=(W-A).normalized();blend=sm(24,31,f) if f<=120 else 1
   newSleeve=[]
   for ob,aa,bb,c1,c2 in [(sleeve,A,E,A+(E-A)*.30,E-tangent*(E-A).length*.28),(skin,E,W,E+tangent*(W-E).length*.30,W-(W-E)*.23)]:
    oldarm=draw[ob.name][src];pts=[]
    for i in range(19):
     t=i/18;point=cbez(aa,c1,c2,bb,t);tang=3*(1-t)**2*(c1-aa)+6*(1-t)*t*(c2-c1)+3*t*t*(bb-c2);n=norm(tang);width=(oldarm[2*i+1]-oldarm[2*i]).length*.5
     if ob==sleeve:width*=1-.13*(1-sm(0,.18,t))
     for j,sign in enumerate([-1,1]):q=point+n*width*sign;q.y=oldarm[2*i+j].y;pts.append(oldarm[2*i+j].lerp(q,blend))
    setpts(ob,f,pts)
    if ob==sleeve:newSleeve=pts
   setpts(cuff,f,[Vector((q.x,q.y-.001,q.z)) for q in newSleeve[-8:]])
for ob in pair.all_objects:
 if ob.type!='MESH' or not ob.data.shape_keys:continue
 sk=ob.data.shape_keys
 if ob.name in draw:
  clear(sk)
  for f in range(1,N+1):
   key=sk.key_blocks[f'POSE_{f:03d}']
   for frame,val in [(max(1,f-1),0),(f,1),(min(N,f+1),0)]:key.value=val;key.keyframe_insert('value',frame=frame)
  for f in [1,N]:key=sk.key_blocks[f'POSE_{f:03d}'];key.value=1;key.keyframe_insert('value',frame=f)
  sk.animation_data.action.name=ob.name+' | V010 native drawings168F';stash(sk,sk.animation_data.action,'V010 drawing clock')
 elif ob.name in values:
  clear(sk)
  for f in range(1,N+1):
   for name,val in values[ob.name][min(f,120)].items():
    if f>120 and ob.get('skin_region') in ['body','dress']:val+=.07*math.sin((f-120)*math.pi/36)*sm(120,132,f)
    key=sk.key_blocks[name];key.value=val;key.keyframe_insert('value',frame=f)
  sk.animation_data.action.name=ob.name+' | V010 living cloth168F';stash(sk,sk.animation_data.action,'V010 cloth clock')
clear(distance)
for f,d in enumerate(ND,1):distance.location.x=d;distance.keyframe_insert('location',index=0,frame=f)
distance.animation_data.action.name='V010_ROOT__V009_FIRST120_PLUS_CONSTANT_EXTENSION';stash(distance,distance.animation_data.action,'V010 separate travel extension')
pair.name='WTSC_STUMBLE_POLISH_CONTINUATION_v010';root['motion_revision']='v010_polish_continuation';root['travel_total_m']=ND[-1];root['original_five_second_total_m']=oldD[-1];root['review_status']='Isolated narrowly scoped polish and separately identified2s continuation. Artistic review pending.'
for ob in list(pair.all_objects):
 if ob.type=='CURVE':bpy.data.objects.remove(ob,do_unlink=True)
cfg=runpy.run_path(str(P/'scripts/configure_v010.py'))['configure_v010'];cfg(start=1,root_motion=False,root=root)
for text in list(bpy.data.texts):bpy.data.texts.remove(text)
text=bpy.data.texts.new('configure_v010.py');text.write((P/'scripts/configure_v010.py').read_text())
S.name='V010 | stumble polish plus separate2s continuation';S.frame_start=1;S.frame_end=N
for o in S.objects:
 if o.type=='FONT':o.data.body='WTSC / v010 MOTION STUDY / FIVE SECONDS + SEPARATE TWO SECOND CONTINUATION' if 'title' in o.name else 'EARLY BALANCE / SOFTER ARMS / V009 TRAVEL RETAINED / 0.288m/s CONTINUATION'
S.render.resolution_x=960;S.render.resolution_y=540;S.render.resolution_percentage=100;S.render.threads_mode='FIXED';S.render.threads=2;S.eevee.taa_render_samples=16;S.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Stumble_Polish_Continuation_v010.blend'),compress=True)
for name,frames in [('travel_original_5s_v010.csv',range(1,121)),('travel_extension_80_82s_v010.csv',range(120,N+1)),('travel_complete_study_v010.csv',range(1,N+1))]:
 with (P/'evidence'/name).open('w',newline='') as out:
  wr=csv.writer(out);wr.writerow(['source_frame','global_frame','time_seconds','absolute_distance_m','extension_delta_from_frame120_m'])
  for f in frames:wr.writerow([f,1800+f,75+(f-1)/24,ND[f-1],max(0,ND[f-1]-ND[119])])
report={'version':bpy.app.version_string,'frames':N,'first120_travel_error_m':max(abs(ND[i]-oldD[i]) for i in range(120)),'first120_foot_matrices':'Direct v009 copies, checked in independent validation','extension':{'first_new_global':1921,'last_global':1968,'boundary_global':1969,'fps':24,'speed_mps':.288,'increment_per_frame_m':.012,'absolute_at1920_m':oldD[-1],'absolute_at1968_m':ND[-1],'overlap_frame':1920},'events':{w+'_'+side:steps for (w,side),steps in events.items()},'head':'Original coherent right profile retained. No backward turn.','polish':'Independent early balance gestures, short compression/torso lag, wrist bend limit, softer sleeve/forearm curves. Light touch retained; no load bearing.','protected':'Only new v010 folder written.'}
(P/'evidence/build_report.json').write_text(json.dumps(report,indent=2));(P/'evidence/authored_poses.json').write_text(json.dumps({w:{str(f):{n:[list(v) for v in m] for n,m in poses[w][f].items()} for f in [25,33,37,45,53,69,119,120,121,122,128,134,142,148,152,160,166,168]} for w in rigs},indent=2));print('V010_BUILT',json.dumps(report),flush=True)
