"""Seven-second paired acting candidate, using only the existing painted assets."""
import bpy, math, json, hashlib, sys, importlib.util
from pathlib import Path
from mathutils import Vector, Matrix

R=Path(__file__).resolve().parents[3]; O=R/'work/first_danger_acting_v066'
SRC=R/'work/first_danger_conform_v065/native/WTSC_First_Danger_Conformed_v065f.blend'
NATIVE=O/'native/WTSC_First_Danger_Acting_v066.blend'
for d in ['native','evidence','renders','previews']:(O/d).mkdir(parents=True,exist_ok=True)
SOURCE_HASH=hashlib.sha256(SRC.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False,use_scripts=False)
S=bpy.data.scenes['WTSC_FIRST_DANGER_WORLD_v065'];bpy.context.window.scene=S
S.name='WTSC_FIRST_DANGER_ACTING_WORLD_v066'
RIGS={w:bpy.data.objects['V044 '+w+' | estimated joint centres'] for w in ['BOY','GIRL']}
ROOT=bpy.data.objects['V047 | shared travel | steady .73125mps']
G0,G1=913,1080
FRAMES=[G0+i*.5 for i in range((G1-G0)*2+1)]
spec=importlib.util.spec_from_file_location('existing_model_spec',R/'locomotion/connected_model_fit_v049/scripts/model_spec.py')
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)

def curves(block):
 ad=getattr(block,'animation_data',None)
 return [f for l in ad.action.layers for st in l.strips for bag in st.channelbags for f in bag.fcurves] if ad and ad.action else []
def sha_art():return {im.name:hashlib.sha256(im.packed_file.data).hexdigest() for im in bpy.data.images if im.packed_file}
def uv_signature():return {o.name:hashlib.sha256(repr([(u.name,[tuple(x.uv) for x in u.data]) for u in o.data.uv_layers]).encode()).hexdigest() for o in S.objects if o.type=='MESH'}
ART_BEFORE=sha_art();UV_BEFORE=uv_signature()
WORLD_OBJECTS={o.name:[list(v) for v in o.matrix_world] for o in S.objects if o.type=='MESH' and o.parent not in RIGS.values()}
CAMERA_ACTION=ROOT.animation_data.action.name

def clamp(x,a=0.,b=1.):return max(a,min(b,x))
def ease(x):x=clamp(x);return x*x*(3-2*x)
def interp(t,ks):
 if t<=ks[0][0]:return ks[0][1]
 if t>=ks[-1][0]:return ks[-1][1]
 for (a,x),(b,y) in zip(ks,ks[1:]):
  if a<=t<=b:return x+(y-x)*ease((t-a)/(b-a))
def cyclic(t,ks,period=16):
 t=t%period
 return interp(t,ks)
def axis(a,up=False):
 a=math.radians(a);return Vector((math.sin(a),0,math.cos(a) if up else -math.cos(a)))
def rotation(beta):return Matrix.Rotation(-beta,4,'Y').to_3x3()
def mat(r,n,a,b):
 rb=r.data.bones[n];q=(rb.tail_local-rb.head_local).normalized().rotation_difference((b-a).normalized())
 return Matrix.Translation(a)@q.to_matrix().to_4x4()@rb.matrix_local.to_3x3().to_4x4()
def ik(H,A,l1,l2,lower=False):
 d=A-H;length=d.length
 if length>=l1+l2-.00001:raise ValueError(('unreachable',length,l1+l2,list(H),list(A)))
 U=d/max(length,1e-9);x=(l1*l1-l2*l2+length*length)/(2*max(length,1e-9));h=math.sqrt(max(0,l1*l1-x*x));p=Vector((-U.z,0,U.x))
 a=H+U*x+p*h;b=H+U*x-p*h
 return (a if a.z<b.z else b) if lower else a

