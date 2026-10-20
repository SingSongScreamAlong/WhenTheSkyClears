"""Continuous native outlines. Original paint fills geometry; it never defines it.
Absolute shape keys carry vertex identities through every frame, no pose alpha blends.
"""
import bpy,bmesh,math,random,json,hashlib,struct,re
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parents[1]
s=bpy.data.scenes['FX_PROOF_v006 | painted impulse depth tracers and ground'];bpy.context.window.scene=s
old_comp=s.compositing_node_group
bg=next(n.image for n in old_comp.nodes if n.type=='IMAGE' and n.image.size[0]==3840)
fg=next(n.image for n in old_comp.nodes if n.type=='IMAGE' and 'Native_Foreground_Alpha' in n.image.name)
depth=next(n.image for n in old_comp.nodes if n.type=='IMAGE' and 'Native_Depth_Alpha_Y10_' in n.image.name)
atlas=next(im for im in bpy.data.images if im.name.startswith('FXv003 | ORIGINAL four cold forms'))
helper=bpy.data.node_groups['FXv006 | HDR FX bloom over | append helper'].copy();helper.name='FXv008 | FX-only restrained bloom over'
for col in list(s.collection.children):s.collection.children.unlink(col)
for ob in list(s.collection.objects):
    if ob!=s.camera:s.collection.objects.unlink(ob)
for layer in list(s.view_layers)[1:]:s.view_layers.remove(layer)
s.view_layers[0].name='ONE_COHERENT_BLAST';s.name='FXv008 | coherent silhouette validation'
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=24;s.render.threads_mode='FIXED';s.render.threads=2
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.fps=24;s.frame_start=1818;s.frame_end=1937
s.render.film_transparent=True;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.media_type='IMAGE'
s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0;s.view_settings.gamma=1
if hasattr(s.render,'compositor_device'):s.render.compositor_device='GPU'
asset=bpy.data.collections.new('FXv008 | ONE COHERENT NATIVE BLAST');s.collection.children.link(asset)
def point_for_screen(u,v,y):
    c=s.camera.matrix_world.translation;b=world_to_camera_view(s,s.camera,Vector((c.x,y,c.z)));px=world_to_camera_view(s,s.camera,Vector((c.x+1,y,c.z)));pz=world_to_camera_view(s,s.camera,Vector((c.x,y,c.z+1)))
    return Vector((c.x+(u-b.x)/(px.x-b.x),y,c.z+(v-b.y)/(pz.y-b.y)))
root=bpy.data.objects.new('FXv008 | fixed world impact and controls',None);asset.objects.link(root);root.location=point_for_screen(.78,.323,10);root.empty_display_type='CIRCLE';root.empty_display_size=.15
for key,value in {'start_frame':1824.,'speed':1.,'size':1.,'intensity':1.,'painted':0.,'age':0.,'light_envelope':0.}.items():root[key]=value
root['motion_method']='132 per-frame absolute native shape keys, persistent vertex IDs, connected outlines; no raster pose crossfades or cel/card scaling.'
def driver(owner,path,expression,index=None):
    f=owner.driver_add(path) if index is None else owner.driver_add(path,index);f.driver.type='SCRIPTED'
    for var in list(f.driver.variables):f.driver.variables.remove(var)
    for name,key in [('t','age'),('I','intensity'),('P','painted'),('L','light_envelope'),('S','size')]:
        if not re.search(r'\b'+name+r'\b',expression):continue
        v=f.driver.variables.new();v.name=name;v.type='SINGLE_PROP';v.targets[0].id=root;v.targets[0].data_path='["'+key+'"]'
    f.driver.expression=expression;return f
f=root.driver_add('["age"]');f.driver.expression='(frame-start)*speed'
for name,key in [('start','start_frame'),('speed','speed')]:
    v=f.driver.variables.new();v.name=name;v.type='SINGLE_PROP';v.targets[0].id=root;v.targets[0].data_path='["'+key+'"]'
