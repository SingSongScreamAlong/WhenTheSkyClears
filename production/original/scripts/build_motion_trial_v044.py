"""Only performance changes: sealed v006 into original EEVEE v043 stage."""
import bpy,json,hashlib,math
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE')
receipt=json.loads((R/'notes/world_v016/motion_snapshot_v044.json').read_text());snapshot=Path(receipt['snapshot']);assert hashlib.sha256(snapshot.read_bytes()).hexdigest()==receipt['snapshot_sha256']
out=R/'shots/world/WTSC_Open_Battlefield_Drawn_Trial_v044.blend';assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(snapshot),load_ui=False)
coll=bpy.data.collections[receipt['collection']];assert not any(o.type in {'LIGHT','CAMERA'} for o in coll.all_objects)
config=bpy.data.texts['configure_v006.py'].as_string();assert 'def configure_v006(' in config and 'duration_scale' in config
snapshot_facts={'objects':len(coll.all_objects),'packed_images':[i.name for i in bpy.data.images if i.packed_file],'native_reopened':True}
base=R/'shots/world/WTSC_Open_Battlefield_Combined_Trial_v043.blend';bpy.ops.wm.open_mainfile(filepath=str(base),load_ui=False)
s=bpy.data.scenes['WTSC_OPEN_BATTLEFIELD_COMBINED_TRIAL_v043'];m=bpy.data.scenes['WTSC_OPEN_5S_MASTER_v043'];bpy.context.window.scene=s
old=next(o for o in s.objects if o.get('loco_pack')=='WTSC_BATTLEFIELD_WEARY_v005');oldtravel=next(o for o in old.children if 'TRAVEL' in o.name)
anchor=old.matrix_world.copy();assert max(abs(anchor[i][3]-v) for i,v in enumerate([107.6339569,0,.7200737]))<1e-5
light=s.objects['v043 OWNED | Brief eruption light'];fx=s.objects['FXv003 | fixed ground origin and controls'];event=s.objects['v041 | Live event binding | awaiting verified FX']
def simple(value):
 if isinstance(value,(str,int,float,bool)) or value is None:return value
 try:return list(value)
 except:return str(value)
def rna_values(obj):
 result={}
 for p in obj.bl_rna.properties:
  if p.identifier=='rna_type' or p.type in {'POINTER','COLLECTION'}:continue
  try:result[p.identifier]=simple(getattr(obj,p.identifier))
  except:pass
 return result
def settings():
 return {'render':rna_values(s.render),'eevee':rna_values(s.eevee) if hasattr(s,'eevee') else None,'view':rna_values(s.view_settings),'camera':rna_values(s.camera.data),'world':s.world.name,'compositor':[(n.bl_idname,n.name) for n in s.compositing_node_group.nodes]}
before_settings=settings();assert 'EEVEE' in s.render.engine,s.render.engine
contacts=[o for o in s.objects if o.name.startswith('v041 sole contact |')];assert len(contacts)==4
hidden=[]
for ob in [old,*old.children_recursive]:
 if not ob.hide_render:hidden.append(ob.name)
 ob.hide_render=True
 if ob.type in {'MESH','GREASEPENCIL','CURVE'}:ob.hide_viewport=True