# Exact painted boot soles determine the ankle and contact height. The motion
# clock changes per child during the check; the stance anchor stays in world space.
FOOT={}
for w,r in RIGS.items():
 ob=next(o for o in S.objects if o.parent==r and o.get('proportion_role')=='boot' and o.name.endswith('near'))
 off=[Vector((v.co.x,0,v.co.z-r.data.bones['foot_near'].head_local.z)) for v in ob.data.vertices]
 z=min(p.z for p in off);heel=min(p.x for p in off if p.z<=z+1e-6)
 FOOT[w]={'offsets':off,'heel':heel}
def geom(w,beta):
 ps=[rotation(beta)@p for p in FOOT[w]['offsets']];z=min(p.z for p in ps);ids=[i for i,p in enumerate(ps) if p.z<=z+1e-7]
 p=sum((ps[i] for i in ids),Vector())/len(ids);flat=sum(FOOT[w]['offsets'][i].x for i in ids)/len(ids)
 return z,p,flat,ids
def D(f):return .78*(f-1)/32
def beta_at(q):
 if q<3:return math.radians(8)*(1-ease(q/3))
 if q<13.5:return 0.
 return -math.radians(18)*ease((q-13.5)/(18.8-13.5))
def stance(g,w,side,q=None):
 start=1 if side=='near' else 17;q=(g-start)%32 if q is None else q;c=g-q;beta=beta_at(q)
 z,p,flat,ids=geom(w,beta);heelworld=D(c)+.20+FOOT[w]['heel'];supportx=heelworld+(flat-FOOT[w]['heel'])
 return Vector((supportx-p.x-D(g),0,-z)),beta,{'stance':True,'contact_start':c,'phase':q,'support_x_plus_D':supportx,'support_indices':ids}
def foot(g,w,side):
 start=1 if side=='near' else 17;q=(g-start)%32;c=g-q
 if q<=18.8:return stance(g,w,side,q)
 u=(q-18.8)/(32-18.8);a=stance(c+18.8,w,side,18.8)[0];b=stance(c+32,w,side,0)[0]
 x=a.x-.78/32*(32-18.8)*u+(b.x-a.x+.78/32*(32-18.8))*ease(u)
 beta=math.radians(-18+22*ease(u/.45)) if u<.45 else math.radians(4+4*ease((u-.45)/.55))
 clearance=.05*(ease(u/.36) if u<=.36 else 1-ease((u-.36)/.64))
 return Vector((x,0,clearance-geom(w,beta)[0])),beta,{'stance':False,'phase':q,'clearance':clearance}

DELTA={
 'GIRL':[(913,0),(952,0),(958,-.065),(967,-.23),(976,-.25),(996,-.18),(1020,-.06),(1056,0),(1080,0)],
 'BOY':[(913,0),(958,0),(966,-.065),(976,-.14),(984,-.14),(1002,-.09),(1030,-.02),(1056,0),(1080,0)]}
# The flash occurs at G957. Girl notices first, boy reads her changed body and
# hand next. A checked supporting step precedes the offered hand and compression.
TRACKS={
 'GIRL':{
 'compress':[(913,0),(954,0),(960,.025),(970,.050),(985,.032),(1001,.045),(1016,.026),(1080,.026)],
 'chest':[(913,0),(954,0),(958,-8),(962,-5),(970,7),(982,15),(996,9),(1012,7),(1080,7)],
 'pelvis':[(913,0),(955,0),(962,-3),(975,5),(991,2),(1080,2)],
 'head':[(913,0),(954,0),(957,-13),(961,-10),(968,8),(977,16),(986,7),(1000,11),(1012,4),(1080,4)],
 'hipx':[(913,0),(954,0),(963,-.024),(975,.020),(992,.007),(1080,.007)]},
 'BOY':{
 'compress':[(913,0),(960,0),(967,.016),(978,.043),(991,.055),(1008,.031),(1080,.024)],
 'chest':[(913,0),(960,0),(965,-5),(972,5),(987,17),(1002,10),(1018,6),(1080,6)],
 'pelvis':[(913,0),(961,0),(969,-2),(981,6),(996,2),(1080,2)],
 'head':[(913,0),(960,0),(964,-9),(968,-6),(978,15),(989,18),(1004,7),(1020,3),(1080,3)],
 'hipx':[(913,0),(960,0),(970,-.018),(985,.020),(1004,.008),(1080,.008)]}}

