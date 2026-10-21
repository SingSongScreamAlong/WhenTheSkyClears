"""Ground-first proof. Bullet fragments baked to native actions; no smoke/painted cloud."""
import bpy,bmesh,math,random,json,time,re,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parents[1]
s=bpy.data.scenes['FX_PROOF_v006 | painted impulse depth tracers and ground'];bpy.context.window.scene=s
old=s.compositing_node_group
bg=next(n.image for n in old.nodes if n.type=='IMAGE' and n.image.size[0]==3840)
fg=next(n.image for n in old.nodes if n.type=='IMAGE' and 'Native_Foreground_Alpha' in n.image.name)
depth=next(n.image for n in old.nodes if n.type=='IMAGE' and 'Native_Depth_Alpha_Y10_' in n.image.name)
for col in list(s.collection.children):s.collection.children.unlink(col)
for ob in list(s.collection.objects):
    if ob!=s.camera:s.collection.objects.unlink(ob)
for layer in list(s.view_layers)[1:]:s.view_layers.remove(layer)
s.name='FXv009 | ground debris proof';s.view_layers[0].name='GROUND_ONLY'
s.frame_start=1;s.frame_end=120;s.render.fps=24;s.render.fps_base=1
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=24;s.render.threads_mode='FIXED';s.render.threads=2
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100
s.render.film_transparent=True;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.media_type='IMAGE'
s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0;s.view_settings.gamma=1
if hasattr(s.render,'compositor_device'):s.render.compositor_device='GPU'
s.gravity=(0,0,-9.81);s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
asset=bpy.data.collections.new('FXv009 | GROUND IMPACT | baked Bullet and crater');s.collection.children.link(asset)
preview=bpy.data.collections.new('FXv009 | PREVIEW lighting and collision only');s.collection.children.link(preview)
def link(ob,col=asset):
    for c in list(ob.users_collection):c.objects.unlink(ob)
    col.objects.link(ob);return ob
def point(u,v,y):
    c=s.camera.matrix_world.translation;b=world_to_camera_view(s,s.camera,Vector((c.x,y,c.z)));x=world_to_camera_view(s,s.camera,Vector((c.x+1,y,c.z)));z=world_to_camera_view(s,s.camera,Vector((c.x,y,c.z+1)))
    return Vector((c.x+(u-b.x)/(x.x-b.x),y,c.z+(v-b.y)/(z.y-b.y)))
root=bpy.data.objects.new('FXv009 | impact anchor and controls',None);asset.objects.link(root);root.location=point(.785,.332,10);root.empty_display_type='CIRCLE';root.empty_display_size=.4
for k,v in {'start_frame':7.,'speed':1.,'size':1.,'age':0.,'dust':0.}.items():root[k]=v
root['construction']='Native faceted 3D ground + Bullet-launched coherent chunks baked into editable NLA actions. No smoke, cloud cards, generated pose dissolves, or cloud mesh deformation.'
def drive(owner,path,expression,index=None):
    f=owner.driver_add(path) if index is None else owner.driver_add(path,index);f.driver.type='SCRIPTED'
    for v in list(f.driver.variables):f.driver.variables.remove(v)
    for n,k in [('t','age'),('start','start_frame'),('speed','speed'),('S','size'),('D','dust')]:
        if not re.search(r'\b'+n+r'\b',expression):continue
        v=f.driver.variables.new();v.name=n;v.type='SINGLE_PROP';v.targets[0].id=root;v.targets[0].data_path='["'+k+'"]'
    f.driver.expression=expression;return f
