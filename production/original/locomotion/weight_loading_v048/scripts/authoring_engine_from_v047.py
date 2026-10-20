"""Purposeful ordinary planar walk. Preserve v046 art and age-ten rest anatomy."""
import bpy,math,json,hashlib,ast
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];BASE=ROOT/'locomotion/painted_outfit_restoration_v046';SRC=BASE/'native/WTSC_Age10_Painted_Outfit_Restoration_v046.blend';SOURCE_SHA=hashlib.sha256(SRC.read_bytes()).hexdigest();assert SOURCE_SHA=='e993540280bc60ff5fcc1dafe316f7c8457c5c8750a1110b8f6e307a865d005d';bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False,use_scripts=False);S=bpy.data.scenes['V046 | AGE10 BONES | restored painted clothing'];bpy.context.window.scene=S;S.name='V047 | STEADY ORDINARY WALK | no stumble baseline';master=bpy.data.collections['V046 | AGE10 PAIR | restored painted outfits'];master.name='V047 | AGE10 PAIR | steady ordinary walk';RIGS={w:bpy.data.objects['V044 '+w+' | estimated joint centres'] for w in ['BOY','GIRL']};ART=bpy.data.collections['V044 | age10 editable profile anatomy'];C=bpy.data.collections['V046 | restored original painted wardrobe'];root=bpy.data.objects['V045 | shared travel | new stride90percent'];root.name='V047 | shared travel | steady .73125mps'
PERIOD=32.;STRIDE=.780;SPEED=STRIDE*30/PERIOD;STANCE=18.8;PHASE={'BOY':0.,'GIRL':2.};TARGET=json.loads((ROOT/'locomotion/age10_proportion_candidate_v044/evidence/STATIC_SCALE_BUILD.json').read_text())['candidate_measurements']
anatomy={w:{b.name:{'head':list(b.head_local),'tail':list(b.tail_local),'length':b.length} for b in r.data.bones} for w,r in RIGS.items()}
def D(f):return STRIDE*(f-1)/PERIOD
def ease5(u):u=max(0,min(1,u));return u*u*u*(10+u*(-15+6*u))
def ease3(u):u=max(0,min(1,u));return u*u*(3-2*u)
def rot(a):return Matrix.Rotation(-a,4,'Y')
FOOT={}
for who,r in RIGS.items():
 b=next(o for o in ART.objects if o.parent==r and o.get('proportion_role')=='boot' and o.name.endswith('near'));off=[Vector((p.co.x,0,p.co.z-TARGET[who]['estimated_ankle_joint_z_m'])) for p in b.data.vertices];z=min(p.z for p in off);heel=min(p.x for p in off if p.z<=z+.000001);FOOT[who]={'offsets':off,'heel':heel}
def angle(q):
 if q<3:return math.radians(8)*(1-ease5(q/3))
 if q<13.5:return 0.
 return -math.radians(18)*ease5((q-13.5)/(STANCE-13.5))
def support_geometry(who,beta):
 Q=[rot(beta).to_3x3()@p for p in FOOT[who]['offsets']];z=min(p.z for p in Q);inds=[i for i,p in enumerate(Q) if p.z<=z+1e-7];p=sum((Q[i] for i in inds),Vector())/len(inds);flatx=sum(FOOT[who]['offsets'][i].x for i in inds)/len(inds);return z,p,flatx,inds
def stance(g,who,side,q=None):
 start=1. if side=='near' else 17.;q=(g-start)%PERIOD if q is None else q;c=g-q;beta=angle(q);z,p,flatx,inds=support_geometry(who,beta);heelworld=D(c)+.20+FOOT[who]['heel'];xworld=heelworld+(flatx-FOOT[who]['heel']);a=Vector((xworld-p.x-D(g),0,-z));return a,beta,{'stance':True,'contact_start':c,'support_indices':inds,'expected_support_x_plus_D':xworld,'phase_frame':q}
