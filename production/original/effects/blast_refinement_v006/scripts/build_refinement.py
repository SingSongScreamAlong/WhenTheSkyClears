"""Editable impulsive painted blasts, persistent impacts and fictional tracers.
Read-only v003 source; all writes confined to this refinement folder.
"""
import bpy, bmesh, math, random, json, hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P = Path(__file__).resolve().parents[1]
s = bpy.data.scenes['FX_PROOF_v003 | 75-80s held shot evolution']
bpy.context.window.scene = s
s.name = 'FX_PROOF_v006 | painted impulse depth tracers and ground'
template = bpy.data.collections['FXv003 | Evolving anchored eruption | NO PRODUCTION LIGHTS']
old_root = bpy.data.objects['FXv003 | fixed ground origin and controls']
old_comp = s.compositing_node_group
background_image = old_comp.nodes['Held real project shot at frame1825'].image
receiver_image = next(n.image for n in old_comp.nodes if n.type=='IMAGE' and ('Native_Local_Light' in n.image.name or 'Native_Local_Light' in n.image.filepath))
s.render.engine = 'BLENDER_EEVEE'; s.eevee.taa_render_samples = 32
s.render.resolution_x = 1920; s.render.resolution_y = 1080; s.render.resolution_percentage = 100
s.render.fps = 24; s.render.threads_mode = 'FIXED'; s.render.threads = 2
s.render.film_transparent = True; s.render.image_settings.media_type = 'IMAGE'
s.render.image_settings.file_format = 'PNG'; s.render.image_settings.color_mode = 'RGB'
s.view_settings.view_transform = 'Standard'; s.view_settings.look = 'None'; s.view_settings.exposure = 0; s.view_settings.gamma = 1
s.frame_start = 1800; s.frame_end = 1919
if hasattr(s.render, 'compositor_device'): s.render.compositor_device = 'GPU'
asset = bpy.data.collections.new('FXv006 | APPEND ASSETS | painted blasts impacts tracers')
s.collection.children.link(asset)
groups = {}
for label in ['MID', 'NEAR', 'FAR', 'TRACER_MID', 'TRACER_FAR']:
    group = bpy.data.collections.new('FXv006 | LAYER | ' + label)
    asset.children.link(group); groups[label] = group

def drive(owner, path, expression, root, index=None, extra=()):
    f = owner.driver_add(path) if index is None else owner.driver_add(path, index)
    f.driver.type = 'SCRIPTED'
    for variable in list(f.driver.variables): f.driver.variables.remove(variable)
    for name, key in [('t','age'),('I','intensity'),('W','wind'),('D','smoke_density'),('H','hot_frames'),('S','size'),('A','atmosphere'),('P','burst_spread'),('R','burst_rise')]:
        v = f.driver.variables.new(); v.name = name; v.type = 'SINGLE_PROP'; v.targets[0].id = root; v.targets[0].data_path = '["' + key + '"]'
    for name, path_value in extra:
        v = f.driver.variables.new(); v.name = name; v.type = 'SINGLE_PROP'; v.targets[0].id = root; v.targets[0].data_path = path_value
    f.driver.expression = expression
    return f

def root_empty(name, collection, position, start, size=1, intensity=.94, atmosphere=.04):
    root = bpy.data.objects.new(name, None); collection.objects.link(root); root.location = position
    root.empty_display_type = 'CIRCLE'; root.empty_display_size = .20
    for key, value in {'start_frame':float(start), 'speed':1., 'size':float(size), 'intensity':float(intensity), 'wind':.10, 'smoke_density':.90, 'hot_frames':10., 'atmosphere':float(atmosphere), 'burst_spread':1., 'burst_rise':1., 'age':0., 'hot_envelope':0., 'light_envelope':0., 'bloom_gain':.35}.items(): root[key] = value
    root['smoke_color'] = [.72,.77,.83]
    f = root.driver_add('["age"]'); f.driver.expression = '(frame-start)*speed'
    for name,key in [('start','start_frame'),('speed','speed')]:
        v=f.driver.variables.new();v.name=name;v.type='SINGLE_PROP';v.targets[0].id=root;v.targets[0].data_path='["'+key+'"]'
    for axis in range(3): drive(root,'scale','max(.01,S)',root,axis)
    envelope = 'max(0,min(1,(t+.35)/1.5))*exp(-max(0,t-1.5)/3.2)*max(0,min(1,(H-t)/3))'
    drive(root,'["hot_envelope"]',envelope,root)
    drive(root,'["light_envelope"]',envelope,root)
    return root

