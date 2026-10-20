"""Joined painted crust fractures over a genuinely depressed native terrain mesh."""
import bpy,bmesh,math,random,json,time,re,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parents[1];s=bpy.data.scenes['FXv009 | ground debris proof'];bpy.context.window.scene=s
old=s.compositing_node_group;bg=next(n.image for n in old.nodes if n.type=='IMAGE' and n.image.size[0]==3840);fg=next(n.image for n in old.nodes if n.type=='IMAGE' and 'Native_Foreground_Alpha' in n.image.name)
depth=bpy.data.images.load(str(P.parent/'blast_refinement_v006/assets/Native_Depth_Alpha_Y10_v006.png'),check_existing=True);depth.alpha_mode='STRAIGHT';depth.pack()
for c in list(s.collection.children):s.collection.children.unlink(c)
for ob in list(s.collection.objects):
    if ob!=s.camera:s.collection.objects.unlink(ob)
for layer in list(s.view_layers)[1:]:s.view_layers.remove(layer)
s.name='FXv010 | joined rupture and ground dust';s.view_layers[0].name='RUPTURE'
s.frame_start=1;s.frame_end=120;s.render.fps=24;s.render.fps_base=1;s.gravity=(0,0,-9.81)
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=24;s.render.threads_mode='FIXED';s.render.threads=2
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.film_transparent=True;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.media_type='IMAGE'
s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0;s.view_settings.gamma=1
if hasattr(s.render,'compositor_device'):s.render.compositor_device='GPU'
asset=bpy.data.collections.new('FXv010 | JOINED EARTH RUPTURE and DUST');s.collection.children.link(asset)
preview=bpy.data.collections.new('FXv010 | PREVIEW lights and solver support');s.collection.children.link(preview)
def move(ob,c):
    for old in list(ob.users_collection):old.objects.unlink(ob)
    c.objects.link(ob);return ob
def point(u,v,y):
    p=s.camera.matrix_world.translation;b=world_to_camera_view(s,s.camera,Vector((p.x,y,p.z)));x=world_to_camera_view(s,s.camera,Vector((p.x+1,y,p.z)));z=world_to_camera_view(s,s.camera,Vector((p.x,y,p.z+1)))
    return Vector((p.x+(u-b.x)/(x.x-b.x),y,p.z+(v-b.y)/(z.y-b.y)))
root=bpy.data.objects.new('FXv010 | fixed impact anchor and timing',None);asset.objects.link(root);root.location=point(.790,.323,10);root.empty_display_type='CIRCLE';root.empty_display_size=.4
for k,v in {'start_frame':7.,'speed':1.,'size':1.,'age':0.,'dust_density':1.}.items():root[k]=v
def drive(owner,path,expr,index=None):
    f=owner.driver_add(path) if index is None else owner.driver_add(path,index);f.driver.type='SCRIPTED'
    for v in list(f.driver.variables):f.driver.variables.remove(v)
    for n,k in [('t','age'),('start','start_frame'),('speed','speed'),('S','size'),('D','dust_density')]:
        if not re.search(r'\b'+n+r'\b',expr):continue
        v=f.driver.variables.new();v.name=n;v.type='SINGLE_PROP';v.targets[0].id=root;v.targets[0].data_path='["'+k+'"]'
    f.driver.expression=expr;return f
drive(root,'["age"]','(frame-start)*speed')
for a in range(3):drive(root,'scale','max(.01,S)',a)
def matte(name,lo,hi):
    m=bpy.data.materials.new('FXv010 | '+name);m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();tc=nt.nodes.new('ShaderNodeTexCoord');noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=24;noise.inputs['Detail'].default_value=4;nt.links.new(tc.outputs['Generated'],noise.inputs[0]);r=nt.nodes.new('ShaderNodeValToRGB');r.color_ramp.elements[0].color=(*lo,1);r.color_ramp.elements[1].color=(*hi,1);nt.links.new(noise.outputs['Fac'],r.inputs[0]);d=nt.nodes.new('ShaderNodeBsdfDiffuse');nt.links.new(r.outputs[0],d.inputs[0]);d.inputs['Roughness'].default_value=1;e=nt.nodes.new('ShaderNodeEmission');e.inputs['Strength'].default_value=.25;nt.links.new(r.outputs[0],e.inputs[0]);add=nt.nodes.new('ShaderNodeAddShader');nt.links.new(d.outputs[0],add.inputs[0]);nt.links.new(e.outputs[0],add.inputs[1]);out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(add.outputs[0],out.inputs[0]);return m
