"""Correct actual v019 motion causes; retain world depth and the held pair."""
import bpy,math,sys,json
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE')
sys.path.insert(0,str(R/'scripts'))
from village_still_refinements_v014 import detail_tile
s=bpy.context.scene;assert s.name=='WTSC_PAINTED_WORLD_4K_100S_v022'
target=R/'shots/world/WTSC_Painted_World_Trailer_v023.blend';assert not target.exists()
s.name='WTSC_PAINTED_WORLD_4K_100S_v023'

def mathn(nt,op,a,b):
    n=nt.nodes.new('ShaderNodeMath');n.operation=op
    for i,v in enumerate([a,b]):
        if isinstance(v,(int,float)):n.inputs[i].default_value=v
        else:nt.links.new(v,n.inputs[i])
    return n.outputs[0]
def remap(nt,a,a0,a1,b0,b1):
    n=nt.nodes.new('ShaderNodeMapRange');n.clamp=True;n.interpolation_type='SMOOTHERSTEP'
    for name,v in [('From Min',a0),('From Max',a1),('To Min',b0),('To Max',b1)]:n.inputs[name].default_value=v
    nt.links.new(a,n.inputs[0]);return n.outputs[0]

# ONE physical surface owns the opening oak, its roots, fence and their painted path.
# It keeps the exact first-view framing, with root/trunk/ground at the same depth.
oldpath=s.objects['v015 | Walking path'];bpy.data.objects.remove(oldpath,do_unlink=True)
oak=s.objects['v015 | Oak frame and near bank'];oak.location.y=2;oak.scale=(18/11,18/11,18/11)
oak.name='v023 | Opening oak roots fence and path | one coherent surface'
oak['coherence']='Complete connected painted oak/fence/path at Y=2. No tree split over Y=-5 and Y=2.'
nt=oak.data.materials[0].node_tree;tex=next(n for n in nt.nodes if n.type=='TEX_IMAGE');sep=next(n for n in nt.nodes if n.type=='SEPXYZ');mix=next(n for n in nt.nodes if n.type=='MIX_SHADER')
alpha=remap(nt,tex.outputs['Alpha'],.025,.98,0,1)
# Foreground bank is a separate continuous surface; the opaque footer is feathered away here.
alpha=mathn(nt,'MULTIPLY',alpha,remap(nt,sep.outputs['Y'],.018,.065,0,1))
alpha=mathn(nt,'MULTIPLY',alpha,remap(nt,sep.outputs['X'],0,.022,0,1))
alpha=mathn(nt,'MULTIPLY',alpha,remap(nt,sep.outputs['X'],.978,1,1,0))
nt.links.new(alpha,mix.inputs[0])
detail_tile(oak,R/'sets/village_lookdev/v014/Path_Detail_Repaint.png',[.25,.46,.06,.22],'v023 | Path repaint locked to whole oak-ground surface')

# Restrict village wind to upper foliage. All facades, roofs, chimneys and the registered bakery stay rigid.
village=s.objects['v015 | Painted village'];base=village.data.shape_keys.key_blocks[0]
uvs={loop.vertex_index:village.data.uv_layers.active.data[loop.index].uv.copy() for loop in village.data.loops}
for key in list(village.data.shape_keys.key_blocks)[1:]:
    for i,p in enumerate(key.data):
        u,v=uvs[i]
        if v<.65 or .32<=u<=.67:p.co=base.data[i].co.copy()

# Stationary real-depth countryside. Initial framing is preserved by proportional depth/scale.
rear=s.objects['v015 | Rear countryside'];rear.animation_data_clear();rear.location=(0,120,3);rear.scale=(136/56,)*3
rear.name='v023 | Distant countryside | fixed world space'
nt=rear.data.materials[0].node_tree;tex=next(n for n in nt.nodes if n.type=='TEX_IMAGE');uv=next(n for n in nt.nodes if n.type=='TEX_COORD')
if tex.inputs['Vector'].is_linked:
    offset=tex.inputs['Vector'].links[0].from_node
    if offset.type=='VECT_MATH':
        try:offset.inputs[1].driver_remove('default_value',0)
        except (TypeError,RuntimeError):pass
        nt.nodes.remove(offset)
