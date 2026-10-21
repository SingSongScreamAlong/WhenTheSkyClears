"""Native painted world continuation. Run against v015 in an isolated Blender process."""
import bpy, math, random, json
from pathlib import Path
from mathutils import Vector

ROOT=Path(r'WTSC_LOCAL_WORKSPACE')
OUT=ROOT/'shots/world/WTSC_Painted_World_Trailer_v016.blend'
assert not OUT.exists(), 'Preserve existing checkpoint; choose a new version.'
S=bpy.context.scene
assert S.name=='WTSC_VILLAGE_PROGRESS_v015'
S.name='WTSC_PAINTED_WORLD_4K_100S_v016'
random.seed(16931)
S.frame_start=1;S.frame_end=2400;S.render.fps=24;S.render.fps_base=1
S.render.resolution_x=3840;S.render.resolution_y=2160;S.render.resolution_percentage=100
S.render.engine='BLENDER_EEVEE';S.eevee.taa_render_samples=16
S.render.image_settings.media_type='VIDEO';S.render.ffmpeg.format='MPEG4';S.render.ffmpeg.codec='H264'
S.render.ffmpeg.constant_rate_factor='HIGH';S.render.ffmpeg.ffmpeg_preset='GOOD';S.render.ffmpeg.audio_codec='NONE'
S.render.film_transparent=False;S.render.use_sequencer=False
S.view_settings.view_transform='Standard';S.view_settings.look='None'
camera=S.camera;camera.name='v016 | CAMERA | continuous world journey'
camera.data.clip_end=500
pair=next(o for o in S.objects if o.type=='GREASEPENCIL')
pair.name='v016 | CHILDREN | held painterly near-age pair'
pair['performance']='One held drawing. Translation only. No gait, acting or limb keys.'
pair['style']='Near-black charcoal/gray paint, tiny off-white eye accents. Boy slightly taller.'

def collection(name):
    c=bpy.data.collections.new(name);S.collection.children.link(c);return c
C={k:collection('v016 | '+name) for k,name in [('sets','02 Regional painted sets'),('ground','03 Continuous painted path'),('wind','04 Wind and foreground foliage'),('smoke','05 Smoke and airborne paint'),('light','06 Painted light and mist'),('title','07 Monumental title terrain')]}

def drive(owner,path,expr,index=None):
    f=owner.driver_add(path) if index is None else owner.driver_add(path,index)
    f.driver.type='SCRIPTED';f.driver.expression=expr;return f

def linear(action):
    if not action:return
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    for k in curve.keyframe_points:k.interpolation='LINEAR'

def keys(socket,points):
    for t,value in points:
        socket.default_value=value;socket.keyframe_insert('default_value',frame=min(2400,round(t*24)+1))
    if socket.id_data.animation_data:linear(socket.id_data.animation_data.action)

def lerp(points,t):
    for (a,x),(b,y) in zip(points,points[1:]):
        if a<=t<=b:return x+(y-x)*(t-a)/(b-a)
    return points[0][1] if t<points[0][0] else points[-1][1]

def mesh(name,verts,faces,owner,mat=None,uvs=None):
    d=bpy.data.meshes.new(name);d.from_pydata(verts,[],faces);d.update()
    o=bpy.data.objects.new(name,d);owner.objects.link(o)
    if mat:d.materials.append(mat)
    if uvs:
        uv=d.uv_layers.new(name='Paint UV')
        for p in d.polygons:
            for li in p.loop_indices:uv.data[li].uv=uvs[d.loops[li].vertex_index]
    return o

def image(path):
    im=bpy.data.images.load(str(path),check_existing=True);im.alpha_mode='STRAIGHT';im.pack();return im

def mathnode(nt,op,a=None,b=None):
    n=nt.nodes.new('ShaderNodeMath');n.operation=op
    for i,x in enumerate([a,b]):
        if x is None:continue
        if isinstance(x,(float,int)):n.inputs[i].default_value=x
        else:nt.links.new(x,n.inputs[i])
    return n.outputs[0]