def remap_drivers(owner, source_root, target_root):
    if owner and owner.animation_data:
        for f in owner.animation_data.drivers:
            for variable in f.driver.variables:
                for target in variable.targets:
                    if target.id == source_root: target.id = target_root

def clone_paint(ob, collection, root, cache):
    new = ob.copy(); new.data = ob.data.copy(); new.name = root.name + ' | ' + ob.name.split(' | ',1)[-1]
    collection.objects.link(new); new.parent = root
    new.data.materials.clear()
    for material in ob.data.materials:
        if material not in cache:
            m=material.copy();m.name=root.name+' | '+material.name.split(' | ',1)[-1];remap_drivers(m.node_tree,old_root,root);cache[material]=m
        new.data.materials.append(cache[material])
    remap_drivers(new,old_root,root)
    if new.data.shape_keys:
        assert new.data.shape_keys != ob.data.shape_keys
        remap_drivers(new.data.shape_keys,old_root,root)
    return new

def quad(name, collection, root, width, height, material, y=0, z=0, centered=False):
    bottom=-height/2 if centered else 0
    vertices=[(-width/2,y,bottom+z),(width/2,y,bottom+z),(width/2,y,bottom+height+z),(-width/2,y,bottom+height+z)]
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],[(0,1,2,3)]);mesh.materials.append(material);mesh.update()
    uv=mesh.uv_layers.new(name='Paint UV')
    for loop in mesh.loops:uv.data[loop.index].uv=[(0,0),(1,0),(1,1),(0,1)][loop.vertex_index]
    ob=bpy.data.objects.new(name,mesh);collection.objects.link(ob);ob.parent=root
    return ob

def simple_paint(name, image, root, opacity, tone=(.65,.63,.58), warm=False):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.surface_render_method='BLENDED';nt=m.node_tree;nt.nodes.clear()
    tex=nt.nodes.new('ShaderNodeTexImage');tex.image=image;tex.extension='CLIP'
    hsv=nt.nodes.new('ShaderNodeHueSaturation');hsv.inputs['Saturation'].default_value=0;nt.links.new(tex.outputs['Color'],hsv.inputs['Color'])
    multiply=nt.nodes.new('ShaderNodeMixRGB');multiply.blend_type='MULTIPLY';multiply.inputs[0].default_value=1;multiply.inputs[2].default_value=(*tone,1);nt.links.new(hsv.outputs[0],multiply.inputs[1])
    color=multiply.outputs[0]
    if warm:
        mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='ADD';mix.inputs[2].default_value=(.35,.13,.025,1);nt.links.new(color,mix.inputs[1]);drive(mix.inputs[0],'default_value','.12*E',root,extra=[('E','["hot_envelope"]')]);color=mix.outputs[0]
    emission=nt.nodes.new('ShaderNodeEmission');emission.inputs['Strength'].default_value=1;nt.links.new(color,emission.inputs['Color'])
    alpha=nt.nodes.new('ShaderNodeMath');alpha.name='Persistent/temporal alpha';alpha.operation='MULTIPLY';nt.links.new(tex.outputs['Alpha'],alpha.inputs[0]);drive(alpha.inputs[1],'default_value',opacity,root)
    transparent=nt.nodes.new('ShaderNodeBsdfTransparent');mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(alpha.outputs[0],mix.inputs[0]);nt.links.new(transparent.outputs[0],mix.inputs[1]);nt.links.new(emission.outputs[0],mix.inputs[2]);out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(mix.outputs[0],out.inputs[0])
    return m

