import bpy,sys,json,hashlib,csv,importlib.util
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1];R=P.parents[1];sys.path.insert(0,str(P/'scripts'));import story_poses as M
source=R/'locomotion/motion_refinement_unpainted_v012/native/WTSC_Unpainted_Motion_Rebuild_v012.blend'
protected=[source,R/'locomotion/motion_refinement_unpainted_v012/scripts/motion_design.py',R/'locomotion/motion_refinement_unpainted_v012/WTSC_v012_Unpainted_Stumble_Recovery_Walk_6s.mp4',R/'shots/world/WTSC_Open_Battlefield_Supported_Trial_v046.blend']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
hashes={str(p):sha(p) for p in protected};(P/'evidence/protected_inputs.json').write_text(json.dumps(hashes,indent=2))
# Existing rig/mesh infrastructure only. Old procedural actions are discarded.
spec=importlib.util.spec_from_file_location('source_rig_rest_reference',str(R/'locomotion/motion_refinement_unpainted_v012/scripts/motion_design.py'));old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
samples={w:{} for w in M.POSES}
for who,rows in M.POSES.items():
 for key in rows:
  try:samples[who][key['frame']]=M.sample_key(who,key)
  except ValueError as e:raise ValueError((who,key['frame'],key['intent'],str(e))) from e
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;s.name='V013 | WHOLE POSE STEPPED BLOCKING';pair=bpy.data.collections['WTSC_UNPAINTED_MOTION_REBUILD_v012'];pair.name='WTSC_WHOLE_POSE_BLOCKING_v013'
for ob in list(bpy.data.objects):
 ob.animation_data_clear()
 if ob.type=='FONT' or ob.name.startswith(('BOY | mass','BOY | support','GIRL | mass','GIRL | support')):bpy.data.objects.remove(ob,do_unlink=True)
for action in list(bpy.data.actions):bpy.data.actions.remove(action)
for text in list(bpy.data.texts):bpy.data.texts.remove(text)
rigs={o['character']:o for o in pair.objects if o.type=='ARMATURE'}
def stepped(action):
 for layer in action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for fc in bag.fcurves:
     for k in fc.keyframe_points:k.interpolation='CONSTANT'
for who,rig in rigs.items():
 first=old.sample(who,1);initial_offset=Vector((first['root_x'],0,0));rest={b.name:(b.head_local.copy(),b.tail_local.copy()) for b in rig.data.bones};restM={b.name:b.matrix_local.copy() for b in rig.data.bones}
 rig.name=who+' | V013 whole-pose blocking rig';rig['motion_status']='Stepped whole-pose study. No recurring gait curves. Review before any curve polish.'
 for f,row in samples[who].items():
  rig.location=(row['root_x'],0,0);rig.keyframe_insert('location',frame=f);off=Vector((row['root_x'],0,0));poses={}
  for name,(A,B) in row['segments'].items():
   ra,rb=rest[name];q=(rb-ra).rotation_difference(B-A);poses[name]=Matrix.Translation(A-off)@q.to_matrix().to_4x4()@Matrix.Translation(-ra)@restM[name]
   if name=='head' and row['face']<0:poses[name]=poses[name]@Matrix.Diagonal((-1,1,1,1))
  for side in ['near','far']:
   name='foot_'+side;poses[name]=Matrix.Translation(-off)@row['feet'][side]['matrix']@first['feet'][side]['matrix'].inverted()@Matrix.Translation(initial_offset)@restM[name]
  for name,mp in poses.items():
   pb=rig.pose.bones[name];pb.rotation_mode='QUATERNION';pb.matrix_basis=pb.bone.convert_local_to_pose(mp,pb.bone.matrix_local,parent_matrix=poses[pb.parent.name] if pb.parent else Matrix.Identity(4),parent_matrix_local=pb.parent.bone.matrix_local if pb.parent else Matrix.Identity(4),invert=True)
   for field in ['location','rotation_quaternion','scale']:pb.keyframe_insert(field,frame=f,group=name)
 rig.animation_data.action.name=who+' | V013 authored complete poses STEPPED';stepped(rig.animation_data.action)
for mode,width in [('INSPECTION',4.8),('SHOT_SIZE',10.4)]:
 cam=bpy.data.objects['TEST | '+mode];cam.location=(.94,-12,.80);cam.data.ortho_scale=width
block=bpy.data.objects['Low test obstacle | far toe track only'];block.location=(.5575,.052,.020)
s.frame_start=1;s.frame_end=72;s.render.fps=24;s.camera=bpy.data.objects['TEST | INSPECTION'];s.eevee.taa_render_samples=8;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100
for key in list(s.timeline_markers):s.timeline_markers.remove(key)
for who,rows in M.POSES.items():
 for row in rows:s.timeline_markers.new(who+' | '+row['intent'],frame=row['frame'])
pair['purpose']='V013 whole-pose blocking only. v012 gate failed. No walking extension, curve polish, painting or production integration.'
pair['head_design_note']='Girl uses one stepped local-X proxy head reflection at12 to block attending profile. No edge-on card rotation, inbetween turn or painted hair/braid solution is claimed.'
for filename in ['story_poses.py','build_blocking.py']:
 t=bpy.data.texts.new(filename);t.write((P/'scripts'/filename).read_text())
# Check evaluated keys before saving; a technical issue must not masquerade as acting.
error=0.
for f in M.KEYS:
 s.frame_set(f);bpy.context.view_layer.update()
 for who,rig in rigs.items():
  row=M.sample(who,f)
  for name,(A,B) in row['segments'].items():
   pb=rig.pose.bones[name];error=max(error,(rig.matrix_world@pb.head-A).length,(rig.matrix_world@pb.tail-B).length)
assert error<1e-5,error
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Whole_Pose_Blocking_v013.blend'),compress=True)
report={'host':bpy.app.version_string,'build_hash':bpy.app.build_hash.decode(),'source_rig':str(source),'authored_key_frames':{w:[p['frame'] for p in rows] for w,rows in M.POSES.items()},'actual_pose_counts':{w:len(rows) for w,rows in M.POSES.items()},'frames':72,'fps':24,'duration_s':3,'interpolation':'CONSTANT; held key poses and deliberate breakdowns. No generated inbetween gait or polished curves.','evaluated_key_joint_error_m':error,'head_profile_note':pair['head_design_note'],'scope':'Blocking candidate only. No artistic approval, walking extension, painting or production integration.'}
(P/'evidence/build_report.json').write_text(json.dumps(report,indent=2));(P/'evidence/authored_story_poses.json').write_text(json.dumps(M.POSES,indent=2))
with (P/'evidence/world_motion_samples.csv').open('w',newline='') as out:
 wr=csv.writer(out);wr.writerow(['frame','seconds','character','exposed_story_key','intent','root_x','hip_z','near_x','near_contact','far_x','far_contact'])
 for f in range(1,73):
  for w in rigs:
   row=M.sample(w,f);wr.writerow([f,(f-1)/24,w,row['key_frame'],row['intent'],row['root_x'],row['hip_z'],row['feet']['near']['x'],row['feet']['near']['state'],row['feet']['far']['x'],row['feet']['far']['state']])
assert all(sha(Path(p))==h for p,h in hashes.items());print('V013_BLOCKING_BUILT',json.dumps(report),flush=True)
