"""Contact/acceptance/passing/push-off performance poses over v051 grounded gait."""
import bpy,json,hashlib,math,sys
from pathlib import Path
from mathutils import Matrix,Vector
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1]
SRC=ROOT/'locomotion/coat_fluidity_v051/native/WTSC_Controlled_Fluid_Coat_v051.blend'
SHA='e888f7b7ab4c01040e675fc7d974e575a09df5e16f991897cae63629ec7dfd4f';assert hashlib.sha256(SRC.read_bytes()).hexdigest()==SHA
sys.path.insert(0,str(ROOT/'locomotion/connected_model_fit_v049/scripts'));import model_spec as M
bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False,use_scripts=False)
S=bpy.data.scenes['V051 | BOY COAT FLUIDITY | exact v050 gait'];bpy.context.window.scene=S
S.name='V053 | AUTHORED WALK BEATS | v051 grounded feet'
bpy.data.collections['V051 | AGE10 PAIR | controlled fluid coat'].name='V053 | AGE10 PAIR | authored walk beats'
C=bpy.data.collections['V046 | restored original painted wardrobe'];R={w:bpy.data.objects['V044 '+w+' | estimated joint centres'] for w in ('BOY','GIRL')}

# Each pair of half-steps has specific support phases. The pair has distinct
# ranges and the girl's existing two-frame phase lead; no random offsets.
TIMES=[0,3,8,12,16,19,24,28]
KEYS={
 'BOY':{
  'pelvis':[0,1.8,.4,-.9,0,1.4,.2,-.7],
  'chest':[.3,4.4,1.2,-.8,0,3.5,1.4,-.6],
  'near_upper':[0,-2.3,-2.8,.5,0,1.6,2.4,1],
  'far_upper':[0,1.6,2.2,0,0,-1.6,-2,.2],
  'near_elbow':[5,11,7,1,0,2,5,7],
  'far_elbow':[1,3,6,8,9,10,6,2],
 },
 'GIRL':{
  'pelvis':[0,1.2,.2,-.6,0,1.3,.3,-.55],
  'chest':[0,2.8,.7,-.3,.2,2.4,1,-.4],
  'near_upper':[0,-1,-1.6,.4,0,1,1.6,.4],
  'far_upper':[0,1,1.4,0,0,-1,-1.4,0],
  'near_elbow':[1,7,8,4,1,0,3,5],
  'far_elbow':[2,1,3,7,9,6,3,1],
 }}
def pose_curve(w,key,f):
 t=(f+(2 if w=='GIRL' else 0)-1)%32;v=KEYS[w][key]
 def slope(i):
  prev=(i-1)%8;next=(i+1)%8;a=TIMES[prev]-(32 if i==0 else 0);b=TIMES[next]+(32 if i==7 else 0)
  return (v[next]-v[prev])/(b-a)
 i=max(j for j,x in enumerate(TIMES) if x<=t);n=(i+1)%8;a=TIMES[i];b=TIMES[n]+(32 if n==0 else 0);u=(t-a)/(b-a);h=b-a
 return (2*u**3-3*u*u+1)*v[i]+(u**3-2*u*u+u)*h*slope(i)+(-2*u**3+3*u*u)*v[n]+(u**3-u*u)*h*slope(n)
def axis(deg):a=math.radians(deg);return Vector((math.sin(a),0,-math.cos(a)))
def downangle(v):return math.degrees(math.atan2(v.x,-v.z))
def upangle(v):return math.degrees(math.atan2(v.x,v.z))
def setbone(r,n,a,b,f,last):
 rb=r.data.bones[n];old=(rb.tail_local-rb.head_local).normalized();new=(b-a).normalized();Q=old.rotation_difference(new);pb=r.pose.bones[n];pb.rotation_mode='QUATERNION'
 pb.matrix=Matrix.Translation(a)@Q.to_matrix().to_4x4()@rb.matrix_local.to_3x3().to_4x4();ident=(r.name,n)
 if ident in last and pb.rotation_quaternion.dot(last[ident])<0:pb.rotation_quaternion.negate()
 last[ident]=pb.rotation_quaternion.copy()
 for prop in ('location','rotation_quaternion','scale'):pb.keyframe_insert(prop,frame=f)

source={w:[] for w in R}
for i in range(129):
 f=1+i/4;S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
 for w,r in R.items():
  e=r.evaluated_get(dg);source[w].append({n:{'head':b.head.copy(),'tail':b.tail.copy()} for n,b in e.pose.bones.items()})