def material(name,path=None,tone=(1,1,1),fade=None,alpha=.999,washed=0,opaque=False):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.surface_render_method='DITHERED'
    nt=m.node_tree;nt.nodes.clear();output=nt.nodes.new('ShaderNodeOutputMaterial');em=nt.nodes.new('ShaderNodeEmission')
    uv=nt.nodes.new('ShaderNodeTexCoord');color=None;opacity=None
    if path:
        tex=nt.nodes.new('ShaderNodeTexImage');tex.image=image(path);tex.interpolation='Linear';tex.extension='CLIP';nt.links.new(uv.outputs['UV'],tex.inputs['Vector'])
        color=tex.outputs['Color'];opacity=tex.outputs['Alpha']
        clean=nt.nodes.new('ShaderNodeMapRange');clean.clamp=True;clean.inputs['From Min'].default_value=.035;clean.inputs['From Max'].default_value=.96
        nt.links.new(opacity,clean.inputs[0]);opacity=clean.outputs['Result']
        hsv=nt.nodes.new('ShaderNodeHueSaturation');nt.links.new(color,hsv.inputs['Color'])
        keys(hsv.inputs['Saturation'],[(0,1),(18,.85),(38,.66),(62,.46),(80,.28),(100,.25)])
        color=hsv.outputs[0]
        mul=nt.nodes.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1;mul.inputs[2].default_value=(*tone,1);nt.links.new(color,mul.inputs[1]);color=mul.outputs[0]
        if washed:
            wash=nt.nodes.new('ShaderNodeMixRGB');wash.inputs[0].default_value=washed;wash.inputs[2].default_value=(.32,.39,.43,1);nt.links.new(color,wash.inputs[1]);color=wash.outputs[0]
        nt.links.new(color,em.inputs[0])
    else:em.inputs[0].default_value=(*tone,1)
    if opaque:nt.links.new(em.outputs[0],output.inputs[0]);return m
    opacity=mathnode(nt,'MULTIPLY',opacity if opacity is not None else 1,alpha)
    if fade:
        mult=nt.nodes.new('ShaderNodeMath');mult.operation='MULTIPLY';nt.links.new(opacity,mult.inputs[0]);keys(mult.inputs[1],fade);opacity=mult.outputs[0]
    opacitynode=nt.nodes.new('ShaderNodeMath');opacitynode.name='FX opacity';opacitynode.operation='MULTIPLY';opacitynode.inputs[1].default_value=1;nt.links.new(opacity,opacitynode.inputs[0])
    mix=nt.nodes.new('ShaderNodeMixShader');tr=nt.nodes.new('ShaderNodeBsdfTransparent');nt.links.new(opacitynode.outputs[0],mix.inputs[0]);nt.links.new(tr.outputs[0],mix.inputs[1]);nt.links.new(em.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],output.inputs[0]);return m

def grid(name,x,y,z,w,h,mat,owner,nx=48,nz=28,uvbox=(0,1,0,1)):
    verts=[];uvs=[]
    u0,u1,v0,v1=uvbox
    for j in range(nz+1):
        for i in range(nx+1):
            u=i/nx;v=j/nz;verts.append(((u-.5)*w,0,(v-.5)*h));uvs.append((u0+u*(u1-u0),v0+v*(v1-v0)))
    faces=[]
    for j in range(nz):
        for i in range(nx):
            a=j*(nx+1)+i;faces.append((a,a+1,a+nx+2,a+nx+1))
    o=mesh(name,verts,faces,owner,mat,uvs);o.location=(x,y,z);return o

def wind(o,amp=.06,mode='tree',phase=0):
    if not o.data.shape_keys:o.shape_key_add(name='Basis')
    base=o.data.shape_keys.key_blocks[0]
    # Grid sources can be XY imported cards or native XZ grids. UVs make the pinning explicit.
    vertsuv={}
    uv=o.data.uv_layers.active
    for loop in o.data.loops:vertsuv[loop.vertex_index]=tuple(uv.data[loop.index].uv)
    xy=abs(o.rotation_euler.x-math.pi/2)<.01
    for name,flutter in [('Wind | rooted branches or pinned cloth',False),('Wind | leaf and edge flutter',True)]:
        key=o.shape_key_add(name=name);key.slider_min=-1;key.slider_max=1
        for i,p in enumerate(key.data):
            u,v=vertsuv[i];co=base.data[i].co.copy()
            if mode=='village':
                # Only painted canopy and washing-line region flex. Roofs/plaster/chimneys remain rigid.
                tree=max(0,min(1,(v-.48)/.44)) if (u<.32 or .67<u<.88) else 0
                cloth=max(0,1-abs(v-.29)/.13)*max(0,min(1,(u-.87)/.10))
                weight=max(tree,cloth)
            elif mode=='cloth':
                weight=math.sin(math.pi*max(0,min(1,(v-.17)/.67)))**2 * (.3+.7*math.sin(math.pi*u)**2)
            elif mode=='oak':weight=max(0,min(1,(v-.27)/.73))**1.6 if v>.25 else max(0,1-v/.08)*.07
            else:weight=max(0,min(1,(v-.16)/.80))**1.6
            dx=amp*weight*(math.sin(u*37+v*24+phase)*.32 if flutter else (.7+.3*math.sin(v*4+u*5)))
            dz=amp*weight*(math.sin(u*24+v*31)*.11 if flutter else .12*math.sin(u*7))
            co.x+=dx
            if xy:co.y+=dz
            else:co.z+=dz
            p.co=co
        expr=f'.58*sin(frame/{14 if flutter else 43}+{phase})+.25*sin(frame/{7 if flutter else 19}+{phase+1})+.17*sin(frame/117)'
        drive(key,'value',expr)
    o['animation']='Native rooted/pinned mesh shape keys. Camera translation is separate.'

