import bpy,sys,json,math
from pathlib import Path
from mathutils import Matrix,Vector
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];sys.path.insert(0,str(P/'scripts'));import rig_pose_api as api
BASE=P/'reference/BASE_EIGHTPOSE_SOURCE_v020_COPY.blend';SOL=json.loads((P/'evidence/coherent_pose_solution.json').read_text());BOOTS=json.loads((P/'reference/ORIGINAL_BOY_BOOT_PIVOTS_v018.json').read_text());OLD=json.loads((P/'reference/v020_eight_pose_matching.json').read_text());DATA=json.loads((P/'reference/fbx_source_inspection.json').read_text());SRC={r['frame']:r for r in DATA['samples']}
def source(f):
 w=round(2+(f-2)%31,6);B=SRC[w]['bones'];return {n:{e:Vector((-v[e][1],0,v[e][2])) for e in ['head','tail']} for n,v in B.items()}
def rows_fc(o):
 if o.animation_data and o.animation_data.action:
  for l in o.animation_data.action.layers:
   for st in l.strips:
    for bag in st.channelbags:yield from bag.fcurves
def keys_constant(o):
 for fc in rows_fc(o):
  for k in fc.keyframe_points:k.interpolation='CONSTANT'
def clear_action(o):
 if o.animation_data:
  o.animation_data.action=None
  for t in list(o.animation_data.nla_tracks):o.animation_data.nla_tracks.remove(t)
def points(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());return [e.matrix_world@v.co for v in e.data.vertices]
bpy.ops.wm.open_mainfile(filepath=str(BASE),load_ui=False,use_scripts=False);S=bpy.context.scene;r,c=api.initialize_from_scene();rig=r['BOY'];T=rig.parent;T.name='V021 | CHILD_SUPPORT_TRAVEL';pack=bpy.data.collections['WTSC_LEAVES_CHILD_EIGHT_POSES_v020'];pack.name='WTSC_CHILD_SUPPORT_POSES_v021';sourceRig=bpy.data.objects['V020 | SOURCE52 | exact FBX sampled poses'];sourceRig.hide_set(False)
def expose(lc):
 if lc.name.startswith('V020 |') and 'skeleton render' in lc.name:lc.hide_viewport=False
 for child in lc.children:expose(child)
for vl in S.view_layers:expose(vl.layer_collection)
goals={}
for side in ['near','far']:
 pivot=bpy.data.objects['V020 | '+side+' | ACTUAL_SOLE_PIVOT'];goal=bpy.data.objects['V020 | '+side+' | SOLE_BONE_GOAL'];swing=bpy.data.objects['V020 | '+side+' | SWING_BONE_GOAL'];cts=[ct for ct in c['BOY','ANKLE_'+side].constraints if ct.type=='COPY_TRANSFORMS'];goals[side]=(pivot,goal,swing,cts)
animated=[*c.values(),rig,T,*[o for g in goals.values() for o in g[:3]]]
for o in animated:clear_action(o)
phases=SOL['poses'];book=json.loads(json.dumps(phases[0]));book['index']=9;book['name']='CYCLE_BOOKEND';book['unwrapped_source_frame']+=31;book['study_frame_30fps']=32;book['seconds_from_study_contact']=31/30;book['source_seconds_from_first_key']+=31/30;book['root_travel_m']=SOL['cycle_stride_m'];book['hip_world_xz'][0]+=SOL['cycle_stride_m']
for d in book['feet'].values():
 d['ankle_xz'][0]+=SOL['cycle_stride_m']
 if 'anchor_xz' in d:d['anchor_xz'][0]+=SOL['cycle_stride_m'];d['flat_x']+=SOL['cycle_stride_m']