crater_image=bpy.data.images.load(str(P/'assets/Painted_Ground_Gouge_v006.png'));crater_image.alpha_mode='STRAIGHT';crater_image.pack()
dust_image=bpy.data.images['FXv002 original granular ground surge | packed']
rock_original=bpy.data.materials['FXv003 | rough broken charcoal and plaster']

def stone_mesh(name, radius, seed):
    rng=random.Random(seed);mesh=bpy.data.meshes.new(name);bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=1,radius=radius)
    for v in bm.verts:
        v.co.x*=rng.uniform(.7,1.3);v.co.y*=rng.uniform(.4,.9);v.co.z*=rng.uniform(.65,1.3)
    bm.to_mesh(mesh);bm.free();mesh.update();return mesh

def point_for_screen(u,v,depth):
    cam=s.camera;origin=cam.matrix_world.translation
    base=world_to_camera_view(s,cam,Vector((origin.x,depth,origin.z)))
    px=world_to_camera_view(s,cam,Vector((origin.x+1,depth,origin.z)))
    pz=world_to_camera_view(s,cam,Vector((origin.x,depth,origin.z+1)))
    return Vector((origin.x+(u-base.x)/(px.x-base.x),depth,origin.z+(v-base.y)/(pz.y-base.y)))

variant_specs=[('MID',10,1824,1.,.94,.04,None,1.,1.,14,221),('NEAR',4,1871,.58,1.,.01,(.91,.32),1.10,.85,12,227),('FAR',11.5,1890,.36,.68,.52,(.69,.33),.82,.90,8,239)]
variant_reports=[];roots={};impact_roots={};trajectory_records=[]
targets=[(-.65,.95),(0,1.4),(.65,1.12),(-.95,.6),(.95,.55),(-.36,1.75),(.43,1.65),(-1.2,.35),(1.18,.38),(-.7,1.6),(.85,1.4),(-.1,.75),(.15,1.1)]
births=[0,0,1,1,2,2,2,3,3,4,4,5,5]
lifetimes=[120,108,116,78,86,125,118,68,73,105,97,62,91]
for label,depth,start,size,intensity,atmosphere,screen,spread,rise,count,seed in variant_specs:
    group=groups[label];blast=bpy.data.collections.new('FXv006 | BLAST | '+label);ground=bpy.data.collections.new('FXv006 | GROUND IMPACT | '+label)
    group.children.link(blast);group.children.link(ground)
    position=Vector(old_root.location) if screen is None else point_for_screen(*screen,depth)
    root=root_empty('FXv006 | '+label+' | Blast controls',blast,position,start,size,intensity,atmosphere)
    root['burst_spread']=spread;root['burst_rise']=rise;root['bloom_gain']=.18 if label=='FAR' else .35
    root['event_type']='Finite impulsive blast; all smoke born within5frames, not a building-fire chimney.'
    roots[label]=root;mat_cache={};copies={}
    for ob in template.objects:
        if ob.type=='MESH' and 'weighted debris' not in ob.name:
            copies[ob.name]=clone_paint(ob,blast,root,mat_cache)
    rng=random.Random(seed)
    for index,ob in enumerate(sorted([v for k,v in copies.items() if 'rolling smoke ' in k],key=lambda o:o.name)):
        birth=births[index];a=f'max(0,t-{birth})';x,z=targets[index];width=rng.uniform(1.22,1.66);height=width*rng.uniform(.73,1.03);phase=rng.uniform(0,6.28);roll=rng.uniform(-.35,.35);life=lifetimes[index]
        drive(ob,'location',f'P*({x})*(1-exp(-{a}/5.2))+W*max(0,{a}-15)/60+.08*sin({phase}+{a}/24)*min(1,{a}/15)',root,0)
        drive(ob,'location',f'.10+R*({z})*(1-exp(-{a}/6.2))+.18*(1-exp(-max(0,{a}-14)/42))',root,2)
        drive(ob,'scale',f'{width}*(.025+.975*(1-exp(-{a}/4.8)))',root,0)
        drive(ob,'scale',f'{height}*(.025+.975*(1-exp(-{a}/6.5)))',root,2)
        drive(ob,'rotation_euler',f'{roll}+{roll}*(1-exp(-{a}/28))+.05*sin({phase}+{a}/27)',root,1)
        if ob.data.shape_keys:
            keys=ob.data.shape_keys.key_blocks
            drive(keys['Independent unequal vortex curl'],'value',f'.6*sin({phase}+{a}/25)',root)
            drive(keys['Differential billow shear'],'value',f'.5*sin({phase}+{a}/31)',root)
        material=ob.data.materials[0];nt=material.node_tree
        drive(nt.nodes['Birth rise and independent dissipating lifetime'].inputs[1],'default_value',f'I*D*.92*exp(-max(0,{a}-32)/110)*max(0,min(1,(t-{birth}+.15)/2.5,({birth+life}-t)/28))',root)
        for node in nt.nodes:
            if node.type=='TEX_NOISE' and node.noise_dimensions=='4D':drive(node.inputs['W'],'default_value',f'{index*3.718}+{a}/24',root)
            if node.type=='MAP_RANGE' and node.name.startswith('Independent evolving density erosion'):
                drive(node.inputs['From Min'],'default_value',f'.13+.25*min(1,{a}/{life})',root)
                drive(node.inputs['From Max'],'default_value',f'.36+.26*min(1,{a}/{life})',root)
        emission=next(n for n in nt.nodes if n.type=='EMISSION');base=emission.inputs['Color'].links[0].from_socket
        haze=nt.nodes.new('ShaderNodeMixRGB');haze.name='Depth atmosphere | painted contrast';haze.inputs[2].default_value=(.11,.13,.15,1);nt.links.new(base,haze.inputs[1]);drive(haze.inputs[0],'default_value','A',root)
        warm=nt.nodes.new('ShaderNodeMixRGB');warm.blend_type='ADD';warm.inputs[2].default_value=(.21,.075,.012,1);nt.links.new(haze.outputs[0],warm.inputs[1]);drive(warm.inputs[0],'default_value','.16*E',root,extra=[('E','["hot_envelope"]')]);nt.links.new(warm.outputs[0],emission.inputs['Color'])
    hot=copies['FXv003 | short hot launch jet | gone after hot_frames'];mat=hot.data.materials[0]
    drive(mat.node_tree.nodes['Shot age opacity'].inputs[1],'default_value','I*.8*max(0,min(1,(t+.3)/1.4))*exp(-max(0,t-1)/3.3)*max(0,min(1,(H-t)/3))',root)
    drive(hot,'scale','.12+.75*(1-exp(-max(0,t+.25)/3))',root,0);drive(hot,'scale','.08+.42*(1-exp(-max(0,t+.25)/3.5))',root,2)
    em=next(n for n in mat.node_tree.nodes if n.type=='EMISSION');drive(em.inputs['Strength'],'default_value','3.2*exp(-max(0,t)/5)',root)
    flash=copies['FXv003 | brief torn ignition core'];mat=flash.data.materials[0]
    drive(mat.node_tree.nodes['Shot age opacity'].inputs[1],'default_value','I*1.2*max(0,min(1,(t+.35)/1.3,(8-t)/5))',root)
    drive(flash,'scale','.08+.92*(1-exp(-max(0,t+.3)/2.3))',root,0);drive(flash,'scale','.06+.94*(1-exp(-max(0,t+.3)/2.8))',root,2)
    em=next(n for n in mat.node_tree.nodes if n.type=='EMISSION');drive(em.inputs['Strength'],'default_value','6*exp(-max(0,t)/4)+.4',root)
    dust=copies['FXv003 | broad low asymmetric dust sheets'];mat=dust.data.materials[0]
    drive(mat.node_tree.nodes['Shot age opacity'].inputs[1],'default_value','I*.70*max(0,min(1,(t-1)/12,(115-t)/35))',root)
    drive(dust,'scale','.08+.82*(1-exp(-max(0,t)/6.5))',root,0);drive(dust,'scale','.18+.32*(1-exp(-max(0,t)/10))',root,2)
    rock=rock_original.copy();rock.name='FXv006 | '+label+' | rough readable chips'
    bs=rock.node_tree.nodes.get('Principled BSDF')
    if bs and 'Emission Color' in bs.inputs:
        if bs.inputs['Base Color'].is_linked:rock.node_tree.links.new(bs.inputs['Base Color'].links[0].from_socket,bs.inputs['Emission Color'])
        bs.inputs['Emission Strength'].default_value=.15
    for i in range(count):
        radius=rng.uniform(.014,.035);mesh=stone_mesh(root.name+' chip',radius,seed*100+i);mesh.materials.append(rock)
        ob=bpy.data.objects.new(root.name+f' | chunky debris {i:02d}',mesh);blast.objects.link(ob);ob.parent=root
        delay=rng.randint(0,4);vz=rng.uniform(3.5,5.7 if label=='MID' else 4.8);vx=rng.uniform(-1.6,1.8);dy=rng.uniform(-.30,.30);flight=2*vz/6.8;a=f'max(0,t-{delay})/24';clamped=f'min({flight},{a})'
        drive(ob,'location',f'{vx}*({clamped})*exp(-.25*({clamped}))',root,0);ob.location.y=dy
        drive(ob,'location',f'max({.025-.14*dy},{.06-.14*dy}+{vz}*({a})-3.4*({a})**2)',root,2)
        for axis in range(3):drive(ob,'rotation_euler',f'{rng.uniform(-2,2)}+{rng.uniform(-8,8)}*({clamped})',root,axis)
        for axis in range(3):drive(ob,'scale',f'max(0,min(1,(t-{delay}+.1)/1.5))',root,axis)
        landing=delay+math.ceil(flight*24);land_x=vx*flight*math.exp(-.25*flight)
        trajectory_records.append({'variant':label,'piece':i,'birth_age':delay,'apex_age':delay+flight*12,'landing_age':landing,'local_landing':[land_x,dy,.025-.14*dy],'radius':radius})
        if i<3:
            puffmat=simple_paint(root.name+f' | landing dust {i}',dust_image,root,f'I*.40*max(0,min(1,(t-{landing})/1.5,({landing+12}-t)/9))',(.62,.60,.56))
            puff=quad(root.name+f' | small landing puff {i}',blast,root,.33,.11,puffmat,y=dy-.015,z=.02-.14*dy);puff.location.x=land_x
    impact=root_empty('FXv006 | '+label+' | Ground impact controls',ground,position,start,size,intensity,atmosphere);impact['impact_visible']=1.;impact['reveal_start']=4.;impact['reveal_duration']=10.;impact['persist']='No end fade. Keep ground collection enabled after dynamic blast ends.';impact_roots[label]=impact
    impact_mat=simple_paint('FXv006 | '+label+' | persistent gouge',crater_image,impact,'V*I*max(0,min(1,(t-B)/max(1,F)))',(.67,.64,.58),True)
    alpha=impact_mat.node_tree.nodes['Persistent/temporal alpha'].inputs[1]
    drive(alpha,'default_value','V*I*max(0,min(1,(t-B)/max(1,F)))',impact,extra=[('V','["impact_visible"]'),('B','["reveal_start"]'),('F','["reveal_duration"]')])
    gouge=quad(impact.name+' | gouge',ground,impact,2.2,.72,impact_mat,y=-.025,z=.06,centered=True);gouge['asset_role']='persistent_ground_gouge'
    for i in range(7):
        mesh=stone_mesh(impact.name+' rubble',rng.uniform(.014,.035),seed*1000+i);mesh.materials.append(rock);ob=bpy.data.objects.new(impact.name+f' | persistent rim rubble {i}',mesh);ground.objects.link(ob);ob.parent=impact;ob.location=(rng.uniform(-1.0,1.0),rng.uniform(-.18,.18),rng.uniform(.015,.05));ob.rotation_euler=(rng.random()*2,rng.random()*2,rng.random()*2)
        for axis in range(3):drive(ob,'scale','max(0,min(1,(t-5)/7))',impact,axis)
    variant_reports.append({'name':label,'depth_y':depth,'start_frame':start,'position':list(position),'projected_anchor':list(world_to_camera_view(s,s.camera,position)),'size':size,'intensity':intensity,'atmosphere':atmosphere,'spread':spread,'rise':rise,'debris_count':count,'last_smoke_birth_age':5,'ground_collection':ground.name})

