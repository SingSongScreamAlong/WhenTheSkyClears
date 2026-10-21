import bpy,json,math
from pathlib import Path
from mathutils import Matrix,Vector
P=Path(__file__).resolve().parents[1];s=bpy.data.scenes['FXv010 | joined rupture and ground dust'];bpy.context.window.scene=s;root=bpy.data.objects['FXv010 | fixed impact anchor and timing'];asset=bpy.data.collections['FXv010 | JOINED EARTH RUPTURE and DUST'];preview=bpy.data.collections['FXv010 | PREVIEW lights and solver support'];domain=bpy.data.objects['FXv010 | bounded native dust mass |64cells'];d=domain.modifiers['FXv010 | Mantaflow finite dust pulse'].domain_settings
s.frame_set(20);bpy.context.view_layer.update();dims=domain.dimensions.copy();res=Vector(d.domain_resolution);dx=dims.x/res.x
ob=bpy.data.objects['FXv010 | retimeable dust volume probe'];ob.name='FXv010 | finite native rolling dust VDB';v=ob.data;v.filepath='//../cache/dust64/data/fluid_data_0001.vdb'
cell=Vector([dims[i]/res[i] for i in range(3)]);offset=-dims/2+cell/2;ratio=Vector([cell[i]/dx for i in range(3)]);ob.matrix_world=domain.matrix_world@Matrix.Translation(offset)@Matrix.Diagonal((*ratio,1));ob.parent=root;ob.matrix_parent_inverse=root.matrix_world.inverted();ob.hide_render=False
for item in list(asset.objects):
    if item==domain or item.name.startswith('FXv010 | finite flow '):asset.objects.unlink(item);preview.objects.link(item);item.hide_render=True
domain.hide_render=True
root['construction']='Shared-boundary solid earth blocks, real depressed cut terrain and native cached finite gas dust. No tiny particles or mature cloud scaling.'
root['terrain_note']='Project-specific held-camera paint projection on the ground apron; reproject/replace for different shots.'
bpy.context.view_layer.update();rows=[]
for start,fr in [(7,20),(107,120),(7,20)]:
    root['start_frame']=float(start);root.update_tag(refresh={'OBJECT'});s.frame_set(fr);bpy.context.view_layer.update();ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());ev.data.grids.load();rows.append({'start':start,'frame':fr,'age':root['age'],'volume_frame_offset':ev.data.frame_offset,'grid_frame':fr+ev.data.frame_offset,'bbox_world':[list(ev.matrix_world@Vector(p)) for p in ev.bound_box]})
assert [r['grid_frame'] for r in rows]==[20,20,20],rows
s.frame_set(20);bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Joined_Rupture_VDB_v010c.blend'),compress=True)
(P/'evidence/native_vdb_playback.json').write_text(json.dumps({'domain_resolution':list(res),'domain_metres':list(dims),'voxel_size':list(cell),'volume_object_matrix':[list(row) for row in ob.matrix_world],'timing_rows':rows,'method':'Completed Mantaflow VDB files imported as native Volume sequence; frame_offset is natively animatable, unlike FluidDomain cache_frame_offset.','native_bake_cache_bytes':sum(f.stat().st_size for f in (P/'cache/dust64').rglob('*') if f.is_file()),'status':'Placement requires actual native/VDB key comparison, artistic acceptance not implied.'},indent=2));print('NATIVE_VDB_RETIMING_READY',json.dumps(rows),flush=True)