allposes=phases+[book];results=[]
for p in allposes:
 f=p['study_frame_30fps'];S.frame_set(int(f),subframe=f-int(f));saved=[]
 for o in animated:
  if o.animation_data and o.animation_data.action:saved.append((o,o.animation_data.action,o.animation_data.action_slot));o.animation_data.action=None
 D=p['root_travel_m'];T.location=(D,0,0);bpy.context.view_layer.update();Hworld=Vector((p['hip_world_xz'][0],0,p['hip_world_xz'][1]));H=Hworld-Vector((D,0,0));rest=rig.data.bones
 for side in ['near','far']:
  d=p['feet'][side];pivot,goal,swing,cts=goals[side];contact=d['mode']=='CONTACT_POLYGON_PIVOT';cts[0].influence=float(contact);cts[1].influence=float(not contact);flat=Matrix(BOOTS[side]['flat_bone']);a=d['angle_rad'];F=Matrix.Rotation(a,4,'Y')@flat.to_3x3().to_4x4();F.translation=(d['ankle_xz'][0],0,d['ankle_xz'][1]);swing.matrix_world=F
  if contact:
   pv=Vector(BOOTS[side]['vertices'][d['vertex']]);pivot.location=(d['anchor_xz'][0],pv.y,d['anchor_xz'][1]);pivot.rotation_euler=(0,a,0);pivot['active_vertex']=d['vertex'];goal.matrix_basis=Matrix.Translation(-pv)@flat
  bpy.context.view_layer.update()
 pel=rest['pelvis'].matrix_local;api.target('BOY','HIP',Matrix.Translation(H)@Matrix.Rotation(p['pelvis_rad'],4,'Y')@Matrix.Translation(-pel.translation)@pel)
 old=OLD[(p['index']-1)%8] if p['index']!=9 else OLD[0];ch=math.radians(old['chest_degrees']);hd=math.radians(old['head_degrees']);rv=rest['chest'].tail_local-rest['chest'].head_local;chrot=ch-math.atan2(rv.x,rv.z);cd=Matrix.Translation(H)@Matrix.Rotation(chrot,4,'Y')@Matrix.Translation(-pel.translation);api.target('BOY','CHEST',cd@rest['chest'].matrix_local);h0=cd@rest['head'].matrix_local;hv=rest['head'].tail_local-rest['head'].head_local;turn=hd-chrot-math.atan2(hv.x,hv.z);api.target('BOY','HEAD_PROFILE',Matrix.Translation(h0.translation)@Matrix.Rotation(turn,4,'Y')@Matrix.Translation(-h0.translation)@h0)
 bpy.context.view_layer.update()
 for side in ['near','far']:
  hip=rig.pose.bones['thigh_'+side].head;u=p['native_leg_angle_rad'][side][0];K=hip+Vector((math.sin(u),0,-math.cos(u)))*rest['thigh_'+side].length;A=Vector((p['feet'][side]['ankle_xz'][0]-D,0,p['feet'][side]['ankle_xz'][1]));pole=K+(K-(hip+A)/2)*4;api.target('BOY','LEG_POLE_'+side,Matrix.Translation(pole))
 B=source(p['unwrapped_source_frame']);arm_rows=[]
 for side,ss in [('near','R'),('far','L')]:
  sh=rig.pose.bones['upper_arm_'+side].head;u=(B['Elbow_'+ss]['head']-B['Shoulder_'+ss]['head']).normalized();v=(B['Hand_'+ss]['head']-B['Elbow_'+ss]['head']).normalized();E=sh+u*rest['upper_arm_'+side].length;W=E+v*rest['forearm_'+side].length;L=rest['upper_arm_'+side].length+rest['forearm_'+side].length
  if L-(W-sh).length<.00025:W=sh+(W-sh).normalized()*(L-.00025)
  hdir=B['Hand_'+ss]['tail']-B['Hand_'+ss]['head'];ang=math.atan2(hdir.z,hdir.x);hb=rest['hand_'+side];d=hb.tail_local-hb.head_local;rot=math.atan2(math.cos(ang),math.sin(ang))-math.atan2(d.x,d.z);M=Matrix.Translation(W)@Matrix.Rotation(rot,4,'Y')@hb.matrix_local.to_3x3().to_4x4();ob=c['BOY','WRIST_'+side]
  for key in ['TorsoFollow','BraceFollow','Reach','Brace']:ob[key]=0.
  ob['FrontLayer']=float(side=='far' and W.x>sh.x);ob.update_tag();api.target('BOY','WRIST_'+side,M);api.target('BOY','ARM_POLE_'+side,Matrix.Translation(E+(E-(sh+W)/2)*4));arm_rows.append({'side':side,'wrist_local':list(W)})
 api.choose_planes('BOY',{});bpy.context.view_layer.update();feet=[];angles=[]
 for side in ['near','far']:
  ob=bpy.data.objects[BOOTS[side]['object']];V=points(ob);d=p['feet'][side];contact_error=(V[d['vertex']]-Vector((d['anchor_xz'][0],V[d['vertex']].y,d['anchor_xz'][1]))).length if 'vertex' in d else None;feet.append({'side':side,'mode':d['mode'],'actual_sole_min_z_m':min(v.z for v in V),'active_contact_error_m':contact_error})
  for bone,a,b in [('thigh','UpperLeg_','LowerLeg_'),('shin','LowerLeg_','Ankle_')]:
   ss='R' if side=='near' else 'L';desired=(B[b+ss]['head']-B[a+ss]['head']).normalized();pb=rig.pose.bones[bone+'_'+side];actual=pb.tail-pb.head;actual.y=0;angles.append({'side':side,'bone':bone,'source_angle_residual_deg':math.degrees(actual.angle(desired))})
 results.append({'phase':p['name'],'study_frame':f,'source_frame':p['unwrapped_source_frame'],'hip_world':list(Hworld),'hip_local':list(H),'foot':feet,'leg_residuals':angles,'IK':api.reach_report()})
 for o,a,slot in saved:o.animation_data.action=a;o.animation_data.action_slot=slot
 api.key_controls(f);T.keyframe_insert('location',frame=f)
 for side in ['near','far']:
  pivot,goal,swing,cts=goals[side]
  for o in [pivot,goal,swing]:
   for path in ['location','scale']:o.keyframe_insert(path,frame=f)
   o.keyframe_insert('rotation_euler' if o==pivot else 'rotation_quaternion',frame=f)
  for ct in cts:ct.keyframe_insert('influence',frame=f)