for axis in range(3):driver(root,'scale','max(.01,S)',axis)
driver(root,'["light_envelope"]','I*max(0,min(1,(t+.25)/.25))*exp(-max(0,t)/1.8)*max(0,min(1,(5-t)/2))')
TIMES=[0,1,2,3,5,8,12,18,24,32,44,60,84,114,132]
def curve(t,values,times=TIMES):
    if t<=times[0]:return values[0]
    if t>=times[-1]:return values[-1]
    j=next(i for i in range(len(times)-1) if times[i]<=t<times[i+1]);h=times[j+1]-times[j];u=(t-times[j])/h
    def slope(i):
        if i==0:return (values[1]-values[0])/(times[1]-times[0])
        if i==len(times)-1:return 0.
        a=(values[i]-values[i-1])/(times[i]-times[i-1]);b=(values[i+1]-values[i])/(times[i+1]-times[i])
        return 0. if a*b<=0 else 2*a*b/(a+b)
    return (2*u**3-3*u*u+1)*values[j]+(u**3-2*u*u+u)*h*slope(j)+(-2*u**3+3*u*u)*values[j+1]+(u**3-u*u)*h*slope(j+1)
def wrap(a):return (a+math.pi)%(2*math.pi)-math.pi
def material(name,color,alpha='I if t>=0 else 0',tile=0,hot=False):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.surface_render_method='BLENDED';nt=m.node_tree;nt.nodes.clear()
    uv=nt.nodes.new('ShaderNodeTexCoord');scale=nt.nodes.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(.38,.38,1);nt.links.new(uv.outputs['UV'],scale.inputs[0]);offset=nt.nodes.new('ShaderNodeVectorMath');offset.operation='ADD';offset.inputs[1].default_value=((tile%2)*.5+.06,(1-tile//2)*.5+.06,0);nt.links.new(scale.outputs['Vector'],offset.inputs[0]);tex=nt.nodes.new('ShaderNodeTexImage');tex.image=atlas;tex.extension='CLIP';nt.links.new(offset.outputs['Vector'],tex.inputs[0])
    hsv=nt.nodes.new('ShaderNodeHueSaturation');hsv.inputs['Saturation'].default_value=.15;hsv.inputs['Value'].default_value=.90;nt.links.new(tex.outputs['Color'],hsv.inputs['Color']);tint=nt.nodes.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1;tint.inputs[2].default_value=(.72,.77,.83,1);nt.links.new(hsv.outputs[0],tint.inputs[1])
    # Original alpha controls pigment contribution only, NEVER the silhouette.
    pigment=nt.nodes.new('ShaderNodeMath');pigment.operation='MULTIPLY';pigment.inputs[1].default_value=.82;nt.links.new(tex.outputs['Alpha'],pigment.inputs[0]);fill=nt.nodes.new('ShaderNodeMixRGB');fill.inputs[1].default_value=(*color,1);nt.links.new(pigment.outputs[0],fill.inputs[0]);nt.links.new(tint.outputs[0],fill.inputs[2]);mode=nt.nodes.new('ShaderNodeMixRGB');mode.name='Paint changes COLOR ONLY';mode.inputs[1].default_value=(*color,1);nt.links.new(fill.outputs[0],mode.inputs[2]);driver(mode.inputs[0],'default_value','P')
    e=nt.nodes.new('ShaderNodeEmission');nt.links.new(mode.outputs[0],e.inputs['Color'])
    if 'receiver' in name:
        nt.links.remove(e.inputs['Color'].links[0]);e.inputs['Color'].default_value=(*color,1)
    if 'rollover shadow' in name:
        shade=nt.nodes.new('ShaderNodeMixRGB');shade.blend_type='MULTIPLY';shade.inputs[0].default_value=1;shade.inputs[2].default_value=(.52,.52,.52,1);nt.links.new(mode.outputs[0],shade.inputs[1]);nt.links.new(shade.outputs[0],e.inputs['Color'])
    if hot:
        e.inputs['Color'].default_value=(.9,.9,.9,1);nt.links.remove(e.inputs['Color'].links[0]);warm=nt.nodes.new('ShaderNodeMixRGB');warm.inputs[1].default_value=(.7,.7,.7,1);warm.inputs[2].default_value=(1,.58,.18,1);driver(warm.inputs[0],'default_value','P');nt.links.new(warm.outputs[0],e.inputs['Color']);driver(e.inputs['Strength'],'default_value','1+2.2*P*L')
    edge=nt.nodes.new('ShaderNodeAttribute');edge.attribute_name='FX_edge';feather=nt.nodes.new('ShaderNodeMapRange');feather.clamp=True;feather.inputs['From Min'].default_value=0;feather.inputs['From Max'].default_value=.045;nt.links.new(edge.outputs['Fac'],feather.inputs['Value']);a=nt.nodes.new('ShaderNodeMath');a.name='Same coverage in silhouette and paint';a.operation='MULTIPLY';nt.links.new(feather.outputs[0],a.inputs[0]);driver(a.inputs[1],'default_value',alpha)
    tr=nt.nodes.new('ShaderNodeBsdfTransparent');mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(a.outputs[0],mix.inputs[0]);nt.links.new(tr.outputs[0],mix.inputs[1]);nt.links.new(e.outputs[0],mix.inputs[2]);out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(mix.outputs[0],out.inputs[0]);return m
M={
 'left':material('FXv008 | left coherent mass',(.055,.060,.062),'I*max(0,min(1,(128-t)/64)) if t>=0 else 0',0),
 'right':material('FXv008 | right coherent mass',(.038,.043,.046),'I*max(0,min(1,(124-t)/62)) if t>=0 else 0',1),
 'core':material('FXv008 | dense ground-connected body',(.028,.032,.034),'I*max(0,min(1,(108-t)/48)) if t>=0 else 0',2),
 'dust':material('FXv008 | connected front dust',(.095,.098,.095),'I*.88*max(0,min(1,(116-t)/52)) if t>=0 else 0',3),
 'fold':material('FXv008 | tracked rollover shadow',(.019,.023,.026),'I*(.28+.35*P)*max(0,min(1,(92-t)/32)) if t>=2 else 0',2),
 'flash':material('FXv008 | compact torn impulse flash',(.7,.7,.7),'max(0,min(1,(4-t)/2)) if t>=0 else 0',0,True),
 'scar':material('FXv008 | persistent gouge pigment',(.018,.017,.015),'I*.92*max(0,min(1,(t-1)/3))',3)}
N=64;RINGS=5
def topology(n=N,rings=RINGS):
    uv=[(.5,.5)];edges=[1.];faces=[]
    for ring in range(1,rings+1):
        u=ring/rings
        for i in range(n):a=2*math.pi*i/n;uv.append((.5+.46*u*math.cos(a),.5+.46*u*math.sin(a)));edges.append(1-u)
    for i in range(n):faces.append((0,1+i,1+(i+1)%n))
    for ring in range(1,rings):
        a=1+(ring-1)*n;b=1+ring*n
        for i in range(n):j=(i+1)%n;faces.append((a+i,b+i,b+j,a+j))
    return uv,edges,faces
geom_records=[];motion_samples={}
def animated_mesh(name,fn,mat,n=N,rings=RINGS,y=0,custom=None):
    uv,edge,faces=custom if custom else topology(n,rings);points=fn(0,n,rings);mesh=bpy.data.meshes.new(name);mesh.from_pydata([(x,y,z) for x,z in points],[],faces);mesh.materials.append(mat);mesh.update();layer=mesh.uv_layers.new(name='Advected paint coordinates')
    for loop in mesh.loops:layer.data[loop.index].uv=uv[loop.vertex_index]
    attr=mesh.attributes.new('FX_edge','FLOAT','POINT')
    for i,value in enumerate(edge):attr.data[i].value=value
    ob=bpy.data.objects.new(name,mesh);asset.objects.link(ob);ob.parent=root;keys=[]
    for age in range(133):
        k=ob.shape_key_add(name=f'AGE_{age:03d}');k.interpolation='KEY_LINEAR';pts=points if age==0 else fn(age,n,rings)
        for index,(x,z) in enumerate(pts):k.data[index].co=(x,y,z)
        keys.append(k)
        if age in [0,1,2,3,5,8,12,18,24,32,44,60,84,114]:
            if name not in motion_samples:motion_samples[name]=[]
            motion_samples[name].append({'age':age,'centroid':list(pts[0]),'bounds':[min(p[0] for p in pts),min(p[1] for p in pts),max(p[0] for p in pts),max(p[1] for p in pts)]})
    mesh.shape_keys.use_relative=False;assert max(abs(k.frame-i*10) for i,k in enumerate(keys))<.01
    driver(mesh.shape_keys,'eval_time','10*max(0,min(132,t))');ob['motion']='Continuous native vertex interpolation; no image-pose or alpha crossfades';ob['persistent_vertex_ids']=True
    geom_records.append({'name':name,'vertices':len(points),'faces':len(faces),'absolute_keys':len(keys),'uv_advected_with_mesh':True});return ob
LEFT={
 'x':[0,-.18,-.36,-.52,-.68,-.76,-.80,-.84,-.88,-.93,-.99,-1.04,-1.07,-1.09,-1.1],
 'z':[.03,.26,.58,.88,1.17,1.31,1.35,1.30,1.18,.98,.72,.54,.44,.36,.32],
 'rx':[.018,.15,.30,.43,.62,.73,.78,.83,.88,.94,.98,.98,.96,.88,.80],
 'rz':[.018,.20,.35,.48,.65,.76,.80,.83,.84,.82,.74,.64,.54,.46,.40]}
RIGHT={
 'x':[0,.13,.25,.38,.53,.66,.73,.79,.83,.87,.92,.97,1.00,1.02,1.03],
 'z':[.025,.16,.34,.54,.77,.94,1.00,.96,.84,.69,.50,.36,.28,.22,.18],
 'rx':[.016,.13,.24,.34,.49,.62,.68,.73,.79,.84,.88,.91,.90,.83,.76],
 'rz':[.016,.13,.27,.36,.50,.62,.66,.69,.70,.67,.60,.49,.39,.30,.24]}
CORE={
 'x':[0,.01,.02,.02,.03,.04,.06,.08,.10,.12,.14,.16,.18,.20,.21],
 'z':[.02,.13,.27,.37,.46,.50,.49,.44,.37,.29,.21,.16,.12,.08,.06],
 'rx':[.025,.22,.39,.52,.65,.77,.87,.95,1.01,1.08,1.12,1.14,1.16,1.18,1.19],
 'rz':[.02,.16,.30,.39,.49,.57,.62,.65,.65,.58,.47,.36,.26,.18,.14]}
def mass_state(t,spec):return {key:curve(t,values) for key,values in spec.items()}
def mass_fn(spec,side=1,seed=0):
    def sample(t,n,rings):
        st=mass_state(t,spec);turn=side*curve(t,[0,0,.02,.05,.14,.30,.53,.87,1.17,1.48,1.73,1.90,2.02,2.10,2.12]);notch=curve(t,[0,0,0,.01,.025,.08,.15,.24,.30,.34,.28,.22,.16,.11,.08]);feature=(math.pi*.65 if side>0 else math.pi*.35)+turn*.7
        c=(st['x'],max(.02,st['z']));out=[c]
        for ring in range(1,rings+1):
            u=ring/rings
            for i in range(n):
                a=2*math.pi*i/n;angle=a+.14*turn*(1-u)**2
                rough=1+.085*math.sin(5*a+seed+.45*turn)+.045*math.sin(9*a-seed+.22*turn)+.022*math.cos(17*a+seed)
                folded=1-notch*math.exp(-(wrap(a-feature)/.36)**2)+.13*math.exp(-(wrap(a-feature-.65)/.43)**2)
                x=c[0]+u*st['rx']*rough*folded*math.cos(angle)
                z=c[1]+u*st['rz']*rough*folded*math.sin(angle)
                # Early directional soil spikes soften into new rolling contours.
                spike=max(0,1-t/7)*.11*min(st['rx'],st['rz'])*u**3*max(0,math.sin(a))**4*math.sin(7*a+seed)
                x+=spike*side*.45;z+=spike
                if z<.006:
                    hit=(c[1]-.006)/(c[1]-z);x=c[0]+(x-c[0])*hit;z=.006
                out.append((x,z))
        return out
    return sample
left=animated_mesh('FXv008 | tracked LEFT pressure mass',mass_fn(LEFT,1,.4),M['left'],y=.06)
right=animated_mesh('FXv008 | tracked RIGHT pressure mass',mass_fn(RIGHT,-1,2.1),M['right'],y=.035)
core=animated_mesh('FXv008 | connected descending ground body',mass_fn(CORE,1,4.0),M['core'],y=.01)
def fold_fn(spec,side):
    def sample(t,n,rings):
        st=mass_state(t,spec);angle=curve(t,[0,0,.02,.05,.12,.26,.45,.69,.92,1.15,1.32,1.40,1.45,1.48,1.50]);out=[];c=(st['x'],max(.03,st['z']))
        for row in range(rings+1):
            u=row/rings
            for i in range(n+1):
                v=i/n;q=.16*math.pi+1.16*math.pi*v+angle
                if side<0:q=math.pi-q
                taper=math.sin(math.pi*v)**.65;radial=.56+.10*math.sin(math.pi*v)+(u-.5)*.15*taper
                x=c[0]+st['rx']*radial*math.cos(q);z=c[1]+st['rz']*radial*math.sin(q)
                if z<.009:
                    hit=(c[1]-.009)/(c[1]-z);x=c[0]+(x-c[0])*hit;z=.009
                out.append((x,z))
        return out
    return sample
def fold_topology(n=48,rows=3):
    uv=[];edge=[];faces=[]
    for row in range(rows+1):
        u=row/rows
        for i in range(n+1):
            v=i/n;q=.16*math.pi+1.16*math.pi*v;r=.56+(u-.5)*.15;uv.append((.5+.46*r*math.cos(q),.5+.46*r*math.sin(q)));edge.append(min(u,1-u,v,1-v)*3)
    for row in range(rows):
        for i in range(n):a=row*(n+1)+i;b=a+n+1;faces.append((a,b,b+1,a+1))
    return uv,edge,faces
animated_mesh('FXv008 | LEFT rollover fold',fold_fn(LEFT,1),M['fold'],n=48,rings=3,y=-.01,custom=fold_topology())
animated_mesh('FXv008 | RIGHT rollover fold',fold_fn(RIGHT,-1),M['fold'],n=48,rings=3,y=-.025,custom=fold_topology())
def dust_fn(t,n,rings):
    left=curve(t,[.04,.20,.48,.77,1.22,1.56,1.74,1.83,1.88,1.92,1.95,1.97,1.98,1.99,2.0]);right=left*.87;height=curve(t,[.025,.16,.28,.36,.43,.40,.33,.27,.22,.17,.12,.085,.055,.03,.02]);c=((right-left)*.20,max(.012,height*.25));out=[c]
    for ring in range(1,rings+1):
        u=ring/rings
        for i in range(n):
            a=2*math.pi*i/n;x=math.cos(a)*(right if math.cos(a)>0 else left)
            z=max(.003,height*(.24+.76*max(0,math.sin(a)))*(1+.20*math.sin(5*a+t*.012))) if math.sin(a)>=0 else .003
            out.append((c[0]+u*(x-c[0]),c[1]+u*(z-c[1])))
    return out
animated_mesh('FXv008 | connected spreading settling FRONT DUST',dust_fn,M['dust'],n=64,rings=3,y=-.16)
def flash_fn(t,n,rings):
    w=curve(t,[.16,.31,.38,.32,.10,0,0,0,0,0,0,0,0,0,0]);h=curve(t,[.22,.44,.37,.18,.01,0,0,0,0,0,0,0,0,0,0]);c=(0,max(.01,h*.32));out=[c]
    for ring in range(1,rings+1):
        u=ring/rings
        for i in range(n):
            a=2*math.pi*i/n;spike=1+.26*math.cos(7*a)+.16*math.sin(11*a+.4);out.append((u*w*math.cos(a)*spike,max(.003,c[1]+u*h*math.sin(a)*spike)))
    return out
animated_mesh('FXv008 | compact torn ground impulse',flash_fn,M['flash'],n=48,rings=3,y=-.22)
# Shallow fixed scar: irregular filled profile rather than a horizontal image slab.
def scar_fn(t,n,rings):
    c=(0,.018);out=[c]
    for ring in range(1,rings+1):
        u=ring/rings
        for i in range(n):
            a=2*math.pi*i/n;r=1+.09*math.sin(7*a)+.05*math.sin(13*a);out.append((u*.69*math.cos(a)*r,.018+u*.045*math.sin(a)*r))
    return out
scar=animated_mesh('FXv008 | persistent irregular ground gouge',scar_fn,M['scar'],n=48,rings=2,y=-.40);scar['persistent']=True
# Independent chunky trajectories, tumbling stops at contact, readable landing puffs.
rng=random.Random(810);debris=[]
chipmat=material('FXv008 | charcoal tumbling debris',(.026,.025,.023),'I if t>=0 else 0',3)
for i,(vx,vz,birth,radius) in enumerate([(-1.9,5.3,0,.044),(-1.15,4.3,1,.035),(-.50,5.7,0,.051),(.40,4.9,2,.041),(1.25,5.8,1,.052),(2.05,4.7,0,.044),(1.65,3.8,3,.032),(-1.65,4.1,2,.035)]):
    mesh=bpy.data.meshes.new(f'FXv008 chip{i}');bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=1,radius=radius)
    for v in bm.verts:v.co.x*=rng.uniform(.7,1.3);v.co.y*=.45;v.co.z*=rng.uniform(.65,1.4)
    bm.to_mesh(mesh);bm.free();mesh.materials.append(chipmat);edge=mesh.attributes.new('FX_edge','FLOAT','POINT')
    for d in edge.data:d.value=1.
    ob=bpy.data.objects.new(f'FXv008 | tumbling chunk {i:02d}',mesh);asset.objects.link(ob);ob.parent=root;ob.location.y=-.45
    flight=2*vz/12;u=f'max(0,t-{birth})/24';limited=f'min({flight},{u})';land_x=vx*flight*math.exp(-.10*flight);land_age=birth+flight*24
    driver(ob,'location',f'{vx}*({limited})*exp(-.1*({limited}))',0);driver(ob,'location',f'{radius*.65}+max(0,{vz}*({u})-6*({u})**2)',2)
    for axis in range(3):driver(ob,'rotation_euler',f'{rng.uniform(-2,2)}+{rng.uniform(-9,9)}*({limited})',axis);driver(ob,'scale',f'1 if t>={birth} else 0',axis)
    debris.append({'piece':i,'birth':birth,'apex_age':birth+vz/12*24,'landing_age':land_age,'landing_x':land_x,'radius':radius})
    if i in [1,3,4,5]:
        mat=material(f'FXv008 | landing puff{i}',(.10,.105,.10),f'I*.75*max(0,min(1,(t-{land_age})/.75,({land_age+11}-t)/8))',3)
        def puff_fn(t,n,rings,land_age=land_age,land_x=land_x):
            a=max(0,t-land_age);w=curve(a,[.01,.10,.18,.24,.28,.30,.31,.31],[0,1,2,3,5,8,11,132]);h=curve(a,[.01,.08,.13,.12,.08,.03,.005,.005],[0,1,2,3,5,8,11,132]);c=(land_x,max(.012,h*.3));out=[c]
            for ring in range(1,rings+1):
                u=ring/rings
                for j in range(n):
                    q=2*math.pi*j/n;r=1+.12*math.sin(5*q+a*.03);out.append((c[0]+u*w*math.cos(q)*r,max(.003,c[1]+u*h*math.sin(q)*r)))
            return out
        animated_mesh(f'FXv008 | connected landing puff{i}',puff_fn,mat,n=32,rings=2,y=-.49)
# Local ground receiver wash, active only in the painted stage. Same source impulse.
lightmat=material('FXv008 | synchronized local receiver',(.45,.20,.04),'.16*P*L',3)
def light_fn(t,n,rings):
    c=(0,.07);out=[c]
    for ring in range(1,rings+1):
        u=ring/rings
        for i in range(n):a=2*math.pi*i/n;out.append((u*1.05*math.cos(a),.07+u*.19*math.sin(a)))
    return out
animated_mesh('FXv008 | local light receiver footprint',light_fn,lightmat,n=40,rings=3,y=.23)
nt=bpy.data.node_groups.new('FXv008 | fixed shot proof','CompositorNodeTree');nt.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor');s.compositing_node_group=nt
bn=nt.nodes.new('CompositorNodeImage');bn.image=bg;scale=nt.nodes.new('CompositorNodeScale');scale.inputs['X'].default_value=.5;scale.inputs['Y'].default_value=.5;nt.links.new(bn.outputs['Image'],scale.inputs['Image']);layer=nt.nodes.new('CompositorNodeRLayers');layer.scene=s;layer.layer='ONE_COHERENT_BLAST';a=nt.nodes.new('CompositorNodeImage');a.image=fg;b=nt.nodes.new('CompositorNodeImage');b.image=depth;maximum=nt.nodes.new('ShaderNodeMath');maximum.operation='MAXIMUM';nt.links.new(a.outputs['Alpha'],maximum.inputs[0]);nt.links.new(b.outputs['Alpha'],maximum.inputs[1]);over=nt.nodes.new('CompositorNodeGroup');over.node_tree=helper;nt.links.new(layer.outputs['Image'],over.inputs['Foreground']);nt.links.new(scale.outputs[0],over.inputs['Background']);nt.links.new(maximum.outputs[0],over.inputs['Occluder']);driver(over.inputs['Bloom gain'],'default_value','.16*P');out=nt.nodes.new('NodeGroupOutput');nt.links.new(over.outputs[0],out.inputs['Image'])
def geometry_hash():
    h=hashlib.sha256()
    for ob in sorted(asset.all_objects,key=lambda o:o.name):
        if ob.type!='MESH':continue
        h.update(ob.name.encode())
        if ob.data.shape_keys:
            for key in ob.data.shape_keys.key_blocks:
                for p in key.data:h.update(struct.pack('<fff',*p.co))
        else:
            for p in ob.data.vertices:h.update(struct.pack('<fff',*p.co))
    return h.hexdigest()
s.frame_set(1827);bpy.context.view_layer.update();invalid=[]
for ob in asset.all_objects:
    assert ob.type not in {'LIGHT','CAMERA'}
    for owner in [ob]+([ob.data.shape_keys] if ob.type=='MESH' and ob.data.shape_keys else [])+([m.node_tree for m in ob.data.materials] if ob.type=='MESH' else []):
        if owner.animation_data:invalid.extend([owner.name,f.data_path] for f in owner.animation_data.drivers if not f.driver.is_valid)
assert not invalid,invalid
signature=geometry_hash();asset['geometry_sha256']=signature
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Coherent_Silhouette_v008.blend'),compress=True)
report={'scene':s.name,'blender':bpy.app.version_string,'fps':24,'frames':[1818,1937],'pixels':[1920,1080],'engine':'BLENDER_EEVEE','samples':24,'root':list(root.location),'screen_origin':list(world_to_camera_view(s,s.camera,root.location)),'objects':len(asset.all_objects),'geometry':geom_records,'geometry_sha256':signature,'invalid_drivers':invalid,'debris':debris,'motion_samples':motion_samples,'painted':False,'native_absolute_keys':True,'raster_pose_crossfades':False,'mature_cloud_card_scaling':False,'new_simulation':False,'reused_paint_image':atlas.name,'source_file_untouched':True,'status':'Await actual silhouette render review before enabling paint.'}
(P/'evidence/build_coherent.json').write_text(json.dumps(report,indent=2));print('COHERENT_NATIVE_BUILT',json.dumps({k:v for k,v in report.items() if k not in ['motion_samples','geometry','debris']}),flush=True)
