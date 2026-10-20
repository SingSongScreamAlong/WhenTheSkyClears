import bpy,json,time
from pathlib import Path
P=Path(__file__).resolve().parents[1]
s=bpy.data.scenes['GAS_PILOT_v004 |40div72frames | held framing'];bpy.context.window.scene=s
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=32;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=2
if hasattr(s.render,'compositor_device'):s.render.compositor_device='GPU'
for key,value in [('volumetric_samples',48),('volumetric_shadow_samples',16)]:
    if hasattr(s.eevee,key):setattr(s.eevee,key,value)
domain=next(o for o in s.objects if o.name.startswith('GasPilotv004 |40div gas domain'))
frames=[];started=time.perf_counter()
for frame in [12,36,64]:
    s.frame_set(frame);bpy.context.view_layer.update();d=domain.evaluated_get(bpy.context.evaluated_depsgraph_get()).modifiers['GasPilotv004 | native Mantaflow GAS'].domain_settings
    values=list(d.density_grid);density={'cells':len(values),'max':max(values,default=0),'sum':sum(values),'positive_cells':sum(v>1e-4 for v in values)}
    s.render.filepath=str(P/f'previews/pilot_key_{frame:04}.png');begin=time.perf_counter();bpy.ops.render.render(write_still=True,scene=s.name)
    frames.append({'frame':frame,'equivalent_v003_frame':1823+frame,'density':density,'render_seconds':time.perf_counter()-begin})
report={'frames':frames,'wall_seconds':time.perf_counter()-started,'renderer':'Eevee32samples','pixels':[1920,1080],'particle_support':{'ParticleSettings':hasattr(bpy.types,'ParticleSettings'),'particle_system_add':hasattr(bpy.ops.object,'particle_system_add')},'method':'Actual native density volume, zero emission/blackbody. Local preview shading lights only, no production pass.'}
if hasattr(bpy.types,'ParticleSettings'):
    for type_name in ['ParticleSettings','ParticleSystem','PointCache']:
        typ=getattr(bpy.types,type_name);report[type_name+'_properties']={p.identifier:{'type':p.type,'enum':[e.identifier for e in p.enum_items] if p.type=='ENUM' else [],'description':p.description} for p in typ.bl_rna.properties}
(P/'evidence/pilot_render_keys.json').write_text(json.dumps(report,indent=2));print('GAS_PILOT_KEYS_COMPLETE',json.dumps({k:v for k,v in report.items() if not k.endswith('_properties')}),flush=True)
