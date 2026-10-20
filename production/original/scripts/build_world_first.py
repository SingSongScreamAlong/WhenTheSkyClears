"""When the Sky Clears: world-first, static silhouettes, continuous 100s layout.
All scene construction runs in the task-owned Blender host through DCC-MCP.
"""
import bpy,math,random,json
from mathutils import Vector
from pathlib import Path
ROOT=Path(r'WTSC_LOCAL_WORKSPACE')
LAYERS=ROOT/'sets/painted_layers'
scene=bpy.context.scene
assert scene.name=='WTSC_WORLD_FIRST_4K'
pair=bpy.data.objects['GP_Pair_STATIC_world_scale']
assert pair.animation_data is None
random.seed(9316)
scene['project']='When the Sky Clears'
scene['scope']='WORLD AND SETS FIRST: held vector silhouettes translate only; no character animation'
scene['status']='PROVISIONAL atmosphere and layout pass; previous mannequin test rejected'
scene['reference_plan']='When animation resumes: actual 3D source behind vector silhouette, not procedural cutout gait'
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=3840;scene.render.resolution_y=2160;scene.render.resolution_percentage=100
scene.render.fps=24;scene.render.fps_base=1;scene.frame_start=1;scene.frame_end=2400
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.image_settings.compression=15
scene.render.film_transparent=False
scene.view_settings.view_transform='Standard';scene.view_settings.look='None'
scene.world=bpy.data.worlds.new('Quiet diffuse world');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.21,.25,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.3
if hasattr(scene,'eevee'):scene.eevee.taa_render_samples=8

def col(name):
    c=bpy.data.collections.new(name);scene.collection.children.link(c);return c
C={k:col(name) for k,name in [
 ('sky','01 | SKY AND FAR HILLS'),('village','02 | VILLAGE intact and empty'),
 ('woods','03 | WOODS layered trunks'),('school','04 | SCHOOL shattered windows'),
 ('camp','05 | CAMP canvas and posts'),('field','06 | BATTLEFIELD crater and ruins'),
 ('title','07 | TITLE terrain and bases'),('ground','08 | CONTINUOUS GROUND'),
 ('fg','09 | FOREGROUND transitions'),('pair','10 | STATIC CHILDREN vector drawing'),
 ('camera','11 | CAMERA and guide'),('fx','12 | ATMOSPHERE and light') ]}
for c in list(pair.users_collection):c.objects.unlink(pair)
C['pair'].objects.link(pair)
pair['motion']='Object translation only. One held GP frame. No bone or limb animation.'
pair['design_status']='Provisional world-scale stand-ins, not final character models'

def linear(action):
    if not action:return
    for l in action.layers:
        for strip in l.strips:
            for bag in strip.channelbags:
                for f in bag.fcurves:
                    for k in f.keyframe_points:k.interpolation='LINEAR'

def key(socket,values):
    for seconds,value in values:
        socket.default_value=value;socket.keyframe_insert('default_value',frame=round(seconds*24)+1)

def mesh(name,verts,faces,owner,mat=None):
    data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update()
    obj=bpy.data.objects.new(name,data);owner.objects.link(obj)
    if mat:obj.data.materials.append(mat)
    return obj

def flat(name,color):
    mat=bpy.data.materials.new(name);mat.use_nodes=True;nt=mat.node_tree;nt.nodes.clear()
    out=nt.nodes.new('ShaderNodeOutputMaterial');em=nt.nodes.new('ShaderNodeEmission');em.inputs[0].default_value=(*color,1)
    nt.links.new(em.outputs[0],out.inputs[0]);mat.diffuse_color=(*color,1);return mat

def quad(name,x,y,z,width,height,owner,material):
    obj=mesh(name,[(x-width/2,y,z),(x+width/2,y,z),(x+width/2,y,z+height),(x-width/2,y,z+height)],[(0,1,2,3)],owner,material)
    uv=obj.data.uv_layers.new(name='Painting UV')
    for i,v in enumerate([(0,0),(1,0),(1,1),(0,1)]):uv.data[i].uv=v
    return obj

