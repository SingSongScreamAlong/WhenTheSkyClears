import bpy,json,time,sys
from pathlib import Path
P=Path(__file__).resolve().parents[1]
s=bpy.data.scenes['GAS_PILOT_v004 |40div72frames | held framing'];bpy.context.window.scene=s;s.frame_set(36)
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=32;s.render.threads_mode='FIXED';s.render.threads=2
if hasattr(s.render,'compositor_device'):s.render.compositor_device='GPU'
m=bpy.data.materials['GasPilotv004 | cold native volume | NO emission'];nt=m.node_tree
volume=next(n for n in nt.nodes if n.type=='PRINCIPLED_VOLUME');gain=next(n for n in nt.nodes if n.type=='MATH');gain.inputs[1].default_value=35
results=[]
for mode in (['VolumeInfo35_TightFroxels'] if '--tight' in sys.argv else ['VolumeInfo35','NativeDensityAttribute35']):
    if mode=='NativeDensityAttribute35':
        for link in list(volume.inputs['Density'].links):nt.links.remove(link)
        volume.inputs['Density'].default_value=35;volume.inputs['Density Attribute'].default_value='density'
    if mode=='VolumeInfo35_TightFroxels':
        settings={}
        for key,value in [('volumetric_samples',128),('volumetric_shadow_samples',64),('use_volumetric_shadows',True),('volumetric_start',18.0),('volumetric_end',34.0),('volumetric_sample_distribution',0.0),('volumetric_tile_size','4')]:
            if hasattr(s.eevee,key):setattr(s.eevee,key,value);settings[key]=getattr(s.eevee,key)
        results.append({'eevee_settings':settings,'available_eevee_volume_properties':{p.identifier:p.description for p in s.eevee.bl_rna.properties if 'volum' in p.identifier}})
    s.render.filepath=str(P/f'previews/binding_{mode}_0036.png');start=time.perf_counter();bpy.ops.render.render(write_still=True,scene=s.name);results.append({'mode':mode,'seconds':time.perf_counter()-start})
(P/('evidence/density_tight_test.json' if '--tight' in sys.argv else 'evidence/density_binding_test.json')).write_text(json.dumps(results,indent=2));print('DENSITY_BINDING_TEST_COMPLETE',json.dumps(results),flush=True)
