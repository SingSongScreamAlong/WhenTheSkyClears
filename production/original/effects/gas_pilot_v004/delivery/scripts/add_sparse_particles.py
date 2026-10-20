"""Native small Newtonian particle systems, isolated proof only."""
import bpy,json,time,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]
s=bpy.data.scenes['GAS_PROOF_v004 |48div120frames | held framing'];bpy.context.window.scene=s
root=bpy.data.objects['FXv003 | fixed ground origin and controls'];origin=Vector(root.location)
for ob in s.objects:
    if ob.name.startswith('FXv003 | weighted debris '):ob.hide_render=True
c=bpy.data.collections.new('GasParticlesv004 |12debris6embers | native NEWTON');s.collection.children.link(c)
def move_collection(ob):
    for old in list(ob.users_collection):old.objects.unlink(ob)
    c.objects.link(ob)
invisible=bpy.data.materials['GasPilotv004 | emitter mesh invisible only']
chipmat=bpy.data.materials['FXv003 | rough broken charcoal and plaster']
embermat=bpy.data.materials.new('GasParticlesv004 | brief matte warm ember');embermat.use_nodes=True;nt=embermat.node_tree;nt.nodes.clear();em=nt.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=(.8,.16,.025,1)
f=em.inputs['Strength'].driver_add('default_value');f.driver.expression='2.2*exp(-max(0,t)/9)*max(0,min(1,(36-t)/8))';v=f.driver.variables.new();v.name='t';v.type='SINGLE_PROP';v.targets[0].id=root;v.targets[0].data_path='["age"]'
out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],out.inputs[0])
systems=[]
for name,count,material,size,speed,lifetime,seed in [('debris',12,chipmat,.010,4.5,48,4026),('embers',6,embermat,.007,3.0,28,913)]:
    # Model lives at world origin, far outside the actual held camera's X range.
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=(0,0,0));model=bpy.context.object;model.name='GasParticlesv004 | instance model '+name
    for vertex in model.data.vertices:vertex.co.x*=.65;vertex.co.y*=.45
    model.data.materials.append(material);move_collection(model)
    mesh=bpy.data.meshes.new('GasParticlesv004 | emission face '+name);mesh.from_pydata([(-.12,-.10,0),(.12,-.10,0),(.12,.10,0),(-.12,.10,0)],[],[(0,1,2,3)]);mesh.materials.append(invisible);mesh.update()
    emitter=bpy.data.objects.new('GasParticlesv004 | anchored '+name+' emitter',mesh);c.objects.link(emitter);emitter.location=origin+Vector((0,-.1,.09))
    bpy.context.view_layer.objects.active=emitter;emitter.select_set(True);bpy.ops.object.particle_system_add();ps=emitter.particle_systems[-1];ps.seed=seed;settings=ps.settings;settings.name='GasParticlesv004 | '+name+' NEWTON seed'+str(seed)
    settings.type='EMITTER';settings.physics_type='NEWTON';settings.emit_from='FACE';settings.count=count;settings.frame_start=1;settings.frame_end=5;settings.lifetime=lifetime;settings.lifetime_random=.3
    settings.normal_factor=speed;settings.factor_random=.65;settings.particle_size=size;settings.size_random=.6;settings.render_type='OBJECT';settings.instance_object=model
    settings.use_rotations=True;settings.rotation_mode='VEL';settings.phase_factor_random=1;settings.angular_velocity_mode='RAND';settings.angular_velocity_factor=1.5
    settings.drag_factor=.10;settings.damping=.02;settings.use_dead=False
    emitter.show_instancer_for_render=False;emitter.show_instancer_for_viewport=False
    ps.point_cache.frame_start=1;ps.point_cache.frame_end=120;ps.point_cache.use_disk_cache=True
    systems.append((emitter,ps,{'kind':name,'count':count,'seed':seed,'particle_size':size,'initial_normal_velocity':speed,'lifetime_frames':lifetime}))
    emitter.select_set(False)