for w,r in RIGS.items():
 r.animation_data_clear()
 for pb in r.pose.bones:
  for constraint in list(pb.constraints):pb.constraints.remove(constraint)
 r['V066_scope']='Fresh support, check, recoil, offer, receive, grip and cautious paired travel; existing painted assets.'
LAST={};CACHE={w:{} for w in RIGS};ROWS=[]
for g in FRAMES:
 S.frame_set(math.floor(g),subframe=g-math.floor(g));bpy.context.view_layer.update()
 allposes={};meta={};worlds={}
 for w,r in RIGS.items():
  delay=interp(g,DELTA[w]);r.location.x=(-.4 if w=='BOY' else .4)+delay;r.keyframe_insert('location',index=0,frame=g)
  f=1+(g-937)*1.25+delay*32/.78;phase=0 if w=='BOY' else 2;clock=f+phase;q=(clock-1)%16
  L=lambda n:interp(g,TRACKS[w][n]);feet={side:foot(clock,w,side) for side in ['near','far']}
  hip=Vector((cyclic(q,[(0,0),(3,.012),(8,-.008),(12,.016),(16,0)])+L('hipx'),0,r.data.bones['pelvis'].head_local.z-.043+cyclic(q,[(0,.005),(3,-.016),(8,.015),(12,.008),(16,.005)])-L('compress')))
  for side,(ankle,_,_) in feet.items():
   l=r.data.bones['thigh_'+side].length+r.data.bones['shin_'+side].length-.003
   dx=ankle.x-hip.x
   hip.z=min(hip.z,ankle.z+math.sqrt(max(.0001,l*l-dx*dx)))
  pa=cyclic(q,[(0,-1.5),(3,3.5),(8,.4),(12,-2.5),(16,-1.5)])+L('pelvis')
  ca=(1.5 if w=='BOY' else 2)+cyclic(q,[(0,0),(3,5.5),(8,-1.5),(12,1),(16,0)])+L('chest')
  waist=hip+axis(pa,True)*r.data.bones['pelvis'].length
  shoulder=waist+axis(ca,True)*r.data.bones['chest'].length
  hb=shoulder+axis(ca,True)*(r.data.bones['head'].head_local.z-r.data.bones['chest'].tail_local.z)
  ha=1+cyclic(q,[(0,0),(4,-1.5),(9,1.3),(13,.2),(16,0)])+L('head')
  pose={'pelvis':(hip,waist),'chest':(waist,shoulder),'head':(hb,hb+axis(ha,True)*r.data.bones['head'].length)}
  phi=math.tau*(clock-1)/32
  for side,(ankle,beta,fm) in feet.items():
   knee=ik(hip,ankle,r.data.bones['thigh_'+side].length,r.data.bones['shin_'+side].length)
   pose['thigh_'+side]=(hip,knee);pose['shin_'+side]=(knee,ankle)
   rb=r.data.bones['foot_'+side];pose['foot_'+side]=(ankle,ankle+rotation(beta)@(rb.tail_local-rb.head_local))
   sign=1 if side=='near' else -1
   upper=-sign*(14 if w=='BOY' else 11)*math.cos(phi-.2)+(ca-3)*.22
   elbowflex=12+5*math.sin(phi+(0 if side=='near' else 1.1))
   protect=interp(g,[(913,0),(958 if w=='GIRL' else 965,0),(975,1),(992,.7),(1016,.3),(1080,.3)])
   if side=='far':upper+=protect*(20 if w=='GIRL' else 17);elbowflex+=protect*28
   E=shoulder+axis(upper)*r.data.bones['upper_arm_'+side].length
   W=E+axis(upper+elbowflex)*r.data.bones['forearm_'+side].length
   pose['upper_arm_'+side]=(shoulder,E);pose['forearm_'+side]=(E,W);pose['hand_'+side]=(W,W+axis(upper+elbowflex-4)*r.data.bones['hand_'+side].length)
  allposes[w]=pose
  meta[w]={'clock':clock,'travel_delta_m':delay,'hip':list(hip),'chest_deg':ca,'head_deg':ha,'compression_m':L('compress'),'feet':{side:fm for side,(_,_,fm) in feet.items()}}
  # Parenting shear is inherited unchanged. Replace only local translation.
  worlds[w]=ROOT.matrix_world@r.matrix_parent_inverse@Matrix.Translation(r.location)
 # A live common contact target settles between the two NEW shoulder poses.
 shoulders={w:worlds[w]@p['upper_arm_near'][0] for w,p in allposes.items()}
 mid=(shoulders['BOY']+shoulders['GIRL'])/2
 handheight=mid.z-interp(g,[(913,.25),(967,.25),(978,.24),(990,.22),(1000,.245),(1080,.245)])
 for w,r in RIGS.items():
  pose=allposes[w];sign=1 if w=='BOY' else -1
  offer=interp(g,[(913,0),(970 if w=='BOY' else 963,0),(985 if w=='BOY' else 979,1),(1080,1)])
  # A small open-hand search precedes the partner receiving it.
  goal=Vector((mid.x-sign*.064,shoulders[w].y,handheight-sign*.004))
  oldwrist=worlds[w]@pose['forearm_near'][1]
  target=worlds[w].inverted()@oldwrist.lerp(goal,offer)
  H=pose['upper_arm_near'][0];l1=r.data.bones['upper_arm_near'].length;l2=r.data.bones['forearm_near'].length
  dist=(target-H).length
  if dist>l1+l2-.004:target=H+(target-H).normalized()*(l1+l2-.004)
  E=ik(H,target,l1,l2,lower=True)
  pose['upper_arm_near']=(H,E);pose['forearm_near']=(E,target)
  olddir=(pose['hand_near'][1]-pose['hand_near'][0]).normalized()
  handdir=olddir.lerp(Vector((sign,0,-.12)),offer).normalized()
  pose['hand_near']=(target,target+handdir*r.data.bones['hand_near'].length)
  data={}
  for n,(a,b) in pose.items():
   matrix=mat(r,n,a,b);pb=r.pose.bones[n];pb.rotation_mode='QUATERNION';pb.matrix=matrix
   key=(w,n)
   if key in LAST and LAST[key].dot(pb.rotation_quaternion)<0:pb.rotation_quaternion.negate()
   LAST[key]=pb.rotation_quaternion.copy()
   for prop in ['location','rotation_quaternion','scale']:pb.keyframe_insert(prop,frame=g)
   data[n]={'head':a.copy(),'tail':b.copy(),'matrix':matrix}
  CACHE[w][g]=data
  meta[w]['offer']=offer;meta[w]['hand_wrist_world']=list(worlds[w]@target)
 ROWS.append({'frame':g,'children':meta})