def densify_imported(o,nx=64,nz=36):
    # Preserve original local dimensions, material, UV, transform, and painted contact arrangement.
    coords=[p.co for p in o.data.vertices];xmin=min(p.x for p in coords);xmax=max(p.x for p in coords);ymin=min(p.y for p in coords);ymax=max(p.y for p in coords)
    old=o.data
    verts=[(xmin+(xmax-xmin)*i/nx,ymin+(ymax-ymin)*j/nz,0) for j in range(nz+1) for i in range(nx+1)]
    faces=[]
    for j in range(nz):
        for i in range(nx):a=j*(nx+1)+i;faces.append((a,a+1,a+nx+2,a+nx+1))
    d=bpy.data.meshes.new(o.name+' | deformable paint grid');d.from_pydata(verts,[],faces);d.update();uv=d.uv_layers.new(name='Paint UV')
    for loop in d.loops:
        idx=loop.vertex_index;uv.data[loop.index].uv=(idx%(nx+1)/nx,idx//(nx+1)/nz)
    for m in old.materials:d.materials.append(m)
    o.data=d

def existing_grade(o):
    nt=o.data.materials[0].node_tree;em=next(n for n in nt.nodes if n.type=='EMISSION');source=em.inputs[0].links[0].from_socket
    hsv=nt.nodes.new('ShaderNodeHueSaturation');nt.links.new(source,hsv.inputs['Color']);nt.links.new(hsv.outputs[0],em.inputs[0])
    keys(hsv.inputs['Saturation'],[(0,1),(14,1),(27,.80),(48,.67),(75,.45),(100,.35)])
    return hsv

village=S.objects['v015 | Painted village'];oak=S.objects['v015 | Oak frame and near bank'];rear=S.objects['v015 | Rear countryside'];path=S.objects['v015 | Walking path']
densify_imported(village);wind(village,.10,'village',1.2)
densify_imported(oak);wind(oak,.075,'oak',.1)
existing_grade(village);existing_grade(path);existing_grade(oak)
rear.scale=(2.4,2.4,2.4)
existing_grade(rear)

# The backmost horizon follows only the camera's X; closer bands stay in real world space.
# Slow painted UV drift supplies cloud movement without shifting the entire village.
nt=rear.data.materials[0].node_tree;tex=next(n for n in nt.nodes if n.type=='TEX_IMAGE');uv=next(n for n in nt.nodes if n.type=='TEX_COORD')
offset=nt.nodes.new('ShaderNodeVectorMath');offset.operation='ADD';nt.links.new(uv.outputs['UV'],offset.inputs[0]);nt.links.new(offset.outputs[0],tex.inputs['Vector']);drive(offset.inputs[1],'default_value','frame*.000003',0)
tex.extension='EXTEND'

# Painted light is localized to the bakery panes and wall, with no architecture deformation.
nt=village.data.materials[0].node_tree;em=next(n for n in nt.nodes if n.type=='EMISSION');source=em.inputs[0].links[0].from_socket
uv=next(n for n in nt.nodes if n.type=='TEX_COORD');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(uv.outputs['UV'],sep.inputs[0])
def rectmask(nt,sep,u0,u1,v0,v1):
    a=mathnode(nt,'GREATER_THAN',sep.outputs['X'],u0);a=mathnode(nt,'MULTIPLY',a,mathnode(nt,'LESS_THAN',sep.outputs['X'],u1))
    a=mathnode(nt,'MULTIPLY',a,mathnode(nt,'GREATER_THAN',sep.outputs['Y'],v0));return mathnode(nt,'MULTIPLY',a,mathnode(nt,'LESS_THAN',sep.outputs['Y'],v1))
mask=rectmask(nt,sep,.405,.555,.191,.294)
flick=nt.nodes.new('ShaderNodeValue');flick.name='Warm pane flicker';drive(flick.outputs[0],'default_value','.025+.025*sin(frame*.71)+.013*sin(frame*1.17+.5)')
fac=mathnode(nt,'MULTIPLY',mask,flick.outputs[0]);mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='ADD';nt.links.new(fac,mix.inputs[0]);nt.links.new(source,mix.inputs[1]);mix.inputs[2].default_value=(1,.39,.075,1);nt.links.new(mix.outputs[0],em.inputs[0])
# Moving soft leaf shadows, restricted to sunlit wall and excluding the warm window.
noise=nt.nodes.new('ShaderNodeTexNoise');noise.noise_dimensions='4D';noise.inputs['Scale'].default_value=15;noise.inputs['Detail'].default_value=1.4;nt.links.new(uv.outputs['UV'],noise.inputs['Vector']);drive(noise.inputs['W'],'default_value','frame/390')
wall=rectmask(nt,sep,.56,.74,.24,.53);fac=mathnode(nt,'MULTIPLY',wall,noise.outputs['Fac']);fac=mathnode(nt,'MULTIPLY',fac,.15)
shadow=nt.nodes.new('ShaderNodeMixRGB');shadow.blend_type='MULTIPLY';nt.links.new(fac,shadow.inputs[0]);nt.links.new(em.inputs[0].links[0].from_socket,shadow.inputs[1]);shadow.inputs[2].default_value=(.29,.36,.41,1);nt.links.new(shadow.outputs[0],em.inputs[0])

# Keep every contact wash parented to the held drawing while it translates.
for o in list(S.objects):
    if 'Ground contact |' in o.name:
        for p in o.data.vertices:p.co-=pair.location
        o.parent=pair

route=[(0,0),(18,12),(35,27),(50,41),(67,56),(80,67),(90,80),(96,87),(100,90)]
for frame in list(range(1,2401,12))+[2400]:
    t=(frame-1)/24;x=lerp(route,t)
    pair.location=(x-1.68912,0,.771372);pair.keyframe_insert('location',frame=frame)
    cx=x if t<=80 else lerp([(80,67),(90,82),(100,82)],t)
    cy=lerp([(0,-16),(80,-16),(90,-35),(96,-56),(100,-56)],t)
    cz=lerp([(0,3),(80,3),(90,4.3),(96,7.4),(100,7.4)],t)
    camera.location=(cx,cy,cz);camera.keyframe_insert('location',frame=frame)
    rear.location.x=cx;rear.location.z=cz;rear.keyframe_insert('location',frame=frame)
for ob in [pair,camera,rear]:linear(ob.animation_data.action)

# Continuous registered path. Source rows clamp below the path; native shader grades the near bank.
groundmat=material('v016 | Registered painted earth',ROOT/'sets/village_lookdev/v014/Path_Detail_Repaint.png',opaque=True)
nt=groundmat.node_tree;tex=next(n for n in nt.nodes if n.type=='TEX_IMAGE');tex.extension='EXTEND'
uv=next(n for n in nt.nodes if n.type=='TEX_COORD');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(uv.outputs['UV'],sep.inputs[0]);fract=mathnode(nt,'PINGPONG',sep.outputs['X'],1)
combine=nt.nodes.new('ShaderNodeCombineXYZ');nt.links.new(fract,combine.inputs['X']);nt.links.new(sep.outputs['Y'],combine.inputs['Y']);nt.links.new(combine.outputs[0],tex.inputs['Vector'])
ground=grid('v016 | Continuous painted earth and path',49,2.06,-9.5,145,22,groundmat,C['ground'],1,1,(-12,145/2.7216-12,(-20.5+.2076)/1.1664,(1.5+.2076)/1.1664))
em=next(n for n in nt.nodes if n.type=='EMISSION');color=em.inputs[0].links[0].from_socket
geo=nt.nodes.new('ShaderNodeNewGeometry');ps=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geo.outputs['Position'],ps.inputs[0]);ramp=nt.nodes.new('ShaderNodeMapRange');ramp.clamp=True;ramp.inputs['From Min'].default_value=-1.2;ramp.inputs['From Max'].default_value=1.1;ramp.inputs['To Min'].default_value=.10;ramp.inputs['To Max'].default_value=.85;nt.links.new(ps.outputs['Z'],ramp.inputs[0])
mul=nt.nodes.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1;nt.links.new(color,mul.inputs[1]);nt.links.new(ramp.outputs[0],mul.inputs[2]);nt.links.new(mul.outputs[0],em.inputs[0])

