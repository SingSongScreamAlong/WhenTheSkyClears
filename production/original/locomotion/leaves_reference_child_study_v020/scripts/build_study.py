"""Eight reference-timed keys only. No broad in-betweens or new painting."""
import bpy,math,json,sys,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];sys.path.insert(0,str(P/'scripts'));import source_match as M;import rig_pose_api as api
BASE=P/'reference/BASE_CONTROL_ASSET_v017_COPY.blend';SOURCE=P/'native/Leaves_Walk_Source_Inspection_v020.blend';MAP={'near':'R','far':'L'}
def curves(o):
 if o.animation_data and o.animation_data.action:
  for l in o.animation_data.action.layers:
   for st in l.strips:
    for bag in st.channelbags:
     yield from bag.fcurves
def constant(o):
 for fc in curves(o):
  for k in fc.keyframe_points:k.interpolation='CONSTANT'
def detach(objects):
 saved=[]
 for o in objects:
  if o.animation_data and o.animation_data.action:saved.append((o,o.animation_data.action,o.animation_data.action_slot));o.animation_data.action=None
 return saved
def restore(saved):
 for o,a,slot in saved:o.animation_data.action=a;o.animation_data.action_slot=slot
def empty(name,col):o=bpy.data.objects.new(name,None);col.objects.link(o);o.empty_display_size=.015;return o
def material(name,color):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;n=m.node_tree.nodes;n.clear();e=n.new('ShaderNodeEmission');e.inputs[0].default_value=(*color,1);out=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(e.outputs[0],out.inputs[0]);return m
def line(name,pts,col,mat,r=.006):
 d=bpy.data.curves.new(name,'CURVE');d.dimensions='3D';d.bevel_depth=r;d.bevel_resolution=2;s=d.splines.new('POLY');s.points.add(len(pts)-1)
 for p,v in zip(s.points,pts):p.co=(*v,1)
 o=bpy.data.objects.new(name,d);col.objects.link(o);d.materials.append(mat);return o
def native_skeleton(rig,col,bones,colors):
 for name in bones:
  mat=colors['R' if (name.endswith('_R') or name.endswith('_near')) else 'L' if (name.endswith('_L') or name.endswith('_far')) else 'body'];targets=[]
  for end in [0,1]:
   o=empty(col.name+' | '+name+' | '+str(end),col);ct=o.constraints.new('COPY_LOCATION');ct.target=rig;ct.subtarget=name;ct.head_tail=end;targets.append(o)
  ob=line(col.name+' | bone '+name,[(0,0,0),(0,1,0)],col,mat);ct=ob.constraints.new('COPY_LOCATION');ct.target=targets[0];ct=ob.constraints.new('DAMPED_TRACK');ct.target=targets[1];ct.track_axis='TRACK_Y'
  fc=ob.driver_add('scale',1);v=fc.driver.variables.new();v.name='length';v.type='LOC_DIFF';v.targets[0].id=targets[0];v.targets[1].id=targets[1];fc.driver.expression='length'
  bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=4,radius=.011);dot=bpy.context.object;dot.name=col.name+' | joint '+name
  for old in list(dot.users_collection):old.objects.unlink(dot)
  col.objects.link(dot);dot.data.materials.append(mat);ct=dot.constraints.new('COPY_LOCATION');ct.target=targets[0]
def points(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());return [e.matrix_world@v.co for v in e.data.vertices]
# Sample complete original source pose bases before constructing the comparison.
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False);S=bpy.context.scene;src=bpy.data.objects['Armature'];basis={}
phases=M.PHASES['phases']+[dict(M.PHASES['phases'][0],index=9,name='CYCLE_BOOKEND',unwrapped_source_frame=M.FIRST+31,wrapped_source_frame=M.FIRST,study_frame_30fps=32.,source_seconds_from_first_key=(M.FIRST+31-2)/30,seconds_from_study_contact=31/30)]
for p in phases:
 w=p['wrapped_source_frame'];S.frame_set(int(w),subframe=w-int(w));bpy.context.view_layer.update();basis[p['index']]={b.name:[list(x) for x in b.matrix_basis] for b in src.pose.bones}
bpy.ops.wm.open_mainfile(filepath=str(BASE),load_ui=False,use_scripts=False);S=bpy.context.scene
for o in list(bpy.data.objects):
 if 'GIRL' in o.name:bpy.data.objects.remove(o,do_unlink=True)