for w,r in RIGS.items():
 r.animation_data.action.name='V066 '+w+' | weighted notice check receive and cautious travel |24fps'
 for fc in curves(r):
  for m in list(fc.modifiers):fc.modifiers.remove(m)
  fc.extrapolation='CONSTANT'
  for k in fc.keyframe_points:k.interpolation='LINEAR'
print('V066_PRIMARY_POSES_BUILT',len(FRAMES),flush=True)

# The existing limb meshes are drawing grids. Refit them to the newly authored
# joints; preserve their original polygons, UVs, packed painting and depth planes.
DRAWINGS=[]
for o in list(S.objects):
 if o.type!='MESH' or o.hide_render or o.parent not in RIGS.values():continue
 role=o.get('wardrobe_role')
 if role not in ['sleeve','leg']:continue
 w='BOY' if 'BOY' in o.name else 'GIRL';side='near' if o.name.endswith('near') else 'far'
 source_y=[v.co.y for v in o.data.vertices];o.shape_key_clear()
 basis=o.shape_key_add(name='Basis | original painted grid | new G913 pose')
 for g in FRAMES:
  v=M.limb_vertices(RIGS[w],CACHE[w][g],side,role,refined=True)
  for i,p in enumerate(v):p.y=source_y[i]
  if g==G0:
   basis.data.foreach_set('co',[c for p in v for c in p]);o.data.vertices.foreach_set('co',[c for p in v for c in p])
  key=o.shape_key_add(name='V066 actual '+role+' G%06.1f'%g)
  key.data.foreach_set('co',[c for p in v for c in p])
  for at,value in [(G0,0),(max(G0,g-.5),0),(g,1),(min(G1,g+.5),0),(G1,0)]:
   # End drawings hold at their boundary instead of receiving a duplicate zero.
   if at==g:value=1
   key.value=value;key.keyframe_insert('value',frame=at)
 for fc in curves(o.data.shape_keys):
  for k in fc.keyframe_points:k.interpolation='LINEAR'
 o.data.shape_keys.animation_data.action.name='V066 '+o.name+' | actual posed drawing sequence'
 o['V066_drawing_cache']='Rebuilt at half production frames from actual new joints; original UV, paintings and depth retained.'
 DRAWINGS.append(o.name)