tracer_specs=[(1808,14,(.42,.89),(.68,.81),3.3,.44),(1816,9,(.96,.57),(.66,.49),3.8,.65),(1841,9,(.60,.63),(.93,.54),2.8,.55),(1868,14,(.52,.97),(.75,.86),4.1,.43),(1882,9,(.95,.59),(.70,.52),3.2,.60),(1908,14,(.38,.92),(.66,.84),3.6,.40)]
tracer_reports=[]
for i,(start,depth,uv_a,uv_b,duration,intensity) in enumerate(tracer_specs):
    group=groups['TRACER_FAR' if depth==14 else 'TRACER_MID'];collection=bpy.data.collections.new(f'FXv006 | TRACER | {i:02d}');group.children.link(collection)
    a=point_for_screen(*uv_a,depth);b=point_for_screen(*uv_b,depth);delta=b-a;length=delta.length
    root=root_empty(f'FXv006 | Tracer {i:02d} controls',collection,a,start,1,intensity,.2);root['duration_frames']=duration;root['width']=.010 if depth==9 else .008;root['path_delta']=list(delta);root.rotation_euler.y=-math.atan2(delta.z,delta.x)
    m=bpy.data.materials.new(root.name+' | tapered warm streak');m.use_nodes=True;m.surface_render_method='BLENDED';nt=m.node_tree;nt.nodes.clear();coord=nt.nodes.new('ShaderNodeTexCoord');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(coord.outputs['UV'],sep.inputs[0])
    ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.15,.075,.025,1);ramp.color_ramp.elements[1].color=(1,.88,.60,1);nt.links.new(sep.outputs['X'],ramp.inputs[0]);em=nt.nodes.new('ShaderNodeEmission');em.inputs['Strength'].default_value=2.6;nt.links.new(ramp.outputs[0],em.inputs[0])
    alpha=nt.nodes.new('ShaderNodeMath');alpha.operation='MULTIPLY';nt.links.new(sep.outputs['X'],alpha.inputs[0]);drive(alpha.inputs[1],'default_value','I*max(0,min(1,(t+.2)/.5,(U+.6-t)/.6))',root,extra=[('U','["duration_frames"]')]);tr=nt.nodes.new('ShaderNodeBsdfTransparent');mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(alpha.outputs[0],mix.inputs[0]);nt.links.new(tr.outputs[0],mix.inputs[1]);nt.links.new(em.outputs[0],mix.inputs[2]);out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(mix.outputs[0],out.inputs[0])
    ob=quad(root.name+' | moving tapered segment',collection,root,1,1,m,centered=True)
    # Canonical strip centred at0: translate to tail + half segment, with a moving head.
    head='max(0,min(1,(t+.25)/U))';tail='max(0,min(1,(t-.5*U)/U))'
    drive(ob,'scale',f'{length}*({head}-{tail})',root,0,extra=[('U','["duration_frames"]')]);drive(ob,'scale','Q',root,2,extra=[('Q','["width"]')]);drive(ob,'location',f'{length}*({head}+{tail})/2',root,0,extra=[('U','["duration_frames"]')])
    tracer_reports.append({'id':i,'start_frame':start,'duration_frames':duration,'depth_y':depth,'world_start':list(a),'world_end':list(b),'screen_start':uv_a,'screen_end':uv_b,'intensity':intensity})

