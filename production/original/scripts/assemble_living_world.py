"""Native UV paint, light-responsive shaders and deterministic environmental motion.
Explicit mesh data was created with Blender's typed MCP mesh interface.
"""
import bpy,math,json,random
from mathutils import Vector
from pathlib import Path
ROOT=Path(r'WTSC_LOCAL_WORKSPACE')
recipe=json.loads((ROOT/'work/living_world_meshes/v008/assembly.json').read_text())
world=bpy.data.scenes['WTSC_WORLD_FIRST_4K'];master=bpy.data.scenes['WTSC_MASTER_4K_100S']
bpy.context.window.scene=world
assert bpy.data.filepath.endswith('WTSC_Living_World_PREBUILD_v008.blend')
R=random.Random(93161016)
atlas=bpy.data.images.load(str(ROOT/'sets/surface_paint/Architecture_Paint_Atlas_v001.png'),check_existing=True);atlas.pack();atlas.filepath='//../../sets/surface_paint/Architecture_Paint_Atlas_v001.png'
leaf=bpy.data.images.load(str(ROOT/'sets/surface_paint/Oak_Foliage_Cluster_v001.png'),check_existing=True);leaf.pack();leaf.alpha_mode='STRAIGHT';leaf.filepath='//../../sets/surface_paint/Oak_Foliage_Cluster_v001.png'
ground_image=bpy.data.images.load(str(ROOT/'sets/painted_layers/Ground_Painted_v001.png'),check_existing=True);ground_image.pack();ground_image.filepath='//../../sets/painted_layers/Ground_Painted_v001.png'
organic=bpy.data.images.load(str(ROOT/'sets/surface_paint/Oak_Bark_Canvas_Atlas_v001.png'),check_existing=True);organic.pack();organic.filepath='//../../sets/surface_paint/Oak_Bark_Canvas_Atlas_v001.png'
village=bpy.data.images.load(str(ROOT/'sets/painted_layers/Village_Warm_v001.png'),check_existing=True);village.pack();village.filepath='//../../sets/painted_layers/Village_Warm_v001.png'
TILES={'Plaster':(0,.5),'Roof':(.5,.5),'Stone':(0,0),'Wood':(.5,0),'Bark':(.5,0),'Charred':(.5,0)}
COLORS={'Plaster':(.98,.95,.88,1),'Roof':(.85,.79,.72,1),'Stone':(.64,.68,.68,1),'Wood':(.74,.72,.62,1),'Bark':(.74,.73,.61,1),'Charred':(.22,.25,.27,1),'Shutter':(.19,.29,.24,1),'Metal':(.12,.15,.17,1),'Bread':(.68,.36,.105,1),'Cloth':(1.3,1.3,1.12,1),'TentCanvas':(.67,.66,.52,1),'Grass':(.12,.17,.048,1),'Flower':(.82,.71,.43,1),'FlowerRed':(.48,.07,.025,1),'Rope':(.28,.24,.15,1),'Chalkboard':(.045,.08,.065,1)}

def driver(socket,expr):
    c=socket.driver_add('default_value');c.driver.type='SCRIPTED';c.driver.expression=expr

def key(obj,path,items):
    for f,value in items:
        setattr(obj,path,value);obj.keyframe_insert(path,frame=f)

def socketkeys(socket,items):
    for f,val in items:socket.default_value=val;socket.keyframe_insert('default_value',frame=f)

