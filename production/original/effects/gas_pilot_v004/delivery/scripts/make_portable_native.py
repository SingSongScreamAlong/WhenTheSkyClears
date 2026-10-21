import bpy,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1]
s=bpy.data.scenes['GAS_PROOF_v004 |48div120frames | held framing'];bpy.context.window.scene=s
target=P/'delivery/native/WTSC_Gas_Particles_Proof_48r_120f_v004.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
domain=next(o for o in s.objects if o.name.startswith('GasPilotv004 |48div gas domain'));d=domain.modifiers['GasPilotv004 | native Mantaflow GAS'].domain_settings
d.cache_directory='//../cache/proof_48r_120f'
s.frame_set(61);s.frame_set(60);bpy.context.view_layer.update();evaluated=domain.evaluated_get(bpy.context.evaluated_depsgraph_get());vals=list(evaluated.modifiers['GasPilotv004 | native Mantaflow GAS'].domain_settings.density_grid)
assert max(vals,default=0)>.1,'Portable cache failed to read actual density.'
live=[];s.frame_set(12);bpy.context.view_layer.update()
for ob in s.objects:
    if ob.name.startswith('GasParticlesv004 | anchored '):
        ps=ob.evaluated_get(bpy.context.evaluated_depsgraph_get()).particle_systems[0];live.append({'emitter':ob.name,'alive':sum(p.alive_state=='ALIVE' for p in ps.particles),'baked':ob.particle_systems[0].point_cache.is_baked})
assert sum(v['alive'] for v in live)==18,live
s.frame_set(60);bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
report={'native':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'cache_relative':d.cache_directory,'cache_resolves_to':bpy.path.abspath(d.cache_directory),'density_at_frame60':{'max':max(vals),'sum':sum(vals)},'particle_frame12':live,'all_images_packed':all(im.packed_file for im in bpy.data.images if im.type!='RENDER_RESULT'),'note':'Portable scene only, with local preview shading lights and transparent test collider. Not approved production integration.'}
assert report['all_images_packed']
(P/'evidence/portable_native_validation.json').write_text(json.dumps(report,indent=2));print('PORTABLE_NATIVE_VALIDATED',json.dumps(report),flush=True)