# Unlink only the in-memory template. The v003 source file is never saved.
s.collection.children.unlink(template)
names=['MID','NEAR','FAR','TRACER_MID','TRACER_FAR']
s.view_layers[0].name='MID'
for name in names[1:]:s.view_layers.new(name=name)
for layer in s.view_layers:
    for label,group in groups.items():
        def find(node):
            if node.collection==group:return node
            for child in node.children:
                answer=find(child)
                if answer:return answer
        find(layer.layer_collection).exclude=label!=layer.name

# Reusable compositing helper: glare is extracted from HDR FX ONLY, then
# added independently of sprite alpha and masked by actual scene occlusion.
helper=bpy.data.node_groups.new('FXv006 | HDR FX bloom over | append helper','CompositorNodeTree')
for name,kind in [('Foreground','NodeSocketColor'),('Background','NodeSocketColor'),('Occluder','NodeSocketFloat'),('Bloom gain','NodeSocketFloat')]:helper.interface.new_socket(name=name,in_out='INPUT',socket_type=kind)
helper.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor')
n=helper.nodes;links=helper.links;inp=n.new('NodeGroupInput');out=n.new('NodeGroupOutput')
inverse=n.new('ShaderNodeMath');inverse.operation='SUBTRACT';inverse.inputs[0].default_value=1;links.new(inp.outputs['Occluder'],inverse.inputs[1])
masked=n.new('CompositorNodeAlphaOver');masked.inputs['Background'].default_value=(0,0,0,0);links.new(inverse.outputs[0],masked.inputs['Factor']);links.new(inp.outputs['Foreground'],masked.inputs['Foreground'])
over=n.new('CompositorNodeAlphaOver');over.inputs['Factor'].default_value=1;links.new(inp.outputs['Background'],over.inputs['Background']);links.new(masked.outputs[0],over.inputs['Foreground'])
glare=n.new('CompositorNodeGlare');glare.inputs['Type'].default_value='Fog Glow';glare.inputs['Quality'].default_value='High';glare.inputs['Threshold'].default_value=1.25;glare.inputs['Strength'].default_value=1;glare.inputs['Size'].default_value=.05;links.new(inp.outputs['Foreground'],glare.inputs['Image'])
gmask=n.new('ShaderNodeMixRGB');gmask.blend_type='MULTIPLY';gmask.inputs[0].default_value=1;links.new(glare.outputs['Glare'],gmask.inputs[1]);links.new(inverse.outputs[0],gmask.inputs[2])
add=n.new('ShaderNodeMixRGB');add.blend_type='ADD';links.new(inp.outputs['Bloom gain'],add.inputs[0]);links.new(over.outputs[0],add.inputs[1]);links.new(gmask.outputs[0],add.inputs[2]);links.new(add.outputs[0],out.inputs['Image'])
nt=bpy.data.node_groups.new('FXv006 | held proof with depth alpha and controlled bloom','CompositorNodeTree');nt.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor');s.compositing_node_group=nt
def image_node(image):
    node=nt.nodes.new('CompositorNodeImage');node.image=image;return node
