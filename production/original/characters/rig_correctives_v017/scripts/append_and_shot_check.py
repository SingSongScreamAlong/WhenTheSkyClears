import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector
P=Path(__file__).resolve().parents[1];R=P.parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Painted_Rig_Corrective_Board_v017.blend'),load_ui=False,use_scripts=False);S=bpy.context.scene;info=json.loads((R/'characters/rig_capability_audit_v016/evidence/actual_v046_camera.json').read_text());cam=S.camera;cam.data.type=info['type'];cam.data.lens=info['lens'];cam.data.sensor_width=info['sensor_width'];cam.data.sensor_fit=info['sensor_fit'];cam.data.shift_x=info['shift_x'];cam.data.shift_y=info['shift_y'];cam.matrix_world=Matrix(info['relative_to_pair_root']);S.render.resolution_x=960;S.render.resolution_y=540
for r in [o for o in S.objects if o.type=='ARMATURE']:r.delta_location.x=.22 if r['character']=='BOY' else -.22
for f in [21,61,161,201]:
 S.frame_set(f);S.render.filepath=str(P/f'previews/SHOT_CHECK_{f:04d}.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
path=P/'native/WTSC_Painted_Rig_Control_Asset_v017.blend'
with bpy.data.libraries.load(str(path),link=False) as (a,b):b.collections=['WTSC_PAINTED_RIG_CORRECTIVES_v017']
pack=b.collections[0];bpy.context.scene.collection.children.link(pack);bpy.context.view_layer.update();objects=set(pack.all_objects);bad=[];driver_count=0
ids=set(objects)
for o in objects:
 if o.type=='MESH' and o.data.shape_keys:ids.add(o.data.shape_keys)
 for mod in o.modifiers:
  if mod.type=='NODES':ids.add(mod.node_group)
for id in ids:
 ad=id.animation_data
 if ad:
  for fc in ad.drivers:
   driver_count+=1
   for var in fc.driver.variables:
    for t in var.targets:
     if t.id and t.id not in ids:bad.append([id.name,fc.data_path,t.id.name])
for o in objects:
 for c in o.constraints:
  if hasattr(c,'target') and c.target and c.target not in objects:bad.append([o.name,c.name,c.target.name])
 for mod in o.modifiers:
  if mod.type=='NODES':
   for n in mod.node_group.nodes:
    if n.bl_idname=='GeometryNodeObjectInfo' and n.inputs['Object'].default_value not in objects:bad.append([o.name,n.name,'outside collection'])
report={'appended_objects':len(objects),'meshes':sum(o.type=='MESH' for o in objects),'armatures':sum(o.type=='ARMATURE' for o in objects),'IK_chains':sum(c.type=='IK' for o in objects if o.type=='ARMATURE' for b in o.pose.bones for c in b.constraints),'actions':len(bpy.data.actions),'native_drivers_checked':driver_count,'external_dependencies':bad,'packed_original_images':[i.name for i in bpy.data.images if i.packed_file],'pass':not bad and len(bpy.data.actions)==0}
(P/'evidence/fresh_append_validation.json').write_text(json.dumps(report,indent=2));print('V017_APPEND',json.dumps(report))