drive(root,'["age"]','(frame-start)*speed')
for a in range(3):drive(root,'scale','max(.01,S)',a)
rng=random.Random(9139)
def pigment(name,lo,hi):
    m=bpy.data.materials.new('FXv009 | '+name);m.use_nodes=True;nt=m.node_tree;nt.nodes.clear()
    c=nt.nodes.new('ShaderNodeTexCoord');noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=36;noise.inputs['Detail'].default_value=3;nt.links.new(c.outputs['Generated'],noise.inputs['Vector'])
    ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.25;ramp.color_ramp.elements[0].color=(*lo,1);ramp.color_ramp.elements[1].position=.75;ramp.color_ramp.elements[1].color=(*hi,1);nt.links.new(noise.outputs['Fac'],ramp.inputs[0])
    diff=nt.nodes.new('ShaderNodeBsdfDiffuse');diff.inputs['Roughness'].default_value=1;nt.links.new(ramp.outputs[0],diff.inputs['Color'])
    em=nt.nodes.new('ShaderNodeEmission');em.inputs['Strength'].default_value=.35;nt.links.new(ramp.outputs[0],em.inputs['Color']);add=nt.nodes.new('ShaderNodeAddShader');nt.links.new(diff.outputs[0],add.inputs[0]);nt.links.new(em.outputs[0],add.inputs[1]);out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(add.outputs[0],out.inputs[0]);return m
soil=pigment('cold broken soil',(.025,.028,.027),(.095,.096,.087));rim=pigment('fresh torn rim',(.075,.075,.064),(.18,.173,.145));pit=pigment('deep charcoal inner wall',(.007,.009,.010),(.024,.026,.025));plaster=pigment('broken dusty plaster',(.11,.11,.098),(.26,.25,.21))
def meshob(name,verts,faces,mats,inds=None):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
    for mat in mats:me.materials.append(mat)
    if inds:
        for poly,i in zip(me.polygons,inds):poly.material_index=i
    ob=bpy.data.objects.new('FXv009 | '+name,me);asset.objects.link(ob);ob.parent=root;return ob
# Actual bowl, fractured raised rim, outer apron. Horizontal plan has depth.
N=48;verts=[];faces=[];mi=[]
profiles=[(.0,-.16),(.35,-.15),(.69,-.06),(.85,.135),(1.0,.02),(1.32,0)]
for ring,(r,z) in enumerate(profiles):
    for j in range(N):
        a=j*2*math.pi/N;rough=1+.10*math.sin(7*a+.4)+.045*math.sin(13*a);front=max(0,-math.sin(a));zz=z
        if ring==3:zz*=1-.65*front
        if ring>1:zz+=.018*math.sin(11*a+ring)
        verts.append((r*.72*math.cos(a)*rough,r*.67*math.sin(a)*rough,zz))
for ring in range(len(profiles)-1):
    for j in range(N):
        a=ring*N+j;b=ring*N+(j+1)%N;c=b+N;d=a+N;faces.append((a,b,c,d));mi.append(2 if ring<2 else (1 if ring==2 else 0))
ground=meshob('persistent excavated bowl and raised rim',verts,faces,[soil,rim,pit],mi)
for a in range(3):drive(ground,'scale','1 if t>=1 else .0001',a)
ground['persistent']='Never fades after impact; actual bowl and raised asymmetric rim, no flat ground decal.'
# A small cloud of soil clods carries the first impulse; twelve large pieces remain trackable.
chunks=[];spec=[]
for i in range(18):
    side=-1 if i%2==0 else 1
    vx=side*rng.uniform(.60,1.60);vy=rng.uniform(-.18,.32);vz=rng.uniform(4.0,6.4)
    rad=rng.uniform(.068,.108) if i<12 else rng.uniform(.032,.055)
    birth=7+(i%3);origin=Vector((rng.uniform(-.10,.10),rng.uniform(-.05,.10),rad+.01))
    bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=1,radius=rad)
    for v in bm.verts:v.co.x*=rng.uniform(.8,1.45);v.co.y*=rng.uniform(.6,1.0);v.co.z*=rng.uniform(.6,1.15)
    me=bpy.data.meshes.new('FXv009 | rigid fragment geometry');bm.to_mesh(me);bm.free();me.materials.append(plaster if i in [0,3,7,10] else soil)
    ob=bpy.data.objects.new(f'FXv009 | coherent tumbling clod {i:02d}',me);asset.objects.link(ob);ob.location=root.location+origin
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.rigidbody.object_add()
    rb=ob.rigid_body;rb.type='ACTIVE';rb.mass=rad**3*2000;rb.collision_shape='CONVEX_HULL';rb.use_margin=True;rb.collision_margin=.003;rb.friction=.85;rb.restitution=.12;rb.linear_damping=.08;rb.angular_damping=.45
    # Sparse ejecta collide with the floor, not one another at the shared launch point.
    # Avoid artificial impulses from overlapping source clods.
    rb.collision_collections=[j==i for j in range(20)]
    for fr in [1,birth,birth+1,birth+2]:
        dt=max(0,fr-birth)/24;ob.location=root.location+origin+Vector((vx*dt,vy*dt,vz*dt));ob.rotation_euler=(dt*7,dt*11,dt*5);ob.keyframe_insert('location',frame=fr);ob.keyframe_insert('rotation_euler',frame=fr);rb.kinematic=True;rb.keyframe_insert('kinematic',frame=fr)
    rb.kinematic=False;rb.keyframe_insert('kinematic',frame=birth+3)
    chunks.append(ob);spec.append({'name':ob.name,'radius':rad,'launch_frame':birth,'launch_velocity':[vx,vy,vz]})