def material(kind):
    name='LW | Painted '+kind
    if bpy.data.materials.get(name):return bpy.data.materials[name]
    mat=bpy.data.materials.new(name);mat.use_nodes=True;nt=mat.node_tree;nt.nodes.clear()
    out=nt.nodes.new('ShaderNodeOutputMaterial')
    if kind=='WindowGlow':
        em=nt.nodes.new('ShaderNodeEmission');tex=nt.nodes.new('ShaderNodeTexImage');tex.image=village
        nt.links.new(tex.outputs['Color'],em.inputs['Color'])
        driver(em.inputs['Strength'],'.85+0.018*sin(frame*0.13)+0.012*sin(frame*0.071)')
        nt.links.new(em.outputs[0],out.inputs['Surface']);return mat
    if kind=='Glass':
        bs=nt.nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Base Color'].default_value=(.055,.075,.095,1);bs.inputs['Roughness'].default_value=.24
        bs.inputs['Metallic'].default_value=.2;bs.inputs['Alpha'].default_value=.78;mat.surface_render_method='BLENDED'
        nt.links.new(bs.outputs[0],out.inputs[0]);return mat
    coords=nt.nodes.new('ShaderNodeTexCoord');geom=nt.nodes.new('ShaderNodeNewGeometry')
    if kind=='Leaves':
        tex=nt.nodes.new('ShaderNodeTexImage');tex.image=leaf;nt.links.new(coords.outputs['UV'],tex.inputs['Vector']);base=tex.outputs['Color']
        # Generated leaf alpha has low-density background haze: native hard mask,
        # followed by light alpha blending, keeps the original raster unchanged.
        clip=nt.nodes.new('ShaderNodeMath');clip.operation='GREATER_THAN';clip.inputs[1].default_value=.76;nt.links.new(tex.outputs['Alpha'],clip.inputs[0])
    elif kind=='Earth':
        scale=nt.nodes.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs[3].default_value=.32;nt.links.new(coords.outputs['UV'],scale.inputs[0])
        tex=nt.nodes.new('ShaderNodeTexImage');tex.image=ground_image;tex.extension='REPEAT';nt.links.new(scale.outputs[0],tex.inputs[0])
        sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geom.outputs['Position'],sep.inputs[0])
        mp=nt.nodes.new('ShaderNodeMapRange');mp.inputs['From Min'].default_value=-5;mp.inputs['From Max'].default_value=90;mp.clamp=True;nt.links.new(sep.outputs['X'],mp.inputs[0])
        tint=nt.nodes.new('ShaderNodeValToRGB');tint.color_ramp.elements[0].color=(.8,.87,.53,1);tint.color_ramp.elements[1].color=(.40,.48,.53,1)
        nt.links.new(mp.outputs[0],tint.inputs[0]);mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;nt.links.new(tex.outputs['Color'],mix.inputs[1]);nt.links.new(tint.outputs[0],mix.inputs[2]);base=mix.outputs[0]
    elif kind in ['Bark','Charred','Cloth','TentCanvas']:
        mul=nt.nodes.new('ShaderNodeVectorMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=(.5,.095,0);nt.links.new(coords.outputs['UV'],mul.inputs[0])
        frac=nt.nodes.new('ShaderNodeVectorMath');frac.operation='FRACTION';nt.links.new(mul.outputs[0],frac.inputs[0])
        sc=nt.nodes.new('ShaderNodeVectorMath');sc.operation='MULTIPLY';sc.inputs[1].default_value=(.484,.984,1);nt.links.new(frac.outputs[0],sc.inputs[0])
        off=nt.nodes.new('ShaderNodeVectorMath');off.operation='ADD';off.inputs[1].default_value=(.508 if kind in ['Cloth','TentCanvas'] else .008,.008,0);nt.links.new(sc.outputs[0],off.inputs[0])
        tex=nt.nodes.new('ShaderNodeTexImage');tex.image=organic;nt.links.new(off.outputs[0],tex.inputs[0])
        tint=nt.nodes.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1;tint.inputs[2].default_value=COLORS[kind];nt.links.new(tex.outputs['Color'],tint.inputs[1]);base=tint.outputs[0]
    elif kind in TILES:
        mul=nt.nodes.new('ShaderNodeVectorMath');mul.operation='SCALE';mul.inputs[3].default_value=.13 if kind=='Plaster' else .42;nt.links.new(coords.outputs['UV'],mul.inputs[0])
        frac=nt.nodes.new('ShaderNodeVectorMath');frac.operation='FRACTION';nt.links.new(mul.outputs[0],frac.inputs[0])
        sc=nt.nodes.new('ShaderNodeVectorMath');sc.operation='MULTIPLY';sc.inputs[1].default_value=(.484,.484,.484);nt.links.new(frac.outputs[0],sc.inputs[0])
        off=nt.nodes.new('ShaderNodeVectorMath');off.operation='ADD';u,v=TILES[kind];off.inputs[1].default_value=(u+.008,v+.008,0);nt.links.new(sc.outputs[0],off.inputs[0])
        tex=nt.nodes.new('ShaderNodeTexImage');tex.image=atlas;nt.links.new(off.outputs[0],tex.inputs['Vector'])
        tint=nt.nodes.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1;tint.inputs[2].default_value=COLORS[kind];nt.links.new(tex.outputs['Color'],tint.inputs[1]);base=tint.outputs[0]
    else:
        rgb=nt.nodes.new('ShaderNodeRGB');rgb.outputs[0].default_value=COLORS.get(kind,(.5,.5,.5,1));base=rgb.outputs[0]
    paint=nt.nodes.new('ShaderNodeVertexColor');paint.layer_name='PaintVariation'
    mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;nt.links.new(base,mix.inputs[1]);nt.links.new(paint.outputs['Color'],mix.inputs[2])
    hsv=nt.nodes.new('ShaderNodeHueSaturation');nt.links.new(mix.outputs[0],hsv.inputs['Color'])
    socketkeys(hsv.inputs['Saturation'],[(1,.94),(601,.85),(1201,.67),(1801,.43),(2401,.35)])
    diffuse=nt.nodes.new('ShaderNodeBsdfDiffuse');nt.links.new(hsv.outputs[0],diffuse.inputs['Color']);diffuse.inputs['Roughness'].default_value=.6
    noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=7;noise.inputs['Detail'].default_value=2;noise.inputs['Roughness'].default_value=.65;nt.links.new(geom.outputs['Position'],noise.inputs['Vector'])
    bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.23;bump.inputs['Distance'].default_value=.045 if kind!='Earth' else .025;nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],diffuse.inputs['Normal'])
    lit=nt.nodes.new('ShaderNodeShaderToRGB');nt.links.new(diffuse.outputs[0],lit.inputs[0])
    gain=nt.nodes.new('ShaderNodeMixRGB');gain.blend_type='MULTIPLY';gain.inputs[0].default_value=1;gain.inputs[2].default_value=(.83,.83,.83,1);nt.links.new(lit.outputs[0],gain.inputs[1])
    ambient=nt.nodes.new('ShaderNodeMixRGB');ambient.blend_type='MULTIPLY';ambient.inputs[0].default_value=1;ambient.inputs[2].default_value=(.30,.34,.39,1);nt.links.new(hsv.outputs[0],ambient.inputs[1])
    combined=nt.nodes.new('ShaderNodeMixRGB');combined.blend_type='ADD';combined.inputs[0].default_value=1;nt.links.new(gain.outputs[0],combined.inputs[1]);nt.links.new(ambient.outputs[0],combined.inputs[2])
    depth=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geom.outputs['Position'],depth.inputs[0])
    aerial=nt.nodes.new('ShaderNodeMapRange');aerial.clamp=True;aerial.inputs['From Min'].default_value=10;aerial.inputs['From Max'].default_value=35;aerial.inputs['To Min'].default_value=0;aerial.inputs['To Max'].default_value=.48;nt.links.new(depth.outputs['Y'],aerial.inputs[0])
    haze=nt.nodes.new('ShaderNodeMixRGB');haze.blend_type='MIX';haze.inputs[2].default_value=(.22,.28,.32,1);nt.links.new(aerial.outputs[0],haze.inputs[0]);nt.links.new(combined.outputs[0],haze.inputs[1])
    em=nt.nodes.new('ShaderNodeEmission');nt.links.new(haze.outputs[0],em.inputs['Color'])
    if kind=='Leaves':
        mat.surface_render_method='BLENDED';transparent=nt.nodes.new('ShaderNodeBsdfTransparent');ms=nt.nodes.new('ShaderNodeMixShader');nt.links.new(clip.outputs[0],ms.inputs[0]);nt.links.new(transparent.outputs[0],ms.inputs[1]);nt.links.new(em.outputs[0],ms.inputs[2]);nt.links.new(ms.outputs[0],out.inputs[0])
    else:nt.links.new(em.outputs[0],out.inputs[0])
    mat.diffuse_color=COLORS.get(kind,(.25,.35,.15,1))
    return mat