def image_material(name,file,fade=None,variant=None):
    mat=bpy.data.materials.new(name);mat.use_nodes=True
    if hasattr(mat,'surface_render_method'):mat.surface_render_method='DITHERED'
    nt=mat.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial')
    tex=nt.nodes.new('ShaderNodeTexImage');im=bpy.data.images.load(str(LAYERS/file),check_existing=True)
    im.alpha_mode='STRAIGHT';im.pack();im.filepath='//../../sets/painted_layers/'+file
    tex.image=im;tex.interpolation='Linear'
    color=tex.outputs['Color'];alpha=tex.outputs['Alpha']
    if variant:
        second=nt.nodes.new('ShaderNodeTexImage');second.image=bpy.data.images.load(str(LAYERS/variant),check_existing=True);second.image.pack()
        second.image.filepath='//../../sets/painted_layers/'+variant
        mix=nt.nodes.new('ShaderNodeMixRGB');nt.links.new(color,mix.inputs[1]);nt.links.new(second.outputs['Color'],mix.inputs[2]);key(mix.inputs[0],[(0,0),(15,0),(21,1),(100,1)]);color=mix.outputs[0]
    hsv=nt.nodes.new('ShaderNodeHueSaturation');nt.links.new(color,hsv.inputs['Color'])
    key(hsv.inputs['Saturation'],[(0,1.05),(25,.82),(50,.57),(80,.35),(100,.30)])
    key(hsv.inputs['Value'],[(0,1),(35,.88),(65,.78),(80,.90),(100,.94)])
    # Imagegen alpha contains RGB debris at alpha 1-4/255. Remove it in the
    # native shader; source raster files remain unchanged.
    clean=nt.nodes.new('ShaderNodeMapRange');clean.clamp=True;clean.inputs['From Min'].default_value=.08;clean.inputs['From Max'].default_value=.92
    nt.links.new(alpha,clean.inputs['Value'])
    alphaout=clean.outputs['Result']
    if fade:
        mul=nt.nodes.new('ShaderNodeMath');mul.operation='MULTIPLY';nt.links.new(alphaout,mul.inputs[0]);key(mul.inputs[1],fade);alphaout=mul.outputs[0]
    transparent=nt.nodes.new('ShaderNodeBsdfTransparent');em=nt.nodes.new('ShaderNodeEmission');nt.links.new(hsv.outputs[0],em.inputs[0])
    mixshader=nt.nodes.new('ShaderNodeMixShader');nt.links.new(alphaout,mixshader.inputs[0]);nt.links.new(transparent.outputs[0],mixshader.inputs[1]);nt.links.new(em.outputs[0],mixshader.inputs[2]);nt.links.new(mixshader.outputs[0],out.inputs[0])
    return mat

def painting(name,file,x,y,width,baseline=.835,ground=0,owner=None,fade=None,variant=None):
    im=bpy.data.images.load(str(LAYERS/file),check_existing=True);height=width*im.size[1]/im.size[0]
    obj=quad(name,x,y,ground-height*(1-baseline),width,height,owner or C['field'],image_material(name+' paint',file,fade,variant))
    obj['source_layer']=file;obj['depth_band']=y;obj['baseline_fraction']=baseline;return obj

# Sky is one continuous, wide rear painting; it never cuts between locations.
painting('Painted sky | warm left to cold right','Sky_Painted_v001.png',55,90,260,baseline=.54,owner=C['sky'])
for index,(depth,tone,height) in enumerate([(55,(.30,.37,.39),4.5),(35,(.22,.30,.31),3.0),(24,(.15,.23,.22),1.8)]):
    verts=[]
    for i in range(85):
        x=-70+i*3;z=height+math.sin(i*.34+index)*1.1+math.sin(i*.83)*.38
        verts.append((x,depth,z))
    verts += [(182,depth,-4),(-70,depth,-4)]
    mesh('Far hill band %d'%index,verts,[tuple(range(len(verts)))],C['sky'],flat('Hill mist tone %d'%index,tone))

painting('Village A | warmth drains behind tree','Village_Warm_v001.png',5,8,23,owner=C['village'],variant='Village_Empty_v001.png')
painting('Village B | same village abandoned','Village_Empty_v001.png',23,10,23,owner=C['village'])
painting('Woods far canopy','Woods_v001.png',30,16,31,owner=C['woods'])
painting('Woods near trunks','Woods_v001.png',32,4.5,21,owner=C['woods'])
painting('School facade | shattered classroom','School_v001.png',43,6,18,baseline=.80,owner=C['school'])
painting('Camp canvas | displacement edge','Camp_v001.png',50,11,19,baseline=.79,owner=C['camp'])
painting('Battlefield ruin line','Battlefield_v001.png',62,11,31,baseline=.875,owner=C['field'],fade=[(0,1),(78,1),(90,.12),(100,0)])
painting('Far ruined street dissolves into ash','Battlefield_v001.png',78,27,40,baseline=.875,owner=C['field'],fade=[(0,.65),(79,.65),(90,.08),(100,0)])