# Original near-bank paint is repeated at the original scale, preserving organic ground detail.
bankmat=material('v016 | Near bank charcoal paint',ROOT/'sets/village_lookdev/v012/Foreground_Ground.png',tone=(.12,.14,.13),opaque=True)
nt=bankmat.node_tree;tex=next(n for n in nt.nodes if n.type=='TEX_IMAGE');tex.extension='REPEAT'
bank=grid('v016 | Foreground painted bank continuation',48,-5,-6,145,14,bankmat,C['ground'],1,1,(-10,145/7.92-10,-.19,.072))

def painting(name,file,x,y,width,baseline=.835,tone=(1,1,1),washed=0,fade=None,mode=None):
    im=image(ROOT/'sets/painted_layers'/file);h=width*im.size[1]/im.size[0]
    base=3+(.5-.825)*(y+16)*.405
    m=material('v016 | '+name+' paint',ROOT/'sets/painted_layers'/file,tone,fade,washed=washed)
    o=grid('v016 | '+name,x,y,base+h*(baseline-.5),width,h,m,C['sets'])
    o['source_layer']=file;o['depth_m']=y;o['paint_baseline']=baseline
    if mode:wind(o,.11 if y>10 else .065,mode,x*.2)
    return o

empty=painting('Village continues | abandoned','Village_Empty_v001.png',19,12,23,tone=(.87,.91,.96),fade=[(0,0),(9,0),(15,1),(32,1),(40,0),(100,0)],mode='village')
woodsfar=painting('Woods | far silver canopy','Woods_v001.png',29,18,38,tone=(.60,.73,.75),washed=.22,fade=[(0,0),(17,0),(24,1),(42,1),(50,0),(100,0)],mode='tree')
woodsnear=painting('Woods | near rooted oaks','Woods_v001.png',29,6,23,tone=(.38,.45,.39),washed=.04,fade=[(0,0),(20,0),(26,1),(40,1),(47,0),(100,0)],mode='tree')
school=painting('School | broken windows and plaster','School_v001.png',42,10,22,baseline=.80,tone=(.84,.91,.95),fade=[(0,0),(35,0),(39,1),(52,1),(58,0),(100,0)])
camp=painting('Camp | pinned canvas and ropes','Camp_v001.png',53,10,24,baseline=.79,tone=(.76,.82,.87),fade=[(0,0),(46,0),(51,1),(68,1),(74,0),(100,0)],mode='cloth')
field=painting('Battlefield | broken village line','Battlefield_v001.png',65,12,35,baseline=.875,tone=(.74,.84,.93),washed=.05,fade=[(0,0),(59,0),(65,1),(79,1),(88,0),(100,0)])
farfield=painting('Ruins | distant ash street','Battlefield_v001.png',77,28,53,baseline=.875,tone=(.61,.74,.83),washed=.27,fade=[(0,0),(60,0),(66,.8),(82,.8),(94,0),(100,0)])