last={};record={w:[] for w in R}
for i in range(129):
 f=1+i/4;S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update()
 for w,r in R.items():
  old=source[w][i];hip=old['pelvis']['head'];pelvis=old['pelvis'];p=upangle(pelvis['tail']-hip)+pose_curve(w,'pelvis',f)
  waist=hip+Vector((math.sin(math.radians(p)),0,math.cos(math.radians(p))))*(pelvis['tail']-hip).length
  chest=old['chest'];c=upangle(chest['tail']-chest['head'])+pose_curve(w,'chest',f)
  shoulder=waist+Vector((math.sin(math.radians(c)),0,math.cos(math.radians(c))))*(chest['tail']-chest['head']).length
  head=old['head'];base=head['head']+(shoulder-chest['tail']);h=upangle(head['tail']-head['head'])-.35*pose_curve(w,'chest',f)
  headtail=base+Vector((math.sin(math.radians(h)),0,math.cos(math.radians(h))))*(head['tail']-head['head']).length
  setbone(r,'pelvis',hip,waist,f,last);setbone(r,'chest',waist,shoulder,f,last);setbone(r,'head',base,headtail,f,last)
  # Compensate child leg local matrices for the revised pelvis tilt. The
  # already-approved world ankle and boot trajectories remain unchanged.
  for side in ('near','far'):
   for name in ('thigh_'+side,'shin_'+side,'foot_'+side):
    part=old[name];setbone(r,name,part['head'],part['tail'],f,last)
  for side in ('near','far'):
   upper=old['upper_arm_'+side];fore=old['forearm_'+side];hand=old['hand_'+side]
   ua=downangle(upper['tail']-upper['head'])+pose_curve(w,side+'_upper',f)
   flex=(downangle(fore['tail']-fore['head'])-downangle(upper['tail']-upper['head']))+pose_curve(w,side+'_elbow',f)
   fa=ua+flex;oldhand=downangle(hand['tail']-hand['head']);lag=pose_curve(w,side+'_elbow',f-1.5)
   ha=oldhand+pose_curve(w,side+'_upper',f)+.5*lag-.2*pose_curve(w,side+'_elbow',f)
   elbow=shoulder+axis(ua)*(upper['tail']-upper['head']).length
   wrist=elbow+axis(fa)*(fore['tail']-fore['head']).length
   setbone(r,'upper_arm_'+side,shoulder,elbow,f,last)
   setbone(r,'forearm_'+side,elbow,wrist,f,last)
   setbone(r,'hand_'+side,wrist,wrist+axis(ha)*(hand['tail']-hand['head']).length,f,last)
  record[w].append({'frame':f,'pelvis_delta_deg':pose_curve(w,'pelvis',f),'chest_delta_deg':pose_curve(w,'chest',f),'near_elbow_delta_deg':pose_curve(w,'near_elbow',f),'far_elbow_delta_deg':pose_curve(w,'far_elbow',f)})
for w,r in R.items():r.animation_data.action.name='V053 '+w+' | contact loading passing push |32frames'

# New actual arm poses need their original-painted 2.5D sleeve drawings
# refitted. The v051 restrained cap and inner fold are retained.
for w,r in R.items():
 for side in ('near','far'):
  o=next(x for x in C.objects if x.parent==r and x.get('wardrobe_role')=='sleeve' and x.name.endswith(side));assert len(o.data.shape_keys.key_blocks)==128
  for i,key in enumerate(o.data.shape_keys.key_blocks):
   f=1 if i==0 else 1+i/4;S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();e=r.evaluated_get(bpy.context.evaluated_depsgraph_get())
   pose={n:{'head':b.head.copy(),'tail':b.tail.copy(),'matrix':b.matrix.copy()} for n,b in e.pose.bones.items()};verts=M.limb_vertices(r,pose,side,'sleeve')
   if w=='BOY':
    a=pose['upper_arm_'+side]['tail']-pose['upper_arm_'+side]['head'];d=pose['forearm_'+side]['tail']-pose['forearm_'+side]['head'];strength=max(0,min(1,(math.degrees(a.angle(d))-8)/7))
    original=[p.copy() for p in verts]
    for j,p in enumerate(verts):
     row,col=divmod(j,9);t=row/48;s=col/8
     if row<=3 or row>=46:continue
     normal=(original[row*9+8]-original[row*9]).normalized();cap=.003*math.sin(math.pi*max(0,min(1,(t-.06)/.73)))**2 if t<.79 else 0
     fold=.0013*strength*math.exp(-((t-.86)/.075)**2);p-=normal*((s*2-1)*cap+fold*(s*s-.25))
   key.data.foreach_set('co',[c for p in verts for c in p])
   if i==0:o.data.vertices.foreach_set('co',[c for p in verts for c in p])
  o.data.update()
S.frame_set(1);bpy.context.view_layer.update()
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==SHA
S['V053_scope']='Contact/loading/passing/push-off body poses. Same v051 planted world feet, root travel, painted design and damped coat.'
report={'source':str(SRC),'source_sha256':SHA,'source_fps':30,'period_frames':32,'key_phase_frames':TIMES,'key_pose_values_degrees':KEYS,'girl_lead_frames':2,'travel_unchanged':True,'boot_world_target_unchanged':True,'v051_coat_keys_unchanged':True,'samples':record,'artistic_scope':'Purposeful ordinary walk body performance study; no recovery, stumble or support clasp. Contact validation and actual normal-speed review required.'}
(P/'evidence/BEATS_BUILD.json').write_text(json.dumps(report,indent=2))
native=P/'native/WTSC_Authored_Walk_Beats_v053.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
print('V053_AUTHORED_WALK_BEATS_SAVED')