motions=[]
for idx,entry in enumerate(recipe['entries']):
    obj=bpy.data.objects[entry['name']];kind=entry['material'];mesh=obj.data
    for c in list(obj.users_collection):c.objects.unlink(obj)
    bpy.data.collections['LW | '+entry['region']].objects.link(obj)
    obj['provenance']='Original numeric mesh recipe 93161016, created by typed Blender data geometry tool'
    obj['set_region']=entry['region'];obj['surface_paint']='Built-in GPT imagegen architecture atlas / foliage cluster plus original shader brush breakup'
    mesh.materials.clear();mesh.materials.append(material(kind))
    uv=mesh.uv_layers.new(name='Paint UV metre scale')
    for face in mesh.polygons:
        n=face.normal;axis=max(range(3),key=lambda a:abs(n[a]))
        dims=(0,2) if axis==1 else ((1,2) if axis==0 else (0,1))
        for li in face.loop_indices:
            p=mesh.vertices[mesh.loops[li].vertex_index].co
            uv.data[li].uv=(p[dims[0]],p[dims[1]])
        if kind=='Leaves':
            for li,xy in zip(face.loop_indices,[(0,0),(1,0),(1,1),(0,1)]):uv.data[li].uv=xy
        if kind=='WindowGlow':
            points=[mesh.vertices[mesh.loops[li].vertex_index].co for li in face.loop_indices]
            lo=min(p.x for p in points);hi=max(p.x for p in points);bottom=min(p.z for p in points);top=max(p.z for p in points)
            u0,u1,v0,v1=(.337,.425,.226,.318) if (top+bottom)/2<2.8 else (.360,.394,.394,.437)
            for li,p in zip(face.loop_indices,points):uv.data[li].uv=(u0+(u1-u0)*(p.x-lo)/max(.001,hi-lo),v0+(v1-v0)*(p.z-bottom)/max(.001,top-bottom))
        if kind=='Bark':face.use_smooth=True
    attr=mesh.color_attributes.new(name='PaintVariation',type='FLOAT_COLOR',domain='CORNER')
    colors=[]
    for face,tint in zip(mesh.polygons,entry['face_tints']):
        if kind=='Stone' and entry['region'] in ['Terrain','Woods','Ash']:tint*=.62
        for li in face.loop_indices:colors.extend((tint,tint,tint,1))
    attr.data.foreach_set('color',colors)
    if kind in ['Stone','Wood','Plaster','Shutter','Metal']:
        bevel=obj.modifiers.new('Small worn edges catch the light','BEVEL');bevel.width=.018;bevel.segments=1;bevel.limit_method='ANGLE'
    if entry['motion']:
        base=obj.shape_key_add(name='Basis');wind=obj.shape_key_add(name='Wind | editable environmental deformation')
        for v in wind.data:
            p=v.co;weight=max(0,min(1,(p.z-2.2)/4.5))
            if entry['motion'] in ['Cloth','Tent']:
                weight=(.5+.5*math.sin(p.x*2.5))*(.45 if entry['motion']=='Tent' else 1)
                p.y+=.32*weight*math.sin(p.x*2+p.z*2.3);p.x+=.055*weight*math.sin(p.z*3)
            elif entry['motion']=='Grass':
                weight=min(.35,max(0,p.z));p.x+=weight*.21*math.sin(p.x*.8+p.y*1.4);p.y+=weight*.13
            else:
                p.x+=weight*.16*math.sin(p.x*.65+p.y*.2);p.y+=weight*.10*math.sin(p.z*.8+p.x*.2);p.z+=weight*.025*math.cos(p.x)
        wind.driver_add('value').driver.expression=f'.5+.5*sin(frame*0.028+{idx*.71:.4f})'
        motions.append({'object':obj.name,'kind':entry['motion'],'driver':wind.id_data.animation_data.drivers[0].driver.expression})