# Foreground trunks are cropped from the actual painted oak band, with gaps between them.
for i,(x,y) in enumerate([(18,-4),(33,-3),(39,-4),(55,-3)]):
    mat=material('v016 | Transition oak paint '+str(i),ROOT/'sets/painted_layers/Woods_v001.png',tone=(.19,.22,.20),fade=[(0,0),(14,0),(19,1),(69,1),(77,0),(100,0)])
    ob=grid('v016 | Foreground oak transition '+str(i),x,y,3.1,3.0,8.5,mat,C['wind'],18,48,(.012,.20,.16,1))
    wind(ob,.075,'tree',i+.7)

# Painterly atmospheric shapes, with soft brush-textured edges supplied by the smoke asset.
smokepath=ROOT/'sets/fx/Painted_Smoke_Wisp_v016.png'
smoke_specs=[('Bakery chimney',4.44,11.65,5.27,1.55,4.2,0,22,.24),('Far chimney',11.5,12,4.5,1.1,3.1,2,29,.20),('Camp smoke',51,9.4,1.8,2.4,5.5,47,74,.34),('Battlefield smoke',62,14,1.2,4.5,9.0,59,88,.29),('Far battlefield smoke',72,24,1,6,11,64,93,.26)]
for si,(label,x,y,z,w,h,start,end,opacity) in enumerate(smoke_specs):
    for j in range(3):
        m=material('v016 | '+label+' wisp '+str(j),smokepath,tone=(.80,.85,.91),alpha=opacity,fade=[(0,0),(max(0,start),0),(start+1,1),(end-1,1),(end,0),(100,0)])
        ob=grid('v016 | '+label+' | wisp '+str(j),x,y,z+h*.43,w,h,m,C['smoke'],12,30)
        wind(ob,.23,'tree',si+j*2)
        age=f'((frame+{j*91+si*43})%288)/288'
        drive(ob,'location',f'{x}+({age})*.65+.10*sin(frame/48+{j})',0)
        drive(ob,'location',f'{z+h*.43}+({age})*.6',2)
        drive(ob,'scale',f'.75+({age})*.38',0);drive(ob,'scale',f'.80+({age})*.35',2)
        drive(m.node_tree.nodes['FX opacity'].inputs[1],'default_value',f'sin(pi*({age}))**2')

