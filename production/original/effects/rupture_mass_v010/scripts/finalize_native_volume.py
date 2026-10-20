import bpy,json,math
from pathlib import Path
from mathutils import Matrix,Vector
P=Path(__file__).resolve().parents[1];s=bpy.data.scenes['FXv010 | joined rupture and ground dust'];bpy.context.window.scene=s;root=bpy.data.objects['FXv010 | fixed impact anchor and timing'];asset=bpy.data.collections['FXv010 | JOINED EARTH RUPTURE and DUST'];preview=bpy.data.collections['FXv010 | PREVIEW lights and solver support']
# Blended surfaces do not provide the intended native shadow casting. Use dithered
# coverage on the fully solid earth and on the feathered terrain receiver.
for m in bpy.data.materials:
    if m.name.startswith('FXv010 | project paint') or m.name.startswith('FXv010 | original project paint'):m.surface_render_method='DITHERED'
domain=bpy.data.objects['FXv010 | bounded native dust mass |64cells'];d=domain.modifiers['FXv010 | Mantaflow finite dust pulse'].domain_settings;s.frame_set(20);bpy.context.view_layer.update();dims=domain.dimensions.copy();dx=dims.x/64;res=Vector((64,math.ceil(dims.y/dx-1e-5),math.ceil(dims.z/dx-1e-5)))
ed=domain.evaluated_get(bpy.context.evaluated_depsgraph_get()).modifiers['FXv010 | Mantaflow finite dust pulse'].domain_settings
assert len(ed.density_grid)==int(res.x*res.y*res.z),(len(ed.density_grid),list(res))
v=bpy.data.volumes.new('FXv010 | finite rolling dust OpenVDB sequence');v.filepath='//../cache/dust64_flat/data/fluid_data_0001.vdb';v.is_sequence=True;v.frame_start=1;v.frame_duration=120;v.sequence_mode='CLIP';v.materials.append(domain.data.materials[0]);ob=bpy.data.objects.new('FXv010 | retimeable finite dust VDB',v);asset.objects.link(ob)
cell=Vector([dims[i]/res[i] for i in range(3)]);offset=-dims/2+cell/2;ratio=Vector([cell[i]/dx for i in range(3)]);ob.matrix_world=domain.matrix_world@Matrix.Translation(offset)@Matrix.Diagonal((*ratio,1));ob.parent=root;ob.matrix_parent_inverse=root.matrix_world.inverted()
f=v.driver_add('frame_offset');f.driver.type='SCRIPTED';var=f.driver.variables.new();var.name='t';var.type='SINGLE_PROP';var.targets[0].id=root;var.targets[0].data_path='["age"]';f.driver.expression='t+7-frame'
for item in list(asset.objects):
    if item==domain or item.name.startswith('FXv010 | finite flow '):asset.objects.unlink(item);preview.objects.link(item);item.hide_render=True
for item in preview.objects:
    if item.type=='MESH':item.hide_render=True
root['terrain_note']='Projected original terrain and native receiver are specific to the held proof camera. Reproject for another shot.'
root['status']='Prototype keyframe study. Not artistically accepted. No production integration.'
s.frame_set(20);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(dg);ev.data.grids.load()
report={'domain_resolution':list(res),'volume_properties':[p.identifier for p in bpy.types.VolumeGrids.bl_rna.properties],'volume_frame_offset':ev.data.frame_offset,'volume_world_matrix':[list(row) for row in ob.matrix_world],'source_cache':'Completed native Mantaflow64div120frames,38.55MB; no upres.','pending':'Actual VDB/native placement and pixel retime check.'}
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Earth_Rupture_VDB_v010h.blend'),compress=True);(P/'evidence/native_volume_h.json').write_text(json.dumps(report,indent=2));print('CLEAN_NATIVE_VOLUME_PREPARED',json.dumps(report),flush=True)
