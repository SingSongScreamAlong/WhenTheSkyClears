"""Controlled editable 2.5D coat deformation; all v050 gait Actions read-only."""
import bpy,json,hashlib,math,sys
import numpy as np
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];SRC=ROOT/'locomotion/face_hand_finish_v050/native/WTSC_Face_Hand_Finish_v050.blend';SOURCE_HASH='1721ae5ce9146e9d0379419d153c64ef09a122074a972a8e4bd68fb1953d176e';assert hashlib.sha256(SRC.read_bytes()).hexdigest()==SOURCE_HASH
sys.path.insert(0,str(ROOT/'locomotion/connected_model_fit_v049/scripts'));import model_spec as M
bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False,use_scripts=False);S=bpy.data.scenes['V050 | FACE FINISH AND RELAXED HANDS | v049 gait'];bpy.context.window.scene=S;S.name='V051 | BOY COAT FLUIDITY | exact v050 gait';bpy.data.collections['V050 | AGE10 PAIR | face and hand finish'].name='V051 | AGE10 PAIR | controlled fluid coat';C=bpy.data.collections['V046 | restored original painted wardrobe'];r=bpy.data.objects['V044 BOY | estimated joint centres'];body=next(o for o in C.objects if o.parent==r and o.get('wardrobe_role')=='body')
def ah(a):return hashlib.sha256(repr([(f.data_path,f.array_index,[(tuple(k.co),k.interpolation) for k in f.keyframe_points]) for l in a.layers for st in l.strips for b in st.channelbags for f in b.fcurves]).encode()).hexdigest()
protected={a.name:ah(a) for a in bpy.data.actions};rawbody=[v.co.copy() for v in body.data.vertices];poses={};hips=[]
for i in range(129):
 f=1+i/4;S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();e=r.evaluated_get(bpy.context.evaluated_depsgraph_get());poses[f]={n:{'head':b.head.copy(),'tail':b.tail.copy(),'matrix':b.matrix.copy()} for n,b in e.pose.bones.items()}
 if i<128:hips.append(list(e.pose.bones['pelvis'].head))
hips=np.array(hips);dt=1/120;acc=(np.roll(hips,-1,axis=0)-2*hips+np.roll(hips,1,axis=0))/(dt*dt)
targets=np.column_stack([np.clip(-.060*acc[:,0],-.018,.018),np.clip(-.004*acc[:,2],-.009,.009)])
# Damped mass/spring response to the ACTUAL existing support-driven hip
# accelerations. Warm to a periodic state; no start pop, arbitrary sine wobble
# or accumulated simulation cache is required by the delivered native.
omega=math.tau*3.2;zeta=.90;x=np.zeros(2);v=np.zeros(2);values=[]
for cycle in range(14):
 for i in range(128):
  if cycle==13:values.append(x.copy())
  v+=(omega*omega*(targets[i]-x)-2*zeta*omega*v)*dt;x+=v*dt
assert np.linalg.norm(x-values[0])<1e-9;values=np.array(values);assert np.max(abs(values[:,0]))<.016 and np.max(abs(values[:,1]))<.009
# Soft shaped garment outline; exact collar/upper anchor rows0..7 retained.
front=[(0,0),(.11,0),(.24,-.007),(.48,-.013),(.68,-.010),(.9,-.003),(1,-.012)]
rear=[(0,0),(.11,0),(.30,.004),(.52,.010),(.78,.012),(1,.015)]
for i,vertex in enumerate(body.data.vertices):
 row,col=divmod(i,17);t=row/64;s=col/16
 if row<=7:continue
 vertex.co.x+=(1-s)*M.interp(t,rear)+s*M.interp(t,front)
 h=M.smooth((t-.86)/.14);vertex.co.z+=h*(.014*(1-s)**6+.011*s**6+.002*math.sin(math.pi*s)**2)