caps=[o for o in s.objects if o.name.startswith(('v043 rounded knee |','v043 rounded wrist |'))]
assert len(caps)==6,len(caps)
for ob in caps:ob.hide_render=True;ob.hide_viewport=True
with bpy.data.libraries.load(str(snapshot),link=False) as (available,loaded):loaded.collections=[receipt['collection']]
newcoll=loaded.collections[0];s.collection.children.link(newcoll)
root=next(o for o in newcoll.all_objects if o.get('motion_revision')=='v006_drawn_pose_corrections');root.matrix_world=anchor
namespace={};exec(compile(config,'sealed_snapshot_configure_v006.py','exec'),namespace);configured=namespace['configure_v006'](start=1801,duration_scale=1.,root_motion=True,root=root)
travel=next(o for o in root.children if 'TRAVEL' in o.name)
# Camera intentionally retains the old hidden TRAVEL: exactly frozen staging.
camera_targets=[t.id for f in s.camera.animation_data.drivers for v in f.driver.variables for t in v.targets];assert oldtravel in camera_targets
materials={mat for ob in root.children_recursive if hasattr(ob.data,'materials') for mat in ob.data.materials if mat and mat.node_tree};material_rows=[]
for mat in materials:
 nt=mat.node_tree;em=next((n for n in nt.nodes if n.type=='EMISSION'),None)
 if not em or not em.inputs[0].is_linked:continue
 assert not any('physically sourced reflected light' in n.name for n in nt.nodes),mat.name
 basecolor=em.inputs[0].links[0].from_socket;geo=nt.nodes.new('ShaderNodeNewGeometry');pos=nt.nodes.new('ShaderNodeCombineXYZ')
 for i,axis in enumerate(['LOC_X','LOC_Y','LOC_Z']):
  f=pos.inputs[i].driver_add('default_value');f.driver.expression='p';v=f.driver.variables.new();v.name='p';v.type='TRANSFORMS';v.targets[0].id=light;v.targets[0].transform_type=axis;v.targets[0].transform_space='WORLD_SPACE'
 def mathn(op,a,b):
  n=nt.nodes.new('ShaderNodeMath');n.operation=op
  for i,x in enumerate([a,b]):
   if isinstance(x,(int,float)):n.inputs[i].default_value=x
   else:nt.links.new(x,n.inputs[i])
  return n.outputs[0]
 def remap(x,a,b,c,d):
  n=nt.nodes.new('ShaderNodeMapRange');n.clamp=True;n.interpolation_type='SMOOTHERSTEP'
  for name,value in [('From Min',a),('From Max',b),('To Min',c),('To Max',d)]:n.inputs[name].default_value=value
  nt.links.new(x,n.inputs[0]);return n.outputs[0]
 distance=nt.nodes.new('ShaderNodeVectorMath');distance.operation='DISTANCE';nt.links.new(geo.outputs['Position'],distance.inputs[0]);nt.links.new(pos.outputs[0],distance.inputs[1]);fall=remap(distance.outputs['Value'],2,16,1,0)
 power=nt.nodes.new('ShaderNodeValue');f=power.outputs[0].driver_add('default_value');f.driver.expression='p/1800';v=f.driver.variables.new();v.name='p';v.type='SINGLE_PROP';v.targets[0].id_type='LIGHT';v.targets[0].id=light.data;v.targets[0].data_path='energy'
 luma=nt.nodes.new('ShaderNodeRGBToBW');nt.links.new(basecolor,luma.inputs[0]);eye=remap(luma.outputs[0],.18,.65,1,0);protect=remap(luma.outputs[0],.01,.16,.2,1);fac=mathn('MULTIPLY',fall,fall);fac=mathn('MULTIPLY',fac,power.outputs[0]);fac=mathn('MULTIPLY',fac,mathn('MULTIPLY',eye,protect));fac=mathn('MULTIPLY',fac,.025)
 mix=nt.nodes.new('ShaderNodeMix');mix.data_type='RGBA';mix.blend_type='ADD';mix.name='v044 | Same v043 physically sourced reflected light';mix.inputs[7].default_value=(.85,.31,.065,1);nt.links.new(basecolor,mix.inputs[6]);nt.links.new(fac,mix.inputs[0]);nt.links.new(mix.outputs[2],em.inputs[0]);material_rows.append(mat.name)
oldrigs={o['character']:o for o in old.children_recursive if o.type=='ARMATURE'};newrigs={o['character']:o for o in root.children_recursive if o.type=='ARMATURE'};assert len(newrigs)==2
oldboots=[o for o in old.children_recursive if o.type=='MESH' and 'rigid original boot' in o.name];assert len(oldboots)==4
for boot in oldboots:boot.hide_viewport=False # Evaluate hidden reference soles during read-only comparison.
newboots=[o for o in root.children_recursive if o.type=='MESH' and 'boot collar' in o.name and not o.hide_render];assert len(newboots)==4,[o.name for o in root.children_recursive if 'boot' in o.name]
for boot in oldboots:
 who=next(who for who,rig in oldrigs.items() if boot in rig.children_recursive);side='near' if 'near' in boot.name else 'far';newboot=next(o for o in newboots if o in newrigs[who].children_recursive and side in o.name)
 contact=next(o for o in contacts if o.name.endswith(boot.name));contact['v044_new_boot_reference']=newboot.name;contact['binding_method']='Existing120sample sole keys retained: foot matrices/sole extrema verified against new performance.'
def extrema(boot):
 ev=boot.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();points=[ev.matrix_world@v.co for v in mesh.vertices];ev.to_mesh_clear();z=min(p.z for p in points);bottom=[p for p in points if p.z<=z+.004];return [sum(p.x for p in bottom)/len(bottom),sum(p.y for p in bottom)/len(bottom),z]
