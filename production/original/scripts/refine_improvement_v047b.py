"""Review-driven correction: remove knob caps, connect hand direction and taper cuffs."""
import bpy,json,hashlib,math,sys
from pathlib import Path
from mathutils import Vector, Matrix
R=Path(__file__).resolve().parents[1];N=R/'notes/improvement_v047'
previous=json.loads((N/'build_v047a.json').read_text());source=Path(bpy.data.filepath)
assert hashlib.sha256(source.read_bytes()).hexdigest()==previous['sha256']
version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v047b'
assert version in ['v047b','v047c']
out=R/f'shots/world/WTSC_Open_Battlefield_Refinement_{version}.blend';assert not out.exists()
s=bpy.data.scenes[previous['world_scene']];m=bpy.data.scenes[previous['master_scene']];bpy.context.window.scene=s
root=next(o for o in s.objects if o.get('motion_revision')=='v007_drawn_pose_corrections')
rigs={o['character']:o for o in root.children_recursive if o.type=='ARMATURE'}
bone_before={};camera_before={}
for f in range(1801,1921):
 s.frame_set(f);bpy.context.view_layer.update()
 bone_before[f]={who:{p.name:p.matrix.copy() for p in rig.pose.bones} for who,rig in rigs.items()}
 camera_before[f]=s.camera.matrix_world.copy()
removed=[]
for name in previous['rounded_arm_transitions']:
 ob=bpy.data.objects[name];removed.append(name);bpy.data.objects.remove(ob,do_unlink=True)
hands=[];tapers=[]
for who,rig in rigs.items():
 for side in ['near','far']:
  arm=next(o for o in rig.children if o.name==f'V007_{who} | drawn skin {side}')
  hand=next(o for o in rig.children if 'articulated drawn hand '+side in o.name)
  rest=rig.data.bones['hand_'+side].matrix_local.copy();max_rotation=0.;changes=[]
  for key in hand.data.shape_keys.key_blocks:
   local=1 if key.name=='Basis' else int(key.name.rsplit('_',1)[1])
   f=1800+local;s.frame_set(f);bpy.context.view_layer.update()
   skin=arm.data.shape_keys.key_blocks['POSE_'+str(local).zfill(3)]
   a=(skin.data[0].co+skin.data[1].co)*.5;b=(skin.data[-2].co+skin.data[-1].co)*.5
   d=b-a;desired=math.atan2(d.z,d.x)
   pose=rig.pose.bones['hand_'+side].matrix.copy();axis=pose.to_3x3()@Vector((0,1,0))
   angle=math.atan2(axis.z,axis.x);delta=(desired-angle+math.pi)%(math.tau)-math.pi
   # Preserve the offered-touch and brace drawings when direction is credible.
   # Only backward-facing hands that fold into their forearm get redirected.
   weight=max(0,min(1,(abs(delta)-math.radians(60))/math.radians(35)))
   weight=weight*weight*(3-2*weight)
   if version=='v047c':
    settle=max(0,min(1,(local-67)/13));settle=settle*settle*(3-2*settle)
    weight*=1-settle # Preserve all late offered-touch/brace drawing orientations.
   correction=delta*weight;max_rotation=max(max_rotation,abs(correction))
   if abs(correction)>1e-6:
    anchor=pose.translation.copy();transform=Matrix.Translation(anchor)@Matrix.Rotation(-correction,4,'Y')@Matrix.Translation(-anchor)
    mapping=rest@pose.inverted()@transform@pose@rest.inverted()
    for v in key.data:v.co=mapping@v.co
    changes.append(local)
  hands.append({'character':who,'side':side,'changed_local_frames':changes,'max_drawn_rotation_degrees':math.degrees(max_rotation),
                'method':'Only drawing coordinates rotate about existing wrist. Original hand bone/action and wrist anchor remain unchanged. Backward-pointing silhouette corrected toward arm direction.'})
  # Narrow the drawn wrist gradually into the existing palm width.
  for key in arm.data.shape_keys.key_blocks:
   count=len(key.data)//2
   for i in range(count):
    t=i/(count-1);u=max(0,min(1,(t-.72)/.28));u=u*u*(3-2*u);factor=1-.28*u
    a=key.data[2*i].co.copy();b=key.data[2*i+1].co.copy();c=(a+b)*.5
    key.data[2*i].co=c+(a-c)*factor;key.data[2*i+1].co=c+(b-c)*factor
  sleeve=next(o for o in rig.children if o.name==f'V007_{who} | drawn sleeve {side}')
  cuff=next(o for o in rig.children if o.name==f'V007_{who} | drawn source gray cuff {side}')
  for ob in [sleeve,cuff]:
   for key in ob.data.shape_keys.key_blocks:
    count=len(key.data)//2
    for i in range(count):
     t=i/(count-1);u=t if ob==sleeve else .833333+.166667*t
     edge=max(0,min(1,(u-.58)/.42));edge=edge*edge*(3-2*edge);factor=1-.22*edge
     a=key.data[2*i].co.copy();b=key.data[2*i+1].co.copy();c=(a+b)*.5
     key.data[2*i].co=c+(a-c)*factor;key.data[2*i+1].co=c+(b-c)*factor
  tapers.append({'character':who,'side':side,'wrist_width_factor':.72,'sleeve_cuff_end_factor':.78})