def ground_z(x):
    wall=.27*max(0,min(1,(x-13)/.7,(20-x)/.7)) if 13<x<20 else 0
    crater=-.62*math.sin((x-44)/5*math.pi)**2 if 44<x<49 else 0
    title=.10*max(0,math.sin((x-67)*1.8)) if 67<x<94 else 0
    return wall+crater+title

# Continuous contact geometry with the puddle motif and later crater.
groundmat=bpy.data.materials.new('Ground | green earth to cold ash');groundmat.use_nodes=True
nt=groundmat.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');em=nt.nodes.new('ShaderNodeEmission')
geo=nt.nodes.new('ShaderNodeNewGeometry');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geo.outputs['Position'],sep.inputs[0])
mapnode=nt.nodes.new('ShaderNodeMapRange');mapnode.inputs['From Min'].default_value=0;mapnode.inputs['From Max'].default_value=90;nt.links.new(sep.outputs['X'],mapnode.inputs[0])
ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1]);
for i,(pos,color) in enumerate([(0,(.07,.09,.043,1)),(.24,(.045,.065,.047,1)),(.46,(.055,.054,.044,1)),(.68,(.037,.046,.052,1)),(1,(.027,.034,.040,1))]):
    e=ramp.color_ramp.elements[0] if i==0 else ramp.color_ramp.elements.new(pos);e.position=pos;e.color=color
nt.links.new(mapnode.outputs[0],ramp.inputs[0])
noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=7;noise.inputs['Detail'].default_value=3
nt.links.new(geo.outputs['Position'],noise.inputs['Vector']);mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.30;nt.links.new(ramp.outputs[0],mix.inputs[1]);nt.links.new(noise.outputs['Fac'],mix.inputs[2]);nt.links.new(mix.outputs[0],em.inputs[0]);nt.links.new(em.outputs[0],out.inputs[0])
xs=[-35+i*.25 for i in range(680)]
verts=[]
for x in xs:verts.extend([(x,-5,ground_z(x)),(x,18,ground_z(x))])
mesh('Continuous ground top',verts,[(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(xs)-1)],C['ground'],groundmat)
side=[]
for x in xs:side.extend([(x,-5,ground_z(x)),(x,-5,-6)])
mesh('Earth profile foreground edge',side,[(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(xs)-1)],C['ground'],flat('Earth near dark',(.012,.017,.019)))

def rock(name,x,y,z,sx,sz,owner,mat):
    pts=[(-.5,-.1),(-.35,.43),(.05,.56),(.48,.24),(.52,-.2)]
    return mesh(name,[(x+px*sx,y,z+pz*sz) for px,pz in pts],[tuple(range(5))],owner,mat)
ink=flat('Foreground charcoal',(.009,.013,.017));stone=flat('Rubble side tones',(.065,.074,.077));grassmat=flat('Grass silhouette olive',(.026,.041,.024))
for i in range(330):
    x=random.uniform(-12,103);y=random.uniform(-2.9,1.0);z=ground_z(x)
    if x<35:
        h=random.uniform(.05,.26);w=random.uniform(.012,.045)
        mesh('Grass clump %03d'%i,[(x-w,y,z),(x+random.uniform(-.09,.09),y,z+h),(x+w,y,z)],[(0,1,2)],C['ground'],grassmat)
    else:rock('Stone fragment %03d'%i,x,y,z,random.uniform(.07,.25),random.uniform(.05,.15),C['ground'],stone)
water=flat('Puddle reflects amber',(.23,.25,.20))
quad('Puddle side glint | first crossing',8,-.20,.006,1.25,.025,C['ground'],water)
for i in range(8):quad('Puddle broken reflection %d'%i,7.5+i*.14,-.22,.010,.085,.009,C['ground'],flat('Puddle warm glint %d'%i,(.47,.38,.22)))

