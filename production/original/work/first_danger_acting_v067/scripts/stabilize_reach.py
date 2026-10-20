"""Stable walking bend; continuous girl FK transition into the backward offer."""
import bpy,json,math,hashlib,importlib.util
from pathlib import Path
from mathutils import Vector,Matrix
O=Path(__file__).resolve().parents[1];R=O.parents[1];B=json.loads((O/'evidence/BUILD.json').read_text());SOURCE=Path(B['native']);SHA=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False);S=bpy.data.scenes[B['world_scene']];bpy.context.window.scene=S
RIGS={w:bpy.data.objects['V044 '+w+' | estimated joint centres'] for w in ['BOY','GIRL']};CACHE={w:{} for w in RIGS};frames=[r['frame'] for r in B['rows']]
def curves(o):return [f for l in o.animation_data.action.layers for st in l.strips for bag in st.channelbags for f in bag.fcurves]
def axis(a):a=math.radians(a);return Vector((math.sin(a),0,-math.cos(a)))
def direction(a,b,t):
 x=math.atan2(a.x,-a.z);y=math.atan2(b.x,-b.z);d=(y-x+math.pi)%math.tau-math.pi
 return Vector((math.sin(x+t*d),0,-math.cos(x+t*d)))
def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
def ik(H,A,l1,l2,branch):
 delta=A-H;d=delta.length;U=delta/d;x=(l1*l1-l2*l2+d*d)/(2*d);h=math.sqrt(max(0,l1*l1-x*x));return H+U*x+Vector((-U.z,0,U.x))*h*branch
def matrix(r,n,a,b):
 rb=r.data.bones[n];q=(rb.tail_local-rb.head_local).normalized().rotation_difference((b-a).normalized());return Matrix.Translation(a)@q.to_matrix().to_4x4()@rb.matrix_local.to_3x3().to_4x4()
for g in frames:
 S.frame_set(int(g),subframe=g-int(g));bpy.context.view_layer.update()
 for w,r in RIGS.items():CACHE[w][g]={n:{'head':b.head.copy(),'tail':b.tail.copy(),'matrix':b.matrix.copy()} for n,b in r.pose.bones.items()}
for w,r in RIGS.items():
 r.animation_data.action=r.animation_data.action.copy();r.animation_data.action.name='V067 '+w+' | continuous elbow bend and contact'
 for l in r.animation_data.action.layers:
  for st in l.strips:
   for bag in st.channelbags:
    for fc in list(bag.fcurves):
     if any(fc.data_path.startswith('pose.bones["'+n+'"].') for n in ['upper_arm_near','forearm_near','hand_near']):bag.fcurves.remove(fc)
last={};max_late_difference=0
for row in B['rows']:
 g=row['frame'];S.frame_set(int(g),subframe=g-int(g));bpy.context.view_layer.update()
 for w,r in RIGS.items():
  p=CACHE[w][g];H=p['upper_arm_near']['head'];W=p['forearm_near']['tail'];l1=r.data.bones['upper_arm_near'].length;l2=r.data.bones['forearm_near'].length
  if w=='BOY':E=ik(H,W,l1,l2,-1)
  else:
   Egoal=ik(H,W,l1,l2,1);clock=row['children'][w]['clock'];phi=math.tau*(clock-1)/32;ca=row['children'][w]['chest_deg'];upper=-11*math.cos(phi-.2)+(ca-3)*.22;fore=upper+12+5*math.sin(phi)
   t=ease((g-963)/20);U=direction(axis(upper),(Egoal-H).normalized(),t);F=direction(axis(fore),(W-Egoal).normalized(),t);E=H+U*l1;W=E+F*l2
  hd=(p['hand_near']['tail']-p['hand_near']['head']).normalized();ends={'upper_arm_near':(H,E),'forearm_near':(E,W),'hand_near':(W,W+hd*r.data.bones['hand_near'].length)}
  for n,(a,b) in ends.items():
   if g>=984:max_late_difference=max(max_late_difference,(a-p[n]['head']).length,(b-p[n]['tail']).length)
   mat=matrix(r,n,a,b);pb=r.pose.bones[n];pb.rotation_mode='QUATERNION';pb.matrix=mat
   if (w,n) in last and pb.rotation_quaternion.dot(last[w,n])<0:pb.rotation_quaternion.negate()
   last[w,n]=pb.rotation_quaternion.copy()
   for prop in ['location','rotation_quaternion','scale']:pb.keyframe_insert(prop,frame=g)
   p[n]={'head':a.copy(),'tail':b.copy(),'matrix':mat}
  row['children'][w]['hand_wrist_world']=list(r.matrix_world@W)
 for r in RIGS.values():
  for fc in curves(r):
   for key in fc.keyframe_points:key.interpolation='LINEAR'
sp=importlib.util.spec_from_file_location('model_spec',R/'locomotion/connected_model_fit_v049/scripts/model_spec.py');M=importlib.util.module_from_spec(sp);sp.loader.exec_module(M)
for w,r in RIGS.items():
 o=bpy.data.objects['V060 '+w+' | reach sleeve near'];ys=[v.co.y for v in o.data.vertices];o.shape_key_clear();basis=o.shape_key_add(name='Basis | original pigment and stable bend')
 for g in frames:
  vertices=M.limb_vertices(r,CACHE[w][g],'near','sleeve',True)
  for i,v in enumerate(vertices):v.y=ys[i]
  if g==913:basis.data.foreach_set('co',[c for p in vertices for c in p]);o.data.vertices.foreach_set('co',[c for p in vertices for c in p])
  key=o.shape_key_add(name='V067 stable sleeve G%06.1f'%g);key.data.foreach_set('co',[c for p in vertices for c in p])
  for at in sorted(set([913,max(913,g-.5),g,min(1080,g+.5),1080])):key.value=float(at==g);key.keyframe_insert('value',frame=at)
 for fc in curves(o.data.shape_keys):
  for k in fc.keyframe_points:k.interpolation='LINEAR'
assert max_late_difference<.000002,max_late_difference
S.frame_set(990);bpy.context.view_layer.update();P=O/'native/WTSC_First_Danger_Acting_v067e.blend';bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True)
B['bend_source_native']=str(SOURCE);B['bend_source_sha256']=SHA;B['native']=str(P);B['native_sha256']=hashlib.sha256(P.read_bytes()).hexdigest();B['elbow_correction']='Fixed boy IK branch, original natural walking FK for girl with a continuous20-frame direction transition into the backward offer. No nearest-low-elbow branch switching.';B['late_near_arm_endpoint_max_difference_m']=max_late_difference
(O/'evidence/BUILD_FINAL_E.json').write_text(json.dumps(B,indent=2));assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA;print('V067E_STABLE_BEND_SAVED',max_late_difference,flush=True)