error=0.;cam_error=0.
for f in range(1801,1921):
 s.frame_set(f);bpy.context.view_layer.update()
 for who,rig in rigs.items():
  for p in rig.pose.bones:
   error=max(error,max(abs(p.matrix[i][j]-bone_before[f][who][p.name][i][j]) for i in range(4) for j in range(4)))
 cam_error=max(cam_error,max(abs(s.camera.matrix_world[i][j]-camera_before[f][i][j]) for i in range(4) for j in range(4)))
assert error==cam_error==0
s.name='WTSC_OPEN_BATTLEFIELD_REFINEMENT_'+version;m.name='WTSC_OPEN_5S_REFINEMENT_MASTER_'+version
report=dict(previous);report.update({'native':str(out),'world_scene':s.name,'master_scene':m.name,
 'previous_iteration':{'native':str(source),'sha256':previous['sha256'],'review':'Head drawings improve the turn. Circular arm caps read as exposed mechanical knobs; rejected and removed.'},
 'rounded_arm_transitions':[],'removed_knob_caps':removed,'hand_drawing_corrections':hands,'tapered_arm_contours':tapers,
 'all120_errors':{'camera':cam_error,'all_rig_bone_matrices':error},
 'scope':'Same new painterly turn drawings and GP contours. Removed failed round caps; corrected backward hand silhouette direction at fixed wrists, tapered cuffs/forearms. Body/feet/root/camera/world/FXv003/actions preserved.',
 'artistic_acceptance':False,'full_trailer_propagated':False})
if version=='v047c':
 report['reviewed_intermediate']={'native':str(R/'shots/world/WTSC_Open_Battlefield_Refinement_v047b.blend'),
  'finding':'Early hand direction improved, but applying the correction late weakened the offered-touch silhouette. v047c fades corrections out at local67..80; later hand drawing orientations match v046.'}
text=bpy.data.texts.new('CURRENT '+version+' | Reviewed iteration and fixes');text.write(json.dumps(report,indent=2))
bpy.context.window.scene=m;m.frame_set(1844);bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report['sha256']=hashlib.sha256(out.read_bytes()).hexdigest();(N/f'build_{version}.json').write_text(json.dumps(report,indent=2))
print('V047_NATIVE_BUILT',version,json.dumps({'native':str(out),'errors':report['all120_errors'],'hand_max_rotations':[h['max_drawn_rotation_degrees'] for h in hands]}),flush=True)
