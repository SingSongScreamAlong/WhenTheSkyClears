"""Bounded finite native gas pulse supports connected earth and low rolling dust."""
import bpy,math,json,time,re
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];s=bpy.data.scenes['FXv010 | joined rupture and ground dust'];bpy.context.window.scene=s
root=bpy.data.objects['FXv010 | fixed impact anchor and timing'];asset=bpy.data.collections['FXv010 | JOINED EARTH RUPTURE and DUST'];preview=bpy.data.collections['FXv010 | PREVIEW lights and solver support']
def move(ob,col):
    for c in list(ob.users_collection):c.objects.unlink(ob)
    col.objects.link(ob);return ob
def drive(owner,path,expr):
    f=owner.driver_add(path);f.driver.type='SCRIPTED'
    for v in list(f.driver.variables):f.driver.variables.remove(v)
    for n,k in [('t','age'),('D','dust_density')]:
        if not re.search(r'\b'+n+r'\b',expr):continue
        v=f.driver.variables.new();v.name=n;v.type='SINGLE_PROP';v.targets[0].id=root;v.targets[0].data_path='["'+k+'"]'
    f.driver.expression=expr
invis=bpy.data.materials['FXv010 | invisible solver support']
collider=bpy.data.objects['FXv010 | TEST actual terrain collision solid'];collider.hide_render=False
fm=collider.modifiers.new('FXv010 | ground contact for dust','FLUID');fm.fluid_type='EFFECTOR';bpy.context.view_layer.update();fm.effector_settings.effector_type='COLLISION';fm.effector_settings.surface_distance=.03
bpy.ops.mesh.primitive_cube_add(size=1,location=root.location+Vector((0,0,1.0)));domain=move(bpy.context.object,asset);domain.name='FXv010 | bounded native dust mass |64cells';domain.dimensions=(6.0,2.4,2.8);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
domain.parent=root;domain.matrix_parent_inverse=root.matrix_world.inverted()
dm=domain.modifiers.new('FXv010 | Mantaflow finite dust pulse','FLUID');dm.fluid_type='DOMAIN';bpy.context.view_layer.update();d=dm.domain_settings;d.domain_type='GAS';d.resolution_max=64;d.cache_type='MODULAR';d.cache_frame_start=1;d.cache_frame_end=120;d.cache_data_format='OPENVDB';d.cache_directory=str(P/'cache/dust64_flat');d.cache_resumable=False;d.use_noise=False;d.use_adaptive_domain=False;d.timesteps_min=1;d.timesteps_max=2;d.cfl_condition=4;d.time_scale=1;d.alpha=1.6;d.beta=0;d.vorticity=1.3;d.use_dissolve_smoke=True;d.dissolve_speed=40;d.use_dissolve_smoke_log=True
for name in ['front','back','left','right','top','bottom']:
    key='use_collision_border_'+name
    if hasattr(d,key):setattr(d,key,False)
mat=bpy.data.materials.new('FXv010 | cold ink dust volume no heat or glow');mat.use_nodes=True;nt=mat.node_tree;nt.nodes.clear();info=nt.nodes.new('ShaderNodeVolumeInfo');tc=nt.nodes.new('ShaderNodeTexCoord');noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=13;noise.inputs['Detail'].default_value=3;nt.links.new(tc.outputs['Generated'],noise.inputs[0]);grain=nt.nodes.new('ShaderNodeMath');grain.operation='MULTIPLY_ADD';grain.inputs[1].default_value=.30;grain.inputs[2].default_value=.85;nt.links.new(noise.outputs['Fac'],grain.inputs[0]);mul=nt.nodes.new('ShaderNodeMath');mul.operation='MULTIPLY';nt.links.new(info.outputs['Density'],mul.inputs[0]);nt.links.new(grain.outputs[0],mul.inputs[1]);gain=nt.nodes.new('ShaderNodeMath');gain.operation='MULTIPLY';drive(gain.inputs[1],'default_value','32*D');nt.links.new(mul.outputs[0],gain.inputs[0]);vol=nt.nodes.new('ShaderNodeVolumePrincipled');vol.inputs['Color'].default_value=(.095,.108,.105,1);vol.inputs['Anisotropy'].default_value=.1
for name in ['Density Attribute','Color Attribute','Temperature Attribute']:
    if name in vol.inputs:vol.inputs[name].default_value=''
