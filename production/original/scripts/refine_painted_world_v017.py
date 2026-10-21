import bpy,sys,math,json
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE')
s=bpy.context.scene
s.name='WTSC_PAINTED_WORLD_4K_100S_v017'
assert not (R/'shots/world/WTSC_Painted_World_Trailer_v017.blend').exists()
C=bpy.data.collections['v016 | 03 Continuous painted path']
def mesh(name,verts,mat,uvs=None):
    d=bpy.data.meshes.new(name);d.from_pydata(verts,[],[(0,1,2,3)]);d.update();d.materials.append(mat)
    if uvs:
        uv=d.uv_layers.new(name='Paint UV')
        for loop in d.loops:uv.data[loop.index].uv=uvs[loop.vertex_index]
    o=bpy.data.objects.new(name,d);C.objects.link(o);return o
def quad(name,y,z0,z1,mat,uvs=None):
    return mesh(name,[(-24,y,z0),(122,y,z0),(122,y,z1),(-24,y,z1)],mat,uvs)
def earthmat(name,a,b):
    m=bpy.data.materials.new(name);m.use_nodes=True;nt=m.node_tree;nt.nodes.clear()
    out=nt.nodes.new('ShaderNodeOutputMaterial');em=nt.nodes.new('ShaderNodeEmission');n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=23;n.inputs['Detail'].default_value=3
    geo=nt.nodes.new('ShaderNodeNewGeometry');nt.links.new(geo.outputs['Position'],n.inputs['Vector']);r=nt.nodes.new('ShaderNodeValToRGB');r.color_ramp.elements[0].color=(*a,1);r.color_ramp.elements[1].color=(*b,1);nt.links.new(n.outputs['Fac'],r.inputs[0]);nt.links.new(r.outputs[0],em.inputs[0]);nt.links.new(em.outputs[0],out.inputs[0]);return m

# Re-register the exact finite painted path band; transparent top rows stay transparent.
ground=s.objects['v016 | Continuous painted earth and path'];m=ground.data.materials[0]
bpy.data.objects.remove(ground,do_unlink=True)
nt=m.node_tree;tex=next(n for n in nt.nodes if n.type=='TEX_IMAGE');tex.extension='EXTEND'
em=next(n for n in nt.nodes if n.type=='EMISSION');out=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL')
tr=nt.nodes.new('ShaderNodeBsdfTransparent');mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(tex.outputs['Alpha'],mix.inputs[0]);nt.links.new(tr.outputs[0],mix.inputs[1]);nt.links.new(em.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],out.inputs[0])
u0=(-24+1.8792)/2.7216;u1=(122+1.8792)/2.7216
quad('v017 | Finite painted path band',2.06,-.2076,.9588,m,[(u0,0),(u1,0),(u1,1),(u0,1)])
quad('v017 | Earth beneath painted band',2.08,-30,-.20755,earthmat('v017 | Earth underpainting',(.025,.031,.018),(.052,.058,.032)))

bank=s.objects['v016 | Foreground painted bank continuation'];m=bank.data.materials[0]
bpy.data.objects.remove(bank,do_unlink=True)
nt=m.node_tree;tex=next(n for n in nt.nodes if n.type=='TEX_IMAGE');tex.extension='EXTEND'
uv=next(n for n in nt.nodes if n.type=='TEX_COORD');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(uv.outputs['UV'],sep.inputs[0]);ping=nt.nodes.new('ShaderNodeMath');ping.operation='PINGPONG';ping.inputs[1].default_value=1;nt.links.new(sep.outputs['X'],ping.inputs[0]);combine=nt.nodes.new('ShaderNodeCombineXYZ');nt.links.new(ping.outputs[0],combine.inputs[0]);nt.links.new(sep.outputs['Y'],combine.inputs[1]);nt.links.new(combine.outputs[0],tex.inputs['Vector'])
u0=(-24)/7.92+.5;u1=122/7.92+.5
quad('v017 | Narrow painted foreground bank',-4.99,.7725,1.106625,m,[(u0,0),(u1,0),(u1,.075),(u0,.075)])
quad('v017 | Charcoal earth under near bank',-4.985,-30,.77255,earthmat('v017 | Near earth brush texture',(.006,.010,.008),(.017,.021,.014)))

# Match distant/near canopy value separation while retaining the lighter painted leaf accents.
near=bpy.data.materials['v016 | Woods | near rooted oaks paint']
mul=next(n for n in near.node_tree.nodes if n.type=='MIX_RGB' and n.blend_type=='MULTIPLY');mul.inputs[2].default_value=(.53,.60,.54,1)
# Soft feather at cropped transition paint boundaries, avoiding a visible rectangular card edge.
for ob in s.objects:
    if not ob.name.startswith('v016 | Foreground oak transition '):continue
    nt=ob.data.materials[0].node_tree;uv=next(n for n in nt.nodes if n.type=='TEX_COORD');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(uv.outputs['UV'],sep.inputs[0])
    ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
    for i,(v,a) in enumerate([(.012,0),(.035,1),(.165,1),(.20,0)]):
        e=ramp.color_ramp.elements[0] if i==0 else ramp.color_ramp.elements.new(v);e.position=v;e.color=(a,a,a,1)
    nt.links.new(sep.outputs['X'],ramp.inputs[0]);mix=next(n for n in nt.nodes if n.type=='MIX_SHADER');old=mix.inputs[0].links[0].from_socket;mul=nt.nodes.new('ShaderNodeMath');mul.operation='MULTIPLY';nt.links.new(old,mul.inputs[0]);nt.links.new(ramp.outputs[0],mul.inputs[1]);nt.links.new(mul.outputs[0],mix.inputs[0])

# The distant atmosphere cools over the route while the architecture retains its own local treatment.
rear=s.objects['v015 | Rear countryside'];nt=rear.data.materials[0].node_tree;em=next(n for n in nt.nodes if n.type=='EMISSION');old=em.inputs[0].links[0].from_socket
cool=nt.nodes.new('ShaderNodeMixRGB');cool.blend_type='MULTIPLY';cool.inputs[2].default_value=(.65,.81,1.0,1);nt.links.new(old,cool.inputs[1]);nt.links.new(cool.outputs[0],em.inputs[0])
for t,v in [(0,0),(18,.08),(42,.38),(67,.85),(80,1),(100,1)]:cool.inputs[0].default_value=v;cool.inputs[0].keyframe_insert('default_value',frame=min(2400,round(t*24)+1))

# Source notes reflect current source rather than a superseded still-only gate.
for text in bpy.data.texts:
    if text.name.startswith('START HERE v016'):
        content=text.as_string().replace('v016','v017')+'\nGround extension repaired in native material/mesh authoring: finite alpha path band, narrow near-bank paint, textured earth below; no wrapped vertical imagery.\n'
        text.name='START HERE v017 | Painted world trailer';text.clear();text.write(content)
s.render.filepath=str(R/'renders/world_v016/WTSC_Painted_World_4K_v017.mp4')
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(R/'shots/world/WTSC_Painted_World_Trailer_v017.blend'),compress=True)
out=R/'renders/world_v016/inspection_v017';out.mkdir(exist_ok=True)
s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
for name,f in [('01_village',1),('02_woods',721),('03_school',1057),('04_camp',1417),('05_battlefield',1777),('06_title',2305)]:
    s.frame_set(f);s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);print('V017_REVIEW',name,f,flush=True)