def softmat(name,color,opacity):
    m=material(name,tone=color,alpha=opacity)
    nt=m.node_tree;uv=next(n for n in nt.nodes if n.type=='TEX_COORD');dist=nt.nodes.new('ShaderNodeVectorMath');dist.operation='DISTANCE';dist.inputs[1].default_value=(.5,.5,0);nt.links.new(uv.outputs['UV'],dist.inputs[0]);r=nt.nodes.new('ShaderNodeMapRange');r.clamp=True;r.interpolation_type='SMOOTHERSTEP';r.inputs['From Min'].default_value=.03;r.inputs['From Max'].default_value=.5;r.inputs['To Min'].default_value=1;r.inputs['To Max'].default_value=0;nt.links.new(dist.outputs['Value'],r.inputs[0])
    mix=next(n for n in nt.nodes if n.type=='MIX_SHADER');a=mix.inputs[0].links[0].from_socket;nt.links.new(mathnode(nt,'MULTIPLY',a,r.outputs[0]),mix.inputs[0]);return m

# Low drifting haze at distinct depths; opacity remains low enough to read silhouettes and foliage.
for i,(x,y,z,w,h) in enumerate([(24,16,1.4,24,2.1),(32,8,1.0,18,1.1),(49,16,1.1,23,1.5),(65,18,.8,30,2.2),(79,19,1.1,35,2.6)]):
    m=softmat('v016 | Layered mist '+str(i),(.47,.53,.56),.10 if i<2 else .16)
    ob=grid('v016 | Slow ground mist '+str(i),x,y,z,w,h,m,C['light'],1,1)
    drive(ob,'location',f'{x}+1.2*sin(frame/490+{i})',0)
    drive(m.node_tree.nodes['FX opacity'].inputs[1],'default_value',f'.70+.24*sin(frame/170+{i})')

# Small moving warm pools at the bakery windows and lantern. These are painted light overlays.
for i,(x,z,w,h) in enumerate([(1.5,.43,2.5,.5),(.90,1.58,.47,.65)]):
    m=softmat('v016 | Bakery warm pool '+str(i),(.75,.30,.045),.10)
    ob=grid('v016 | Warm painted light pool '+str(i),x,11.6 if i else 1.92,z,w,h,m,C['light'],1,1)
    drive(ob,'scale',f'1+.045*sin(frame/.{71 if i else 93})+.025*sin(frame/7)',0)
    drive(m.node_tree.nodes['FX opacity'].inputs[1],'default_value',f'.8+.14*sin(frame*.71+{i})+.05*sin(frame*1.17)')

# Fine physical foreground grass, with irregular drawn profiles and rooted wind.
grassmat=material('v016 | Painted grass ink',tone=(.019,.025,.015),opaque=True)
for i in range(105):
    x=random.uniform(2,70);y=random.uniform(-3.9,-1.5);z=.59+random.uniform(-.09,.05);h=random.uniform(.08,.28)
    verts=[];faces=[]
    for b in range(3):
        bx=random.uniform(-.07,.07);lean=random.uniform(-.09,.09);wid=random.uniform(.006,.014);base=len(verts)
        verts += [(bx-wid,0,0),(bx+wid,0,0),(bx+lean*.6,0,h*.7),(bx+lean,0,h)]
        faces.append((base,base+1,base+2,base+3))
    ob=mesh('v016 | Rooted grass %03d'%i,verts,faces,C['wind'],grassmat);ob.location=(x,y,z)
    ob.shape_key_add(name='Basis');key=ob.shape_key_add(name='Wind | rooted tips');key.slider_min=-1
    for p in key.data:p.co.x+=.035*(p.co.z/h)**2
    drive(key,'value',f'.75*sin(frame/22+{x})+.25*sin(frame/9+{i})')

# Windborne leaves, later torn paper and ash. Each has a small editable irregular mesh.
leafmats=[material('v016 | Airborne painted tone '+str(i),tone=c,alpha=.76) for i,c in enumerate([(.13,.15,.055),(.30,.20,.07),(.46,.49,.46),(.11,.15,.18)])]
for i in range(76):
    late=i>=40;x=random.uniform(2,42) if not late else random.uniform(43,82);y=random.uniform(-3,12);z=random.uniform(1.5,6.2)
    size=random.uniform(.018,.045) if i<40 else random.uniform(.016,.06)
    points=[(-size,0,0),(-size*.23,0,size*.45),(size,0,0),(size*.05,0,-size*.36)]
    ob=mesh('v016 | '+('Paper or ash ' if late else 'Windborne leaf ')+str(i),points,[(0,1,2,3)],C['smoke'],leafmats[2+(i%2)] if late else leafmats[i%2]);ob.location=(x,y,z)
    drive(ob,'location',f'{x}+2.4*sin(frame/320+{i})+.14*sin(frame/31+{i})',0)
    drive(ob,'location',f'{z}+.38*sin(frame/79+{i})',2)
    drive(ob,'rotation_euler',f'frame/31+{i}',1);drive(ob,'rotation_euler',f'.8*sin(frame/19+{i})',2)