r,c=api.initialize_from_scene();rig=r['BOY'];T=rig.parent;T.matrix_world=Matrix.Identity(4);T.name='V020 | CHILD_SOURCE_TRAVEL';rig.matrix_basis=Matrix.Identity(4);bpy.context.view_layer.update();pack=bpy.data.collections['WTSC_PAINTED_RIG_CORRECTIVES_v017'];pack.name='WTSC_LEAVES_CHILD_EIGHT_POSES_v020'
for o in S.objects:
 if o.name not in pack.all_objects:o.hide_render=True
for o in list(pack.all_objects):
 if o.animation_data:
  o.animation_data.action=None
  for tr in list(o.animation_data.nla_tracks):o.animation_data.nla_tracks.remove(tr)
paint=[o for o in rig.children if o.type=='MESH'];stage=bpy.data.collections.new('V020 | study stage and sole controls');pack.children.link(stage)
with bpy.data.libraries.load(str(SOURCE),link=False) as (a,b):b.objects=['Armature']
source=b.objects[0];stage.objects.link(source);source.name='V020 | SOURCE52 | exact FBX sampled poses';original=source.animation_data.action;original.use_fake_user=True;original.name='LEAVES ORIGINAL | 30fps | '+original.name;source.animation_data.action=None
orient=empty('V020 | source -Y mapped to +X',stage);orient.rotation_euler.z=math.pi/2;orient.location.x=-M.ROOT_START;source.parent=orient;source.matrix_basis=Matrix(M.DATA['object_matrix'])
goals={}
for side in ['near','far']:
 pivot=empty('V020 | '+side+' | ACTUAL_SOLE_PIVOT',stage);goal=empty('V020 | '+side+' | SOLE_BONE_GOAL',stage);goal.parent=pivot;goal.rotation_mode='QUATERNION';swing=empty('V020 | '+side+' | SWING_BONE_GOAL',stage);swing.rotation_mode='QUATERNION';cts=[]
 for target in [goal,swing]:ct=c['BOY','ANKLE_'+side].constraints.new('COPY_TRANSFORMS');ct.target=target;ct.owner_space='WORLD';ct.target_space='WORLD';ct.mix_mode='REPLACE';ct.name='V020 | '+target.name;cts.append(ct)
 goals[side]=(pivot,goal,swing,cts)