vol.inputs['Emission Strength'].default_value=0;vol.inputs['Blackbody Intensity'].default_value=0;nt.links.new(gain.outputs[0],vol.inputs['Density']);out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(vol.outputs['Volume'],out.inputs['Volume']);domain.data.materials.append(mat)
noise.inputs['Scale'].default_value=55;grain.inputs[1].default_value=1.2;grain.inputs[2].default_value=.30;vol.inputs['Color'].default_value=(.18,.20,.18,1)
next(f for f in nt.animation_data.drivers if f.data_path.endswith('inputs[1].default_value')).driver.expression='19*D'
sources=[]
specs=[
 ('short earth core',(0,0,.10),(.40,.28,.22),(.1,0,2.5),7,9,1.6),
 ('left low dust',(-.24,-.18,.07),(.38,.32,.16),(-4.5,-.08,.22),7,9,1.5),
 ('right low dust',(.24,-.18,.07),(.38,.32,.16),(4.4,-.06,.20),7,9,1.5),
 ('rear rolling dust',(0,.20,.12),(.42,.25,.16),(.1,.18,.5),8,10,1.0)]
for name,pos,scale,vel,birth,end,density in specs:
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=root.location+Vector(pos));ob=move(bpy.context.object,asset);ob.name='FXv010 | finite flow '+name
    for v in ob.data.vertices:v.co.x*=scale[0];v.co.y*=scale[1];v.co.z*=scale[2]
    ob.parent=root;ob.matrix_parent_inverse=root.matrix_world.inverted();ob.data.materials.append(invis)
    flowmod=ob.modifiers.new('FXv010 | finite native dust source','FLUID');flowmod.fluid_type='FLOW';bpy.context.view_layer.update();f=flowmod.flow_settings;f.flow_type='SMOKE';f.flow_behavior='INFLOW';f.use_initial_velocity=True;f.velocity_coord=vel;f.velocity_normal=.25;f.velocity_random=.18;f.temperature=0;f.density=density;f.surface_distance=1.2;f.volume_density=1
    for fr,on in [(1,False),(birth-1,False),(birth,True),(end,True),(end+1,False)]:f.use_inflow=on;f.keyframe_insert('use_inflow',frame=fr)
    sources.append({'object':ob.name,'birth':birth,'last_inflow':end,'velocity':vel,'density':density})
# Compact controlled volume settings. No noise upres or expensive broad render.
for key,value in [('volumetric_samples',96),('volumetric_shadow_samples',24),('use_volumetric_shadows',True),('use_volume_custom_range',True),('volumetric_start',24.0),('volumetric_end',30.0),('volumetric_sample_distribution',0.0),('volumetric_tile_size','4')]:
    if hasattr(s.eevee,key):setattr(s.eevee,key,value)
s.frame_set(1);bpy.context.view_layer.update();bpy.ops.object.select_all(action='DESELECT');domain.select_set(True);bpy.context.view_layer.objects.active=domain
native=P/'native/WTSC_Earth_Rupture_Dust_v010f.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
config={'resolution':64,'domain_metres':[6,2.4,2.8],'frames':[1,120],'threads':2,'noise_upres':False,'sources':sources,'density_buoyancy':1.6,'heat_buoyancy':0,'vorticity':1.3,'cache_limit_bytes':134217728,'render_status':'Eight keyframes only after bake; no full animation yet.'}
(P/'evidence/dust_config_f.json').write_text(json.dumps(config,indent=2));print('BOUNDED_DUST_BAKE_START',json.dumps(config),flush=True)
t=time.perf_counter();result=bpy.ops.fluid.bake_data();elapsed=time.perf_counter()-t;assert 'FINISHED' in result and d.has_cache_baked_data
files=[f for f in (P/'cache/dust64_flat').rglob('*') if f.is_file()];total=sum(f.stat().st_size for f in files);assert total<134217728,total
d.cache_directory='//../cache/dust64_flat'
s.frame_set(20);bpy.context.view_layer.update();values=list(domain.evaluated_get(bpy.context.evaluated_depsgraph_get()).modifiers['FXv010 | Mantaflow finite dust pulse'].domain_settings.density_grid);assert max(values,default=0)>.01
bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
report={'bake_seconds':elapsed,'cache_bytes':total,'cache_files':len(files),'density_at_frame20_max':max(values),'density_at_frame20_sum':sum(values),'relative_cache':d.cache_directory,'status':'Await actual keyframe review of the combined construction.'}
(P/'evidence/dust_bake_f.json').write_text(json.dumps(report,indent=2));print('BOUNDED_DUST_BAKED',json.dumps(report),flush=True)
