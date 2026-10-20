import bpy,math,json
from pathlib import Path
ROOT=Path(r'WTSC_LOCAL_WORKSPACE')
scene=bpy.context.scene
assert scene.name=='WTSC_WORLD_FIRST_4K'
for obj in scene.objects:
    if obj.name.startswith(('Far hill band','Grass clump','Stone fragment','Transition tree trunk','Transition branch','Transition twig')):
        obj.hide_render=True;obj.hide_viewport=True;obj['status']='Superseded layout guide; hidden from render'

def matcopy(name,image):
    mat=bpy.data.materials['Village B | same village abandoned paint'].copy();mat.name=name
    im=bpy.data.images.load(str(ROOT/'sets/painted_layers'/image),check_existing=True);im.pack();im.alpha_mode='STRAIGHT';im.filepath='//../../sets/painted_layers/'+image
    for n in mat.node_tree.nodes:
        if n.type=='TEX_IMAGE':n.image=im
    return mat

def plane(name,x,y,z,w,h,material,collection,uvs=None):
    me=bpy.data.meshes.new(name);me.from_pydata([(x-w/2,y,z),(x+w/2,y,z),(x+w/2,y,z+h),(x-w/2,y,z+h)],[],[(0,1,2,3)]);me.update()
    ob=bpy.data.objects.new(name,me);collection.objects.link(ob);me.materials.append(material)
    uv=me.uv_layers.new(name='Painting UV')
    for i,p in enumerate(uvs or [(0,0),(1,0),(1,1),(0,1)]):uv.data[i].uv=p
    return ob

sky=bpy.data.collections['01 | SKY AND FAR HILLS']
plane('Painted distant wooded hills',54,48,-3.0,155,14,matcopy('Distant hills painterly','Distant_Hills_v001.png'),sky)
fg=bpy.data.collections['09 | FOREGROUND transitions']
woods=matcopy('Foreground tree painting','Woods_v001.png')
for i,x in enumerate([-5.8,16.3,38.4]):
    # Crop the first genuine painted tree in the native UVs, keeping the source
    # bitmap unchanged. Branches at the outer edge leave and enter the frame.
    plane('Painted transition tree %d'%i,x,-5.2,-1.7,4.3,10,woods,fg,[(0,0),(.22,0),(.22,1),(0,1)])

ground=bpy.data.materials['Ground | green earth to cold ash'];nt=ground.node_tree
em=next(n for n in nt.nodes if n.type=='EMISSION')
geometry=next(n for n in nt.nodes if n.type=='NEW_GEOMETRY')
mapping=nt.nodes.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(.13,.16,.0)
nt.links.new(geometry.outputs['Position'],mapping.inputs[0])
texture=nt.nodes.new('ShaderNodeTexImage');texture.image=bpy.data.images.load(str(ROOT/'sets/painted_layers/Ground_Painted_v001.png'),check_existing=True);texture.image.pack();texture.image.filepath='//../../sets/painted_layers/Ground_Painted_v001.png';texture.extension='REPEAT';nt.links.new(mapping.outputs[0],texture.inputs[0])
mapnode=next(n for n in nt.nodes if n.type=='MAP_RANGE')
tint=nt.nodes.new('ShaderNodeValToRGB')
tint.color_ramp.elements[0].color=(.85,.79,.58,1);tint.color_ramp.elements[1].color=(.22,.28,.34,1)
nt.links.new(mapnode.outputs[0],tint.inputs[0])
mul=nt.nodes.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1;nt.links.new(texture.outputs['Color'],mul.inputs[1]);nt.links.new(tint.outputs[0],mul.inputs[2])
hsv=nt.nodes.new('ShaderNodeHueSaturation');nt.links.new(mul.outputs[0],hsv.inputs['Color'])
hsv.inputs['Saturation'].default_value=.8;hsv.inputs['Saturation'].keyframe_insert('default_value',frame=1)
hsv.inputs['Saturation'].default_value=.13;hsv.inputs['Saturation'].keyframe_insert('default_value',frame=2161)
nt.links.new(hsv.outputs[0],em.inputs[0])

# Contact is represented only by a held ground shadow; no leg motion is added.
shadow=bpy.data.materials.new('Held pair soft contact shade');shadow.use_nodes=True
if hasattr(shadow,'surface_render_method'):shadow.surface_render_method='DITHERED'
nodes=shadow.node_tree.nodes;nodes.clear();o=nodes.new('ShaderNodeOutputMaterial');tr=nodes.new('ShaderNodeBsdfTransparent');ink=nodes.new('ShaderNodeEmission');ink.inputs[0].default_value=(.005,.008,.010,1);mix=nodes.new('ShaderNodeMixShader');mix.inputs[0].default_value=.28
shadow.node_tree.links.new(tr.outputs[0],mix.inputs[1]);shadow.node_tree.links.new(ink.outputs[0],mix.inputs[2]);shadow.node_tree.links.new(mix.outputs[0],o.inputs[0])
verts=[(.62*math.cos(i*math.tau/32),-.36+.19*math.sin(i*math.tau/32),.008) for i in range(32)]
me=bpy.data.meshes.new('Held pair contact');me.from_pydata(verts,[],[tuple(range(32))]);me.materials.append(shadow);me.update()
ob=bpy.data.objects.new('Held pair contact',me);bpy.data.collections['10 | STATIC CHILDREN vector drawing'].objects.link(ob);ob.parent=bpy.data.objects['GP_Pair_STATIC_world_scale']

scene['paint_package']='9 GPT imagegen set layers plus one held pair source; rasters packed in the native project'
scene.frame_set(1);scene.render.filepath='//../../renders/world/frames_4k/frame_'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'shots/world/WTSC_World_First_v002.blend'))
print('WORLD v002 saved: painterly hills, ground and foreground trees; no character pose animation')
