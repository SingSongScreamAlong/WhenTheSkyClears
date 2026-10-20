"""Subtle support-linked chest and distal arm overlap on the frozen v051 walk."""
import bpy, json, hashlib, math, sys
from pathlib import Path
from mathutils import Matrix, Vector
import numpy as np

P=Path(__file__).resolve().parents[1];ROOT=P.parents[1]
SRC=ROOT/'locomotion/coat_fluidity_v051/native/WTSC_Controlled_Fluid_Coat_v051.blend'
SHA='e888f7b7ab4c01040e675fc7d974e575a09df5e16f991897cae63629ec7dfd4f'
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==SHA
sys.path.insert(0,str(ROOT/'locomotion/connected_model_fit_v049/scripts'))
import model_spec as M
bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False,use_scripts=False)
S=bpy.data.scenes['V051 | BOY COAT FLUIDITY | exact v050 gait'];bpy.context.window.scene=S
S.name='V052 | SUPPORT LINKED UPPER BODY | v051 contacts'
bpy.data.collections['V051 | AGE10 PAIR | controlled fluid coat'].name='V052 | AGE10 PAIR | support linked upper body'
C=bpy.data.collections['V046 | restored original painted wardrobe']
R={w:bpy.data.objects['V044 '+w+' | estimated joint centres'] for w in ('BOY','GIRL')}

def ah(a):
 return hashlib.sha256(repr([(f.data_path,f.array_index,[(tuple(k.co),k.interpolation) for k in f.keyframe_points]) for l in a.layers for st in l.strips for b in st.channelbags for f in b.fcurves]).encode()).hexdigest()
protected={a.name:ah(a) for a in bpy.data.actions}
snapshots={w:[] for w in R}
for i in range(129):
 f=1+i/4;S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
 for w,r in R.items():
  e=r.evaluated_get(dg);snapshots[w].append({n:{'head':b.head.copy(),'tail':b.tail.copy(),'matrix':b.matrix.copy()} for n,b in e.pose.bones.items()})

def angle(v):return math.degrees(math.atan2(v.x,-v.z))
def axis(deg):a=math.radians(deg);return Vector((math.sin(a),0,-math.cos(a)))
def pulse(q,center,width):
 d=abs((q-center+16)%32-16)
 return math.exp(-.5*(d/width)**2)
def setbone(r,n,a,b,f,last):
 rb=r.data.bones[n];old=(rb.tail_local-rb.head_local).normalized();new=(b-a).normalized();Q=old.rotation_difference(new);pb=r.pose.bones[n];pb.rotation_mode='QUATERNION'
 pb.matrix=Matrix.Translation(a)@Q.to_matrix().to_4x4()@rb.matrix_local.to_3x3().to_4x4()
 key=(r.name,n)
 if key in last and pb.rotation_quaternion.dot(last[key])<0:pb.rotation_quaternion.negate()
 last[key]=pb.rotation_quaternion.copy()
 for prop in ('location','rotation_quaternion','scale'):pb.keyframe_insert(prop,frame=f)

def elbow_delta(w,side,f):
 lead=0 if w=='BOY' else 2
 qn=(f+lead-1)%32;qf=(f+lead-17)%32
 n=pulse(qn,2.8,2.5);a=pulse(qf,4.4,2.8)
 if w=='BOY':return 2.4*n-.65*a if side=='near' else 1.65*a-.45*n
 return 1.25*n-.35*a if side=='near' else 1.8*a-.35*n

measure={};last={}
for w,r in R.items():
 poses=snapshots[w];z=np.array([p['pelvis']['head'].z for p in poses[:128]])
 velocity=(np.roll(z,-1)-np.roll(z,1))*2 # central derivative per source frame
 amplitude=float(np.max(abs(velocity)));assert amplitude>0
 modified=[]
 for i,old in enumerate(poses):
  f=1+i/4;idx=i%128;v=float(velocity[idx]/amplitude);lead=0 if w=='BOY' else 2
  qn=(f+lead-1)%32;load=pulse(qn,2.8,2.5)
  # The pelvis/hip trajectory remains fixed for the planted soles. Chest
  # counters its measured rise/fall and settles slightly after heel loading.
  chest_delta=-(.90 if w=='BOY' else .65)*v-(.28 if w=='BOY' else .18)*load
  chest=old['chest'];chest_axis=chest['tail']-chest['head'];oldlean=math.degrees(math.atan2(chest_axis.x,chest_axis.z));newlean=oldlean+chest_delta
  shoulder=chest['head']+Vector((math.sin(math.radians(newlean)),0,math.cos(math.radians(newlean))))*(chest['tail']-chest['head']).length
  head=old['head'];headbase=head['head']+(shoulder-chest['tail']);headtail=headbase+(head['tail']-head['head'])
  S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update()
  setbone(r,'chest',chest['head'],shoulder,f,last)
  setbone(r,'head',headbase,headtail,f,last)
  for side in ('near','far'):
   upper=old['upper_arm_'+side];fore=old['forearm_'+side];hand=old['hand_'+side]
   upper_angle=angle(upper['tail']-upper['head']);fore_angle=angle(fore['tail']-fore['head']);hand_angle=angle(hand['tail']-hand['head'])
   d=elbow_delta(w,side,f);lag=elbow_delta(w,side,f-1.4)
   elbow=shoulder+axis(upper_angle)*(upper['tail']-upper['head']).length
   wrist=elbow+axis(fore_angle+d)*(fore['tail']-fore['head']).length
   handtail=wrist+axis(hand_angle+.55*lag)*(hand['tail']-hand['head']).length
   setbone(r,'upper_arm_'+side,shoulder,elbow,f,last)
   setbone(r,'forearm_'+side,elbow,wrist,f,last)
   setbone(r,'hand_'+side,wrist,handtail,f,last)
  modified.append({'frame':f,'chest_delta_degrees':chest_delta,'near_elbow_delta_degrees':elbow_delta(w,'near',f),'far_elbow_delta_degrees':elbow_delta(w,'far',f)})
 measure[w]={'hip_vertical_velocity_peak_m_per_source_frame':amplitude,'samples':modified}
 # Existing cycle Action now has edited quarter-frame keys. Retain its
 # native interpolation/modifiers and rename to make the change explicit.
 r.animation_data.action.name='V052 '+w+' | support linked upper body | 32frames'