fx=bpy.data.collections['LW | Atmosphere']
def move(obj,col=fx):
    for c in list(obj.users_collection):c.objects.unlink(obj)
    col.objects.link(obj);return obj

def light(name,typ,loc,energy,color,size=4):
    data=bpy.data.lights.new(name,typ);data.energy=energy;data.color=color
    if typ=='AREA':data.shape='DISK';data.size=size
    obj=bpy.data.objects.new(name,data);fx.objects.link(obj);obj.location=loc;return obj

sun=light('LW Sun | warmth drains into cold light','SUN',(0,-10,12),2.2,(1,.79,.51))
sun.rotation_euler=Vector((.45,.7,-1)).to_track_quat('-Z','Y').to_euler();sun.data.angle=.12
key(sun.data,'energy',[(1,2.2),(481,1.8),(1201,1.2),(1801,.8),(2401,.95)])
key(sun.data,'color',[(1,(1,.79,.51)),(601,(.92,.88,.70)),(1321,(.64,.75,.9)),(1801,(.58,.68,.82)),(2401,(.66,.75,.88))])
fill=light('LW huge soft sky fill','AREA',(43,-4,25),4000,(.56,.68,.83),80)
fill.rotation_euler=Vector((0,1,-1)).to_track_quat('-Z','Y').to_euler()
lamp=light('LW Bakery warm practical','AREA',(3.05,4.75,1.85),30,(1,.47,.12),2.2);lamp.rotation_euler=(math.pi/2,0,0)
driver(lamp.data,'') if False else None
if bpy.data.objects.get('Cold side light on title'):bpy.data.objects['Cold side light on title'].data.energy=800
world.eevee.taa_render_samples=16
world.eevee.volumetric_samples=32
world.eevee.volumetric_tile_size='8'
world.eevee.use_raytracing=True
world.camera.data.dof.use_dof=True
world.camera.data.dof.focus_object=bpy.data.objects['GP_Pair_STATIC_world_scale']
world.camera.data.dof.aperture_fstop=5.6