nt.links.new(uv.outputs['UV'],tex.inputs['Vector'])
sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(uv.outputs['UV'],sep.inputs[0])
alpha=mathn(nt,'MULTIPLY',tex.outputs['Alpha'],remap(nt,sep.outputs['X'],0,.075,0,1))
alpha=mathn(nt,'MULTIPLY',alpha,remap(nt,sep.outputs['X'],.925,1,1,0))
alpha=mathn(nt,'MULTIPLY',alpha,remap(nt,sep.outputs['Y'],.86,1,1,0))
mix=next(n for n in nt.nodes if n.type=='MIX_SHADER');nt.links.new(alpha,mix.inputs[0]);rear.data.materials[0].surface_render_method='BLENDED'
rear['motion']='Fixed world-space landscape at Y=120. No camera-follow keys, no drifting landscape UV.'
width=40.32*136/56
for i in [-1,1,2]:
    ob=rear.copy();ob.animation_data_clear();ob.name='v023 | Distant landscape continuation '+str(i);s.collection.objects.link(ob);ob.location.x=i*width*.84;ob.location.y=120+abs(i)*.002

# Far sky overscan. Only clouds drift; the landscape stays fixed to the world.
m=bpy.data.materials.new('v023 | Far painted sky and cloud drift');m.use_nodes=True;nt=m.node_tree;nt.nodes.clear()
tex=nt.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(R/'sets/painted_layers/Sky_Painted_v001.png'),check_existing=True);tex.image.pack();tex.extension='EXTEND'
uv=nt.nodes.new('ShaderNodeTexCoord');offset=nt.nodes.new('ShaderNodeVectorMath');offset.operation='ADD';nt.links.new(uv.outputs['UV'],offset.inputs[0]);nt.links.new(offset.outputs[0],tex.inputs['Vector']);f=offset.inputs[1].driver_add('default_value',0);f.driver.expression='frame*.0000015'
hsv=nt.nodes.new('ShaderNodeHueSaturation');nt.links.new(tex.outputs['Color'],hsv.inputs['Color'])
cool=nt.nodes.new('ShaderNodeMixRGB');cool.blend_type='MULTIPLY';cool.inputs[2].default_value=(.65,.81,1,1);nt.links.new(hsv.outputs[0],cool.inputs[1])
for t,sat,cold in [(0,1,0),(18,.85,.08),(42,.66,.38),(67,.46,.85),(80,.28,1),(100,.25,1)]:
    frame=min(2400,t*24+1);hsv.inputs['Saturation'].default_value=sat;hsv.inputs['Saturation'].keyframe_insert('default_value',frame=frame);cool.inputs[0].default_value=cold;cool.inputs[0].keyframe_insert('default_value',frame=frame)
em=nt.nodes.new('ShaderNodeEmission');nt.links.new(cool.outputs[0],em.inputs[0]);out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],out.inputs[0])
d=bpy.data.meshes.new('v023 | Far sky overscan');d.from_pydata([(-220,260,-70),(380,260,-70),(380,260,110),(-220,260,110)],[],[(0,1,2,3)]);d.materials.append(m);d.update();uvlayer=d.uv_layers.new(name='Sky paint UV')
for loop,co in zip(uvlayer.data,[(0,0),(1,0),(1,1),(0,1)]):loop.uv=co
sky=bpy.data.objects.new('v023 | Sky | fixed depth, drifting clouds only',d);s.collection.objects.link(sky)

for text in bpy.data.texts:
    if text.name.startswith('START HERE v022'):
        value=text.as_string().replace('v022','v023')+'\nMotion correction after user feedback: opening oak, roots, fence and path share one Y=2 painted mesh; registered path repaint uses that mesh UV. Countryside is fixed at real depth Y=120 with world-space continuation paintings. Only the separate sky carries cloud drift. Near bank remains a distinct continuous surface at Y=-4.99. Architecture is excluded from canopy wind. Children remain held.\n'
        text.name='START HERE v023 | Painted world trailer';text.clear();text.write(value)
s['motion_coherence']='Corrected split oak/root depths and screen-locked rear countryside. All rigid sets fixed in world space; camera supplies parallax.'
s.render.filepath=str(R/'renders/world_v016/WTSC_Painted_World_4K_v023.mp4');s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
out=R/'renders/world_v016/inspection_v023';out.mkdir(exist_ok=True)
s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
for name,f in [('01_village',1),('02_woods',721),('03_school',1057),('04_camp',1417),('05_battlefield',1777),('06_title',2305)]:
    s.frame_set(f);s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);print('V023_REVIEW',name,f,flush=True)
