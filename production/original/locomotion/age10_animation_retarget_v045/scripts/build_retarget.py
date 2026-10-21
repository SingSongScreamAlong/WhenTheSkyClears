"""Stage 2: retarget preferred timing to the separately established age-ten bodies.
New native only. Contact is rebuilt for shorter boots and a shorter stride.
"""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];STATIC=ROOT/'locomotion/age10_proportion_candidate_v044/native/WTSC_Age10_Static_Proportion_Candidate_v044.blend';STATIC_HASH=hashlib.sha256(STATIC.read_bytes()).hexdigest();A=json.loads((P/'evidence/PREFERRED_EIGHTH_FRAME_REFERENCE.json').read_text());ROWS=A['samples'];TARGET=json.loads((ROOT/'locomotion/age10_proportion_candidate_v044/evidence/STATIC_SCALE_BUILD.json').read_text())['candidate_measurements'];bpy.ops.wm.open_mainfile(filepath=str(STATIC),load_ui=False,use_scripts=False);S=bpy.data.scenes['V044 | AGE TEN | STATIC SCALE FIRST'];bpy.context.window.scene=S;S.name='V045 | AGE TEN | RETARGET AFTER STATIC SCALE';S.frame_start=1;S.frame_end=94;S.render.fps=30;S.render.resolution_x=1280;S.render.resolution_y=720;S.render.resolution_percentage=100;S.render.dither_intensity=0;S.eevee.taa_render_samples=32;S.render.threads_mode='FIXED';S.render.threads=2
OLD_STRIDE=A['old_stride_m'];STEP_RATIO=.90;STRIDE=OLD_STRIDE*STEP_RATIO;PERIOD=31.;SPEED=STRIDE*30/PERIOD
RIGS={w:bpy.data.objects['V044 '+w+' | estimated joint centres'] for w in ['BOY','GIRL']};ART=bpy.data.collections['V044 | age10 editable profile anatomy'];master=bpy.data.collections.new('V045 | AGE TEN WALKING PAIR | retarget proof');S.collection.children.link(master);S.collection.children.unlink(ART);master.children.link(ART);travel=bpy.data.objects.new('V045 | shared travel | new stride90percent',None);master.objects.link(travel);travel['stride_m']=STRIDE;travel['period_frames']=31.;travel['fps']=30;travel['source_clock']='F=1+(G-G0)*30/24 for production24fps';travel['source_distance_formula']='D(F)=stride_m*(F-1)/31';travel['phase_girl_frames']=3.5
for who,r in RIGS.items():r.parent=travel;r.location.x=-.4 if who=='BOY' else .4;r.animation_data_clear();r['motion_stage']='v045 retarget after separate v044 static scale checkpoint; actual proof range1..94; body cycles repeat31frames.'
def overlap_piece(who,side,kind):
 r=RIGS[who];t=TARGET[who];depth=(-.044 if side=='near' else .036)
 if kind=='ankle':
  depth=(-.035 if side=='near' else .045);za=t['estimated_ankle_joint_z_m'];rows=[(za+.065,.023),(za+.044,.028),(za+.023,.031)];bones=['shin_'+side,'foot_'+side];source=next(o for o in ART.objects if o.parent==r and o.get('proportion_role')=='boot' and o.name.endswith(side));name='boot shaft overlap'
 else:
  zw=t['estimated_shoulder_joint_z_m']-t['upper_arm_joint_length_m']-t['forearm_joint_length_m'];rows=[(zw+.014,.014),(zw,.015),(zw-.014,.014)];bones=['forearm_'+side,'hand_'+side];source=next(o for o in ART.objects if o.parent==r and o.get('proportion_role')=='forearm' and o.name.endswith(side));name='wrist paint overlap'
 verts=[(sign*w,depth,z) for z,w in rows for sign in [-1,1]];me=bpy.data.meshes.new('V045 '+who+' '+name+' '+side);me.from_pydata(verts,[],[(0,1,3,2),(2,3,5,4)]);me.update()
 for m in source.data.materials:me.materials.append(m)
 # Interior pigment samples from the existing painted material. The connector
 # sits behind original art and fills the exposed join; no raster is repainted.
 for layer in source.data.uv_layers:
  uv=me.uv_layers.new(name=layer.name);values=[u.uv for u in layer.data];mean=sum(values,Vector((0,0)))/len(values)
  for q in uv.data:q.uv=mean
 ob=bpy.data.objects.new('V045 '+who+' | '+name+' '+side,me);ART.objects.link(ob);ob.parent=r;ob['proportion_role']=name;ob['scope']='Animated overlap only; original static anatomy and artwork remain unchanged.'
 for n in bones:ob.vertex_groups.new(name=n)
 for row in range(3):
  for j in range(2):
   ob.vertex_groups[bones[0]].add([row*2+j],1-row/2,'REPLACE');ob.vertex_groups[bones[1]].add([row*2+j],row/2,'REPLACE')
 mod=ob.modifiers.new('V045 continuous attachment','ARMATURE');mod.object=r
