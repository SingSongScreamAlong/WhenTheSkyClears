"""Recover completed native cache and probe portable animated Volume playback."""
import bpy,json,math,time
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];s=bpy.data.scenes['FXv010 | joined rupture and ground dust'];bpy.context.window.scene=s;root=bpy.data.objects['FXv010 | fixed impact anchor and timing'];asset=bpy.data.collections['FXv010 | JOINED EARTH RUPTURE and DUST'];preview=bpy.data.collections['FXv010 | PREVIEW lights and solver support']
domain=bpy.data.objects['FXv010 | bounded native dust mass |64cells'];d=domain.modifiers['FXv010 | Mantaflow finite dust pulse'].domain_settings;d.cache_directory='//../cache/dust64';d.cache_frame_offset=0
s.frame_set(20);bpy.context.view_layer.update();values=list(domain.evaluated_get(bpy.context.evaluated_depsgraph_get()).modifiers['FXv010 | Mantaflow finite dust pulse'].domain_settings.density_grid);assert max(values,default=0)>.01
volume=bpy.data.volumes.new('FXv010 | native OpenVDB dust playback');volume.filepath=str(P/'cache/dust64/data/fluid_data_0001.vdb');volume.is_sequence=True;volume.frame_start=1;volume.frame_duration=120;volume.sequence_mode='CLIP'
ob=bpy.data.objects.new('FXv010 | retimeable dust volume probe',volume);asset.objects.link(ob);volume.materials.append(domain.data.materials[0]);ob.hide_render=True
props={p.identifier:{'animatable':p.is_animatable,'description':p.description} for p in volume.bl_rna.properties if p.identifier in ['frame_start','frame_offset','frame_duration','filepath']}
try:
    f=volume.driver_add('frame_offset');f.driver.type='SCRIPTED';v=f.driver.variables.new();v.name='t';v.type='SINGLE_PROP';v.targets[0].id=root;v.targets[0].data_path='["age"]';f.driver.expression='t+7-frame';driver_result='created'
except Exception as e:driver_result=str(e)
s.frame_set(19);s.frame_set(20);bpy.context.view_layer.update();volume.grids.load();dg=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(dg);bbox=[list(ev.matrix_world@Vector(p)) for p in ev.bound_box]
report={'reconciled_cache_files':len(list((P/'cache/dust64/data').glob('*.vdb'))),'cache_bytes':sum(f.stat().st_size for f in (P/'cache/dust64').rglob('*') if f.is_file()),'native_density_frame20':{'max':max(values),'sum':sum(values),'count':len(values)},'volume_properties':props,'volume_offset_driver':driver_result,'volume_bbox_at_origin':bbox,'domain_world_matrix':[list(row) for row in domain.matrix_world],'domain_bbox_world':[list(domain.matrix_world@Vector(p)) for p in domain.bound_box],'grids':[{'name':g.name,'type':g.data_type} for g in volume.grids],'source':'Completed actual Mantaflow bake retained after non-animatable native-domain offset was detected; no rebake.'}
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Joined_Rupture_Dust_Probe_v010b.blend'),compress=True);(P/'evidence/volume_playback_probe.json').write_text(json.dumps(report,indent=2));print('CACHE_RECOVERED_VOLUME_PROBED',json.dumps(report),flush=True)