# Refit the sleeve drawing caches to the new arm poses. Original UV/image
# payloads and the v051 restrained cap/fold treatment remain on these meshes.
for w,r in R.items():
 for side in ('near','far'):
  o=next(x for x in C.objects if x.parent==r and x.get('wardrobe_role')=='sleeve' and x.name.endswith(side))
  assert len(o.data.shape_keys.key_blocks)==128
  for i,key in enumerate(o.data.shape_keys.key_blocks):
   f=1 if i==0 else 1+i/4;S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();e=r.evaluated_get(bpy.context.evaluated_depsgraph_get())
   pose={n:{'head':b.head.copy(),'tail':b.tail.copy(),'matrix':b.matrix.copy()} for n,b in e.pose.bones.items()}
   verts=M.limb_vertices(r,pose,side,'sleeve')
   if w=='BOY':
    a=pose['upper_arm_'+side]['tail']-pose['upper_arm_'+side]['head'];d=pose['forearm_'+side]['tail']-pose['forearm_'+side]['head']
    strength=max(0,min(1,(math.degrees(a.angle(d))-8)/7))
    for j,p in enumerate(verts):
     row,col=divmod(j,9);t=row/48;s=col/8
     if row<=3 or row>=46:continue
     normal=(verts[row*9+8]-verts[row*9]).normalized()
     cap=.003*math.sin(math.pi*max(0,min(1,(t-.06)/.73)))**2 if t<.79 else 0
     fold=.0013*strength*math.exp(-((t-.86)/.075)**2);inner=fold*(s*s-.25)
     p-=normal*((s*2-1)*cap+inner)
   key.data.foreach_set('co',[c for p in verts for c in p])
   if i==0:o.data.vertices.foreach_set('co',[c for p in verts for c in p])
  o.data.update()

for name,h in protected.items():
 if name.startswith('V048 BOY |') or name.startswith('V048 GIRL |'):continue
 if name.startswith('V047 BOY |') or name.startswith('V047 GIRL |'):continue
 # Rig Actions are deliberately revised; every other old action is retained.
 if name not in bpy.data.actions:continue
 assert ah(bpy.data.actions[name])==h,name
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==SHA
S.frame_set(1);bpy.context.view_layer.update();S['V052_scope']='Upper body support timing only. v051 coat, age-ten design and exact planted-foot/leg/root curves retained.'
native=P/'native/WTSC_Support_Linked_Upper_Body_v052.blend';native.parent.mkdir(parents=True,exist_ok=True)
(P/'evidence').mkdir(parents=True,exist_ok=True)
report={'source':str(SRC),'source_sha256':SHA,'period_frames':32,'source_fps':30,'root_camera_leg_boot_actions_unchanged':True,'upper_arm_angles_not_deliberately_dephased':True,'support_driver':'Measured existing hip vertical velocity plus near-foot acceptance pulse; deterministic32-frame periodic','chest_motion':'Measured hip rise/fall counterbalance, boy max.90deg, girl max.65deg, plus small acceptance settle','elbow_motion':'Boy near+2.4deg / far+1.65deg load flex, girl near+1.25deg / far+1.8deg; opposite-leg pulse offset and limited cross-term','wrist_overlap':'55percent of elbow correction delayed1.4source frames','sleeve_cache_refit':True,'samples':measure,'source_unchanged':True}
(P/'evidence/UPPER_BODY_BUILD.json').write_text(json.dumps(report,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
print('V052_SUPPORT_LINKED_UPPER_BODY_SAVED')
