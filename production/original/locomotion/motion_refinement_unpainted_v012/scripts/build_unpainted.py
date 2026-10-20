import bpy,sys,math,json,csv,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1];R=P.parents[1];sys.path.insert(0,str(P/'scripts'));import motion_design as M
for folder in ['native','evidence','previews']:(P/folder).mkdir(exist_ok=True)
protected=['locomotion/stumble_polish_continuation_v010/native/WTSC_Stumble_Polish_Continuation_v010.blend','locomotion/stumble_polish_continuation_v010/native/WTSC_v010_Matched_Review_Copy.blend','locomotion/stumble_polish_continuation_v010/WTSC_v010_Matched_5s_Polish_PLUS_Separate_2s_Continuation.mp4','shots/world/WTSC_Open_Battlefield_Supported_Trial_v046.blend']
protected+=['locomotion/motion_rebuild_unpainted_v011/native/WTSC_Unpainted_Motion_Rebuild_v011.blend','locomotion/motion_rebuild_unpainted_v011/WTSC_v011_Unpainted_Stumble_Recovery_Walk_6s.mp4','locomotion/motion_rebuild_unpainted_v011/evidence/world_motion_samples.csv']
(P/'evidence/protected_inputs.json').write_text(json.dumps({n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in protected},indent=2))
samples={w:{f:M.sample(w,f) for f in range(1,M.N+1)} for w in M.PROPORTIONS}
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.name='V012 | UNPAINTED FUNDAMENTAL MOTION TEST';s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;s.render.fps=24;s.frame_start=1;s.frame_end=M.N;s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=8;s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=2
pair=bpy.data.collections.new('WTSC_UNPAINTED_MOTION_REBUILD_v012');s.collection.children.link(pair);stage=bpy.data.collections.new('TEST STAGE | no production assets');s.collection.children.link(stage);diag=bpy.data.collections.new('OPTIONAL | support and mass proxy diagnostics');s.collection.children.link(diag);diag.hide_render=True
def place(ob,col):
 for c in list(ob.users_collection):c.objects.unlink(ob)
 col.objects.link(ob);return ob
def mat(name,rgb):
 out=bpy.data.materials.new(name);out.diffuse_color=(*rgb,1);out.use_nodes=True;p=out.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*rgb,1);p.inputs['Roughness'].default_value=.86;return out
colors={'BOY':(.12,.19,.23),'GIRL':(.33,.19,.12)};materials={w:{'near':mat(w+' | plain proxy',color),'far':mat(w+' | far limb',tuple(v*.72+.12 for v in color))} for w,color in colors.items()};floorMat=mat('Neutral test ground',(.60,.61,.60));tickMat=mat('World fixed ticks',(.33,.36,.36));green=mat('Diagnostic support',(.12,.48,.23));orange=mat('Diagnostic mass proxy',(.8,.3,.05))
def ellipsoid(name,A,B,rx,ry,col,material):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=10,radius=1);ob=bpy.context.object;ob.name=name;place(ob,col);v=B-A;T=Matrix.Translation((A+B)*.5)@Vector((0,0,1)).rotation_difference(v).to_matrix().to_4x4()@Matrix.Diagonal((rx,ry,v.length*.5,1));ob.data.transform(T);ob.data.materials.append(material)
 for poly in ob.data.polygons:poly.use_smooth=True
 return ob
def bind(ob,rig,bone):
 ob.parent=rig;group=ob.vertex_groups.new(name=bone);group.add(list(range(len(ob.data.vertices))),1,'REPLACE');mod=ob.modifiers.new('Editable native bone deformation','ARMATURE');mod.object=rig;ob['test_only']='Unpainted proxy. No production character mesh or material.'
def linear(action):
 for layer in action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for fc in bag.fcurves:
     for k in fc.keyframe_points:k.interpolation='LINEAR'