def branch(name,a,b,width,owner,mat):
    a=Vector(a);b=Vector(b);d=(b-a).normalized();n=Vector((d.z,0,-d.x))*width/2
    return mesh(name,[tuple(a-n),tuple(a+n),tuple(b+n*.55),tuple(b-n*.55)],[(0,1,2,3)],owner,mat)
for ti,x in enumerate([-4,16.3,24,38.2,55.5]):
    y=-5.5 if ti in [0,1,4] else -3.5;h=6.0 if ti<3 else 4.8
    branch('Transition tree trunk %d'%ti,(x,y,-.2),(x-.12,y,h),.48,C['fg'],ink)
    for side in [-1,1]:
        for j in range(3):
            z=2.6+j*.88;reach=side*(1.2+j*.3)
            branch('Transition branch %d %d %d'%(ti,side,j),(x,y,z),(x+reach,y,z+.7),.10,C['fg'],ink)
            branch('Transition twig %d %d %d'%(ti,side,j),(x+reach*.68,y,z+.45),(x+reach*.80,y,z+1.0),.04,C['fg'],ink)
for i,x in enumerate([39.0,40.2,52.7,54.0,59.0]):
    branch('Camp to battlefield post %d'%i,(x,-2.5,0),(x+.05,-2.5,1.9),.10,C['fg'],ink)
    if i%2==0:branch('Broken rail %d'%i,(x-.6,-2.6,.65),(x+1.3,-2.6,.9),.075,C['fg'],ink)

# The monumental title is real editable lettering and 3D bases, not a card.
titlemat=bpy.data.materials.new('Title weathered charcoal stone');titlemat.use_nodes=True
bs=titlemat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.052,.062,.071,1);bs.inputs['Roughness'].default_value=.98
bs.inputs['Emission Color'].default_value=(.023,.031,.041,1);bs.inputs['Emission Strength'].default_value=.8
tex=titlemat.node_tree.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=5;tex.inputs['Detail'].default_value=4
bump=titlemat.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.45;bump.inputs['Distance'].default_value=.045
titlemat.node_tree.links.new(tex.outputs['Fac'],bump.inputs['Height']);titlemat.node_tree.links.new(bump.outputs[0],bs.inputs['Normal'])
font=bpy.data.curves.new('WHEN THE SKY CLEARS | editable text','FONT');font.body='WHEN THE SKY CLEARS';font.size=4;font.extrude=.28;font.bevel_depth=.035;font.bevel_resolution=1;font.space_character=1.08
title=bpy.data.objects.new('WHEN THE SKY CLEARS | monumental terrain',font);C['title'].objects.link(title);title.rotation_euler=(math.pi/2,0,0);title.location=(66,2.4,.08);title.data.materials.append(titlemat)
bpy.context.view_layer.update();title.scale.x=32/max(title.dimensions.x,.001);title.scale.y=4/max(title.dimensions.z,.001)
title['use']='Physical landscape, keep editable. Original Blender built-in font.'
for i,x in enumerate([66.5,69,72.2,75.1,79.4,82.6,86.8,90.6,94.2]):
    bpy.ops.mesh.primitive_cube_add(size=1,location=(x,1.0,.15))
    ob=bpy.context.object;ob.name='Title broken base %02d'%i;ob.scale=(.65,.48,.15);ob.data.materials.append(titlemat)
    for c in list(ob.users_collection):c.objects.unlink(ob)
    C['title'].objects.link(ob)
    bevel=ob.modifiers.new('Weathered base corners','BEVEL');bevel.width=.04;bevel.segments=1

lightdata=bpy.data.lights.new('Cold side light on title','AREA');lightdata.energy=1900;lightdata.shape='DISK';lightdata.size=12
light=bpy.data.objects.new('Cold side light on title',lightdata);C['fx'].objects.link(light);light.location=(78,-4,9);light.rotation_euler=(Vector((81,2,1.8))-light.location).to_track_quat('-Z','Y').to_euler()

route=[(0,0),(18,12),(35,27),(50,41),(67,56),(80,67),(90,80),(96,87),(100,90)]
def lerp_keys(keys,t):
    for (a,x),(b,y) in zip(keys,keys[1:]):
        if a<=t<=b:return x+(y-x)*(t-a)/(b-a)
    return keys[-1][1]