bg=image_node(background_image);scale=nt.nodes.new('CompositorNodeScale');scale.inputs['X'].default_value=.5;scale.inputs['Y'].default_value=.5;nt.links.new(bg.outputs['Image'],scale.inputs['Image'])
li=image_node(receiver_image);lit=nt.nodes.new('CompositorNodeAlphaOver');nt.links.new(scale.outputs[0],lit.inputs['Background']);nt.links.new(li.outputs['Image'],lit.inputs['Foreground']);drive(lit.inputs['Factor'],'default_value','min(1,max(0,I/.94*E))',roots['MID'],extra=[('E','["light_envelope"]')])
fg=bpy.data.images.load(str(P.parent/'benchmark_v002/assets/Native_Foreground_Alpha_1080_v002.png'),check_existing=True);fg.alpha_mode='STRAIGHT';fg.pack();fg_node=image_node(fg)
previous=lit.outputs[0]
for label,mask_name in [('TRACER_FAR','14'),('FAR','11p5'),('MID','10'),('TRACER_MID','09'),('NEAR','04')]:
    layer=nt.nodes.new('CompositorNodeRLayers');layer.scene=s;layer.layer=label
    im=bpy.data.images.load(str(P/f'assets/Native_Depth_Alpha_Y{mask_name}_v006.png'),check_existing=True);im.alpha_mode='STRAIGHT';im.pack();mask=image_node(im)
    maximum=nt.nodes.new('ShaderNodeMath');maximum.operation='MAXIMUM';nt.links.new(mask.outputs['Alpha'],maximum.inputs[0]);nt.links.new(fg_node.outputs['Alpha'],maximum.inputs[1])
    node=nt.nodes.new('CompositorNodeGroup');node.node_tree=helper;node.name='Depth composite | '+label;nt.links.new(layer.outputs['Image'],node.inputs['Foreground']);nt.links.new(previous,node.inputs['Background']);nt.links.new(maximum.outputs[0],node.inputs['Occluder']);node.inputs['Bloom gain'].default_value=.18 if label in ['FAR','TRACER_FAR'] else .35
    if label in roots:drive(node.inputs['Bloom gain'],'default_value','B',roots[label],extra=[('B','["bloom_gain"]')])
    previous=node.outputs['Image']