soil=matte('fresh charcoal soil edges',(.008,.012,.013),(.055,.064,.061))
def plate_material(name,terrain=False):
    m=bpy.data.materials.new('FXv010 | '+name);m.use_nodes=True;m.surface_render_method='BLENDED';nt=m.node_tree;nt.nodes.clear();tex=nt.nodes.new('ShaderNodeTexImage');tex.image=bg;tex.extension='EXTEND';uv=nt.nodes.new('ShaderNodeTexCoord');nt.links.new(uv.outputs['UV'],tex.inputs[0]);mult=nt.nodes.new('ShaderNodeMixRGB');mult.blend_type='MULTIPLY';mult.inputs[0].default_value=1;nt.links.new(tex.outputs['Color'],mult.inputs[1]);mult.inputs[2].default_value=(1,1,1,1)
    if terrain:
        a=nt.nodes.new('ShaderNodeAttribute');a.attribute_name='ground_shade';nt.links.new(a.outputs['Fac'],mult.inputs[2])
    em=nt.nodes.new('ShaderNodeEmission');nt.links.new(mult.outputs[0],em.inputs[0]);out=nt.nodes.new('ShaderNodeOutputMaterial')
    if terrain:
        a=nt.nodes.new('ShaderNodeAttribute');a.attribute_name='ground_coverage';tr=nt.nodes.new('ShaderNodeBsdfTransparent');mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(a.outputs['Fac'],mix.inputs[0]);nt.links.new(tr.outputs[0],mix.inputs[1]);nt.links.new(em.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],out.inputs[0])
    else:
        # At rest the intact crust matches the held painting. During rupture it
        # exposes cold broken earth, instead of carrying bright path fragments.
        tc=nt.nodes.new('ShaderNodeTexCoord');noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=17;noise.inputs['Detail'].default_value=4;nt.links.new(tc.outputs['Generated'],noise.inputs[0]);ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.008,.013,.014,1);ramp.color_ramp.elements[1].color=(.075,.085,.077,1);nt.links.new(noise.outputs['Fac'],ramp.inputs[0]);mix=nt.nodes.new('ShaderNodeMixRGB');nt.links.new(mult.outputs[0],mix.inputs[1]);nt.links.new(ramp.outputs[0],mix.inputs[2]);drive(mix.inputs[0],'default_value','max(0,min(1,t))');nt.links.new(mix.outputs[0],em.inputs[0]);nt.links.new(em.outputs[0],out.inputs[0])
    return m
terrainmat=plate_material('project paint on excavated ground',True);capmat=plate_material('original project paint on rigid crust')
SLOPE=0.;N=64;profiles=[(.0,-.32),(.30,-.32),(.65,-.25),(.84,-.12),(1.,.006),(1.25,0),(1.75,0)]
def outline(a):return 1+.10*math.sin(5*a+.6)+.045*math.sin(11*a-1.2)+.035*math.sin(17*a)
def xy(r,a):return (.65*r*math.cos(a)*outline(a),.55*r*math.sin(a)*outline(a))
def bank(x,y,r):return .25*y*max(0,1-(r/1.25)**4)
verts=[];faces=[];shade=[];coverage=[]
for ring,(r,z) in enumerate(profiles):
    for j in range(N):
        a=j*2*math.pi/N;x,y=xy(r,a);zz=z+bank(x,y,r)
        if ring==4:zz+=.012*max(0,math.sin(7*a+.4))
        verts.append((x,y,zz));shade.append([.065,.065,.18,.44,.94,1,1][ring]);coverage.append(0 if ring==6 else 1)
for r in range(len(profiles)-1):
    for i in range(N):a=r*N+i;b=r*N+(i+1)%N;c=b+N;d=a+N;faces.append((a,d,c,b))
me=bpy.data.meshes.new('FXv010 | depressed irregular terrain');me.from_pydata(verts,[],faces);me.materials.append(terrainmat);me.update()
for name,values in [('ground_shade',shade),('ground_coverage',coverage)]:
    attr=me.attributes.new(name,'FLOAT','POINT')
    for d,v in zip(attr.data,values):d.value=v