camdata=bpy.data.cameras.new('Continuous side camera');camdata.type='PERSP';camdata.lens=50;camdata.sensor_width=36;camdata.clip_start=.1;camdata.clip_end=400
camera=bpy.data.objects.new('CAMERA | continuous lateral route',camdata);C['camera'].objects.link(camera);camera.rotation_euler=(math.pi/2,0,0);scene.camera=camera
for frame in list(range(1,2402,12))+[2401]:
    t=(frame-1)/24;x=lerp_keys(route,t)
    pair.location=(x,0,ground_z(x));pair.keyframe_insert('location',frame=frame)
    cx=lerp_keys([(0,2.1),(80,69.1),(90,82),(96,82),(100,82)],t) if t>80 else x+2.1
    cy=lerp_keys([(0,-20),(80,-20),(90,-35),(96,-56),(100,-56)],t)
    cz=lerp_keys([(0,3.1),(80,3.1),(90,4.3),(96,7.4),(100,7.4)],t)
    camera.location=(cx,cy,cz);camera.keyframe_insert('location',frame=frame)
linear(pair.animation_data.action);linear(camera.animation_data.action)

seq=scene.sequence_editor_create();sound=seq.strips.new_sound('MUSIC | user supplied 100s',str(ROOT/'edit/When_The_Sky_Clears_Trailer_Music_100s.wav'),channel=1,frame_start=1)
sound.sound.filepath='//../../edit/When_The_Sky_Clears_Trailer_Music_100s.wav'
sound.volume=1;sound.keyframe_insert('volume',frame=2161);sound.volume=0;sound.keyframe_insert('volume',frame=2401)
# A sound-only sequencer must not replace the scene picture.
scene.render.use_sequencer=False
scene.use_nodes=True;nt=bpy.data.node_groups.new('WTSC final picture fade','CompositorNodeTree');scene.compositing_node_group=nt
nt.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor')
rl=nt.nodes.new('CompositorNodeRLayers');comp=nt.nodes.new('NodeGroupOutput')
fade=nt.nodes.new('CompositorNodeExposure');nt.links.new(rl.outputs['Image'],fade.inputs['Image']);nt.links.new(fade.outputs['Image'],comp.inputs['Image'])
fade.inputs['Exposure'].default_value=0;fade.inputs['Exposure'].keyframe_insert('default_value',frame=1)
for f in range(2353,2402):
    fade.inputs['Exposure'].default_value=math.log2(max(2**-24,(2400-f)/47));fade.inputs['Exposure'].keyframe_insert('default_value',frame=f)
for label,seconds in [('VILLAGE',0),('VILLAGE EMPTIES / WOODS',18),('WOODS',28),('SCHOOL',39),('CAMP',47),('BATTLEFIELD / CRATER',54),('RUINS AND ASH',67),('TITLE TERRAIN',80),('AUDIO FADE',90),('CAMERA HOLD',96),('PICTURE FADE',98),('100 SECOND END boundary',100)]:scene.timeline_markers.new(label,frame=int(seconds*24)+1)

note=bpy.data.texts.new('READ ME | WORLD FIRST')
note.write('When the Sky Clears — WORLD FIRST\n\n3840 x 2160 UHD, 24 fps, frames 1–2400 = 100 seconds.\n\nThis pass reviews the continuous world, atmosphere, palette, region changes and title scale.\nThe children are one held editable Grease Pencil vector drawing, translated intact through the route. There is no limb, bone, walk or facial animation in this file.\n\nDistinct sets: village (intact and abandoned), woods at two depths, school, camp, battlefield/crater, ruins/ash, physical title terrain.\nPaint layers are genuine built-in GPT imagegen outputs, packed and copied into sets/painted_layers. Native source rasters are 1672 x 941 approximately; the render master is native UHD.\n\nMusic is the user-supplied 100-second WAV, referenced relatively. Its fade starts at 90 seconds. Picture fades during the final two seconds.\n\nThe earlier segmented mannequin motion was rejected. When animation resumes, align a verified animated 3D source behind the vector silhouette and adapt its gait. Do not reuse the rejected procedural gait.\n\nThis is a provisional world and mood pass, not a finished trailer or approved art package.\n')
scene.frame_set(1)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
scene.render.filepath='//../../renders/world/frames_4k/frame_'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'shots/world/WTSC_World_First_v001.blend'))
print('WORLD_FIRST_SAVED',len(scene.objects),'objects,',len(C),'depth/set collections,100seconds,3840x2160')