# Distal finger shapes and thumb opposition already exist in the source atlas.
# Give them a new open/search/receive/close schedule that follows the acting.
for w in RIGS:
 hand=bpy.data.objects['V060 '+w+' | retained paint hand fold near'];keys=hand.data.shape_keys
 keys.animation_data_clear()
 for g in FRAMES:
  for key in list(keys.key_blocks)[1:]:
   if 'finger fold' in key.name:value=interp(g,[(913,0),(979 if w=='GIRL' else 984,0),(990 if w=='GIRL' else 994,1),(1080,1)])
   elif 'opposed thumb' in key.name:value=interp(g,[(913,0),(965,0),(983,1),(1080,1)])
   elif 'pronation depth' in key.name:value=math.sin(math.pi*interp(g,[(913,0),(965,0),(983,1),(1080,1)]))
   else:value=0
   key.value=value;key.keyframe_insert('value',frame=g)
 for fc in curves(keys):
  for k in fc.keyframe_points:k.interpolation='LINEAR'

# Native, editable garment correctives retain every original pigment coordinate.
for w,r in RIGS.items():
 body=next(o for o in S.objects if o.parent==r and o.get('wardrobe_role')=='body' and not o.hide_render)
 if not body.data.shape_keys:body.shape_key_add(name='Basis | original painted garment')
 key=body.shape_key_add(name='V066 | weight compression and chest fold')
 hipz=r.data.bones['pelvis'].head_local.z;shoulderz=r.data.bones['chest'].tail_local.z
 for i,v in enumerate(body.data.vertices):
  p=v.co.copy();u=clamp((p.z-hipz)/(shoulderz-hipz));center=math.sin(math.pi*u)
  p.x+=center*(-.012 if p.x<0 else -.006);p.z-=.008*center
  key.data[i].co=p
 lag=body.shape_key_add(name='V066 | lower cloth follows the checked body')
 for i,v in enumerate(body.data.vertices):
  p=v.co.copy();u=clamp((hipz-p.z)/.35);p.x+=.022*u*u;p.z+=.004*u*math.sin(i%17/16*math.pi);lag.data[i].co=p
 for g in FRAMES:
  key.value=clamp(interp(g,TRACKS[w]['compress'])/.05);key.keyframe_insert('value',frame=g)
  lag.value=interp(g,[(913,0),(959,0),(973,-.8),(985,.7),(999,-.25),(1018,.2),(1080,.1)])
  lag.slider_min=-1;lag.keyframe_insert('value',frame=g)
 for fc in curves(body.data.shape_keys):
  for k in fc.keyframe_points:k.interpolation='LINEAR'