uv=me.uv_layers.new(name='Fixed original project projection')
for loop in me.loops:
    co=root.location+me.vertices[loop.vertex_index].co;q=world_to_camera_view(s,s.camera,co);uv.data[loop.index].uv=(q.x,q.y)
terrain=bpy.data.objects.new('FXv010 | true depressed ground and irregular cut wall',me);asset.objects.link(terrain);terrain.parent=root;terrain['pit_depth_metres']=.32;terrain['rim_max_height_metres']=.018
# Closed duplicate of this actual terrain is the local Bullet and gas collider.
cm=me.copy();bm=bmesh.new();bm.from_mesh(cm);boundary=[v for v in bm.verts if v.index>=6*N];outer=[]
for v in boundary:outer.append(bm.verts.new((v.co.x*4,v.co.y*4,SLOPE*v.co.y*4)))
for i in range(N):j=(i+1)%N;bm.faces.new((boundary[i],outer[i],outer[j],boundary[j]))
boundary=outer;bottom=[]
for v in boundary:bottom.append(bm.verts.new((v.co.x,v.co.y,-5)))
for i in range(N):j=(i+1)%N;bm.faces.new((boundary[i],bottom[i],bottom[j],boundary[j]))
bm.faces.new(tuple(reversed(bottom)));bm.to_mesh(cm);bm.free();cm.materials.clear()
collider=bpy.data.objects.new('FXv010 | TEST actual terrain collision solid',cm);preview.objects.link(collider);collider.parent=root;collider.hide_render=True
bpy.context.view_layer.update();bpy.context.view_layer.objects.active=collider;collider.select_set(True);bpy.ops.rigidbody.object_add();collider.rigid_body.type='PASSIVE';collider.rigid_body.collision_shape='MESH';collider.rigid_body.friction=.9;collider.rigid_body.restitution=.08;collider.rigid_body.use_margin=True;collider.rigid_body.collision_margin=.002;collider.rigid_body.collision_collections=[True]*20
# Eight Voronoi-like shared-boundary solid crust blocks, not radial pie shards.
def clip(poly,n,b):
    out=[]
    for i,p in enumerate(poly):
        q=poly[(i+1)%len(poly)];dp=n[0]*p[0]+n[1]*p[1]-b;dq=n[0]*q[0]+n[1]*q[1]-b
        if dp<=1e-8:out.append(p)
        if (dp<0)!=(dq<0):u=dp/(dp-dq);out.append((p[0]+u*(q[0]-p[0]),p[1]+u*(q[1]-p[1])))
    return out
rng=random.Random(10219);chunks=[];records=[];seeds=[]
while len(seeds)<16:
    x=rng.uniform(-.57,.57);y=rng.uniform(-.47,.47)
    if (x/.63)**2+(y/.54)**2>.90 or any((x-a)**2+(y-b)**2<.19**2 for a,b in seeds):continue
    seeds.append((x,y))
