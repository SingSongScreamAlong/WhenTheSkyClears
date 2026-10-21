"""Undo only the added positive boy torso/head lean in the narrow tangent window.
Keep all other evaluated bone matrices, native drawings and clocks from v010.
"""
import bpy,math
from mathutils import Matrix
def sm(a,b,t):
 u=max(0,min(1,(t-a)/(b-a)));return u*u*(3-2*u)
def cv(keys,t):
 if t<=keys[0][0]:return keys[0][1]
 for (a,x),(b,y) in zip(keys,keys[1:]):
  if t<=b:return x+(y-x)*sm(a,b,t)
 return keys[-1][1]
def correction_angle(f):
 added=cv([(24,0),(31,-.035),(37,.045),(43,.065),(51,-.025),(62,.01),(77,0)],f)
 return max(0,added)*sm(37,40,f)*(1-sm(47,51,f))
def linear(action):
 for layer in action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for fc in bag.fcurves:
     for key in fc.keyframe_points:key.interpolation='LINEAR'
def apply_correction(scene,root,start):
 rig=next(o for o in root.children_recursive if o.type=='ARMATURE' and o.get('character')=='BOY');poses={}
 for f in range(1,169):
  scene.frame_set(start+f-1);bpy.context.view_layer.update();p={b.name:b.matrix.copy() for b in rig.pose.bones};a=correction_angle(f)
  if a:
   hip=p['pelvis'].translation;undo=Matrix.Translation(hip)@Matrix.Rotation(-a,4,'Y')@Matrix.Translation(-hip)
   for name in ['chest','head']:p[name]=undo@p[name]
  poses[f]=p
 rig.animation_data.action=None
 for track in list(rig.animation_data.nla_tracks):rig.animation_data.nla_tracks.remove(track)
 rig.animation_data.action=bpy.data.actions.new('V010a_BOY__NARROW_ADDED_LEAN_REVERT_168F')
 for f,p in poses.items():
  for name,m in p.items():
   bone=rig.pose.bones[name];bone.rotation_mode='QUATERNION';bone.matrix=m
   for field in ['location','rotation_quaternion','scale']:bone.keyframe_insert(field,frame=f,group=name)
 action=rig.animation_data.action;linear(action);slot=rig.animation_data.action_slot;rig.animation_data.action=None;track=rig.animation_data.nla_tracks.new();track.name='V010a narrow lean correction';strip=track.strips.new(action.name,start,action);strip.action_slot=slot;strip.action_frame_start=1;strip.action_frame_end=168;strip.frame_end=start+167;strip.extrapolation='HOLD';action.use_fake_user=True
 root['motion_revision']='v010a_lean_gap_correction';root['correction_scope']='Only positive added boy chest/head lean feathered local38..48; full removal40..47. Arms, girl, drawings, root/boots and continuation retained.'
 return {'changed_local_frames':[f for f in range(1,169) if correction_angle(f)>1e-10],'angle_removed_radians':{str(1800+f):correction_angle(f) for f in range(38,49)},'target_bones':['BOY/chest','BOY/head'],'other_bone_world_matrices':'Retained explicitly from v010; preservation verified after cold reopen.'}