rows=[];root_rows=[];source_pose_errors=[]
for p in phases:
 f=p['study_frame_30fps'];sf=p['unwrapped_source_frame'];S.frame_set(int(f),subframe=f-int(f));saved=detach([*c.values(),rig,T,source,*[o for v in goals.values() for o in v[:3]]]);v=M.parameters(sf,rig,MAP);B=v['source'];D=v['root_travel_m'];T.location=(D,0,0);bpy.context.view_layer.update()
 for side in ['near','far']:
  pivot,goal,swing,cts=goals[side];F,meta=v['foot'][side];is_contact=meta['mode']=='CONTACT_POLYGON_PIVOT';cts[0].influence=float(is_contact);cts[1].influence=float(not is_contact)
  if is_contact:pivot.location=meta['anchor'];pivot.rotation_euler=(0,meta['angle_rad'],0);goal.matrix_basis=Matrix.Translation(-Vector(meta['pivot_flat']))@Matrix(M.BOOTS[side]['flat_bone']);pivot['active_vertex']=meta['active_vertex']
  swing.matrix_world=F;bpy.context.view_layer.update()
 H=v['hip_fitted']-Vector((D,0,0));rest=rig.data.bones;pel=rest['pelvis'].matrix_local
 api.target('BOY','HIP',Matrix.Translation(H)@Matrix.Rotation(v['pelvis_angle'],4,'Y')@Matrix.Translation(-pel.translation)@pel)
 rest_ch=rest['chest'].tail_local-rest['chest'].head_local;chrot=v['chest_angle']-math.atan2(rest_ch.x,rest_ch.z);cd=Matrix.Translation(H)@Matrix.Rotation(chrot,4,'Y')@Matrix.Translation(-pel.translation);api.target('BOY','CHEST',cd@rest['chest'].matrix_local)
 hr=rest['head'].matrix_local;h0=cd@hr;rest_hd=rest['head'].tail_local-rest['head'].head_local;hd=v['head_angle']-chrot-math.atan2(rest_hd.x,rest_hd.z);api.target('BOY','HEAD_PROFILE',Matrix.Translation(h0.translation)@Matrix.Rotation(hd,4,'Y')@Matrix.Translation(-h0.translation)@h0)
 for side in ['near','far']:
  A=rig.matrix_world.inverted()@v['foot'][side][0].translation;api.target('BOY','LEG_POLE_'+side,Matrix.Translation((H.x+1,0,(H.z+A.z)/2)))
 bpy.context.view_layer.update();arms=[]
 for side in ['near','far']:
  srcside=MAP[side];S0=rig.pose.bones['upper_arm_'+side].head;su=M.point(B,'Elbow_'+srcside)-M.point(B,'Shoulder_'+srcside);sv=M.point(B,'Hand_'+srcside)-M.point(B,'Elbow_'+srcside);su.normalize();sv.normalize();E=S0+su*rest['upper_arm_'+side].length;W=E+sv*rest['forearm_'+side].length
  # Source directional match with exact child lengths, not adult endpoints.
  arm_total=rest['upper_arm_'+side].length+rest['forearm_'+side].length;gap=arm_total-(W-S0).length;soft=0.
  if gap<.00025:old=W.copy();W=S0+(W-S0).normalized()*(arm_total-.00025);soft=(W-old).length
  hdir=M.point(B,'Hand_'+srcside,'tail')-M.point(B,'Hand_'+srcside);angle=math.atan2(hdir.z,hdir.x);hb=rest['hand_'+side];hvec=hb.tail_local-hb.head_local;rot=math.atan2(math.cos(angle),math.sin(angle))-math.atan2(hvec.x,hvec.z);HM=Matrix.Translation(W)@Matrix.Rotation(rot,4,'Y')@hb.matrix_local.to_3x3().to_4x4();ob=c['BOY','WRIST_'+side]
  for key in ['TorsoFollow','BraceFollow','Reach','Brace']:ob[key]=0.
  ob['FrontLayer']=float(side=='far' and W.x>S0.x);ob.update_tag();api.target('BOY','WRIST_'+side,HM);pole=E+(E-(S0+W)/2)*4;api.target('BOY','ARM_POLE_'+side,Matrix.Translation(pole));arms.append({'side':side,'source_side':srcside,'ideal_elbow':list(E),'wrist':list(W),'source_direction_softening_m':soft})
 api.choose_planes('BOY',{});bpy.context.view_layer.update()
 # Original source pose basis and real cumulative root translation are retained.
 loop=math.floor((sf-2)/31);source.matrix_basis=Matrix(M.DATA['object_matrix']);source.location.y-=loop*1.5
 for bone in source.pose.bones:bone.matrix_basis=Matrix(basis[p['index']][bone.name])
 bpy.context.view_layer.update();srcerr=max(((source.matrix_world@source.pose.bones[n].head)-Vector((-B[n]['head'].y-M.ROOT_START,B[n]['head'].x,B[n]['head'].z))).length for n in M.DATA['bones']);source_pose_errors.append(srcerr)
 feet=[]
 for side in ['near','far']:
  ob=bpy.data.objects[M.BOOTS[side]['object']];V=points(ob);meta=v['foot'][side][1];feet.append({'side':side,**meta,'minimum_drawn_sole_z_m':min(x.z for x in V),'actual_contact_error_m':(V[meta['active_vertex']]-Vector(meta['anchor'])).length if 'active_vertex' in meta else None})
 row={**p,'root_travel_m':D,'child_stride_m':v['stride_m'],'leg_scale':v['scale'],'hip_wanted':list(v['hip_wanted']),'hip_fitted':list(v['hip_fitted']),'hip_correction_m':v['hip_correction_m'],'pelvis_degrees':math.degrees(v['pelvis_angle']),'chest_degrees':math.degrees(v['chest_angle']),'head_degrees':math.degrees(v['head_angle']),'arms':arms,'feet':feet,'IK':api.reach_report(),'source_pose_world_error_m':srcerr};rows.append(row);root_rows.append({'source_frame':sf,'study_frame':f,'seconds_from_study_start':(sf-M.FIRST)/30,'root_travel_m':D})
 restore(saved);api.key_controls(f);T.keyframe_insert('location',frame=f);source.keyframe_insert('location',frame=f)
 for bone in source.pose.bones:
  bone.rotation_mode='QUATERNION'
  for field in ['location','rotation_quaternion','scale']:bone.keyframe_insert(field,frame=f)
 for side in ['near','far']:
  pivot,goal,swing,cts=goals[side]
  for o in [pivot,goal,swing]:
   if o==pivot:
    o.keyframe_insert('location',frame=f);o.keyframe_insert('rotation_euler',frame=f)
   else:
    for field in ['location','rotation_quaternion','scale']:o.keyframe_insert(field,frame=f)
  for ct in cts:ct.keyframe_insert('influence',frame=f)