# Transparent local test collider only. Production continues to own live contact.
bpy.ops.mesh.primitive_plane_add(size=2,location=origin+Vector((0,0,-.02)));floor=bpy.context.object;floor.name='GasParticlesv004 | TEST ONLY transparent collision floor';floor.scale=(2,1.5,1);floor.rotation_euler.x=-.14;floor.data.materials.append(invisible);move_collection(floor)
floor.modifiers.new('GasParticlesv004 | sparse particle contact','COLLISION');floor.collision.damping_factor=.85;floor.collision.friction_factor=.8
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=32;s.render.threads_mode='FIXED';s.render.threads=2
if hasattr(s.render,'compositor_device'):s.render.compositor_device='GPU'
for name,value in [('volumetric_samples',96),('volumetric_shadow_samples',32),('use_volumetric_shadows',True),('use_volume_custom_range',True),('volumetric_start',18.0),('volumetric_end',34.0),('volumetric_sample_distribution',0.0),('volumetric_tile_size','4')]:
    if hasattr(s.eevee,name):setattr(s.eevee,name,value)
# Mild3D grain is finish only. The evolving contour comes from cached gas.
mat=bpy.data.materials['GasPilotv004 | cold native volume | NO emission'];nt=mat.node_tree;gain=next(n for n in nt.nodes if n.type=='MATH');density=gain.inputs[0].links[0].from_socket
noise=nt.nodes.new('ShaderNodeTexNoise');noise.name='Subtle3D wash grain | NOT simulated detail';noise.inputs['Scale'].default_value=15;noise.inputs['Detail'].default_value=2;coord=nt.nodes.new('ShaderNodeTexCoord');nt.links.new(coord.outputs['Generated'],noise.inputs[0])
mul=nt.nodes.new('ShaderNodeMath');mul.operation='MULTIPLY_ADD';mul.inputs[1].default_value=.16;mul.inputs[2].default_value=.84;nt.links.new(noise.outputs['Fac'],mul.inputs[0])
grain=nt.nodes.new('ShaderNodeMath');grain.operation='MULTIPLY';nt.links.new(density,grain.inputs[0]);nt.links.new(mul.outputs[0],grain.inputs[1]);nt.links.new(grain.outputs[0],gain.inputs[0])
native=P/'native/WTSC_Gas_Particles_Proof_48r_120f_v004.blend';s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
start=time.perf_counter();reports=[]
for emitter,ps,report in systems:
    bpy.ops.object.select_all(action='DESELECT');emitter.select_set(True);bpy.context.view_layer.objects.active=emitter
    with bpy.context.temp_override(scene=s,object=emitter,active_object=emitter,point_cache=ps.point_cache):
        result=bpy.ops.ptcache.bake(bake=True)
    report.update({'bake_result':list(result),'is_baked':ps.point_cache.is_baked,'disk_cache':ps.point_cache.use_disk_cache})
    assert ps.point_cache.is_baked,report
    reports.append(report)
elapsed=time.perf_counter()-start
samples=[]
for frame in [6,12,24,48,100]:
    s.frame_set(frame);bpy.context.view_layer.update();states=[]
    for emitter,ps,report in systems:
        particles=emitter.evaluated_get(bpy.context.evaluated_depsgraph_get()).particle_systems[0].particles
        alive=[p for p in particles if p.alive_state=='ALIVE'];states.append({'kind':report['kind'],'alive':len(alive),'sample_positions':[list(p.location) for p in alive[:3]]})
    samples.append({'frame':frame,'systems':states})
s.frame_set(36);bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
files=[f for f in (P/'native').rglob('*.bphys') if f.is_file()]
report={'native':str(native),'systems':reports,'particle_bake_seconds':elapsed,'pointcache_files':len(files),'pointcache_bytes':sum(f.stat().st_size for f in files),'samples':samples,'smoke':'Native cached48-division gas. No smoke particles pretending to be volume.','finishing':'Subtle16percent3D noise density wash; actual large structures are simulated. Cold volume emission/blackbody remain zero.','lighting':'Separate preview-only shading lights. No production lighting edit.','collider':'Separate transparent test floor; does not establish production contact.'}
(P/'evidence/particle_setup.json').write_text(json.dumps(report,indent=2));print('GAS_PARTICLES_READY',json.dumps(report),flush=True)