count=len(seeds)
for i in range(count):
    poly=[xy(1.035,j*2*math.pi/N) for j in range(N)];seed=seeds[i]
    for j,other in enumerate(seeds):
        if j==i:continue
        poly=clip(poly,(other[0]-seed[0],other[1]-seed[1]),(other[0]**2+other[1]**2-seed[0]**2-seed[1]**2)/2)
    # The same deterministic wavy edge is used by each adjacent pair of cells.
    jagged=[]
    for j,p in enumerate(poly):
        q=poly[(j+1)%len(poly)];lo,hi=sorted([p,q]);dx=hi[0]-lo[0];dy=hi[1]-lo[1];length=math.hypot(dx,dy);normal=(-dy/length,dx/length) if length>1e-8 else (0,0);phase=(lo[0]+hi[0])*17+(lo[1]+hi[1])*23
        for u in [0,1/3,2/3]:
            cu=u if p==lo else 1-u;warp=.018*math.sin(math.pi*cu)*math.sin(phase)+.007*math.sin(2*math.pi*cu)*math.cos(phase*.7);jagged.append((p[0]+u*(q[0]-p[0])+normal[0]*warp,p[1]+u*(q[1]-p[1])+normal[1]*warp))
    poly=jagged;cx=sum(p[0] for p in poly)/len(poly);cy=sum(p[1] for p in poly)/len(poly);center=Vector((cx,cy,.003));V=[]
    def rough(x,y):return .012*math.sin(17*x+8*y)+.009*math.sin(23*y-5*x)
    V=[(0,0,.055+rough(cx,cy)+bank(cx,cy,math.hypot(cx/.65,cy/.55)))]
    for x,y in poly:V.append(tuple(Vector((x,y,bank(x,y,math.hypot(x/.65,y/.55))+.004+rough(x,y)))-center))
    thickness=rng.uniform(.10,.15)
    for x,y in poly:V.append(tuple(Vector((cx+(x-cx)*.88,cy+(y-cy)*.88,bank(x,y,math.hypot(x/.65,y/.55))-thickness+rough(x,y)))-center))
    m=len(poly);F=[];inds=[]
    for j in range(m):k=(j+1)%m;F.append((0,1+j,1+k));inds.append(0);F.append((1+j,1+m+j,1+m+k,1+k));inds.append(1)
    F.append(tuple(reversed(range(1+m,1+2*m))));inds.append(1)
    me=bpy.data.meshes.new(f'FXv010 | connected crust sector {i}');me.from_pydata(V,[],F);me.materials.append(capmat);me.materials.append(soil);me.update()
    for f,ind in zip(me.polygons,inds):f.material_index=ind
    uv=me.uv_layers.new(name='Rigid carried original paint')
    for loop in me.loops:q=world_to_camera_view(s,s.camera,root.location+center+me.vertices[loop.vertex_index].co);uv.data[loop.index].uv=(q.x,q.y)
    ob=bpy.data.objects.new(f'FXv010 | connected crust section {i:02d}',me);asset.objects.link(ob);ob.location=root.location+center
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.rigidbody.object_add();rb=ob.rigid_body;rb.mass=.9;rb.collision_shape='CONVEX_HULL';rb.use_margin=True;rb.collision_margin=.002;rb.friction=.9;rb.restitution=.08;rb.linear_damping=.16;rb.angular_damping=.5;rb.collision_collections=[j==i for j in range(20)]
    a=math.atan2(cy,cx);vx=1.40*math.cos(a)+.10;vy=.80*math.sin(a);vz=rng.uniform(3.9,5.0);spin=Vector((rng.uniform(-3,3),rng.uniform(-4,4),rng.uniform(-2,2)))
    for fr in [1,7,8,9]:
        dt=max(0,fr-7)/24;ob.location=root.location+center+Vector((vx*dt,vy*dt,vz*dt-4.905*dt*dt));ob.rotation_euler=spin*dt;ob.keyframe_insert('location',frame=fr);ob.keyframe_insert('rotation_euler',frame=fr);rb.kinematic=True;rb.keyframe_insert('kinematic',frame=fr)
    rb.kinematic=False;rb.keyframe_insert('kinematic',frame=10)
    action=ob.animation_data.action
    for layer in action.layers:
        for st in layer.strips:
            for bag in st.channelbags:
                for f in bag.fcurves:
                    for k in f.keyframe_points:k.interpolation='CONSTANT' if 'kinematic' in f.data_path else 'LINEAR'
    chunks.append(ob);records.append({'object':ob.name,'center':list(center),'velocity':[vx,vy,vz]})
rw=s.rigidbody_world;rw.substeps_per_frame=10;rw.solver_iterations=24;rw.point_cache.frame_start=1;rw.point_cache.frame_end=120
samples={o.name:[] for o in chunks};start=time.perf_counter()
for fr in range(1,121):
    s.frame_set(fr);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
    for o in chunks:samples[o.name].append(o.evaluated_get(dg).matrix_world.copy())
for o,rec in zip(chunks,records):
    base=[v.co.copy() for v in o.data.vertices];o.animation_data_clear();bpy.context.view_layer.objects.active=o;bpy.ops.rigidbody.object_remove();o.parent=root;o.location=(0,0,0);o.rotation_euler=(0,0,0);o.scale=(1,1,1)
    for age in range(114):
        ma=Matrix.Translation(-root.location)@samples[o.name][age+6];k=o.shape_key_add(name=f'RIGID_CRUST_AGE_{age:03d}');k.interpolation='KEY_LINEAR'
        for d,v in zip(k.data,base):d.co=ma@v
    o.data.shape_keys.use_relative=False;drive(o.data.shape_keys,'eval_time','10*max(0,min(113,t))')
    zs=[m.translation.z-root.location.z for m in samples[o.name]];rec.update({'apex_height':max(zs),'apex_frame':zs.index(max(zs))+1,'final_center':list(samples[o.name][-1].translation-root.location)})
    assert max(zs)>.6,rec
    final=samples[o.name][-1].translation-root.location
    assert abs(final.z-SLOPE*final.y)<.65,rec