for o in animated:keys_constant(o)
S['V021_status']='Eight corrected support poses; no continuous animation. Original child proportions/painting; global step and free pelvis solve, explicit source residuals.';S['V021_stride_m']=SOL['cycle_stride_m'];S['V021_no_post_fit_pelvis_projection']=True;S['V021_source_limit']='Adult reference and contact onset estimates retained; not approved child acting.';rig['V021_art']='Base unchanged. Separate variant demonstrates one passing-pose corrective only.'
S.frame_set(1);srcCol=bpy.data.collections['V020 | source skeleton render'];skelCol=bpy.data.collections['V020 | child native skeleton render'];srcCol.hide_render=True;skelCol.hide_render=True;paint=[o for o in rig.children if o.type=='MESH']
for ob in paint:ob.hide_render=False
S.camera=bpy.data.objects['V020 | CHILD | CLOSE'];bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Child_Coherent_Support_Eight_Poses_v021.blend'),compress=True);(P/'evidence/authored_native_poses.json').write_text(json.dumps(results,indent=2))
print('V021_NATIVE',json.dumps({'bad_IK':[(x['phase'],q) for x in results for q in x['IK'] if not q['reachable']],'max_leg_residual_deg':max(q['source_angle_residual_deg'] for x in results for q in x['leg_residuals'])}))
for p in phases:
 f=p['study_frame_30fps'];S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update()
 for mode in ['SOURCE','CHILD_SKELETON','PAINTED']:
  srcCol.hide_render=mode!='SOURCE';skelCol.hide_render=mode!='CHILD_SKELETON'
  for ob in paint:ob.hide_render=mode!='PAINTED'
  for scale in ['CLOSE','SHOT']:
   S.camera=bpy.data.objects['V020 | '+('SOURCE' if mode=='SOURCE' else 'CHILD')+' | '+scale];out=P/f'previews/{mode}_{scale}';out.mkdir(exist_ok=True);S.render.filepath=str(out/f'{p["index"]:02d}.png');bpy.ops.render.render(write_still=True)
print('V021_CORRECTED_POSES_RENDERED')