for who in RIGS:
 for side in ['near','far']:
  for kind in ['ankle','wrist']:overlap_piece(who,side,kind)
for o in bpy.data.collections['V044 | dimension grid and surface landmarks'].objects:
 o.hide_render=True;o.hide_viewport=True
review=bpy.data.collections.new('V045 | review-only fixed metric ground');S.collection.children.link(review)
def review_line(n,a,b,width,mat):
 a=Vector(a);b=Vector(b);delta=(b-a).normalized();side=Vector((-delta.z,0,delta.x))*width/2;me=bpy.data.meshes.new(n);me.from_pydata([a-side,b-side,b+side,a+side],[],[(0,1,2,3)]);me.materials.append(mat);ob=bpy.data.objects.new(n,me);review.objects.link(ob)
for i in range(-20,61):review_line('V045 fixed ground grid X'+str(i),(i*.1,.2,-.10),(i*.1,.2,1.75),.00035,bpy.data.materials['V044 quiet metric grid'])
for i in range(18):review_line('V045 fixed height grid Z'+str(i),(-2,.2,i*.1),(6,.2,i*.1),.00035,bpy.data.materials['V044 quiet metric grid'])
review_line('V045 outside-sole ground line',(-2,-.18,0),(6,-.18,0),.002,bpy.data.materials['V044 guide ink'])
for c in [bpy.data.collections['V044 | before F1 source painting snapshots'],bpy.data.collections['V044 | front CONSTRUCTION ONLY | no front art available']]:
 for o in c.objects:o.hide_render=True;o.hide_viewport=True
def D(f):return STRIDE*(f-1)/PERIOD
def ref(f):
 f=1+(f-1)%PERIOD;z=(f-1)*8;i=min(247,int(z));a=z-i;ra,rb=ROWS[i],ROWS[i+1]
 def mix(x,y):
  if isinstance(x,list):return [mix(u,v) for u,v in zip(x,y)]
  if isinstance(x,dict):return {k:mix(x[k],y[k]) for k in x if k!='frame'}
  return x+(y-x)*a
 return mix(ra,rb)
def v(x):return Vector(x)
def unit2(a):q=Vector((a.x,0,a.z));return q.normalized()
def rot(a):return Matrix.Rotation(-a,4,'Y')
def smooth(u):u=max(0,min(1,u));return u*u*u*(u*(u*6-15)+10)
FOOT={}
for who,r in RIGS.items():
 b=next(o for o in ART.objects if o.parent==r and o.get('proportion_role')=='boot' and o.name.endswith('near'));off=[p.co-Vector((0,0,TARGET[who]['estimated_ankle_joint_z_m'])) for p in b.data.vertices];z=min(p.z for p in off);heel=min(p.x for p in off if p.z<=z+.000001);FOOT[who]={'offsets':off,'heel':heel}
def stance(g,who,side):
 start=1. if side=='near' else 17.;k=math.floor((g-start)/31);c=start+k*31;theta=ref(g)['boots'][side]['angle_xz'];R=rot(theta);offsets=FOOT[who]['offsets'];q=[R.to_3x3()@p for p in offsets];z=min(p.z for p in q);inds=[i for i,p in enumerate(q) if p.z<=z+.0000001];p=sum((q[i] for i in inds),Vector())/len(inds);flatx=sum(offsets[i].x for i in inds)/len(inds);H=ref(start)['boots'][side]['support_x_min']*STEP_RATIO+D(start)+k*STRIDE;xworld=H+(flatx-FOOT[who]['heel']);ank=Vector((xworld-p.x-D(g),0,-z));return ank,theta,{'source_clock':g,'contact_start':c,'expected_support_x_plus_D':xworld,'support_indices':inds,'stance':True}