bpy.context.view_layer.objects.active=collider;bpy.ops.rigidbody.object_remove();bpy.ops.rigidbody.world_remove()
# Native local collider remains transparent solver support for the bounded dust bake.
invis=bpy.data.materials.new('FXv010 | invisible solver support');invis.use_nodes=True;nt=invis.node_tree;nt.nodes.clear();tr=nt.nodes.new('ShaderNodeBsdfTransparent');out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(tr.outputs[0],out.inputs[0]);collider.data.materials.append(invis)
# Fixture-only restrained volume light; receiving production lighting is untouched.
for name,offset,energy,size in [('soft key',(-2,-4,5),460,4),('low fill',(3,-2,2),55,3)]:
    ld=bpy.data.lights.new('FXv010 PREVIEW | '+name,'AREA');ld.energy=energy;ld.shape='DISK';ld.size=size;ld.color=(.80,.84,.84);o=bpy.data.objects.new(ld.name,ld);preview.objects.link(o);o.location=root.location+Vector(offset);o.rotation_euler=(root.location+Vector((0,0,.5))-o.location).to_track_quat('-Z','Y').to_euler()
nt=bpy.data.node_groups.new('FXv010 | held project proof','CompositorNodeTree');nt.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor');s.compositing_node_group=nt
bn=nt.nodes.new('CompositorNodeImage');bn.image=bg;sc=nt.nodes.new('CompositorNodeScale');sc.inputs['X'].default_value=.5;sc.inputs['Y'].default_value=.5;nt.links.new(bn.outputs['Image'],sc.inputs['Image']);rl=nt.nodes.new('CompositorNodeRLayers');rl.scene=s;rl.layer='RUPTURE'
a=nt.nodes.new('CompositorNodeImage');a.image=fg;b=nt.nodes.new('CompositorNodeImage');b.image=depth;mx=nt.nodes.new('ShaderNodeMath');mx.operation='MAXIMUM';nt.links.new(a.outputs['Alpha'],mx.inputs[0]);nt.links.new(b.outputs['Alpha'],mx.inputs[1]);inv=nt.nodes.new('ShaderNodeMath');inv.operation='SUBTRACT';inv.inputs[0].default_value=1;nt.links.new(mx.outputs[0],inv.inputs[1]);mul=nt.nodes.new('ShaderNodeMath');mul.operation='MULTIPLY';nt.links.new(rl.outputs['Alpha'],mul.inputs[0]);nt.links.new(inv.outputs[0],mul.inputs[1]);sa=nt.nodes.new('CompositorNodeSetAlpha');nt.links.new(rl.outputs['Image'],sa.inputs['Image']);nt.links.new(mul.outputs[0],sa.inputs['Alpha']);over=nt.nodes.new('CompositorNodeAlphaOver');nt.links.new(sc.outputs[0],over.inputs['Background']);nt.links.new(sa.outputs[0],over.inputs['Foreground']);out=nt.nodes.new('NodeGroupOutput');nt.links.new(over.outputs[0],out.inputs['Image'])
s.frame_set(9);root.update_tag(refresh={'OBJECT'});bpy.context.view_layer.update();native=P/'native/WTSC_Joined_Ground_Only_v010e.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
report={'blender':bpy.app.version_string,'build_hash':bpy.app.build_hash.decode(),'scene':s.name,'root':list(root.location),'root_uv':list(world_to_camera_view(s,s.camera,root.location)),'fps':24,'frames':[1,120],'impact':7,'pit_depth_metres':.32,'maximum_cut_lip_height':.018,'crust_sections':records,'physics_seconds':time.perf_counter()-start,'native_method':'Eight contiguous shared-boundary solid crust sectors; Bullet launch/contact baked directly into native rigid vertex poses. No tiny-particle spray. Project-owned paint is carried rigidly on solid top faces.','terrain':'Depressed closed collider and visible cut surface; outer paint projection blends into held terrain; no raised full ring.','status':'Await actual few final-camera keyframes. No full render yet.'}
(P/'evidence/build_rupture_e.json').write_text(json.dumps(report,indent=2));print('JOINED_GROUND_BUILT',json.dumps({k:v for k,v in report.items() if k!='crust_sections'}),flush=True)