rigs={};ref={}
for who,prop in M.PROPORTIONS.items():
 first=samples[who][1];x0=first['root_x'];offset=Vector((x0,0,0));rest={n:(A-offset,B-offset) for n,(A,B) in first['segments'].items()}
 for side in ['near','far']:
  A=first['feet'][side]['ankle'];B=first['feet'][side]['matrix']@Vector((.135,0,.025));B.y=A.y;rest['foot_'+side]=(A-offset,B-offset)
 data=bpy.data.armatures.new(who+' | rebuilt joint structure');rig=bpy.data.objects.new(who+' | native unpainted rig',data);pair.objects.link(rig);rig['character']=who;rig['height_basis_m']=prop['height'];rig['motion_status']='New diagnostic motion; previous v010 motion artistically rejected.';rigs[who]=rig;bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
 for name,(A,B) in rest.items():b=data.edit_bones.new(name);b.head=A;b.tail=B
 for name,b in data.edit_bones.items():
  parent='pelvis' if name in ['lumbar'] or name.startswith('thigh_') else 'lumbar' if name=='chest' else 'neck' if name=='head' else 'chest' if name=='neck' or name.startswith('upper_arm_') else 'thigh_'+name.split('_')[-1] if name.startswith('shin_') else 'shin_'+name.split('_')[-1] if name.startswith('foot_') else 'upper_arm_'+name.split('_')[-1] if name.startswith('forearm_') else 'forearm_'+name.split('_')[-1] if name.startswith('hand_') else None
  if parent:b.parent=data.edit_bones[parent]
 bpy.ops.object.mode_set(mode='OBJECT');rig.select_set(False);ref[who]={'x0':x0,'rest':rest,'bone_matrices':{b.name:b.matrix_local.copy() for b in data.bones}}
 for name,(A,B) in rest.items():
  if name.startswith('foot_'):continue
  side='far' if name.endswith('far') else 'near';material=materials[who][side]
  if name=='pelvis':ob=ellipsoid(who+' | pelvis mass',A-Vector((0,0,.045)),A+Vector((0,0,.095)),.085,.060,pair,material)
  elif name=='head':ob=ellipsoid(who+' | plain head',A,B,prop['head'][0],.065,pair,material)
  else:
   radius=.095 if name=='lumbar' else .105 if name=='chest' else .035 if name=='neck' else .043 if name.startswith('thigh_') else .030 if name.startswith('shin_') else .030 if name.startswith('upper_arm_') else .023 if name.startswith('forearm_') else .024
   ob=ellipsoid(who+' | '+name,A-(B-A).normalized()*.008,B+(B-A).normalized()*.008,radius,.05 if name in ['lumbar','chest'] else radius*.8,pair,material)
  bind(ob,rig,name)
 # Simple nose establishes forward direction; no face/turnaround artwork.
 A,B=rest['head'];center=(A+B)*.5;me=bpy.data.meshes.new(who+' proxy profile nose');me.from_pydata([center+Vector((prop['head'][0]-.01,-.04,-.035)),center+Vector((prop['head'][0]+.035,-.04,-.070)),center+Vector((prop['head'][0]-.01,-.04,-.095))],[],[(0,1,2)]);ob=bpy.data.objects.new(who+' | fixed profile cue',me);pair.objects.link(ob);me.materials.append(materials[who]['near']);bind(ob,rig,'head')
 if who=='GIRL':
  A,B=rest['head'];a=A+Vector((-.12,.025,.15));b=A+Vector((-.18,.025,.055));c=A+Vector((-.205,.025,-.025))
  for i,(q,r) in enumerate([(a,b),(b,c)]):ob=ellipsoid('GIRL | fixed simple braid cue'+str(i),q,r,.025,.022,pair,materials[who]['near']);bind(ob,rig,'head')
 for side in ['near','far']:
  ft=first['feet'][side];dep=-.052 if side=='near' else .052;verts=[ft['matrix']@Vector((x,y+dep,z))-offset for x,y,z in [(-.075,-.032,0),(.135,-.032,0),(.135,.032,0),(-.075,.032,0),(-.075,-.032,.045),(.105,-.032,.045),(.105,.032,.045),(-.075,.032,.045)]];me=bpy.data.meshes.new(who+' '+side+' foot');me.from_pydata(verts,[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);ob=bpy.data.objects.new(who+' | flat sole '+side,me);pair.objects.link(ob);me.materials.append(materials[who][side]);bind(ob,rig,'foot_'+side)
  bevel=ob.modifiers.new('Small proxy bevel','BEVEL');bevel.width=.004;bevel.segments=2;ob['foot_side']=side
  # A rigid boot/ankle bridge overlaps the shin tip and sole instead of floating.
  a=ft['ankle']+Vector((0,0,.012))-offset;b=ft['matrix']@Vector((.015,dep,.024))-offset;ob=ellipsoid(who+' | ankle connector '+side,a,b,.027,.026,pair,materials[who][side]);bind(ob,rig,'foot_'+side);ob['attachment_role']='ankle_connector'
 # Every joint is native, editable and preserves segment length. No sampled v010 Action.
 for f,row in samples[who].items():
  rig.location=(row['root_x'],0,0);rig.keyframe_insert('location',frame=f);off=Vector((row['root_x'],0,0));poses={}
  for name,(A,B) in row['segments'].items():
   ra,rb=rest[name];q=(rb-ra).rotation_difference(B-A);poses[name]=Matrix.Translation(A-off)@q.to_matrix().to_4x4()@Matrix.Translation(-ra)@ref[who]['bone_matrices'][name]
  for side in ['near','far']:
   name='foot_'+side;poses[name]=Matrix.Translation(-off)@row['feet'][side]['matrix']@first['feet'][side]['matrix'].inverted()@Matrix.Translation(offset)@ref[who]['bone_matrices'][name]
  for name,Mpose in poses.items():
   pb=rig.pose.bones[name];pb.rotation_mode='QUATERNION'
   # Resolve each keyed basis against explicit target parent matrices; assigning
   # pose matrices against stale parent evaluation displaces connected pieces.
   parent_matrix=poses[pb.parent.name] if pb.parent else Matrix.Identity(4);parent_rest=pb.parent.bone.matrix_local if pb.parent else Matrix.Identity(4)
   pb.matrix_basis=pb.bone.convert_local_to_pose(Mpose,pb.bone.matrix_local,parent_matrix=parent_matrix,parent_matrix_local=parent_rest,invert=True)
   for field in ['location','rotation_quaternion','scale']:pb.keyframe_insert(field,frame=f,group=name)
 rig.animation_data.action.name=who+' | V012 new weight and contact performance144F';linear(rig.animation_data.action)
 # Optional mass/stance diagnostic objects, hidden in primary preview.
 for name in ['mass','support_near','support_far']:
  bpy.ops.mesh.primitive_uv_sphere_add(segments=10,ring_count=6,radius=1);ob=place(bpy.context.object,diag);ob.name=who+' | '+name;ob.data.materials.append(orange if name=='mass' else green)
  for f,row in samples[who].items():
   if name=='mass':ob.location=row['com_proxy'];ob.scale=(.018,.018,.018);ob.hide_render=False
   else:
    side=name.split('_')[-1];ft=row['feet'][side];ob.hide_render=ft['state']=='swing';q=(ft['heel']+ft['toe'])*.5 if ft['state']=='flat' else ft['toe'] if ft['state'].startswith('toe') else ft['heel'];ob.location=(q.x,-.16,-.012);ob.scale=(.105 if ft['state']=='flat' else .02,.012,.007)
   ob.keyframe_insert('location',frame=f);ob.keyframe_insert('scale',frame=f);ob.keyframe_insert('hide_render',frame=f)
  linear(ob.animation_data.action)
def cube(name,location,scale,material):
 bpy.ops.mesh.primitive_cube_add(size=1,location=location);ob=place(bpy.context.object,stage);ob.name=name;ob.scale=scale;ob.data.materials.append(material);return ob
cube('World-fixed floor line',(2.,.20,-.015),(15.,.04,.025),floorMat)
# Visible geometry for a toe interruption, not an explosion or production obstacle.
cube('Low test obstacle | far toe track only',(.7775,.052,.020),(.045,.066,.040),tickMat)
for i in range(-12,33):cube('World tick '+str(i),(i*.25,.18,-.048),(.006,.02,.065),tickMat)
# Matte studio lighting. No source painting, world, smoke, audio or production camera.
s.world=bpy.data.worlds.new('Plain test world');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.73,.75,.74,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.8
lightdata=bpy.data.lights.new('Soft test light','AREA');light=bpy.data.objects.new('Soft test light',lightdata);stage.objects.link(light);light.location=(1,-4,5);light.rotation_euler=(Vector((1,0,.8))-light.location).to_track_quat('-Z','Y').to_euler();lightdata.energy=450;lightdata.shape='DISK';lightdata.size=5
cameras={}
for name,width in [('INSPECTION',5.4),('SHOT_SIZE',10.4)]:
 data=bpy.data.cameras.new(name);data.type='ORTHO';data.ortho_scale=width;camera=bpy.data.objects.new('TEST | '+name,data);stage.objects.link(camera);camera.rotation_euler=(math.pi/2,0,0);cameras[name]=camera
 for f in range(1,145):
  camera.location=((samples['BOY'][f]['root_x']+samples['GIRL'][f]['root_x'])*.5,-12,.82);camera.keyframe_insert('location',frame=f)
 linear(camera.animation_data.action)
s.camera=cameras['INSPECTION']
def text(name,body,y,size):
 data=bpy.data.curves.new(name,'FONT');data.body=body;data.size=size;data.materials.append(tickMat);ob=bpy.data.objects.new(name,data);stage.objects.link(ob);ob.parent=cameras['INSPECTION'];ob.location=(-2.45,y,-5);return ob
text('Test title','UNPAINTED / NEW WEIGHT AND TIMING TEST',1.20,.11)
for a,b,label in [(1,22,'APPROACH'),(23,29,'TOE INTERRUPTION / MOMENTUM'),(30,40,'CATCH STEP / COMPRESSION'),(41,65,'WEIGHT OVER FRONT FOOT'),(66,83,'RESTART'),(84,144,'CONTINUE WALK')]:
 ob=text('Phase '+label,label,1.02,.085)
 for f in range(1,145):ob.hide_render=not(a<=f<=b);ob.keyframe_insert('hide_render',frame=f)
for file in ['motion_design.py','build_unpainted.py']:
 t=bpy.data.texts.new(file);t.write((P/'scripts'/file).read_text())
joint_error=0
for f in range(1,145):
 s.frame_set(f);bpy.context.view_layer.update()
 for who,rig in rigs.items():
  for name,(A,B) in samples[who][f]['segments'].items():
   pb=rig.pose.bones[name];joint_error=max(joint_error,(rig.matrix_world@pb.head-A).length,(rig.matrix_world@pb.tail-B).length)
  for side in ['near','far']:joint_error=max(joint_error,(rig.matrix_world@rig.pose.bones['foot_'+side].head-samples[who][f]['feet'][side]['ankle']).length)
assert joint_error<1e-5,joint_error
for ob in stage.objects:
 if ob.type=='FONT':ob.animation_data_clear();ob.hide_render=True
pair['purpose']='Isolated unpainted refinement. v011 failed the repaint gate; no production integration or artistic approval.';s.view_settings.view_transform='Standard';s.render.filepath=str(P/'previews/INSPECTION');s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Unpainted_Motion_Rebuild_v012.blend'),compress=True)
report={'version':bpy.app.version_string,'frames':144,'fps':24,'duration_s':6,'new_motion':'Independent roots, toe scuff, catch-step loading, front-foot recovery, shorter low restart steps. No source v010 curves retained.','proportion_basis':M.PROPORTIONS,'kinematic_changes':'Overall child height/head/body/reach preserved approximately; elbow positions rebuilt so boy forearm is not less than half the upper-arm length.','not_physics':'Authored support-aware kinematics, fixed segment lengths and mass proxy. No force/dynamics or measured child mocap claim.','camera':'Separate pair-average follow; source world not used. Inspection and shot-size cameras.','source_assets':'None imported. No painting, cloth, FX, title, music or full-trailer edits.'}
report['all144_evaluated_joint_target_error_m']=joint_error
report['v012_changes']='Toe interruption at24 with forward incoming speed and pinned toe/heel kick; catch36/load40; girl controlled heel26/load29 and waiting support shift; phased pelvis/chest/head and earlier toe release; continuous boot/ankle proxy geometry. No repaint gate claimed.'
(P/'evidence/build_report.json').write_text(json.dumps(report,indent=2))
with (P/'evidence/world_motion_samples.csv').open('w',newline='') as out:
 wr=csv.writer(out);wr.writerow(['frame','seconds','character','root_x','hip_z','desired_hip_z','com_proxy_x','com_proxy_z','near_x','near_state','far_x','far_state'])
 for f in range(1,145):
  for w in samples:
   row=samples[w][f];wr.writerow([f,(f-1)/24,w,row['root_x'],row['hip_z'],row['desired_hip_z'],row['com_proxy'].x,row['com_proxy'].z,row['feet']['near']['x'],row['feet']['near']['state'],row['feet']['far']['x'],row['feet']['far']['state']])
(P/'evidence/joint_targets.json').write_text(json.dumps({w:{str(f):{'joints':{k:list(v) for k,v in row['joints'].items()},'feet':{side:{k:list(v) if isinstance(v,Vector) else v for k,v in ft.items() if k!='matrix'} for side,ft in row['feet'].items()}} for f,row in rows.items()} for w,rows in samples.items()}))
assert all(hashlib.sha256((R/n).read_bytes()).hexdigest()==sha for n,sha in json.loads((P/'evidence/protected_inputs.json').read_text()).items());print('V012_UNPAINTED_BUILT',json.dumps(report),flush=True)