def foot(g,who,side):
 start=1. if side=='near' else 17.;q=(g-start)%PERIOD;c=g-q
 if q<=STANCE+1e-8:return stance(g,who,side,q)
 u=(q-STANCE)/(PERIOD-STANCE);a0=stance(c+STANCE,who,side,STANCE)[0];a1=stance(c+PERIOD,who,side,0)[0];duration=PERIOD-STANCE;velocity=-STRIDE/PERIOD
 # Zero world velocity at both contacts; decisive early swing avoids the old
 # slow backward hold followed by a late catch-up. Local cubic is C1 at entry.
 x=a0.x+velocity*duration*u+(a1.x-a0.x-velocity*duration)*ease3(u)
 beta=math.radians(-18+22*ease5(u/.45)) if u<.45 else math.radians(4+4*ease5((u-.45)/.55));z=support_geometry(who,beta)[0];clearance=.045*(ease3(u/.36) if u<=.36 else 1-ease3((u-.36)/.64))
 return Vector((x,0,clearance-z)),beta,{'stance':False,'phase_frame':q,'swing_u':u,'authored_clearance_m':clearance}
def ik(H,A,l1,l2):
 delta=A-H;distance=delta.length;assert distance<l1+l2-.00005,(distance,l1+l2,H[:],A[:]);U=delta/distance;x=(l1*l1-l2*l2+distance*distance)/(2*distance);height=math.sqrt(max(0,l1*l1-x*x));return H+U*x+Vector((-U.z,0,U.x))*height
lastQ={}
def setbone(r,n,a,b,f):
 rb=r.data.bones[n];old=(rb.tail_local-rb.head_local).normalized();new=(b-a).normalized();Q=old.rotation_difference(new);pb=r.pose.bones[n];pb.rotation_mode='QUATERNION';pb.matrix=Matrix.Translation(a)@Q.to_matrix().to_4x4()@rb.matrix_local.to_3x3().to_4x4();key=(r.name,n)
 if key in lastQ and pb.rotation_quaternion.dot(lastQ[key])<0:pb.rotation_quaternion.negate()
 lastQ[key]=pb.rotation_quaternion.copy()
 for prop in ['location','rotation_quaternion','scale']:pb.keyframe_insert(prop,frame=f)
def axis(deg):a=math.radians(deg);return Vector((math.sin(a),0,-math.cos(a)))
for r in RIGS.values():r.animation_data_clear()
records=[]
for i in range(129):
 f=1+i/4;S.frame_set(int(f),subframe=f-int(f))
 for who,r in RIGS.items():
  g=f+PHASE[who];phi=math.tau*(g-1)/PERIOD;t=TARGET[who];hip=Vector((.0015*math.sin(2*phi),0,t['estimated_hip_joint_z_m']-.032+.026*math.sin(phi)**2));pelvis_dir=Vector((math.sin(math.radians(.25*math.sin(2*phi+.2))),0,math.cos(math.radians(.25*math.sin(2*phi+.2)))));lean=(1.8 if who=='BOY' else 2.2)+.35*math.sin(2*phi+.2);chest_dir=Vector((math.sin(math.radians(lean)),0,math.cos(math.radians(lean))));waist=hip+pelvis_dir*r.data.bones['pelvis'].length;shoulder=waist+chest_dir*r.data.bones['chest'].length;headbase=shoulder+chest_dir*(r.data.bones['head'].head_local.z-t['estimated_shoulder_joint_z_m']);headangle=(1.0 if who=='BOY' else 1.3)+.15*math.sin(2*phi+.1);head_dir=Vector((math.sin(math.radians(headangle)),0,math.cos(math.radians(headangle))));setbone(r,'pelvis',hip,waist,f);setbone(r,'chest',waist,shoulder,f);setbone(r,'head',headbase,headbase+head_dir*t['vertical_head_m'],f)
  feet={}
  for side in ['near','far']:
   ankle,beta,meta=foot(g,who,side);knee=ik(hip,ankle,r.data.bones['thigh_'+side].length,r.data.bones['shin_'+side].length);setbone(r,'thigh_'+side,hip,knee,f);setbone(r,'shin_'+side,knee,ankle,f);rb=r.data.bones['foot_'+side];setbone(r,'foot_'+side,ankle,ankle+rot(beta).to_3x3()@(rb.tail_local-rb.head_local),f);feet[side]={'ankle':list(ankle),'beta_degrees':math.degrees(beta),**meta}
   sign=1 if side=='near' else -1
   if who=='BOY':upper=-sign*12*math.cos(phi-.10);elbow_flex=11+2*math.sin(phi-.3);fore=upper+elbow_flex;hand=fore-4+1.2*math.sin(phi-.4)
   else:upper=(-4 if side=='near' else 0)-sign*(9 if side=='near' else 11)*math.cos(phi-.15);fore=upper+(13 if side=='near' else 10)+1.5*math.sin(phi-.4);hand=fore-4+1*math.sin(phi-.6)
   elbow=shoulder+axis(upper)*r.data.bones['upper_arm_'+side].length;wrist=elbow+axis(fore)*r.data.bones['forearm_'+side].length;setbone(r,'upper_arm_'+side,shoulder,elbow,f);setbone(r,'forearm_'+side,elbow,wrist,f);setbone(r,'hand_'+side,wrist,wrist+axis(hand)*.13,f)
  records.append({'frame':f,'character':who,'hip':list(hip),'torso_lean_degrees':lean,'head_lean_degrees':headangle,'feet':feet})