# Water receives moving normals and an actual planar reflection response.
water=bpy.data.materials.new('LW | Wind brushed puddle');water.use_nodes=True;nt=water.node_tree;bs=nt.nodes.get('Principled BSDF')
bs.inputs['Base Color'].default_value=(.14,.19,.21,1);bs.inputs['Roughness'].default_value=.22;bs.inputs['Metallic'].default_value=.45
noise=nt.nodes.new('ShaderNodeTexNoise');noise.noise_dimensions='4D';noise.inputs['Scale'].default_value=10;driver(noise.inputs['W'],'frame/180')
bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.21;bump.inputs['Distance'].default_value=.015;nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],bs.inputs['Normal'])
verts=[(8+.90*math.cos(i*math.tau/64),.45*math.sin(i*math.tau/64),.018) for i in range(64)]
me=bpy.data.meshes.new('LW Puddle surface');me.from_pydata(verts,[],[tuple(range(64))]);me.materials.append(water);me.update()
ob=bpy.data.objects.new('LW Puddle | physical reflective surface',me);bpy.data.collections['LW | Terrain'].objects.link(ob)

# Deterministic moving 3D noise volumes; no uncached physics or frame handlers.
def volume_mat(name,density,color,seed):
    mat=bpy.data.materials.new(name);mat.use_nodes=True;nt=mat.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial')
    volume=nt.nodes.new('ShaderNodeVolumePrincipled');volume.inputs['Color'].default_value=(*color,1);volume.inputs['Anisotropy'].default_value=.25
    tex=nt.nodes.new('ShaderNodeTexNoise');tex.noise_dimensions='4D';tex.inputs['Scale'].default_value=2.8;tex.inputs['Detail'].default_value=2;driver(tex.inputs['W'],f'{seed}+frame/420')
    coords=nt.nodes.new('ShaderNodeTexCoord');nt.links.new(coords.outputs['Generated'],tex.inputs[0])
    ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.30;ramp.color_ramp.elements[1].position=.68;nt.links.new(tex.outputs['Fac'],ramp.inputs[0])
    mul=nt.nodes.new('ShaderNodeMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=density;nt.links.new(ramp.outputs[0],mul.inputs[0]);nt.links.new(mul.outputs[0],volume.inputs['Density']);nt.links.new(volume.outputs[0],out.inputs['Volume']);return mat

mist=volume_mat('LW | Thin woodland air',.025,(.54,.61,.62),.1)
bpy.ops.mesh.primitive_cube_add(size=1,location=(31,14,4.5));air=move(bpy.context.object);air.name='LW Woodland atmospheric depth';air.scale=(24,22,10);air.data.materials.append(mist)
smoke=volume_mat('LW | Moving battlefield smoke',.28,(.20,.24,.29),.7)
for j,(x,y,z,s) in enumerate([(64,20,3.2,1.6),(64.7,20,5.4,2.1),(66,21,8.1,2.8),(69,23,10.4,3.8),(77,28,4.1,2.3),(78.5,29,7.2,3.2),(80,30,10.3,4.2)]):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=1,location=(x,y,z));ob=move(bpy.context.object);ob.name=f'LW Smoke rolling volume {j:02d}';ob.scale=(s,s*.8,s*1.18);ob.data.materials.append(smoke)
    ob.driver_add('location',0).driver.expression=f'{x}+.33*sin(frame*.007+{j})'
    ob.driver_add('location',2).driver.expression=f'{z}+.27*sin(frame*.011+{j*.8})'

ember=bpy.data.materials.new('LW | Distant restrained ember');ember.diffuse_color=(.8,.18,.025,1);ember.use_nodes=True
ebs=ember.node_tree.nodes.get('Principled BSDF');ebs.inputs['Base Color'].default_value=(.4,.10,.015,1);ebs.inputs['Emission Color'].default_value=(1,.19,.014,1)
driver(ebs.inputs['Emission Strength'],'2.2+.5*sin(frame*.17)+.4*sin(frame*.071)')
for j in range(18):
    x=R.uniform(60,79);y=R.uniform(9,24);z=R.uniform(.3,1.1)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=R.uniform(.025,.07),location=(x,y,z));ob=move(bpy.context.object);ob.name=f'LW Distant ember {j:02d}';ob.scale=(1,.7,R.uniform(1.3,2.4));ob.data.materials.append(ember)
    ob.driver_add('location',2).driver.expression=f'{z}+.07*sin(frame*.08+{j})'