# School window: a torn curtain fragment moves independently of the rigid wall.
curtainmat=material('v016 | School curtain shadow',tone=(.12,.15,.16),alpha=.55)
curtain=grid('v016 | School torn curtain | upper edge pinned',41.15,9.85,2.13,.34,.65,curtainmat,C['wind'],8,16)
wind(curtain,.038,'cloth',2.7)

# Restrained distant flash and dusty expansion; no rapid repeated strobing.
for i,(t,x,y) in enumerate([(58.2,56,22),(73.1,71,25)]):
    m=softmat('v016 | Distant flash '+str(i),(1,.61,.26),.55)
    ob=grid('v016 | Distant light bloom '+str(i),x,y,2.9,9,6,m,C['light'],1,1)
    socket=m.node_tree.nodes['FX opacity'].inputs[1];keys(socket,[(0,0),(t-.15,0),(t,.75),(t+.45,.12),(t+1.4,0),(100,0)])

# Real extruded editable title, original block font installed on the user's machine.
titlemat=bpy.data.materials.new('v016 | Title | brush-grained weathered charcoal');titlemat.use_nodes=True
nt=titlemat.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.96
noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=9;noise.inputs['Detail'].default_value=4;noise.inputs['Roughness'].default_value=.8
ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.025,.037,.046,1);ramp.color_ramp.elements[1].color=(.15,.18,.19,1);nt.links.new(noise.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],bs.inputs['Base Color'])
bs.inputs['Emission Color'].default_value=(.021,.029,.035,1);bs.inputs['Emission Strength'].default_value=.7
bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.27;bump.inputs['Distance'].default_value=.035;nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],bs.inputs['Normal'])
font=bpy.data.curves.new('v016 | WHEN THE SKY CLEARS | editable text','FONT');font.body='WHEN THE SKY CLEARS';font.size=4;font.extrude=.24;font.bevel_depth=.025;font.bevel_resolution=2;font.space_character=1.03
font.font=bpy.data.fonts.load(r'C:\Windows\Fonts\ariblk.ttf')
try:font.font.pack()
except (AttributeError,RuntimeError):pass
title=bpy.data.objects.new('v016 | WHEN THE SKY CLEARS | monumental lettering',font);C['title'].objects.link(title);title.rotation_euler=(math.pi/2,0,0);title.location=(66,2.4,.15);font.materials.append(titlemat)
bpy.context.view_layer.update();coords=[Vector(c) for c in title.bound_box];width=max(p.x for p in coords)-min(p.x for p in coords);height=max(p.y for p in coords)-min(p.y for p in coords)
title.scale=(32/width,3.6/height,1)
title['purpose']='Real editable extruded lettering, resolved as the camera widens.'
for i,x in enumerate([67,70,73.4,76.8,80.5,84,87.2,90.8,95.3]):
    bpy.ops.mesh.primitive_cube_add(size=1,location=(x,2.0,.1));ob=bpy.context.object;ob.name='v016 | Broken title foundation '+str(i);ob.scale=(.65,.38,.16)
    for c in list(ob.users_collection):c.objects.unlink(ob)
    C['title'].objects.link(ob);ob.data.materials.append(titlemat)
    bevel=ob.modifiers.new('Weathered edge','BEVEL');bevel.width=.055;bevel.segments=2
lightdata=bpy.data.lights.new('v016 | Cold title side light','AREA');lightdata.energy=2300;lightdata.shape='DISK';lightdata.size=12
light=bpy.data.objects.new('v016 | Cold title side light',lightdata);C['light'].objects.link(light);light.location=(79,-5,10);light.rotation_euler=(Vector((82,2,2))-light.location).to_track_quat('-Z','Y').to_euler()