for o in [*c.values(),rig,T,source,*[o for v in goals.values() for o in v[:3]]]:constant(o)
S.render.fps=30;S.frame_start=1;S.frame_end=32;S.render.resolution_x=640;S.render.resolution_y=360;S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG';S.render.engine='BLENDER_EEVEE';S.view_settings.view_transform='Standard';S.view_settings.look='None';S.world.use_nodes=True;S.world.node_tree.nodes['Background'].inputs[0].default_value=(.88,.85,.78,1);S.world.node_tree.nodes['Background'].inputs[1].default_value=.8
if hasattr(S.eevee,'taa_render_samples'):S.eevee.taa_render_samples=32
colors={'R':material('V020 right / child near',(.48,.23,.14)),'L':material('V020 left / child far',(.13,.36,.39)),'body':material('V020 torso',(.25,.24,.21))};ground=material('V020 ground',(.45,.43,.39));line('V020 fixed metre ground',[(-1,-.14,0),(3,-.14,0)],stage,ground,.0015)
for i in range(-4,13):line('V020 fixed tick '+str(i),[(i*.25,-.14,0),(i*.25,-.14,-.025)],stage,ground,.001)
srcSkel=bpy.data.collections.new('V020 | source skeleton render');pack.children.link(srcSkel);childSkel=bpy.data.collections.new('V020 | child native skeleton render');pack.children.link(childSkel)
source_bones=['Hips','Spine_01','Spine_02','Spine_03','Neck','Head','Clavicle_R','Shoulder_R','Elbow_R','Hand_R','Clavicle_L','Shoulder_L','Elbow_L','Hand_L','UpperLeg_R','LowerLeg_R','Ankle_R','Ball_R','UpperLeg_L','LowerLeg_L','Ankle_L','Ball_L'];native_skeleton(source,srcSkel,source_bones,colors);native_skeleton(rig,childSkel,[b.name for b in rig.data.bones],colors)
rootTracker=empty('V020 | SOURCE root camera tracking',stage);ct=rootTracker.constraints.new('COPY_LOCATION');ct.target=source;ct.subtarget='Root';ct.use_y=False;ct.use_z=False;cameras={}
for who,parent in [('SOURCE',rootTracker),('CHILD',T)]:
 for scale in ['CLOSE','SHOT']:
  cam=bpy.data.objects.new('V020 | '+who+' | '+scale,bpy.data.cameras.new('V020 '+who+' '+scale));stage.objects.link(cam);cam.parent=parent
  if scale=='CLOSE':cam.location=(0,-7,.79);cam.rotation_euler=(math.pi/2,0,0);cam.data.type='ORTHO';cam.data.ortho_scale=3.55
  else:cam.matrix_basis=Matrix(((1,0,0,1.7280044556),(0,-4.371e-8,-1,-16),(0,1,-4.371e-8,2.2799263),(0,0,0,1)));cam.data.type='PERSP';cam.data.lens=100;cam.data.sensor_width=36;cam.data.sensor_fit='HORIZONTAL';cam.data.shift_x=-.3000002205;cam.data.shift_y=-.2670553327
  cameras[who,scale]=cam
srcSkel.hide_render=True;childSkel.hide_render=True;S.camera=cameras['CHILD','CLOSE'];S['V020_status']='Eight unique reference-matched stepped poses plus duplicate bookend. No finished walk or in-betweens. Source adult is reference only.';S['V020_mapping']='Child near=sourceR;far=sourceL. Original proportions, painting and planar profile retained. Projected source directions; native sole polygons; pelvis reach accommodation reported.';S['V020_timing']='Source30fps; period31frames /1.0333s. Child stride1.021383492m from average leg ratio0.680922328. Contact onset inferred without source heel joint.'
S.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Leaves_Reference_Child_Eight_Poses_v020.blend'),compress=True);(P/'evidence/eight_pose_matching.json').write_text(json.dumps(rows,indent=2));(P/'reference/DERIVED_TRAVEL_KEYS_v020.json').write_text(json.dumps(root_rows,indent=2))
print('V020_MATCHING',json.dumps({'bad_IK':[(x['name'],q) for x in rows for q in x['IK'] if not q['reachable']],'source_pose_error_m':max(source_pose_errors),'max_hip_accommodation_m':max(x['hip_correction_m'] for x in rows)}))
for p in M.PHASES['phases']:
 f=p['study_frame_30fps'];S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update()
 for mode in ['SOURCE','CHILD_SKELETON','PAINTED']:
  srcSkel.hide_render=mode!='SOURCE';childSkel.hide_render=mode!='CHILD_SKELETON'
  for ob in paint:ob.hide_render=mode!='PAINTED'
  for scale in ['CLOSE','SHOT']:
   S.camera=cameras['SOURCE' if mode=='SOURCE' else 'CHILD',scale];path=P/f'previews/{mode}_{scale}';path.mkdir(exist_ok=True);S.render.filepath=str(path/f'{p["index"]:02d}.png');bpy.ops.render.render(write_still=True)
print('V020_EIGHT_POSE_COMPARISON_RENDERED')
