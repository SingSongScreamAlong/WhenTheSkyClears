import bpy,math,json
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE')
s=bpy.context.scene;assert s.name=='WTSC_PAINTED_WORLD_4K_100S_v019'
target=R/'shots/world/WTSC_Painted_World_Trailer_v020.blend';assert not target.exists()
s.name='WTSC_PAINTED_WORLD_4K_100S_v020'
C=bpy.data.collections['v016 | 03 Continuous painted path']
for name in ['v017 | Finite painted path band','v017 | Earth beneath painted band','v017 | Narrow painted foreground bank','v017 | Charcoal earth under near bank']:
    bpy.data.objects.remove(s.objects[name],do_unlink=True)

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
def tex(nt,path,vector):
    n=nt.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(path),check_existing=True);n.image.pack();n.extension='EXTEND';nt.links.new(vector,n.inputs[0]);return n
def vec(nt,x,y):
    n=nt.nodes.new('ShaderNodeCombineXYZ');nt.links.new(x,n.inputs[0]);nt.links.new(y,n.inputs[1]);return n.outputs[0]
def mix(nt,a,b,f,mode='MIX'):
    n=nt.nodes.new('ShaderNodeMixRGB');n.blend_type=mode
    for i,v in enumerate([f,a,b]):
        if isinstance(v,(int,float)):n.inputs[i].default_value=v
        elif isinstance(v,tuple):n.inputs[i].default_value=v
        else:nt.links.new(v,n.inputs[i])
    return n.outputs[0]

def continuous_ground(near):
    m=bpy.data.materials.new('v020 | '+('Near' if near else 'Path')+' continuous painted earth blend');m.use_nodes=True;m.surface_render_method='DITHERED';nt=m.node_tree;nt.nodes.clear()
    geo=nt.nodes.new('ShaderNodeNewGeometry');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geo.outputs['Position'],sep.inputs[0]);x=sep.outputs['X'];z=sep.outputs['Z']
    noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=8;noise.inputs['Detail'].default_value=2;nt.links.new(geo.outputs['Position'],noise.inputs[0])
    irregular=mathn(nt,'ADD',z,mathn(nt,'MULTIPLY',mathn(nt,'SUBTRACT',noise.outputs['Fac'],.5),.14))
    earth=tex(nt,R/'sets/painted_layers/Ground_Painted_v001.png',vec(nt,mathn(nt,'PINGPONG',mathn(nt,'MULTIPLY',x,.15),1),mathn(nt,'PINGPONG',mathn(nt,'MULTIPLY',z,.25),1)))
    earthcolor=mix(nt,earth.outputs['Color'],(.13,.17,.16,1) if near else (.37,.41,.33,1),1,'MULTIPLY')
    if near:
        uvx=mathn(nt,'PINGPONG',mathn(nt,'ADD',mathn(nt,'MULTIPLY',x,1/7.92),.5),1)
        uvy=remap(nt,z,.7725,1.106625,0,.075)
        bank=tex(nt,R/'sets/village_lookdev/v012/Foreground_Ground.png',vec(nt,uvx,uvy))
        bankcolor=mix(nt,bank.outputs['Color'],(.16,.18,.16,1),1,'MULTIPLY')
        factor=mathn(nt,'MULTIPLY',remap(nt,irregular,.68,.87,0,1),remap(nt,irregular,.97,1.15,1,0))
        color=mix(nt,earthcolor,bankcolor,factor)
        alpha=remap(nt,irregular,1.00,1.18,1,0)
    else:
        uvx=mathn(nt,'PINGPONG',mathn(nt,'MULTIPLY',mathn(nt,'ADD',x,1.8792),1/2.7216),1)
        uvy=remap(nt,z,-.2076,.9588,0,1)
        path=tex(nt,R/'sets/village_lookdev/v014/Path_Detail_Repaint.png',vec(nt,uvx,uvy))
        color=mix(nt,earthcolor,path.outputs['Color'],remap(nt,irregular,-.20,.04,0,1))
        alpha=mathn(nt,'MAXIMUM',path.outputs['Alpha'],remap(nt,z,.70,.955,1,0))
    hsv=nt.nodes.new('ShaderNodeHueSaturation');nt.links.new(color,hsv.inputs['Color'])
    for t,v in [(0,1),(18,.85),(38,.66),(62,.46),(80,.28),(100,.25)]:hsv.inputs['Saturation'].default_value=v;hsv.inputs['Saturation'].keyframe_insert('default_value',frame=min(2400,t*24+1))
    em=nt.nodes.new('ShaderNodeEmission');nt.links.new(hsv.outputs[0],em.inputs[0]);tr=nt.nodes.new('ShaderNodeBsdfTransparent');sh=nt.nodes.new('ShaderNodeMixShader');nt.links.new(alpha,sh.inputs[0]);nt.links.new(tr.outputs[0],sh.inputs[1]);nt.links.new(em.outputs[0],sh.inputs[2]);out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(sh.outputs[0],out.inputs[0])
    y=-4.99 if near else 2.06;top=1.25 if near else .9588
    d=bpy.data.meshes.new('Continuous painted terrain');d.from_pydata([(-24,y,-30),(122,y,-30),(122,y,top),(-24,y,top)],[],[(0,1,2,3)]);d.materials.append(m);d.update()
    o=bpy.data.objects.new('v020 | '+('Foreground bank' if near else 'Walking path')+' | continuous blended paint',d);C.objects.link(o)
    o['repair']='One continuous surface, painted earth underlayer, irregular shader feather; no visible rectangular join.'
continuous_ground(False);continuous_ground(True)
s.eevee.taa_render_samples=32
s['approval']='Current painterly direction liked by user; ongoing world development authorized. No final artistic acceptance inferred.'
s['scope']='Full 100s world animation; near-age painterly children remain held and translate intact.'
pair=next(o for o in s.objects if o.type=='GREASEPENCIL');pair['render_style']='Near-black painterly gray detail with small off-white eye marks. Native editable vector boundary.'
for text in bpy.data.texts:
    if text.name.startswith('START HERE v019'):
        value=text.as_string().replace('v019','v020')+'\nGround continuation: continuous native painted earth surfaces with irregular shader feathers replace the narrow opaque foreground strip. Most base paintings remain 1672x941; smoke is 1024x1536. Native UHD rendering uses 32 samples.\n'
        text.name='START HERE v020 | Painted world trailer';text.clear();text.write(value)
s.render.filepath=str(R/'renders/world_v016/WTSC_Painted_World_4K_v020.mp4');s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
out=R/'renders/world_v016/inspection_v020';out.mkdir(exist_ok=True)
s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
for name,f in [('01_village',1),('02_woods',721),('03_school',1057),('04_camp',1417),('05_battlefield',1777),('06_title',2305)]:
    s.frame_set(f);s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);print('V020_REVIEW',name,f,flush=True)