# Passive local collision surface is test support, removed after bake.
bpy.ops.mesh.primitive_cube_add(size=1,location=root.location+Vector((0,0,-.07)));floor=link(bpy.context.object,preview);floor.name='FXv009 | temporary Bullet collision floor';floor.scale=(20,20,.14);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
bpy.ops.rigidbody.object_add();floor.rigid_body.type='PASSIVE';floor.rigid_body.friction=.85;floor.rigid_body.restitution=.10;floor.rigid_body.use_margin=True;floor.rigid_body.collision_margin=.001;floor.rigid_body.collision_collections=[True]*20;floor.hide_render=True
rw=s.rigidbody_world;rw.substeps_per_frame=8;rw.solver_iterations=20;rw.point_cache.frame_start=1;rw.point_cache.frame_end=120
start=time.perf_counter();samples={ob.name:[] for ob in chunks}
for fr in range(1,121):
    s.frame_set(fr);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
    for ob in chunks:samples[ob.name].append(ob.evaluated_get(dg).matrix_world.copy())
duration=time.perf_counter()-start
for ob,info in zip(chunks,spec):
    matrices=samples[ob.name];ob.animation_data_clear();bpy.context.view_layer.objects.active=ob;bpy.ops.rigidbody.object_remove();ob.parent=root
    for fr,ma in enumerate(matrices,1):
        local=Matrix.Translation(-root.location)@ma;loc,rot,scale=local.decompose();ob.location=loc;ob.rotation_mode='QUATERNION';ob.rotation_quaternion=rot;ob.keyframe_insert('location',frame=fr);ob.keyframe_insert('rotation_quaternion',frame=fr)
    action=ob.animation_data.action;action.name=ob.name+' | baked Bullet transform';ob.animation_data.action=None
    track=ob.animation_data.nla_tracks.new();strip=track.strips.new('RETIME using root start_frame and speed',1,action);strip.use_animated_time=True;strip.frame_end=100000;strip.blend_type='REPLACE';strip.extrapolation='HOLD';drive(strip,'strip_time','max(1,min(120,t+7))')
    for a in range(3):drive(ob,'scale',f'1 if t>={info["launch_frame"]-7} else .0001',a)
    z=[m.translation.z-root.location.z for m in matrices];info.update({'apex_frame':max(range(120),key=lambda k:z[k])+1,'apex_height':max(z),'final_local_location':list(matrices[-1].translation-root.location),'height_samples':z})
    assert max(z)>.4,info
    assert abs(z[-1])<.3,info
bpy.data.objects.remove(floor,do_unlink=True)
if s.rigidbody_world:bpy.ops.rigidbody.world_remove()
# Fracture slabs settle around the rim, not a single dark smear.
for i in range(15):
    a=2*math.pi*i/15;rad=rng.uniform(.048,.105);bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=rad);ob=link(bpy.context.object);ob.name=f'FXv009 | attached broken rim piece {i:02d}';ob.parent=root;ob.location=(.66*math.cos(a),.61*math.sin(a),.05);ob.scale=(1.4,.7,.60);ob.data.materials.append(rim if i%3 else plaster)
    for axis,value in enumerate(list(ob.scale)):drive(ob,'scale',f'{value}*max(0,min(1,(t-1)/3))',axis)