def foot(g,who,side):
 start=1. if side=='near' else 17.;q=(g-start)%31;c=g-q;end=18.5 if side=='near' else 19.25
 if q<=end+.0000001:return stance(g,who,side)
 r=ref(g)['boots'][side];theta=r['angle_xz'];a0=stance(c+end,who,side)[0];a1=stance(c+31,who,side)[0];old0=ref(c+end)['boots'][side]['origin'][0]*STEP_RATIO;old1=ref(c+31)['boots'][side]['origin'][0]*STEP_RATIO;u=smooth((q-end)/(31-end));x=r['origin'][0]*STEP_RATIO+(a0.x-old0)*(1-u)+(a1.x-old1)*u;off=[rot(theta).to_3x3()@p for p in FOOT[who]['offsets']];z=max(0,r['min_z'])-min(p.z for p in off);return Vector((x,0,z)),theta,{'source_clock':g,'stance':False}
def ik(H,A,l1,l2):
 delta=A-H;d=delta.length;assert d<l1+l2+.000001,(d,l1+l2);d=max(.00001,d);U=delta/d;x=(l1*l1-l2*l2+d*d)/(2*d);h=math.sqrt(max(0,l1*l1-x*x));perp=Vector((-U.z,0,U.x));return H+U*x+perp*h
lastQ={};first={};poseRecords=[]
def setbone(r,n,a,b,f):
 rb=r.data.bones[n];old=unit2(rb.tail_local-rb.head_local);new=unit2(b-a);Q=old.rotation_difference(new);pb=r.pose.bones[n];pb.rotation_mode='QUATERNION';pb.matrix=Matrix.Translation(a)@Q.to_matrix().to_4x4()@rb.matrix_local.to_3x3().to_4x4();key=(r.name,n)
 if key in lastQ and pb.rotation_quaternion.dot(lastQ[key])<0:pb.rotation_quaternion.negate()
 lastQ[key]=pb.rotation_quaternion.copy()
 for p in ['location','rotation_quaternion','scale']:pb.keyframe_insert(p,frame=f)
 return pb.matrix.copy()
for i in range(125):
 f=1+i/4;S.frame_set(int(f),subframe=f-int(f))
 for who,r in RIGS.items():
  t=TARGET[who];phase=0 if who=='BOY' else 3.5;g=f+phase;rr=ref(g);feet={s:foot(g,who,s) for s in ['near','far']};hip0=t['estimated_hip_joint_z_m'];hipx=rr['bones']['pelvis']['head'][0]*STEP_RATIO;hipz=rr['bones']['pelvis']['head'][2]+(.132 if who=='BOY' else .126);l1=r.data.bones['thigh_near'].length;l2=r.data.bones['shin_near'].length;cap=min(a[0].z+math.sqrt(max(.001,(l1+l2-.002)**2-(a[0].x-hipx)**2)) for a in feet.values());hipz=.5*(hipz+cap-math.sqrt((hipz-cap)**2+.004**2));hip=Vector((hipx,0,hipz));chestD=unit2(v(rr['bones']['chest']['tail'])-v(rr['bones']['chest']['head']));pelvisD=unit2(v(rr['bones']['pelvis']['tail'])-v(rr['bones']['pelvis']['head']))
  if who=='GIRL':chestD=rot(math.radians(2.)).to_3x3()@chestD
  waist=hip+pelvisD*r.data.bones['pelvis'].length;shoulder=waist+chestD*r.data.bones['chest'].length;headBase=shoulder+chestD*(r.data.bones['head'].head_local.z-t['estimated_shoulder_joint_z_m']);headD=unit2(v(rr['bones']['head']['tail'])-v(rr['bones']['head']['head']));setbone(r,'pelvis',hip,waist,f);setbone(r,'chest',waist,shoulder,f);setbone(r,'head',headBase,headBase+headD*t['vertical_head_m'],f)
  for side in ['near','far']:
   ank,theta,_=feet[side];knee=ik(hip,ank,r.data.bones['thigh_'+side].length,r.data.bones['shin_'+side].length);setbone(r,'thigh_'+side,hip,knee,f);setbone(r,'shin_'+side,knee,ank,f);rb=r.data.bones['foot_'+side];ft=ank+rot(theta).to_3x3()@(rb.tail_local-rb.head_local);setbone(r,'foot_'+side,ank,ft,f)
   uD=unit2(v(rr['bones']['upper_arm_'+side]['tail'])-v(rr['bones']['upper_arm_'+side]['head']));fore=ref(g-(.75 if who=='GIRL' else 0))['bones']['forearm_'+side];fD=unit2(v(fore['tail'])-v(fore['head']));hD=unit2(v(rr['bones']['hand_'+side]['tail'])-v(rr['bones']['hand_'+side]['head']))
   if who=='GIRL':
    phi=math.tau*(f-1)/31
    # She watches the route and leaves a restrained hand back toward the boy.
    # The other arm balances forward. These are authored intentions, not a
    # phase-shifted copy of the boy's arm curves. No clasp is claimed.
    angles=([-18+2.0*math.sin(phi+.3),-54+2.5*math.sin(phi-.5),-48+2*math.sin(phi-.9)] if side=='near' else [17+4*math.sin(phi+1.0),32+3*math.sin(phi+.2),23+2*math.sin(phi-.3)])
    uD,fD,hD=[Vector((math.sin(math.radians(a)),0,-math.cos(math.radians(a)))) for a in angles]
   elbow=shoulder+uD*r.data.bones['upper_arm_'+side].length;wrist=elbow+fD*r.data.bones['forearm_'+side].length;setbone(r,'upper_arm_'+side,shoulder,elbow,f);setbone(r,'forearm_'+side,elbow,wrist,f);setbone(r,'hand_'+side,wrist,wrist+hD*.13,f)
  if i==0:first[who]={n:pb.matrix.copy() for n,pb in r.pose.bones.items()}
  looperr=max(max(abs(pb.matrix[j][k]-first[who][n][j][k]) for j in range(4) for k in range(4)) for n,pb in r.pose.bones.items()) if i==124 else None
  poseRecords.append({'frame':f,'character':who,'hip':list(hip),'source_phase_frames':phase,'ankles':{s:list(a[0]) for s,a in feet.items()},'closing_pose_matrix_max_error':looperr})
 for r in RIGS.values():
  if r.animation_data and r.animation_data.action:r.animation_data.action.name='V045 '+('BOY' if r==RIGS['BOY'] else 'GIRL')+' | age10 retarget |31frameclock'
