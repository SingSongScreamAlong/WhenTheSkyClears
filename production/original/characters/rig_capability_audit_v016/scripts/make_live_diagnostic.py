"""Controlled rig diagnostics, not a new story performance."""
import bpy,sys,math,json,copy
from pathlib import Path
from mathutils import Matrix,Vector
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'scripts'));import rig_pose_api as api
bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Painted_Rig_Capability_v016.blend'),load_ui=False,use_scripts=False)
S=bpy.context.scene;rigs,controls=api.initialize_from_scene()
def snapshot(frame):
 S.frame_set(frame);bpy.context.view_layer.update()
 return {'controls':{k:{'basis':o.matrix_basis.copy(),'props':{n:o[n] for n in ['Reach','Brace','BraceFollow','TorsoFollow'] if n in o}} for k,o in controls.items()},'rigs':{w:{'location':r.location.copy(),'angles':{b.name:c.pole_angle for b in r.pose.bones for c in b.constraints if c.type=='IK'}} for w,r in rigs.items()}}
snap={f:snapshot(f) for f in [1,41,101,161,181]}
def clear_actions():
 for o in [*controls.values(),*rigs.values()]:
  if o.animation_data:
   o.animation_data.action=None
   for track in list(o.animation_data.nla_tracks):o.animation_data.nla_tracks.remove(track)
 for a in list(bpy.data.actions):bpy.data.actions.remove(a)
def apply(state):
 for w,r in rigs.items():
  r.location=state['rigs'][w]['location']
  for b in r.pose.bones:
   for c in b.constraints:
    if c.type=='IK':c.pole_angle=state['rigs'][w]['angles'][b.name]
 for key,ob in controls.items():
  ob.matrix_basis=state['controls'][key]['basis']
  for n,v in state['controls'][key]['props'].items():ob[n]=v
  ob.update_tag()
 bpy.context.view_layer.update()
clear_actions();apply(snap[1]);S.frame_start=1;S.frame_end=1;S.frame_set(1)
S['native_asset_role']='UNKEYED editable control asset. Technical linkage study; art readiness remains unpassed.'
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Painted_Rig_Control_Asset_v016.blend'),compress=True)
sections=[('PLANT_HIP_EDIT',41),('HEEL_FLAT_TOE_ROLL',101),('PAINTED_BRACE_FOLLOW',161),('PROFILE_HEAD_BRAID',181)]
samples=[]
def lerp(keys,u):
 for (a,x),(b,y) in zip(keys,keys[1:]):
  if u<=b:return x+(y-x)*max(0,min(1,(u-a)/(b-a)))
 return keys[-1][1]
for frame in range(1,97):
 S.frame_set(frame);index=(frame-1)//24;u=((frame-1)%24)/23;name,base=sections[index]
 saved=[]
 for o in [*controls.values(),*rigs.values()]:
  if o.animation_data and o.animation_data.action:saved.append((o,o.animation_data.action,o.animation_data.action_slot));o.animation_data.action=None
 apply(snap[base])
 if index in [0,2]:
  for w in rigs:
   c=controls[w,'HIP'];M=c.matrix_world.copy();M.translation+=Vector((.012*math.sin(math.pi*u) if index==0 else .005*math.sin(math.pi*u),0,-.015*math.sin(math.pi*u) if index==0 else .009*math.sin(2*math.pi*u)));c.matrix_world=M
 elif index==1:
  for w in rigs:
   side='near' if u<.5 else 'far';q=u*2 if u<.5 else (u-.5)*2
   deg=lerp([(0,-12),(.25,0),(.55,30),(.8,10),(1,0)],q);lift=lerp([(0,0),(.55,0),(.8,.035),(1,0)],q)
   api.set_foot(w,side,.13 if side=='near' else -.10,deg,lift)
 else:
  for w in rigs:
   c=controls[w,'HEAD_PROFILE'];M=c.matrix_world.copy();c.matrix_world=Matrix.Translation(M.translation)@Matrix.Rotation(math.radians(5*math.sin(2*math.pi*u)),4,'Y')@Matrix.Translation(-M.translation)@M
 bpy.context.view_layer.update()
 errs=[]
 for w,r in rigs.items():
  for side in ['near','far']:
   for n,t in [('shin','ANKLE_'),('forearm','WRIST_')]:errs.append((r.pose.bones[n+'_'+side].tail-r.matrix_world.inverted()@controls[w,t+side].matrix_world.translation).length)
 samples.append({'frame':frame,'section':name,'u':u,'max_IK_error_m':max(errs)})
 for o,a,slot in saved:o.animation_data.action=a;o.animation_data.action_slot=slot
 for r in rigs.values():r.keyframe_insert('location',frame=frame)
 api.key_controls(frame)
 if (frame-1)%24==0:S.timeline_markers.new(name,frame=frame)
# Per-frame linear keys expose the test directly; there is no automatic gait.
for o in [*controls.values(),*rigs.values()]:
 for l in o.animation_data.action.layers:
  for st in l.strips:
   for bag in st.channelbags:
    for fc in bag.fcurves:
     for k in fc.keyframe_points:k.interpolation='LINEAR'
for m in list(S.timeline_markers):
 if m.name.startswith(tuple(str(i).zfill(2)+'_' for i in range(1,13))):S.timeline_markers.remove(m)
S.frame_start=1;S.frame_end=96;S.render.fps=24;S.frame_set(1);S['native_asset_role']='Four-second technical control diagnostic, not story performance or approved final art.'
S.render.resolution_x=960;S.render.resolution_y=540
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Painted_Rig_Live_Diagnostic_v016.blend'),compress=True)
(P/'evidence/live_diagnostic_samples.json').write_text(json.dumps(samples,indent=2))
for mode in ['INSPECTION','MATCHED_SHOT']:
 folder=P/'previews'/mode;folder.mkdir(exist_ok=True)
 if mode=='MATCHED_SHOT':
  info=json.loads((P/'evidence/actual_v046_camera.json').read_text());S.camera.data.type=info['type'];S.camera.data.lens=info['lens'];S.camera.data.sensor_width=info['sensor_width'];S.camera.data.sensor_fit=info['sensor_fit'];S.camera.data.shift_x=info['shift_x'];S.camera.data.shift_y=info['shift_y'];S.camera.matrix_world=Matrix(info['relative_to_pair_root'])
 for f in (range(1,97) if mode=='INSPECTION' else [1,13,25,37,49,61,73,85]):
  S.frame_set(f);S.render.filepath=str(folder/f'{f:04d}.png');bpy.ops.render.render(write_still=True)
print('V016_LIVE_DIAGNOSTIC_COMPLETE','MAX_IK',max(p['max_IK_error_m'] for p in samples))
