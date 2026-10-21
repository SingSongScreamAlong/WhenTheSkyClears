"""Capped40-division native gas pilot in the isolated v003 held-shot fixture."""
import bpy,json,time,math,hashlib,os,sys
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]
proof='--proof' in sys.argv
resolution=48 if proof else 40
end_frame=120 if proof else 72
cache_name='proof_48r_120f' if proof else 'pilot_40r_72f'
s=bpy.data.scenes['FX_PROOF_v003 | 75-80s held shot evolution'];bpy.context.window.scene=s
s.name='GAS_PROOF_v004 |48div120frames | held framing' if proof else 'GAS_PILOT_v004 |40div72frames | held framing'
root=bpy.data.objects['FXv003 | fixed ground origin and controls'];root['start_frame']=1.0;root.update_tag()
for ob in bpy.data.objects:
    if ob.name.startswith('FXv003 | rolling smoke '):ob.hide_render=True
s.frame_start=1;s.frame_end=end_frame;s.render.fps=24;s.render.threads_mode='FIXED';s.render.threads=2
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100
if hasattr(s.render,'compositor_device'):s.render.compositor_device='CPU'
# Zero physics gravity on the old fixture is not assumed. Native smoke uses
# deliberately modest buoyancy and a short initial upward flow pulse.
s.gravity=(0,0,-9.81)
c=bpy.data.collections.new('GasPilotv004 | native bounded smoke ONLY');s.collection.children.link(c)
anchor=bpy.data.objects.new('GasPilotv004 | fixed source origin',None);c.objects.link(anchor);anchor.location=root.location;anchor.empty_display_type='CIRCLE'
def in_collection(ob):
    for old in list(ob.users_collection):old.objects.unlink(ob)
    c.objects.link(ob)
bpy.ops.mesh.primitive_cube_add(size=1,location=anchor.location+Vector((.35,0,1.93)))
domain=bpy.context.object;domain.name=f'GasPilotv004 |{resolution}div gas domain4.2x2.8x4.0m';domain.dimensions=(4.2,2.8,4.0)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);in_collection(domain)
domain.parent=anchor;domain.matrix_parent_inverse=anchor.matrix_world.inverted()
dm=domain.modifiers.new('GasPilotv004 | native Mantaflow GAS','FLUID');dm.fluid_type='DOMAIN';bpy.context.view_layer.update();d=dm.domain_settings;d.domain_type='GAS'
d.resolution_max=resolution;d.cache_type='MODULAR';d.cache_frame_start=1;d.cache_frame_end=end_frame
d.cache_data_format='OPENVDB';d.cache_directory=str(P/'cache'/cache_name);d.cache_resumable=False
d.use_noise=False;d.use_adaptive_domain=False;d.timesteps_min=1;d.timesteps_max=2;d.cfl_condition=4
d.time_scale=1;d.alpha=.7 if proof else 0;d.beta=.5 if proof else .35;d.vorticity=.55 if proof else 1.1
if hasattr(d,'use_dissolve_smoke'):d.use_dissolve_smoke=not proof
d.dissolve_speed=48
if hasattr(d,'use_dissolve_smoke_log'):d.use_dissolve_smoke_log=True
for key in ['front','back','right','left','top','bottom']:
    name='use_collision_border_'+key
    if hasattr(d,name):setattr(d,name,False)
mat=bpy.data.materials.new('GasPilotv004 | cold native volume | NO emission');mat.use_nodes=True;nt=mat.node_tree;nt.nodes.clear()
info=nt.nodes.new('ShaderNodeVolumeInfo');gain=nt.nodes.new('ShaderNodeMath');gain.operation='MULTIPLY';gain.inputs[1].default_value=25 if proof else 4.2;nt.links.new(info.outputs['Density'],gain.inputs[0])
volume=nt.nodes.new('ShaderNodeVolumePrincipled');volume.inputs['Color'].default_value=(.24,.265,.30,1);volume.inputs['Anisotropy'].default_value=.10
for name in ['Density Attribute','Color Attribute','Temperature Attribute']:
    if name in volume.inputs:volume.inputs[name].default_value=''
