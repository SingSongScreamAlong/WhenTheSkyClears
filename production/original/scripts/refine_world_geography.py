import bpy,math
from pathlib import Path
ROOT=Path(r'WTSC_LOCAL_WORKSPACE')
s=bpy.context.scene
assert s.name=='WTSC_WORLD_FIRST_4K'
# Remove the visibly cropped tree experiment and simple line blocking props.
for ob in s.objects:
    if ob.name.startswith(('Painted transition tree','Camp to battlefield post','Broken rail','Earth profile foreground edge')):
        ob.hide_render=True;ob.hide_viewport=True
for v in bpy.data.objects['Continuous ground top'].data.vertices:
    if v.co.y<0:v.co.y=-40
bpy.data.objects['Continuous ground top'].data.update()

def reposition(name,x,width=None):
    ob=bpy.data.objects[name]
    coords=[v.co.x for v in ob.data.vertices];center=(max(coords)+min(coords))/2
    ratio=width/(max(coords)-min(coords)) if width else 1
    for v in ob.data.vertices:v.co.x=x+(v.co.x-center)*ratio
    ob.data.update()
reposition('Village B | same village abandoned',17)
reposition('Woods near trunks',29,20)
reposition('Woods far canopy',29,27)
reposition('School facade | shattered classroom',41,14)
reposition('Camp canvas | displacement edge',53,18)
reposition('Battlefield ruin line',67,30)

title=bpy.data.objects['WHEN THE SKY CLEARS | monumental terrain']
title.scale=(1,1,1);bpy.context.view_layer.update()
native_width=title.dimensions.x;native_height=title.dimensions.y
title.scale=(32/native_width,3.8/native_height,1)
title['height_m']=3.8;title['width_m']=32

source=bpy.data.materials['Village B | same village abandoned paint']
tree=source.copy();tree.name='Whole foreground oak alpha'
image=bpy.data.images.load(str(ROOT/'sets/painted_layers/Foreground_Tree_v001.png'),check_existing=True);image.alpha_mode='STRAIGHT';image.pack();image.filepath='//../../sets/painted_layers/Foreground_Tree_v001.png'
for node in tree.node_tree.nodes:
    if node.type=='TEX_IMAGE':node.image=image
    if node.type=='MAP_RANGE':node.inputs['From Min'].default_value=.35;node.inputs['From Max'].default_value=.97
fg=bpy.data.collections['09 | FOREGROUND transitions']
for i,(x,y,width) in enumerate([(-6.8,-5.0,12.0),(15.8,-4.5,11.0),(38.5,-4.0,10.0)]):
    h=width*1024/1536;bottom=-h*.05
    me=bpy.data.meshes.new('Whole painted oak %d'%i);me.from_pydata([(x-width/2,y,bottom),(x+width/2,y,bottom),(x+width/2,y,bottom+h),(x-width/2,y,bottom+h)],[],[(0,1,2,3)]);me.update()
    uv=me.uv_layers.new(name='Painting UV')
    for j,p in enumerate([(0,0),(1,0),(1,1),(0,1)]):uv.data[j].uv=p
    ob=bpy.data.objects.new('Whole painted oak %d'%i,me);fg.objects.link(ob);me.materials.append(tree)

# Native UV feather masks remove rectangular layer ends without altering the
# generated PNGs or fading whole locations out in front of the viewer.
materials={mat for ob in s.objects if ob.type=='MESH' and not ob.hide_render for mat in ob.data.materials if mat and any(n.type=='BSDF_TRANSPARENT' for n in mat.node_tree.nodes)}
for mat in materials:
    nt=mat.node_tree
    mix=next((n for n in nt.nodes if n.type=='MIX_SHADER'),None)
    if not mix or not mix.inputs[0].is_linked:continue
    alpha=mix.inputs[0].links[0].from_socket
    uv=nt.nodes.new('ShaderNodeTexCoord');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(uv.outputs['UV'],sep.inputs[0])
    inv=nt.nodes.new('ShaderNodeMath');inv.operation='SUBTRACT';inv.inputs[0].default_value=1;nt.links.new(sep.outputs['X'],inv.inputs[1])
    near=nt.nodes.new('ShaderNodeMath');near.operation='MINIMUM';nt.links.new(sep.outputs['X'],near.inputs[0]);nt.links.new(inv.outputs[0],near.inputs[1])
    edge=nt.nodes.new('ShaderNodeMath');edge.operation='MULTIPLY';edge.use_clamp=True;edge.inputs[1].default_value=18;nt.links.new(near.outputs[0],edge.inputs[0])
    mul=nt.nodes.new('ShaderNodeMath');mul.operation='MULTIPLY';nt.links.new(alpha,mul.inputs[0]);nt.links.new(edge.outputs[0],mul.inputs[1]);nt.links.new(mul.outputs[0],mix.inputs[0])

s.frame_set(1);s.render.filepath='//../../renders/world/frames_4k/frame_'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'shots/world/WTSC_World_First_v003.blend'))
print('WORLD v003 saved: continuous ground extended, isolated full trees, set geography separated, title corrected')
