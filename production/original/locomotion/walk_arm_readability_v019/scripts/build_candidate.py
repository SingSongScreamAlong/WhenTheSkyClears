"""Wrist paths/order only; retain the v018 gait, body and native contact keys."""
import bpy,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];sys.path.insert(0,str(P/'scripts'));import rig_pose_api as api
SRC=ROOT/'locomotion/reference_walk_exercise_v018/native/WTSC_Boy_Travelling_Walk_v018.blend'
bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False,use_scripts=False);S=bpy.context.scene;r,c=api.initialize_from_scene();rig=r['BOY']
def fcurves(ob):
 if ob.animation_data and ob.animation_data.action:
  for l in ob.animation_data.action.layers:
   for st in l.strips:
    for bag in st.channelbags:
     for fc in bag.fcurves:yield fc
def action_data(ob,exclude=False):
 rows=[]
 for fc in fcurves(ob):
  if exclude and fc.data_path in ['location','rotation_quaternion','["FrontLayer"]']:continue
  rows.append({'path':fc.data_path,'index':fc.array_index,'extrapolation':fc.extrapolation,'keys':[[*k.co,k.interpolation] for k in fc.keyframe_points]})
 return sorted(rows,key=lambda x:(x['path'],x['index']))
def digest(x):return hashlib.sha256(json.dumps(x,separators=(',',':'),sort_keys=True).encode()).hexdigest()
before={o.name:digest(action_data(o, bool(o.get('v016_control','').startswith('WRIST')))) for o in S.objects}
times=sorted({round(float(k.co.x),8) for fc in fcurves(c['BOY','WRIST_near']) for k in fc.keyframe_points})
for side in ['near','far']:
 ob=c['BOY','WRIST_'+side];ob.animation_data.action=ob.animation_data.action.copy();ob.animation_data.action.name='V019 | WRIST ARC AND ORDER | '+side
 # Preserve all unrelated wrist channels and the source key times.
 for l in ob.animation_data.action.layers:
  for st in l.strips:
   for bag in st.channelbags:
    for fc in list(bag.fcurves):
     if fc.data_path in ['location','rotation_quaternion','["FrontLayer"]']:bag.fcurves.remove(fc)
rows=[]
for f in times:
 S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update()
 for side,sign,amp,bend in [('near',-1,28,30),('far',1,24,27)]:
  ob=c['BOY','WRIST_'+side];a=ob.animation_data.action;slot=ob.animation_data.action_slot;ob.animation_data.action=None
  shoulder=rig.pose.bones['upper_arm_'+side].head
  def arc(q):
   a=2*math.pi*q/24
   return sign*amp*math.cos(a)+(12*math.sin(a)**2 if side=='near' else 0)
  u=math.radians(arc(f-1));v=math.radians(arc(f-1-1.5)+bend)
  L1=rig.data.bones['upper_arm_'+side].length;L2=rig.data.bones['forearm_'+side].length;elbow=shoulder+Vector((L1*math.sin(u),0,-L1*math.cos(u)));wrist=elbow+Vector((L2*math.sin(v),0,-L2*math.cos(v)))
  api.set_wrist('BOY',side,wrist.x,wrist.z,math.degrees(v)-98,'Relax',fit_reach=False)
  ob['FrontLayer']=float(side=='far' and (((f-1)%24)<7 or ((f-1)%24)>=18));ob.update_tag();bpy.context.view_layer.update();ob.animation_data.action=a;ob.animation_data.action_slot=slot
  for path in ['location','rotation_quaternion']:ob.keyframe_insert(path,frame=f)
  ob.keyframe_insert('["FrontLayer"]',frame=f)
  rows.append({'frame':f,'side':side,'wrist_local':list(wrist),'FrontLayer':ob['FrontLayer']})
for side in ['near','far']:
 for fc in fcurves(c['BOY','WRIST_'+side]):
  if fc.data_path in ['location','rotation_quaternion','["FrontLayer"]']:
   for k in fc.keyframe_points:k.interpolation='CONSTANT' if fc.data_path.startswith('["') else 'LINEAR'
after={o.name:digest(action_data(o, bool(o.get('v016_control','').startswith('WRIST')))) for o in S.objects};equal=before==after
report={'scope':'Only wrist location/quaternion curves and far-arm FrontLayer order changed. All other object/rig action channels identical.','allowed_channels':['BOY | WRIST_near location/quaternion','BOY | WRIST_far location/quaternion and FrontLayer'],'non_wrist_action_identity':equal,'before':before,'after':after,'curve_times_unchanged':times,'art_edit':'None. Original painting, geometry, UVs and modifiers retained.','body_foot_travel_timing':'Frozen v018 curves copied without resynthesis.','pose_proposal':'Near swing28deg plus12deg*sin(phase)^2 forward bias, far24deg, elbows30/27deg with existing1.5frame lower-arm phase offset. Hands flex8deg toward vertical relative to forearm. Far layer1 forward phase0..7 and18..24; behind torso during rear phase7..18. Source near always in front.'}
if not equal:raise RuntimeError('Unexpected non-wrist animation edit')
pack=bpy.data.collections['WTSC_BOY_TRAVELLING_WALK_v018'];pack.name='WTSC_BOY_ARM_READABILITY_v019';S['V019_scope']='Bounded wrist/order diagnostic only. Broad artistic rejection of v018 remains; not a finished walk.';S['V019_gait']='All source foot goals, travel, timing, body/head/poles and rig action keys frozen.';rig['V019_status']='Diagnostic, artistic approval NOT PASSED.'
S.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Boy_Arm_Readability_v019.blend'),compress=True)
(P/'evidence/change_contract.json').write_text(json.dumps(report,indent=2));(P/'evidence/wrist_path_proposal.json').write_text(json.dumps(rows,indent=2))
for label,path in [('AFTER',P/'native/WTSC_Boy_Arm_Readability_v019.blend'),('BEFORE',SRC)]:
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);S=bpy.context.scene
 for f in [1,7,10,11,12,13,14,15,16,19,22]:
  S.frame_set(f);S.render.filepath=str(P/f'previews/{label}/{f:04d}.png');bpy.ops.render.render(write_still=True)
print('V019_BOUNDED_CANDIDATE_READY',equal)