out=nt.nodes.new('NodeGroupOutput');nt.links.new(previous,out.inputs['Image'])
s.frame_set(1824);bpy.context.view_layer.update()
invalid=[]
for ob in asset.all_objects:
    owners=[ob]
    if ob.type=='MESH' and ob.data.shape_keys:owners.append(ob.data.shape_keys)
    owners += [m.node_tree for m in ob.data.materials if m and m.node_tree] if ob.type=='MESH' else []
    for owner in owners:
        if owner.animation_data:
            invalid += [{'id':owner.name,'path':f.data_path,'expression':f.driver.expression} for f in owner.animation_data.drivers if not f.driver.is_valid]
assert not invalid,invalid
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Painted_Blast_Proof_v006.blend'),compress=True)
bpy.data.libraries.write(str(P/'native/WTSC_Painted_Blast_Assets_v006.blend'),{asset,helper},fake_user=True,compress=True)
samples=[]
for frame in list(range(1822,1841))+[1848,1860,1880,1919,2064]:
    s.frame_set(frame);bpy.context.view_layer.update();mid=roots['MID'];flash=next(o for o in groups['MID'].all_objects if o.name.endswith('brief torn ignition core'));impact=impact_roots['MID'];crater=next(o for o in groups['MID'].all_objects if o.get('asset_role')=='persistent_ground_gouge')
    samples.append({'frame':frame,'age':mid['age'],'flash_scale_xz':[flash.scale.x,flash.scale.z],'light_envelope':mid['light_envelope'],'anchor':list(mid.matrix_world.translation),'impact_alpha':crater.data.materials[0].node_tree.nodes['Persistent/temporal alpha'].inputs[1].default_value,'impact_anchor':list(impact.matrix_world.translation)})