frozen=json.loads((R/'notes/world_v016/frozen_staging_v043.json').read_text());errors={k:0. for k in ['camera_matrix','new_vs_old_travel','fx_origin','fx_clock','physical_light','receiver_watts','protected_foot_world_matrices','sole_extrema']};rows=[]
for sample in frozen['samples']:
 frame=sample['frame'];s.frame_set(frame);bpy.context.view_layer.update()
 errors['camera_matrix']=max(errors['camera_matrix'],max(abs(s.camera.matrix_world[i][j]-sample['camera_matrix'][i][j]) for i in range(4) for j in range(4)))
 errors['new_vs_old_travel']=max(errors['new_vs_old_travel'],(travel.matrix_world.translation-oldtravel.matrix_world.translation).length)
 errors['fx_origin']=max(errors['fx_origin'],max(abs(fx.matrix_world.translation[i]-sample['fx_root_world'][i]) for i in range(3)))
 errors['fx_clock']=max(errors['fx_clock'],abs(fx['age']-sample['fx_age']),abs(fx['hot_envelope']-sample['hot_envelope']))
 errors['physical_light']=max(errors['physical_light'],abs(light.data.energy-sample['physical_light_watts']));errors['receiver_watts']=max(errors['receiver_watts'],abs(event['power_watts']-sample['receiver_watts']))
 for who in oldrigs:
  for bn in ['foot_near','foot_far']:
   a=oldrigs[who].matrix_world@oldrigs[who].pose.bones[bn].matrix;b=newrigs[who].matrix_world@newrigs[who].pose.bones[bn].matrix;errors['protected_foot_world_matrices']=max(errors['protected_foot_world_matrices'],max(abs(a[i][j]-b[i][j]) for i in range(4) for j in range(4)))
 for boot in oldboots:
  contact=next(o for o in contacts if o.name.endswith(boot.name));newboot=s.objects[contact['v044_new_boot_reference']];a=extrema(boot);b=extrema(newboot);errors['sole_extrema']=max(errors['sole_extrema'],max(abs(x-y) for x,y in zip(a,b)))
 rows.append({'frame':frame,'camera_matrix':[list(r) for r in s.camera.matrix_world],'travel_world':list(travel.matrix_world.translation),'physical_light_watts':light.data.energy,'fx_age':fx['age']})
assert max(errors.values())<3e-5,errors
for boot in oldboots:boot.hide_viewport=True
after_settings=settings();assert before_settings==after_settings,'Original render/camera/world settings changed'
assert all(o.hide_render for o in old.children_recursive) and all(o.hide_render for o in caps)
assert not any(o.type=='LIGHT' for o in newcoll.all_objects)
s.name='WTSC_OPEN_BATTLEFIELD_DRAWN_TRIAL_v044';m.name='WTSC_OPEN_5S_MASTER_v044'
for scene,name in [(s,'WTSC_Drawn_Picture_Only_v044.mp4'),(m,'WTSC_Drawn_Open_75_80_4K_v044.mp4')]:scene.render.filepath='//../../renders/world_v016/integration_v044/'+name
s['integration_status']='v006 drawn corrections only, fixed v043 EEVEE world/camera/travel/light/FX. Review candidate; no full-film propagation.'
report={'source':str(out),'base':str(base),'base_sha256':receipt['preserved_inputs']['shots/world/WTSC_Open_Battlefield_Combined_Trial_v043.blend'],'snapshot':receipt,'snapshot_facts':snapshot_facts,'world_scene':s.name,'master_scene':m.name,'configured':configured,'actor_origin':list(root.location),'actor_scale':list(root.scale),'camera_follow':'Original hidden v005TRAVEL retained unchanged; newTRAVEL matches every frame. No double travel.','engine':s.render.engine,'original_settings_before':before_settings,'original_settings_after':after_settings,'frames':[1801,1920],'fps':24,'resolution':[3840,2160],'errors_vs_frozen_v043':errors,'samples':rows,'contacts':'All4 existing native animated planes retained. No root drivers; new boot references recorded, sole extrema verified over120frames.','old_pair_hidden':hidden,'old_caps_hidden':[o.name for o in caps],'new_materials_bound_to_existing_light':sorted(material_rows),'artistic_status':'Fresh append and contact tests do not constitute artistic acceptance. Actual moving review pending.','preserved_inputs':receipt['preserved_inputs']}
note=bpy.data.texts.new('CURRENT v044 | Matched motion candidate and provenance');note.write(json.dumps(report,indent=2));bpy.context.window.scene=m;m.frame_set(1801);bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report['source_sha256']=hashlib.sha256(out.read_bytes()).hexdigest()
for name,sha in receipt['preserved_inputs'].items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==sha,name
(R/'notes/world_v016/motion_trial_build_v044.json').write_text(json.dumps(report,indent=2));print('V044_MATCHED_NATIVE_SAVED',json.dumps({'source':str(out),'sha256':report['source_sha256'],'errors':errors,'engine':s.render.engine}),flush=True)