flash=light('LW Distant blast light | restrained','POINT',(63,15,3.5),0,(1,.65,.29))
key(flash.data,'energy',[(1,0),(1240,0),(1250,2600),(1264,450),(1290,0),(1710,0),(1717,1800),(1735,0),(2401,0)])

# Paper and falling leaves have actual depth, tumbling geometry and wind paths.
paper=bpy.data.materials.new('LW | Windblown old paper');paper.use_nodes=True;pbs=paper.node_tree.nodes.get('Principled BSDF');pbs.inputs['Base Color'].default_value=(.56,.56,.48,1);pbs.inputs['Roughness'].default_value=.95
for j in range(22):
    x=R.uniform(39,82);y=R.uniform(1.5,7);z=R.uniform(.07,.25)
    me=bpy.data.meshes.new('LW Paper scrap');me.from_pydata([(-.07,-.05,0),(.08,-.045,.015),(.055,.06,0),(-.065,.055,-.005)],[],[(0,1,2,3)]);me.materials.append(paper);me.update()
    ob=bpy.data.objects.new(f'LW Paper tumbling {j:02d}',me);fx.objects.link(ob)
    ob.driver_add('location',0).driver.expression=f'{x}+.45*sin(frame*.017+{j})'
    ob.driver_add('location',1).driver.expression=f'{y}+.2*cos(frame*.011+{j})'
    ob.driver_add('location',2).driver.expression=f'{z}+.11*(1+sin(frame*.041+{j}))'
    ob.driver_add('rotation_euler',0).driver.expression=f'frame*.018+{j}'
    ob.driver_add('rotation_euler',2).driver.expression=f'frame*.011+{j*.6}'

for matname in ['Title weathered charcoal stone']:
    mat=bpy.data.materials.get(matname)
    if mat:
        bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Emission Strength'].default_value=.10;bs.inputs['Base Color'].default_value=(.065,.075,.08,1)
        bs.inputs['Roughness'].default_value=.95
world['environment_motion']='Native shape keys: canopy/branches, grass, washing and tent canvas. Animated reflective water normals, 3D smoke density and drift, restrained practical/ember/blast light, tumbling papers. Deterministic native drivers, no external handler.'
world['new_geometry_counts']=json.dumps(recipe['counts'])
world['quality_status']='First dimensional world production pass; artistic approval and final character performance remain pending.'
world.render.resolution_percentage=100;master.render.resolution_percentage=100
world.render.filepath='//../../renders/living_world/still_'
master.render.filepath='//../../renders/living_world/WTSC_Living_World_4K_v008.mp4'
world.frame_set(1);master.frame_set(1);bpy.context.window.scene=world
note=bpy.data.texts.new('READ ME | LIVING WORLD v008')
note.write('When the Sky Clears — dimensional living world\n\n100 seconds, 3840 x 2160, 24 fps.\nNew collection 20 | LIVING WORLD contains original native 3D buildings with openings, individual curved roof tiles, branching trees, thick ruins, classroom furniture, tents and terrain. Materials use the two new built-in GPT imagegen paint sources, plus retained ground paint.\n\nWind, cloth, paper, water, smoke and light are animated with editable native keys/drivers. The held Grease Pencil pair is preserved, without the rejected procedural walk. Character gait must later use an actual 3D motion reference behind vector outlines.\n\nConcept planes are retained hidden as guides; only sky, distant hills and far ruined street remain as distant matte layers. All project images and source music are packed.\nSelect WTSC_MASTER_4K_100S to render the full movie with music.\n\nThis is a production iteration for visual review, not final artistic approval.\n')
target=ROOT/'shots/world/WTSC_Living_World_v008.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(target))
(ROOT/'notes/living_world/native_assembly_v008.json').write_text(json.dumps({'source':str(target),'seed':recipe['seed'],'typed_mesh_counts':recipe['counts'],'animated_meshes':motions,'images':[{'name':i.name,'size':list(i.size),'packed':bool(i.packed_file)} for i in [atlas,leaf,ground_image,organic]],'scope':world['environment_motion']},indent=2),encoding='utf-8')
print(json.dumps({'saved':str(target),'typed_meshes':len(recipe['entries']),'ambient_motion_groups':len(motions),'world_objects':len(world.objects)}))