# Old contact paint belongs to the old boots. Rebuild from evaluated new soles.
contact=bpy.data.collections.get('V060 | evaluated boot contact paint | no physical shadow claim')
if contact:
 for ob in list(contact.all_objects):bpy.data.objects.remove(ob,do_unlink=True)
 bpy.data.collections.remove(contact)
import runpy
boots=[o for o in S.objects if o.type=='MESH' and o.parent in RIGS.values() and o.get('proportion_role')=='boot' and not o.hide_render]
stage=ROOT.parent;z0=stage.matrix_world.translation.z;y0=stage.matrix_world.translation.y;slope=(3-z0)/(16+y0)
contacts=runpy.run_path(str(R/'work/trailer_development_v060/scripts/add_measured_contacts.py'))['apply'](S,boots,FRAMES,lambda y:3-slope*(y+16))

S.frame_start=G0;S.frame_end=G1;S.render.fps=24
for sc in bpy.data.scenes:
 if 'V065' in sc.name or 'v065' in sc.name or sc==S:
  sc.render.resolution_x=3840;sc.render.resolution_y=2160;sc.render.resolution_percentage=100
  sc.view_settings.view_transform='Standard';sc.view_settings.look='None';sc.view_settings.exposure=0;sc.view_settings.gamma=1
  sc.render.threads_mode='FIXED';sc.render.threads=2
  if hasattr(sc,'eevee'):sc.eevee.taa_render_samples=32
S.timeline_markers.clear()
for g,label in [(913,'IN | ordinary travel'),(957,'THREAT | girl notices'),(966,'CHECK | weight accepted'),(979,'OFFER | partner responds'),(990,'GRIP | both bodies settle'),(1016,'LOWER | cautious paired steps'),(1080,'OUT | keep going')]:S.timeline_markers.new(label,frame=g)
S['V066_review_scope']='Seven seconds G913-1080 / 24fps. Original artwork. No full-film integration or artistic approval.'
S['V066_acting']='Notice before reach; new checked support and pelvis/chest response; delayed partner receive and grip; low cautious continuation.'
S['V066_handles']='Global camera/root route retained. Per-child check offsets return to zero by G1056. New cautious posture continues through outgoing handle.'
assert sha_art()==ART_BEFORE,'Packed paintings changed'
assert all(UV_BEFORE[k]==v for k,v in uv_signature().items() if k in UV_BEFORE),'Original UV registration changed'
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==SOURCE_HASH
bpy.context.window.scene=S;S.frame_set(990);bpy.context.view_layer.update()
report={'source':str(SRC),'source_sha256':SOURCE_HASH,'native':str(NATIVE),'world_scene':S.name,'range':[G0,G1],'fps':24,'packed_art_unchanged':sha_art()==ART_BEFORE,'original_UVs_unchanged':True,'new_rig_actions':[r.animation_data.action.name for r in RIGS.values()],'drawing_caches':DRAWINGS,'sample_spacing_frames':.5,'contacts':contacts,'rows':ROWS,'artwork_hashes':ART_BEFORE,'camera_and_root_route':'Inherited v065f route. Per-child check offsets return to zero before outgoing handle.','status':'Review candidate; not integrated into full trailer.'}
text=bpy.data.texts.new('START HERE | V066 | paired danger acting candidate');text.write(json.dumps({k:v for k,v in report.items() if k not in ['rows','artwork_hashes']},indent=2,default=str))
bpy.ops.wm.save_as_mainfile(filepath=str(NATIVE),compress=True)
report['native_sha256']=hashlib.sha256(NATIVE.read_bytes()).hexdigest()
(O/'evidence/BUILD.json').write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
print('V066_NATIVE_SAVED',str(NATIVE),flush=True)