# Fixture-only lighting. This collection is explicitly excluded from append asset.
world=bpy.data.worlds.new('FXv009 | proof neutral world');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.20,.21,1);world.node_tree.nodes['Background'].inputs[1].default_value=.55;s.world=world
ld=bpy.data.lights.new('FXv009 | preview soft daylight','AREA');ld.energy=220;ld.shape='DISK';ld.size=5;ob=bpy.data.objects.new(ld.name,ld);preview.objects.link(ob);ob.location=root.location+Vector((-2,-4,6));ob.rotation_euler=(root.location-ob.location).to_track_quat('-Z','Y').to_euler()
sun=bpy.data.lights.new('FXv009 | preview key','SUN');sun.energy=.9;sun.angle=.12;ob=bpy.data.objects.new(sun.name,sun);preview.objects.link(ob);ob.rotation_euler=(.6,-.45,-.8)
# Composite only FX over the actual held production framing, with native masks.
nt=bpy.data.node_groups.new('FXv009 | held shot proof compositor','CompositorNodeTree');nt.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor');s.compositing_node_group=nt
bn=nt.nodes.new('CompositorNodeImage');bn.image=bg;scale=nt.nodes.new('CompositorNodeScale');scale.inputs['X'].default_value=.5;scale.inputs['Y'].default_value=.5;nt.links.new(bn.outputs['Image'],scale.inputs['Image']);rl=nt.nodes.new('CompositorNodeRLayers');rl.scene=s;rl.layer='GROUND_ONLY'
a=nt.nodes.new('CompositorNodeImage');a.image=fg;b=nt.nodes.new('CompositorNodeImage');b.image=depth;mx=nt.nodes.new('ShaderNodeMath');mx.operation='MAXIMUM';nt.links.new(a.outputs['Alpha'],mx.inputs[0]);nt.links.new(b.outputs['Alpha'],mx.inputs[1]);inv=nt.nodes.new('ShaderNodeMath');inv.operation='SUBTRACT';inv.inputs[0].default_value=1;nt.links.new(mx.outputs[0],inv.inputs[1]);mul=nt.nodes.new('ShaderNodeMath');mul.operation='MULTIPLY';nt.links.new(rl.outputs['Alpha'],mul.inputs[0]);nt.links.new(inv.outputs[0],mul.inputs[1]);sa=nt.nodes.new('CompositorNodeSetAlpha');nt.links.new(rl.outputs['Image'],sa.inputs['Image']);nt.links.new(mul.outputs[0],sa.inputs['Alpha']);over=nt.nodes.new('CompositorNodeAlphaOver');nt.links.new(scale.outputs[0],over.inputs['Background']);nt.links.new(sa.outputs[0],over.inputs['Foreground']);out=nt.nodes.new('NodeGroupOutput');nt.links.new(over.outputs[0],out.inputs['Image'])
s.frame_set(20);bpy.context.view_layer.update()
outpath=P/'native/WTSC_Ground_Debris_Proof_v009.blend';bpy.ops.wm.save_as_mainfile(filepath=str(outpath),compress=True)
report={'status':'Unreviewed ground-only key render pending. No smoke authorized until visual weight passes.','blender':bpy.app.version_string,'build_hash':bpy.app.build_hash.decode(),'fps':24,'frames':[1,120],'impact_frame':7,'pixels':[1920,1080],'root':list(root.location),'screen_root':list(world_to_camera_view(s,s.camera,root.location)),'construction':'Native 3D crater and Bullet rigid-body launch/contact, baked NLA transform animation; no smoke.','simulation_seconds':duration,'source_unchanged':True,'debris':spec,'objects':len(asset.all_objects)}
(P/'evidence/build_ground.json').write_text(json.dumps(report,indent=2));print('GROUND_PROOF_BUILT',json.dumps({k:v for k,v in report.items() if k!='debris'}),flush=True)