if 'Emission Strength' in volume.inputs:volume.inputs['Emission Strength'].default_value=0
if 'Blackbody Intensity' in volume.inputs:volume.inputs['Blackbody Intensity'].default_value=0
nt.links.new(gain.outputs[0],volume.inputs['Density']);out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(volume.outputs['Volume'],out.inputs['Volume']);domain.data.materials.append(mat)
invisible=bpy.data.materials.new('GasPilotv004 | emitter mesh invisible only');invisible.use_nodes=True;nn=invisible.node_tree;nn.nodes.clear();tr=nn.nodes.new('ShaderNodeBsdfTransparent');out=nn.nodes.new('ShaderNodeOutputMaterial');nn.links.new(tr.outputs[0],out.inputs[0])
sources=[]
for index,(position,radius,velocity,end,temp,density) in enumerate([
    ((0,0,.22),.31,(.12,0,1.55),5,.75,1.0),
    ((-.25,.10,.23),.24,(-.38,.12,1.35),4,.85,.8),
    ((.23,-.11,.31),.22,(.45,-.12,1.6),6,.65,.9),
]):
    if proof:radius*=1.25;end+=2
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=radius,location=anchor.location+Vector(position));ob=bpy.context.object;ob.name=f'GasPilotv004 | short smoke inflow{index}'
    for vertex in ob.data.vertices:
        vertex.co.z*=.78;vertex.co.x*=1+.09*math.sin(vertex.co.y*19+index)
    in_collection(ob);ob.parent=anchor;ob.matrix_parent_inverse=anchor.matrix_world.inverted();ob.data.materials.append(invisible)
    fm=ob.modifiers.new('GasPilotv004 | smoke flow','FLUID');fm.fluid_type='FLOW';bpy.context.view_layer.update();flow=fm.flow_settings
    flow.flow_type='SMOKE';flow.flow_behavior='INFLOW';flow.use_inflow=True;flow.use_initial_velocity=True;flow.velocity_coord=velocity;flow.velocity_normal=.35;flow.velocity_random=.25;flow.temperature=temp;flow.density=density;flow.surface_distance=1.5;flow.volume_density=1
    flow.use_inflow=True;flow.keyframe_insert(data_path='use_inflow',frame=1);flow.keyframe_insert(data_path='use_inflow',frame=end);flow.use_inflow=False;flow.keyframe_insert(data_path='use_inflow',frame=end+1)
    sources.append({'object':ob.name,'source_local_position':position,'radius':radius,'velocity':velocity,'emission_end_frame':end})
domain.hide_render=False
# Small lights affect only this isolated volume/debris render over the held
# plate. They are not production receiver materials or a main lighting pass.
preview=bpy.data.collections.new('GasPilotv004 | PREVIEW shading lights only');s.collection.children.link(preview)
for name,offset,power,size,color in [
    ('soft overhead key',(-3,-4,6),650,4.0,(.72,.80,.94)),
    ('weak lateral fill',(3,-1,4),90,3.0,(.56,.65,.80)),
]:
    ld=bpy.data.lights.new('GasPilotv004 PREVIEW | '+name,'AREA');ld.energy=power;ld.shape='DISK';ld.size=size;ld.color=color
    lo=bpy.data.objects.new(ld.name,ld);preview.objects.link(lo);lo.location=anchor.location+Vector(offset);lo.rotation_euler=(anchor.location+Vector((0,0,1.6))-lo.location).to_track_quat('-Z','Y').to_euler()
s.frame_set(1);bpy.context.view_layer.update()
bpy.ops.object.select_all(action='DESELECT');domain.select_set(True);bpy.context.view_layer.objects.active=domain
native=P/('native/WTSC_Gas_Proof_48r_120f_v004.blend' if proof else 'native/WTSC_Gas_Pilot_40r_72f_v004.blend')
bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
config={'blender':bpy.app.version_string,'solver':'Installed native FLUID/GAS (Mantaflow)','domain_object':domain.name,'domain_metres':[4.2,2.8,4.0],'resolution_max':resolution,'cache_frames':[1,end_frame],'fps':24,'seconds':end_frame/24,'cache_type':'MODULAR OPENVDB','noise_upres':False,'adaptive_domain':False,'threads':2,'cache_path':d.cache_directory,'source_world_position':list(anchor.location),'sources':sources,'buoyancy':{'density':d.alpha,'heat':d.beta},'vorticity':d.vorticity,'dissolve_smoke':getattr(d,'use_dissolve_smoke',None),'timesteps':[1,2],'hard_supervisor_limits':{'wall_seconds':120,'cache_MiB':128,'rss_MiB':2048},'note':'Technique test only. No production edit and no main lighting pass. v003 smoke cards are hidden only in this isolated copy.'}
(P/('evidence/proof_config.json' if proof else 'evidence/pilot_config.json')).write_text(json.dumps(config,indent=2));print('GAS_BAKE_START',json.dumps(config),flush=True)
start=time.perf_counter();result=bpy.ops.fluid.bake_data();elapsed=time.perf_counter()-start
assert 'FINISHED' in result and d.has_cache_baked_data,(str(result),d.has_cache_baked_data)
files=[file for file in (P/'cache'/cache_name).rglob('*') if file.is_file()]
assert any(file.suffix.lower()=='.vdb' for file in files)
report={'operator_result':list(result),'has_cache_baked_data':d.has_cache_baked_data,'bake_seconds':elapsed,'cache_files':len(files),'cache_bytes':sum(file.stat().st_size for file in files),'cache_vdb_files':sum(file.suffix.lower()=='.vdb' for file in files),'native_path':str(native),'volume_node_inputs':[i.name for i in volume.inputs]}
bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
(P/('evidence/proof_bake_result.json' if proof else 'evidence/bake_result.json')).write_text(json.dumps(report,indent=2));print('GAS_BAKE_COMPLETE',json.dumps(report),flush=True)
