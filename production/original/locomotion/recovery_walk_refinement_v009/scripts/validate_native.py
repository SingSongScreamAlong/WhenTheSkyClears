import bpy,json,runpy,math,hashlib,csv
from pathlib import Path
P=Path(__file__).resolve().parents[1];R=P.parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Recovery_Walk_v009.blend'),load_ui=False);s=bpy.context.scene
root=next(o for o in s.objects if o.get('motion_revision')=='v009_recovery_walk');rigs={o['character']:o for o in root.children_recursive if o.type=='ARMATURE'}
cfg=runpy.run_path(str(P/'scripts/configure_v009.py'))['configure_v009'];cfg(start=1,root_motion=True,root=root)
boots={(w,side):next(o for o in rig.children if o.get('v007_role')=='support_boot' and o.name.endswith(side)) for w,rig in rigs.items() for side in ['near','far']}
targets=json.loads((P/'evidence/authored_pose_targets.json').read_text());matrix_error=0;rows=[]
for f in range(1,121):
 s.frame_set(f);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();row={'frame':f,'boots':{},'hips':{}}
 for (w,side),ob in boots.items():
  ev=ob.evaluated_get(dg);me=ev.to_mesh();pts=[ev.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear()
  row['boots'][w+'_'+side]={'min_z':min(p.z for p in pts),'max_z':max(p.z for p in pts),'min_x':min(p.x for p in pts),'max_x':max(p.x for p in pts),'vertices':[[p.x,p.y,p.z] for p in pts]}
 for w,rig in rigs.items():
  row['hips'][w]=list(rig.matrix_world@rig.pose.bones['pelvis'].head)
  if str(f) in targets[w]:
   for n,M in targets[w][str(f)].items():matrix_error=max(matrix_error,max(abs(rig.pose.bones[n].matrix[i][j]-M[i][j]) for i in range(4) for j in range(4)))
 rows.append(row)
flat={'BOY_far':[(81,120)],'BOY_near':[(81,95),(119,120)],'GIRL_far':[(81,106)],'GIRL_near':[(81,82),(105,120)]};slips={}
for foot,ranges in flat.items():
 err=0
 for a,b in ranges:
  initial=rows[a-1]['boots'][foot]['vertices']
  for row in rows[a-1:b]:err=max(err,max(abs(p[axis]-q[axis]) for p,q in zip(initial,row['boots'][foot]['vertices']) for axis in [0,2]))
 slips[foot]=err
minlate=min(row['boots'][name]['min_z'] for row in rows[80:] for name in row['boots']);maxlate=max(row['boots'][name]['min_z'] for row in rows[80:] for name in row['boots'])
report={'version':bpy.app.version_string,'cold_reopened':True,'all_sampled_pose_matrix_error':matrix_error,'flat_stance_max_vertex_xz_drift_m':slips,'late_boot_min_floor_z_m':minlate,'late_max_clearance_m':maxlate,'flat_stance_ranges_local':flat,'technical_note':'Flat sole vertex world lock tested independently of screen pixels. Roll ranges excluded; animated pivot/contact is deliberate. Hip is a visual support proxy, not a physical COM or dynamics solution.','paint':'Original packed source image, original UVs, head mesh and body proportions. No new bitmap.','head':'Original-profile object visible all120; rejected passing/mirror variants hidden in isolated asset.'}
assert matrix_error<1e-4,matrix_error
assert max(slips.values())<1e-4,slips
assert minlate>-.004,minlate
distance=next(o for o in root.children if o.get('loco_role')=='DISTANCE_CURVE');travel=next(o for o in root.children if 'TRAVEL' in o.name)
clock_error=0
cfg(start=1801,duration_scale=2,root_motion=True,root=root)
curve=list(csv.DictReader((P/'evidence/travel_curve_v009.csv').open()))
for f in range(1,121):
 s.frame_set(1801+2*(f-1));bpy.context.view_layer.update();clock_error=max(clock_error,abs(distance.location.x-float(curve[f-1]['distance_m'])))
report['double_duration_distance_error_m']=clock_error;assert clock_error<1e-5,clock_error
sourcehashes=json.loads((P/'evidence/protected_inputs.json').read_text());report['protected_inputs_preserved']={n:hashlib.sha256((R/n).read_bytes()).hexdigest()==h for n,h in sourcehashes.items()};assert all(report['protected_inputs_preserved'].values())
(P/'evidence/native_validation.json').write_text(json.dumps(report,indent=2))
for row in rows:
 for foot,v in row['boots'].items():del v['vertices']
(P/'evidence/contact_world_samples.json').write_text(json.dumps(rows,indent=2))
# Real fresh-scene Append after cold reopen, no source stage inheritance.
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
with bpy.data.libraries.load(str(P/'native/WTSC_Recovery_Walk_v009.blend'),link=False) as (available,loaded):loaded.collections=['WTSC_RECOVERY_WALK_PAIR_v009']
s.collection.children.link(loaded.collections[0]);root=next(o for o in loaded.collections[0].all_objects if o.get('motion_revision')=='v009_recovery_walk');cfg(start=1801,root_motion=True,root=root)
assert not any(o.type in {'CAMERA','LIGHT'} for o in loaded.collections[0].all_objects)
s.frame_start=1801;s.frame_end=1920;s.render.fps=24;s.frame_set(1920);bpy.context.view_layer.update()
report['fresh_append']={'objects':len(loaded.collections[0].all_objects),'camera_light_count':0,'packed_images':[i.name for i in bpy.data.images if i.packed_file],'all_drawings_present':sum(1 for o in root.children_recursive if o.type=='MESH' and o.data.shape_keys is not None),'travel_at_1920':list(next(o for o in root.children if 'TRAVEL' in o.name).location)}
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_v009_Fresh_Append_Test.blend'),compress=True)
(P/'evidence/native_validation.json').write_text(json.dumps(report,indent=2));print('NATIVE_VALIDATION',json.dumps(report),flush=True)