body.data.update();basis=body.shape_key_add(name='Basis | V051 soft coat, anchored collar');horizontal=body.shape_key_add(name='V051 | hem inertia X | metres');vertical=body.shape_key_add(name='V051 | hem settling Z | metres')
for key,axis in [(horizontal,0),(vertical,2)]:
 key.slider_min=-.04;key.slider_max=.04
 for i,p in enumerate(key.data):
  row,col=divmod(i,17);t=row/64;s=col/16;w=M.smooth((t-.28)/.72);w*=.75+.25*(1-s)
  if axis==0:p.co.x+=w
  else:p.co.z+=w
 for i in range(129):key.value=float(values[i%128,axis//2]);key.keyframe_insert('value',frame=1+i/4)
action=body.data.shape_keys.animation_data.action;action.name='V051 BOY coat | damped support-driven hem response |32frames'
for l in action.layers:
 for st in l.strips:
  for bag in st.channelbags:
   for fc in bag.fcurves:
    for k in fc.keyframe_points:k.interpolation='LINEAR'
    cy=fc.modifiers.new('CYCLES');cy.mode_before=cy.mode_after='REPEAT'
body['V051_fabric']='Original painting/UVs on editable soft contour and two native garment shape keys. Damped hip-acceleration response,14-cycle periodic warmup. Collar rows0..7 pinned. No rig/gait changes.'
# Keep both sleeves bound to the SAME original pose caches and timing. Quiet
# cap bulk and a1mm-scale inner elbow compression leave top/cuff rows fixed.
sleeve_records=[]
for side in ['near','far']:
 o=next(o for o in C.objects if o.parent==r and o.get('wardrobe_role')=='sleeve' and o.name.endswith(side));assert len(o.data.shape_keys.key_blocks)==128
 def fitted(f):
  pose=poses[f];verts=M.limb_vertices(r,pose,side,'sleeve');a=pose['upper_arm_'+side]['tail']-pose['upper_arm_'+side]['head'];d=pose['forearm_'+side]['tail']-pose['forearm_'+side]['head'];flex=math.degrees(a.angle(d));strength=max(0,min(1,(flex-8)/7));out=[]
  for i,p in enumerate(verts):
   row,col=divmod(i,9);t=row/48;s=col/8
   if row<=3 or row>=46:out.append(p);continue
   left=verts[row*9];right=verts[row*9+8];normal=(right-left).normalized();cap=.003*math.sin(math.pi*max(0,min(1,(t-.06)/.73)))**2 if t<.79 else 0
   fold=.0013*strength*math.exp(-((t-.86)/.075)**2);inner=fold*(s*s-.25);p=p-normal*((s*2-1)*cap+inner);out.append(p)
  return out
 for i,key in enumerate(o.data.shape_keys.key_blocks):
  f=1. if i==0 else 1+i/4;verts=fitted(f);key.data.foreach_set('co',[c for p in verts for c in p])
  if i==0:o.data.vertices.foreach_set('co',[c for p in verts for c in p])
 o.data.update();o['V051_fabric']='Same actual bones and original cache Action. Cap bulk reduced up to3mm; inner elbow fold about1mm. First4/last3rows unchanged.';sleeve_records.append(o.name)
for name,h in protected.items():assert ah(bpy.data.actions[name])==h,name
anchor=max((body.data.vertices[i].co-p).length for i,p in enumerate(rawbody) if i//17<=7);assert anchor==0
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==SOURCE_HASH;S.frame_set(1);bpy.context.view_layer.update();native=P/'native/WTSC_Controlled_Fluid_Coat_v051.blend'
report={'source':str(SRC),'source_sha256':SOURCE_HASH,'all_existing_actions_preserved':protected,'gait_changed':False,'body_timing_changed':False,'original_images_materials_and_uvs_edited':False,'coat_top_anchor_error_m':anchor,'outline_front_delta_keys_m':front,'outline_rear_delta_keys_m':rear,'hem_corner_rounding_m':[.014,.011],'fabric_driver':'Actual existing pelvis local accelerations, quarter-frame samples, periodic damped spring. No full3D cloth simulation.','spring_hz':3.2,'damping_ratio':zeta,'warmup_cycles':14,'hip_acceleration_x_range_m_s2':[float(acc[:,0].min()),float(acc[:,0].max())],'hip_acceleration_z_range_m_s2':[float(acc[:,2].min()),float(acc[:,2].max())],'hem_x_range_m':[float(values[:,0].min()),float(values[:,0].max())],'hem_z_range_m':[float(values[:,1].min()),float(values[:,1].max())],'periodic_state_seam_error_m':float(np.linalg.norm(x-values[0])),'sleeves':sleeve_records,'samples':[{'source_frame':1+i/4,'hem_x_m':float(values[i%128,0]),'hem_z_m':float(values[i%128,1])} for i in range(129)],'scope':'Cloth-only candidate, exact v050 gait/face/hands/scale retained. Same-pose and normal-speed A/B needed. Technical checks are not artistic approval.'};(P/'evidence/FLUID_COAT_BUILD.json').write_text(json.dumps(report,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);print('V051_CONTROLLED_FLUID_COAT_NATIVE_SAVED_GAIT_UNCHANGED')