for r in RIGS.values():
 for lay in r.animation_data.action.layers:
  for st in lay.strips:
   for bag in st.channelbags:
    for fc in bag.fcurves:
     fc.extrapolation='LINEAR'
     for k in fc.keyframe_points:k.interpolation='LINEAR'
     cy=fc.modifiers.new('CYCLES');cy.mode_before=cy.mode_after='REPEAT'
for f in [1,94]:
 travel.location.x=D(f);travel.keyframe_insert('location',index=0,frame=f);S.camera.location=(D(f),-10,.80);S.camera.keyframe_insert('location',frame=f)
for ob in [travel,S.camera]:
 for l in ob.animation_data.action.layers:
  for st in l.strips:
   for bag in st.channelbags:
    for fc in bag.fcurves:
     fc.extrapolation='LINEAR'
     for k in fc.keyframe_points:k.interpolation='LINEAR'
S.camera.data.ortho_scale=3.25;S['stage']='STAGE2 ANIMATION RETARGET AFTER SEPARATE AGE10 STATIC CHECKPOINT. Unapproved movement proof, not recovery acting.';S['travel_contract']=f'D(F)={STRIDE:.17g}*(F-1)/31 metres;30fps.24fps:G maps F=1+(G-G0)*30/24. Root travel is already active in this proof; do not add it twice.';S['artistic_limit']='Girl retains older charcoal painting. Her restrained backward offered hand and forward balancing arm are authored independently; shared gait timing alone is not acting. No load-bearing clasp, crouch-to-walk restart or full-trailer integration is authored here.'
ns=bpy.data.texts.new('READ FIRST v045 | after static scale');ns.write(S['stage']+'\n'+S['travel_contract']+'\n'+S['artistic_limit']);S.frame_set(1);bpy.context.view_layer.update();assert hashlib.sha256(STATIC.read_bytes()).hexdigest()==STATIC_HASH
out={'stage':S['stage'],'static_source_sha256':STATIC_HASH,'static_source_preserved':True,'old_stride_m':OLD_STRIDE,'stride_ratio':STEP_RATIO,'new_stride_m':STRIDE,'new_speed_m_per_second':SPEED,'period_frames':31,'fps':30,'girl_phase_lead_frames':3.5,'distance_formula':S['travel_contract'],'pose_samples_per_cycle':125,'poses':poseRecords,'artistic_limit':S['artistic_limit']};(P/'evidence/RETARGET_BUILD.json').write_text(json.dumps(out,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Age10_Walk_Retarget_Proof_v045.blend'),compress=True);print('AGE10_RETARGET_BUILT',STRIDE,SPEED,flush=True)