for who,r in RIGS.items():
 a=r.animation_data.action;a.name='V047 '+who+' | steady ordinary walk |32frames'
 for l in a.layers:
  for st in l.strips:
   for bag in st.channelbags:
    for fc in bag.fcurves:
     for k in fc.keyframe_points:k.interpolation='LINEAR'
     cy=fc.modifiers.new('CYCLES');cy.mode_before=cy.mode_after='REPEAT'
root.animation_data_clear();S.camera.animation_data_clear()
for f in [1,257]:root.location.x=D(f);root.keyframe_insert('location',index=0,frame=f);S.camera.location=(D(f),-10,.80);S.camera.keyframe_insert('location',frame=f)
for o in [root,S.camera]:
 for l in o.animation_data.action.layers:
  for st in l.strips:
   for bag in st.channelbags:
    for fc in bag.fcurves:
     fc.extrapolation='LINEAR'
     for k in fc.keyframe_points:k.interpolation='LINEAR'
root['stride_m']=STRIDE;root['period_frames']=PERIOD;root['fps']=30;root['phase_girl_frames']=PHASE['GIRL'];root['source_distance_formula']='D(F)=.78*(F-1)/32 metres';root['source_clock']='F=1+(G-G0)*30/24'
# Rebuild ALL cached limb clothing from the new actual bones; keep their
# v046 original meshes' materials, image pixels, UV registrations and depths.
tree=ast.parse((BASE/'scripts/build_outfits.py').read_text());tree.body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['interp','smooth','rounded']];exec(compile(tree,'v046_clothing_geometry_functions','exec'),globals());CACHE={w:{} for w in RIGS}
for i in range(129):
 f=1+i/4;S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
 for who,r in RIGS.items():e=r.evaluated_get(dg);CACHE[who][f]={n:{'head':b.head.copy(),'tail':b.tail.copy(),'matrix':b.matrix.copy()} for n,b in e.pose.bones.items()}
def cache(o,poses):
 o.shape_key_clear();o.data.vertices.foreach_set('co',[c for p in poses[1.] for c in p]);o.shape_key_add(name='Basis | steady actual-bone F1')
 for i in range(1,128):
  f=1+i/4;k=o.shape_key_add(name='V047 actual bones F%05.2f'%f);k.data.foreach_set('co',[c for p in poses[f] for c in p])
  for at in [1.,max(1.,f-.25),f,min(33.,f+.25),33.]:k.value=float(at==f);k.keyframe_insert('value',frame=at)
 for l in o.data.shape_keys.animation_data.action.layers:
  for st in l.strips:
   for bag in st.channelbags:
    for fc in bag.fcurves:
     for k in fc.keyframe_points:k.interpolation='LINEAR'
     cy=fc.modifiers.new('CYCLES');cy.mode_before=cy.mode_after='REPEAT'
for who,r in RIGS.items():
 for side in ['near','far']:
  for kind in ['sleeve','leg']:
   o=next(o for o in C.objects if o.parent==r and o.get('wardrobe_role')==kind and o.name.endswith(side));n1=('upper_arm_' if kind=='sleeve' else 'thigh_')+side;n2=('forearm_' if kind=='sleeve' else 'shin_')+side;l1=r.data.bones[n1].length;total=l1+r.data.bones[n2].length;start=-.008 if kind=='sleeve' else -.025;end=l1+.027 if kind=='sleeve' else total-.030;rounding=.018 if kind=='sleeve' else .022;rows=49 if kind=='sleeve' else 65;poses={}
   def radius(t):
    if kind=='sleeve':return interp(t,[(0,.038),(.12,.049),(.5,.045),(.85,.034),(1,.041)])
    return interp(t,[(0,.060),(.13,.063),(.4,.052),(.56,.043),(.77,.044),(.92,.034),(1,.040)]) if who=='BOY' else interp(t,[(0,.043),(.45,.036),(.56,.031),(.78,.033),(1,.024)])
   for f,pose in CACHE[who].items():
    H=pose[n1]['head'];K=pose[n1]['tail'];A=pose[n2]['tail'];V=[]
    for row in range(rows):
     t=row/(rows-1);d=start+(end-start)*t;center,tangent=rounded(H,K,A,l1,d,rounding);normal=Vector((-tangent.z,0,tangent.x))
     for col in range(9):
      s=col/8;p=center+normal*((s*2-1)*radius(t));p.y=0
      if kind=='leg':w=smooth((d-(total-.095))/.065);rest=Vector(((s*2-1)*radius(t),0,r.data.bones[n1].head_local.z-d));bound=pose['foot_'+side]['matrix']@r.data.bones['foot_'+side].matrix_local.inverted()@rest;p=p.lerp(bound,w);p.y=0
      V.append(p)
    poses[f]=V
   cache(o,poses);o['V047_cache']='Regenerated from new32-frame actual-bone walk. Original v046 painting and object-depth origins preserved.'
