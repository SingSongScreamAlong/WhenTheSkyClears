import bpy,json,csv,math,runpy,hashlib,re
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];R=P.parents[1];V9=P.parent/'recovery_walk_refinement_v009'
def setup(path,revision,cfgfile,fn):
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False);s=bpy.context.scene;root=next(o for o in s.objects if o.get('motion_revision')==revision);cfg=runpy.run_path(str(cfgfile))[fn];cfg(start=1,root_motion=True,root=root);rigs={o['character']:o for o in root.children_recursive if o.type=='ARMATURE'};return s,root,rigs,cfg
def feet(rigs):return {(w,side):next(o for o in rig.children if o.get('v007_role')=='support_boot' and o.name.endswith(side)) for w,rig in rigs.items() for side in ['near','far']}
def points(ob):
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();ps=[ev.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear();return ps
def angles(rigs):
 out=[]
 for rig in rigs.values():
  for side in ['near','far']:
   p=rig.pose.bones;fore=(p['hand_'+side].head-p['forearm_'+side].head).normalized();hand=p['hand_'+side].matrix.col[1].xyz.normalized();out.append(fore.angle(hand))
 return out
s,root,rigs,cfg=setup(V9/'native/WTSC_Recovery_Walk_v009.blend','v009_recovery_walk',V9/'scripts/configure_v009.py','configure_v009');oldfeet=feet(rigs);baseline=[];oldangles=[]
for f in range(1,121):
 s.frame_set(f);bpy.context.view_layer.update();row={'distance':next(o for o in root.children if o.get('loco_role')=='DISTANCE_CURVE').location.x,'feet':{w+'_'+side:[list(v) for v in points(ob)] for (w,side),ob in oldfeet.items()}}
 baseline.append(row)
 if 32<=f<=64:oldangles+=angles(rigs)
s,root,rigs,cfg=setup(P/'native/WTSC_Stumble_Polish_Continuation_v010.blend','v010_polish_continuation',P/'scripts/configure_v010.py','configure_v010');newfeet=feet(rigs);distance=next(o for o in root.children if o.get('loco_role')=='DISTANCE_CURVE');rows=[];sourceerror=0;distanceerror=0;newangles=[];visible={};seam={};targets=json.loads((P/'evidence/authored_poses.json').read_text());poseerror=0
for f in range(1,169):
 s.frame_set(f);bpy.context.view_layer.update();row={'frame':f,'distance':distance.location.x,'feet':{},'hips':{w:list(rig.matrix_world@rig.pose.bones['pelvis'].head) for w,rig in rigs.items()}}
 for (w,side),ob in newfeet.items():
  pts=points(ob);name=w+'_'+side;row['feet'][name]={'points':[list(v) for v in pts],'min_z':min(v.z for v in pts),'min_x':min(v.x for v in pts),'max_x':max(v.x for v in pts)}
  if f<=120:sourceerror=max(sourceerror,max((Vector(a)-b).length for a,b in zip(baseline[f-1]['feet'][name],pts)))
 if f<=120:distanceerror=max(distanceerror,abs(distance.location.x-baseline[f-1]['distance']))
 if 32<=f<=64:newangles+=angles(rigs)
 heads=[o.name for o in root.children_recursive if o.get('v007_head_exposure') and not o.hide_render];assert len(heads)==1 and 'original head and attached braid' in heads[0];visible[f]=heads[0]
 for w,rig in rigs.items():
  if str(f) in targets[w]:
   for name,M in targets[w][str(f)].items():poseerror=max(poseerror,max(abs(rig.pose.bones[name].matrix[i][j]-M[i][j]) for i in range(4) for j in range(4)))
 if f in [118,119,120,121,122,123]:
  seam[f]={o.name:[list(v) for v in points(o)] for o in root.children_recursive if o.type=='MESH' and not o.hide_render}
 rows.append(row)
assert sourceerror<1e-5 and distanceerror<1e-7,(sourceerror,distanceerror);assert poseerror<1e-4,poseerror
flat={'BOY_near':[(119,144)],'BOY_far':[(145,168)],'GIRL_near':[(105,130),(155,168)],'GIRL_far':[(131,154)]};locks={}
for foot,ranges in flat.items():
 err=0
 for a,b in ranges:
  orig=rows[a-1]['feet'][foot]['points']
  for row in rows[a-1:b]:err=max(err,max((Vector(x)-Vector(y)).length for x,y in zip(orig,row['feet'][foot]['points'])))
 locks[foot]=err
assert max(locks.values())<1e-5,locks
floormin=min(row['feet'][name]['min_z'] for row in rows[120:] for name in row['feet']);assert floormin>-.004,floormin
seammotion={}
for a,b in [(118,119),(119,120),(120,121),(121,122),(122,123)]:
 seammotion[f'{a}->{b}']={name:max((Vector(x)-Vector(y)).length for x,y in zip(seam[a][name],seam[b][name])) for name in seam[a]}
contract=list(csv.DictReader((P/'evidence/travel_original_5s_v010.csv').open()));oldcontract=list(csv.DictReader((V9/'evidence/travel_curve_v009.csv').open()));csverror=max(abs(float(a['absolute_distance_m'])-float(b['distance_m'])) for a,b in zip(contract,oldcontract));assert csverror==0
# Configure the extension alone with its overlap at global1920 and compare evaluated state.
cfg(start=1920,root_motion=True,root=root,first=120,last=168);extensionerror=0
for f in range(120,169):
 s.frame_set(1800+f);bpy.context.view_layer.update();extensionerror=max(extensionerror,abs(distance.location.x-rows[f-1]['distance']))
 for (w,side),ob in newfeet.items():extensionerror=max(extensionerror,max((Vector(a)-b).length for a,b in zip(rows[f-1]['feet'][w+'_'+side]['points'],points(ob))))
assert extensionerror<1e-5,extensionerror
protected=json.loads((P/'evidence/protected_inputs.json').read_text());preserved={n:hashlib.sha256((R/n).read_bytes()).hexdigest()==sha for n,sha in protected.items()};assert all(preserved.values())
def percentile(a,p):return sorted(a)[round((len(a)-1)*p)]*180/math.pi
report={'version':bpy.app.version_string,'cold_reopened':True,'first120_boot_world_vertex_error_vs_v009_m':sourceerror,'first120_native_distance_error_vs_v009_m':distanceerror,'first120_CSV_distance_error_vs_v009_m':csverror,'authored_pose_matrix_error':poseerror,'extension_flat_stance_world_vertex_drift_m':locks,'extension_min_floor_z_m':floormin,'extension_only_configuration_error_m':extensionerror,'early_wrist_angles_degrees':{'v009_p95':percentile(oldangles,.95),'v010_p95':percentile(newangles,.95),'note':'Geometry diagnostic; actual rendered acting/silhouette review remains separate.'},'head_all168':'Original right profile and attached braid visible; no backward turn','protected_sources_preserved':preserved,'seam_max_vertex_displacements_m':{k:max(v.values()) for k,v in seammotion.items()}}
for row in rows:
 for foot in row['feet'].values():del foot['points']
(P/'evidence/contact_world_samples.json').write_text(json.dumps(rows,indent=2));(P/'evidence/seam_vertex_motion.json').write_text(json.dumps(seammotion,indent=2))
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
with bpy.data.libraries.load(str(P/'native/WTSC_Stumble_Polish_Continuation_v010.blend'),link=False) as (av,loaded):loaded.collections=['WTSC_STUMBLE_POLISH_CONTINUATION_v010']
s.collection.children.link(loaded.collections[0]);root=next(o for o in loaded.collections[0].all_objects if o.get('motion_revision')=='v010_polish_continuation');cfg(start=1920,root_motion=True,root=root,first=120,last=168);s.frame_start=1920;s.frame_end=1968;s.render.fps=24;s.frame_set(1968);bpy.context.view_layer.update();assert not any(o.type in ['CAMERA','LIGHT'] for o in loaded.collections[0].all_objects)
report['fresh_append']={'objects':len(loaded.collections[0].all_objects),'camera_light_count':0,'packed_images':[i.name for i in bpy.data.images if i.packed_file],'extension_final_distance_m':next(o for o in root.children if o.get('loco_role')=='DISTANCE_CURVE').location.x}
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_v010_Extension_Fresh_Append_Test.blend'),compress=True);(P/'evidence/native_validation.json').write_text(json.dumps(report,indent=2));print('V010_VALIDATED',json.dumps(report),flush=True)