# Supplied music remains editable in the source timeline. Final mux uses this exact WAV.
seq=S.sequence_editor_create()
sound=seq.strips.new_sound('MUSIC | user supplied 100 seconds',str(ROOT/'edit/When_The_Sky_Clears_Trailer_Music_100s.wav'),channel=1,frame_start=1)
sound.sound.filepath='//../../edit/When_The_Sky_Clears_Trailer_Music_100s.wav'
sound.volume=1;sound.keyframe_insert('volume',frame=2161);sound.volume=0;sound.keyframe_insert('volume',frame=2400)
S.use_nodes=True;nt=bpy.data.node_groups.new('v016 | Final picture fade','CompositorNodeTree');S.compositing_node_group=nt;nt.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor')
rl=nt.nodes.new('CompositorNodeRLayers');out=nt.nodes.new('NodeGroupOutput');fade=nt.nodes.new('CompositorNodeExposure');nt.links.new(rl.outputs['Image'],fade.inputs['Image']);nt.links.new(fade.outputs['Image'],out.inputs['Image'])
keys(fade.inputs['Exposure'],[(0,0),(98,0)])
for f in range(2353,2401):
    fade.inputs['Exposure'].default_value=math.log2(max(2**-24,(2400-f)/47));fade.inputs['Exposure'].keyframe_insert('default_value',frame=f)
linear(nt.animation_data.action)
for marker in list(S.timeline_markers):S.timeline_markers.remove(marker)
for label,t in [('VILLAGE | warm painted depth',0),('ABANDONED VILLAGE',18),('WOODS | two wind layers',28),('SCHOOL',40),('CAMP | wind and smoke',52),('BATTLEFIELD',67),('TITLE TERRAIN',80),('MUSIC FADE',90),('FINAL WIDE',96),('PICTURE FADE',98)]:S.timeline_markers.new(label,frame=int(t*24)+1)
for text in bpy.data.texts:
    if text.name.startswith('START HERE'):text.clear();text.write('SUPERSEDED CHECKPOINT NOTES. Read START HERE v016.\n')
note=bpy.data.texts.new('START HERE v016 | Painted world trailer')
note.write('When the Sky Clears — painted world animation pass\n3840 x 2160, 24 fps, 2400 frames / 100 seconds.\n\nUser-directed continuation of the liked v015 village art direction. Held near-age painted children, with editable native GP boundary; no walking/acting animation.\n\nActual regional paintings at separate native depths, pinned canopy/cloth shape keys, localized painted window flicker and wall shadows, billowing alpha smoke, low drifting mist, fine grass, leaves/paper/ash, two distant restrained blooms, and editable extruded title. This is 2.5D painted set construction with 3D title geometry, not fully modeled architecture.\n\nRaster sources are primarily 1672 x 941; regional new bakery/path/character repaints and smoke are recorded in the manifest. Native output is UHD; source painting resolution and current artistic limits remain visible in zooms.\n\nMusic: user-supplied WAV under edit/. Fade 90–100 seconds, picture fade 98–100.\n\nThe exact older approved ink-and-wash image remains unavailable; the current direction is the one the user says they like. No claim of Arcane-level finish or finished character performance.\n\nAll earlier Blender sources are preserved. Source created from v015 in a separate process.\n')
S['scope']='Full 100-second animated painted world pass. Children held, object translation only.'
S['source_paint_limit']='Most base rasters 1672x941; native composite render 3840x2160.'
S['latest_user_direction']='Bring world details to life, retain painterly readable depth, near-age pair with slightly taller boy.'
S['art_status']='Work in progress world pass; no artistic acceptance inferred from rendering.'
S.render.filepath=str(ROOT/'renders/world_v016/WTSC_Painted_World_4K_v016.mp4')
S.frame_set(1)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
report={'source':str(OUT),'scene':S.name,'resolution':[3840,2160],'fps':24,'frames':2400,'duration_s':100,'objects':len(S.objects),'shape_key_objects':sum(1 for o in S.objects if o.type=='MESH' and o.data.shape_keys),'children':'Held single GP drawing and matching vector-clipped painted mesh; translation only','assets':[{'name':im.name,'size':list(im.size),'packed':bool(im.packed_file),'path':im.filepath} for im in bpy.data.images if im.source=='FILE'],'depth_bands':[-5,-4,-3,0,2,6,10,12,18,28,40],'motion':'Native mesh shape keys and drivers, smoke advection, localized light masks, leaf/paper/ash drift, layered haze, lateral camera, end pullback','limitations':['2.5D painted architecture, not fully modeled buildings','Source painting resolution below output UHD','Held children per user, gait/acting deferred','Artistic finish still subject to review']}
(ROOT/'notes/world_v016/native_build.json').write_text(json.dumps(report,indent=2))
print('PAINTED_WORLD_SOURCE_SAVED',json.dumps({k:v for k,v in report.items() if k!='assets'}),flush=True)
