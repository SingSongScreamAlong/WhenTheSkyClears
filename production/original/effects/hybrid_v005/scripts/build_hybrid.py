import bpy,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1]
s=bpy.data.scenes['GAS_PROOF_v004 |48div120frames | held framing'];bpy.context.window.scene=s
s.name='HYBRID_v005 | matched control and ONE candidate'
root=bpy.data.objects['FXv003 | fixed ground origin and controls']
root['hybrid_enabled']=1.0;root['hybrid_volume_gain']=1.8;root['start_frame']=1.0;root.update_tag()
for ob in s.objects:
    if ob.name.startswith('GasPilotv004 PREVIEW |'):ob.hide_render=True
    if ob.name.startswith('FXv003 | rolling smoke '):ob.hide_render=False
    if ob.name.startswith('FXv003 | weighted debris '):ob.hide_render=True
domain=next(o for o in s.objects if o.name.startswith('GasPilotv004 |48div gas domain'))
domain.modifiers['GasPilotv004 | native Mantaflow GAS'].domain_settings.cache_directory=str(P/'cache/proof_48r_120f')
f=domain.driver_add('hide_render');f.driver.expression='frame < 1 or H < .5'
for variable in list(f.driver.variables):f.driver.variables.remove(variable)
v=f.driver.variables.new();v.name='H';v.type='SINGLE_PROP';v.targets[0].id=root;v.targets[0].data_path='["hybrid_enabled"]'
m=bpy.data.materials['GasPilotv004 | cold native volume | NO emission'];nt=m.node_tree
volume=next(n for n in nt.nodes if n.type=='PRINCIPLED_VOLUME');gain=volume.inputs['Density'].links[0].from_node;source=gain.inputs[0].links[0].from_socket
volume.inputs['Color'].default_value=(.12,.13,.14,1)
coordinates=nt.nodes.new('ShaderNodeTexCoord');separate=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(coordinates.outputs['Generated'],separate.inputs[0])
def feather(name,socket,lower,upper):
    n=nt.nodes.new('ShaderNodeMapRange');n.name=name;n.clamp=True;n.interpolation_type='SMOOTHERSTEP';n.inputs['From Min'].default_value=lower;n.inputs['From Max'].default_value=upper;nt.links.new(socket,n.inputs[0]);return n.outputs[0]
rear=feather('HYBRID | rear density behind paint',separate.outputs['Y'],.43,.61)
left=feather('HYBRID | keep gas away from children side',separate.outputs['X'],.23,.36)
for name,socket in [('rear',rear),('left',left)]:
    multiply=nt.nodes.new('ShaderNodeMath');multiply.name='HYBRID | '+name+' density restraint';multiply.operation='MULTIPLY';nt.links.new(source,multiply.inputs[0]);nt.links.new(socket,multiply.inputs[1]);source=multiply.outputs[0]
nt.links.new(source,gain.inputs[0])
f=gain.inputs[1].driver_add('default_value');f.driver.expression='G*max(0,min(1,(t-7)/8,(90-t)/30))'
for variable in list(f.driver.variables):f.driver.variables.remove(variable)
for name,key in [('G','hybrid_volume_gain'),('t','age')]:
    v=f.driver.variables.new();v.name=name;v.type='SINGLE_PROP';v.targets[0].id=root;v.targets[0].data_path='["'+key+'"]'
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=32;s.render.threads_mode='FIXED';s.render.threads=2
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.fps=24;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
if hasattr(s.render,'compositor_device'):s.render.compositor_device='GPU'
s.frame_set(60);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Hybrid_Proof_v005.blend'),compress=True)
live=[];s.frame_set(12);bpy.context.view_layer.update()
for ob in s.objects:
    if ob.name.startswith('GasParticlesv004 | anchored '):
        ps=ob.evaluated_get(bpy.context.evaluated_depsgraph_get()).particle_systems[0];live.append({'name':ob.name,'alive':sum(p.alive_state=='ALIVE' for p in ps.particles)})
assert sum(v['alive'] for v in live)==18,live
s.frame_set(60);d=domain.evaluated_get(bpy.context.evaluated_depsgraph_get()).modifiers['GasPilotv004 | native Mantaflow GAS'].domain_settings;density=list(d.density_grid);assert max(density)>.1
old=P.parent/'benchmark_v003/native/WTSC_Evolving_Eruption_Collection_v003.blend';old_hash=hashlib.sha256(old.read_bytes()).hexdigest();assert old_hash=='d089770cccee18b786692d76113b80fbf8514d8034bab4eaae17d6b5f9bd1868'
report={'candidate_count':1,'new_simulation':False,'cached_resolution':48,'gas_gain':1.8,'gas_color':[.12,.13,.14],'rear_generated_y_feather':[.43,.61],'left_generated_x_feather':[.23,.36],'gas_active_ages':[7,90],'cold_painted_layers':13,'particles':live,'gas_density60':{'max':max(density),'sum':sum(density)},'camera_matrix':[list(row) for row in s.camera.matrix_world],'camera_type':s.camera.data.type,'exposure':s.view_settings.exposure,'gamma':s.view_settings.gamma,'view_transform':s.view_settings.view_transform,'look':s.view_settings.look,'renderer':s.render.engine,'samples':32,'pixels':[1920,1080],'fps':24,'timeline':'local+1823=production; review local-23..96','active_preview_lights':[o.name for o in s.objects if o.type=='LIGHT' and not o.hide_render],'v003_source_hash_unchanged':old_hash,'native_sha256':hashlib.sha256((P/'native/WTSC_Hybrid_Proof_v005.blend').read_bytes()).hexdigest(),'status':'One candidate, visual review pending. No production edits.'}
(P/'evidence/hybrid_build.json').write_text(json.dumps(report,indent=2));print('HYBRID_BUILT',json.dumps(report),flush=True)