# Extend the fixed review ground for the longer normal-speed test.
for o in bpy.data.collections['V045 | review-only fixed metric ground'].objects:o.hide_render=True
review=bpy.data.collections.new('V047 | review-only fixed ground');S.collection.children.link(review)
def line(n,a,b,width,mat):
 a=Vector(a);b=Vector(b);d=(b-a).normalized();s=Vector((-d.z,0,d.x))*width/2;me=bpy.data.meshes.new(n);me.from_pydata([a-s,b-s,b+s,a+s],[],[(0,1,2,3)]);me.materials.append(mat);ob=bpy.data.objects.new(n,me);review.objects.link(ob)
for i in range(-20,121):line('V047 fixed10cm X'+str(i),(i*.1,.2,-.1),(i*.1,.2,1.75),.00035,bpy.data.materials['V044 quiet metric grid'])
for i in range(18):line('V047 fixed height Z'+str(i),(-2,.2,i*.1),(12,.2,i*.1),.00035,bpy.data.materials['V044 quiet metric grid'])
line('V047 legible fixed ground',(-2,-.18,0),(12,-.18,0),.003,bpy.data.materials['V044 guide ink'])
for i in range(-5,31):line('V047 fixed40cm contact tick'+str(i),(i*.4,-.17,-.025),(i*.4,-.17,.028),.0015,bpy.data.materials['V044 guide ink'])
for who,r in RIGS.items():
 for b in r.data.bones:assert list(b.head_local)==anatomy[who][b.name]['head'] and list(b.tail_local)==anatomy[who][b.name]['tail']
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==SOURCE_SHA
S.frame_start=1;S.frame_end=257;S.render.fps=30;S['V047_status']='Ordinary steady baseline candidate responding to drunk-stumbling feedback. No new cloth/braid embellishment. v046 paintings and age-ten rest bones retained; new even32-frame gait, quiet torso/pelvis/head, smaller foot roll and coherent reciprocal arms.';S['V047_contract']='D(F)=.78*(F-1)/32 metres at30fps; .73125m/s; F=1+(G-G0)*30/24 at24fps. 25.6 production-frame cycle; do not round.';S.frame_set(1);bpy.context.view_layer.update();report={'source':str(SRC),'source_sha256':SOURCE_SHA,'source_unchanged':True,'period_source_frames':PERIOD,'stride_m':STRIDE,'speed_m_s':SPEED,'half_step_source_frames':16,'stance_source_frames':STANCE,'phase_girl_source_frames':PHASE['GIRL'],'anatomy':anatomy,'paint_images_materials_uvs_changed':False,'new_secondary_motion':False,'authored_body_parameters':{'hip_fore_aft_peak_to_peak_m':.003,'hip_vertical_peak_to_peak_m':.026,'torso_lean_degrees_boy':[1.45,2.15],'torso_lean_degrees_girl':[1.85,2.55],'head_pitch_peak_to_peak_degrees':.30,'heel_strike_toe_up_degrees':8,'toe_off_degrees':-18,'swing_max_authored_sole_clearance_m':.045},'poses':records,'technical_scope':'No COM or physical balance simulation is claimed. Visual weight transfer must be judged from actual normal-speed render.'};(P/'evidence/STEADY_WALK_BUILD.json').write_text(json.dumps(report,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Steady_Ordinary_Walk_v047.blend'),compress=True);print('V047_STEADY_WALK_NATIVE_SAVED',flush=True)
