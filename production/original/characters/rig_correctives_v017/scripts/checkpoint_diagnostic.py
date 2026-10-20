"""Two-second bounded rig fixture; no walk cycle, performance or tutorial claim."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1];R=P.parents[1];sys.path.insert(0,str(P/'scripts'));import rig_pose_api as api
for folder in ['LIVE_AFTER','LIVE_BEFORE']:(P/'previews'/folder).mkdir(exist_ok=True)
PROPS=['Reach','Brace','BraceFollow','TorsoFollow','FrontLayer']
def scene(path):
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);r,c=api.initialize_from_scene();return bpy.context.scene,r,c
def points(o):
 bpy.context.view_layer.update();e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());return [e.matrix_world@v.co for v in e.data.vertices]
def gap(r):
 leg=next(o for o in r.children if o.get('v007_role')=='drawn_leg' and o.name.endswith('near'));hand=next(o for o in r.children if o.get('v007_role')=='drawn_hand' and o.name.endswith('near'));p=points(leg);t=((p[20]+p[21])-(p[12]+p[13])).normalized();t.y=0;t.normalize();n=Vector((-t.z,0,t.x));return min((q-p[17]).dot(n) for q in points(hand)[:8])
def freeze(c,r):
 for o in [*c.values(),*r.values()]:
  if o.animation_data:
   o.animation_data.action=None
   for tr in list(o.animation_data.nla_tracks):o.animation_data.nla_tracks.remove(tr)
def capture(c,r,travel):
 return {'controls':{o.name:{'matrix':[list(x) for x in o.matrix_basis],'props':{k:o[k] for k in PROPS if k in o}} for o in c.values()},'rigs':{w:{'location':list(o.location),'pole':{b.name:ct.pole_angle for b in o.pose.bones for ct in b.constraints if ct.type=='IK'}} for w,o in r.items()},'travel':[list(x) for x in travel.matrix_basis]}
def apply(state,c,r,travel):
 travel.matrix_basis=Matrix(state['travel'])
 for w,o in r.items():
  o.location=state['rigs'][w]['location']
  for b in o.pose.bones:
   for ct in b.constraints:
    if ct.type=='IK':ct.pole_angle=state['rigs'][w]['pole'][b.name]
 for o in c.values():
  d=state['controls'][o.name];o.matrix_basis=Matrix(d['matrix'])
  for k,v in d['props'].items():
   if k in o:o[k]=v
  o.update_tag()
 bpy.context.view_layer.update()
S,r,c=scene(P/'native/WTSC_Painted_Rig_Corrective_Board_v017.blend');travel=bpy.data.objects['V016 | WORLD_TRAVEL | diagnostic zero'];snap={}
for f in [41,161]:S.frame_set(f);bpy.context.view_layer.update();snap[f]=capture(c,r,travel)
freeze(c,r)
for a in list(bpy.data.actions):bpy.data.actions.remove(a)
cache=[]
for f in range(1,49):
 S.frame_set(f);phase=0 if f<=24 else 1;u=((f-1)%24)/23;saved=[]
 for o in [*c.values(),*r.values()]:
  if o.animation_data and o.animation_data.action:saved.append((o,o.animation_data.action,o.animation_data.action_slot));o.animation_data.action=None
 apply(snap[41 if phase==0 else 161],c,r,travel)
 if phase==0:
  for w,rig in r.items():
   M=c[w,'WRIST_near'].matrix_world.copy();oldS=rig.matrix_world@rig.pose.bones['upper_arm_near'].head;D=M.translation-oldS
   hip=c[w,'HIP'];H=hip.matrix_world.copy();H.translation.z-=.020*math.sin(math.pi*u);hip.matrix_world=H;bpy.context.view_layer.update();newS=rig.matrix_world@rig.pose.bones['upper_arm_near'].head
   A=Matrix.Rotation(math.radians(10*math.sin(2*math.pi*u)),4,'Y');M=A@M;M.translation=newS+A.to_3x3()@D;c[w,'WRIST_near'].matrix_world=M
 else:
  for w in r:
   ob=c[w,'HIP'];M=ob.matrix_world.copy();M.translation+=Vector((.005*math.sin(2*math.pi*u),0,.009*math.sin(math.pi*u)));ob.matrix_world=M
 bpy.context.view_layer.update();cache.append({'frame':f,'phase':'CUFF_REACH_AND_COMPRESSION' if phase==0 else 'PAINTED_BRACE_FOLLOW','state':capture(c,r,travel)})
 for o,a,slot in saved:o.animation_data.action=a;o.animation_data.action_slot=slot
 for rig in r.values():rig.keyframe_insert('location',frame=f)
 api.key_controls(f)
for o in [*c.values(),*r.values()]:
 for layer in o.animation_data.action.layers:
  for st in layer.strips:
   for bag in st.channelbags:
    for fc in bag.fcurves:
     mode='CONSTANT' if 'pole_angle' in fc.data_path or fc.data_path.startswith('["') else 'LINEAR'
     for k in fc.keyframe_points:k.interpolation=mode
S.frame_start=1;S.frame_end=48;S.render.fps=24;S.render.resolution_x=960;S.render.resolution_y=540;S['diagnostic_scope']='Two bounded control fixtures; hard cut24->25. Not a walk, performance or tutorial emulation.';S.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Painted_Rig_Diagnostic_v017.blend'),compress=True)
# Fresh saved-file integer and fractional-frame validation; hard cut excluded.
S,r,c=scene(P/'native/WTSC_Painted_Rig_Diagnostic_v017.blend');boots=[o for rig in r.values() for o in rig.children if o.get('v007_role')=='support_boot'];samples=[];base=None
for phase in range(2):
 for i in range(47):
  t=1+phase*24+i*.5;S.frame_set(int(t),subframe=t-int(t));bpy.context.view_layer.update()
  if i==0:base={o.name:points(o) for o in boots}
  samples.append({'sample_frame':t,'IK':api.reach_report(),'boot_drift_m':max(max((a-b).length for a,b in zip(base[o.name],points(o))) for o in boots),'palm_gap_m':{w:gap(rig) for w,rig in r.items()} if phase else None})
(P/'evidence/interpolated_diagnostic_validation.json').write_text(json.dumps(samples,indent=2))
for f in range(1,49):
 S.frame_set(f);S.render.filepath=str(P/f'previews/LIVE_AFTER/{f:04d}.png');bpy.ops.render.render(write_still=True)
# Replay identical target data on the immutable v016 asset for a true before
# comparison. No original file is saved or changed.
S,r,c=scene(R/'characters/rig_capability_audit_v016/native/WTSC_Painted_Rig_Control_Asset_v016.blend');travel=bpy.data.objects['V016 | WORLD_TRAVEL | diagnostic zero'];S.render.resolution_x=960;S.render.resolution_y=540
for row in cache:
 apply(row['state'],c,r,travel);S.render.filepath=str(P/f'previews/LIVE_BEFORE/{row["frame"]:04d}.png');bpy.ops.render.render(write_still=True)
(P/'evidence/diagnostic_target_cache.json').write_text(json.dumps(cache,indent=2))
# Explicit root travel compensation / negative control.
S,r,c=scene(P/'native/WTSC_Painted_Rig_Corrective_Board_v017.blend');S.frame_set(41);bpy.context.view_layer.update();freeze(c,r);travel=bpy.data.objects['V016 | WORLD_TRAVEL | diagnostic zero'];boots=[o for rig in r.values() for o in rig.children if o.get('v007_role')=='support_boot'];base={o.name:points(o) for o in boots};goals={(w,s):c[w,'ANKLE_'+s].matrix_world.copy() for w in r for s in ['near','far']}
travel.location.x=.025;bpy.context.view_layer.update();uncomp=max(max((a-b).length for a,b in zip(base[o.name],points(o))) for o in boots)
for (w,s),M in goals.items():api.set_world_foot_matrix(w,s,M)
comp=max(max((a-b).length for a,b in zip(base[o.name],points(o))) for o in boots);valid=api.reach_report();travel.location.x=.50;bpy.context.view_layer.update()
for (w,s),M in goals.items():api.set_world_foot_matrix(w,s,M)
rejected=False
try:api.require_reachable()
except ValueError:rejected=True
root={'root_travel_test_m':.025,'without_compensation_boot_drift_m':uncomp,'with_world_goal_compensation_boot_drift_m':comp,'compensated_IK':valid,'excess_root_travel_test_m':.5,'excess_unreachable_pose_rejected':rejected,'scope':'Rig-space/world-goal compensation fixture only; no production travel curve or performance.'}
(P/'evidence/root_foot_compensation.json').write_text(json.dumps(root,indent=2))
# Brace reach envelope, measured rather than silently fitted.
S,r,c=scene(P/'native/WTSC_Painted_Rig_Corrective_Board_v017.blend');S.frame_set(161);bpy.context.view_layer.update();freeze(c,r);chests={w:c[w,'CHEST'].matrix_world.copy() for w in r};reach=[]
for deg in [0,10,20,25,30,40,50,60,65]:
 for w in r:
  B=chests[w];c[w,'CHEST'].matrix_world=Matrix.Translation(B.translation)@Matrix.Rotation(math.radians(deg-50),4,'Y')@Matrix.Translation(-B.translation)@B
 bpy.context.view_layer.update();rows=api.reach_report();rejected=False
 try:api.require_reachable()
 except ValueError:rejected=True
 reach.append({'chest_degrees':deg,'chains':rows,'guard_rejected':rejected})
(P/'evidence/brace_reach_limits.json').write_text(json.dumps(reach,indent=2));print('V017_CHECKPOINT_DIAGNOSTIC_DONE',max(x['endpoint_error_m'] for s in samples for x in s['IK']),comp)