assert samples[-1]['impact_alpha']>.9
old_path=P.parent/'benchmark_v003/native/WTSC_Evolving_Eruption_Collection_v003.blend';old_hash=hashlib.sha256(old_path.read_bytes()).hexdigest();assert old_hash=='d089770cccee18b786692d76113b80fbf8514d8034bab4eaae17d6b5f9bd1868'
report={'blender':bpy.app.version_string,'scene':s.name,'fps':24,'range':[1800,1919],'pixels':[1920,1080],'renderer':s.render.engine,'samples':32,'view_layers':names,'variants':variant_reports,'tracers':tracer_reports,'debris':trajectory_records,'frame_samples':samples,'invalid_drivers':invalid,'camera_matrix':[list(row) for row in s.camera.matrix_world],'exposure':s.view_settings.exposure,'gamma':s.view_settings.gamma,'view_transform':s.view_settings.view_transform,'new_bake':False,'gas_used':False,'v005':'Built but not promoted/rendered; user preference and blast-motion feedback superseded chimney-based hybrid.','v003_source_hash_unchanged':old_hash,'crater_pixels':list(crater_image.size),'status':'One authored refinement candidate, review actual shot before acceptance.'}
(P/'evidence/build_refinement.json').write_text(json.dumps(report,indent=2));print('PAINTED_REFINEMENT_BUILT',json.dumps({'variants':variant_reports,'tracers':len(tracer_reports),'drivers_invalid':invalid,'crater_persistent_after_age240':True}),flush=True)
