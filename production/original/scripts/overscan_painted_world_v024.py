import bpy
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE')
s=bpy.context.scene;assert s.name=='WTSC_PAINTED_WORLD_4K_100S_v023';s.name='WTSC_PAINTED_WORLD_4K_100S_v024'
target=R/'shots/world/WTSC_Painted_World_Trailer_v024.blend';assert not target.exists()
rear=s.objects['v023 | Distant countryside | fixed world space'];d=rear.data
for p in d.vertices:
    if p.co.y>11:p.co.y=30
for loop in d.loops:
    co=d.vertices[loop.vertex_index].co;d.uv_layers.active.data[loop.index].uv=((co.x+20.16)/40.32,(co.y+11.34)/22.68)
nt=rear.data.materials[0].node_tree
for n in nt.nodes:
    if n.type=='MAP_RANGE' and abs(n.inputs['From Min'].default_value-.86)<.001:
        n.inputs['From Min'].default_value=1.08;n.inputs['From Max'].default_value=1.55
# Left tree edge begins outside the first camera view and leaves screen immediately;
# fading it inward created an unnecessary visible light strip along the frame boundary.
oak=s.objects['v023 | Opening oak roots fence and path | one coherent surface'];nt=oak.data.materials[0].node_tree
tex=next(n for n in nt.nodes if n.type=='TEX_IMAGE' and 'Foreground_Ground' in n.image.name);sep=next(n for n in nt.nodes if n.type=='SEPXYZ');mix=next(n for n in nt.nodes if n.type=='MIX_SHADER')
def ramp(a,a0,a1,b0,b1):
    n=nt.nodes.new('ShaderNodeMapRange');n.clamp=True;n.interpolation_type='SMOOTHERSTEP'
    for name,v in [('From Min',a0),('From Max',a1),('To Min',b0),('To Max',b1)]:n.inputs[name].default_value=v
    nt.links.new(a,n.inputs[0]);return n.outputs[0]
def mul(a,b):
    n=nt.nodes.new('ShaderNodeMath');n.operation='MULTIPLY';nt.links.new(a,n.inputs[0]);nt.links.new(b,n.inputs[1]);return n.outputs[0]
alpha=mul(ramp(tex.outputs['Alpha'],.025,.98,0,1),ramp(sep.outputs['Y'],.018,.065,0,1));alpha=mul(alpha,ramp(sep.outputs['X'],.978,1,1,0));nt.links.new(alpha,mix.inputs[0])
for text in bpy.data.texts:
    if text.name.startswith('START HERE v023'):
        value=text.as_string().replace('v023','v024')+'\nLandscape overscan extends above the initial framing; its sky feather begins outside the original picture, avoiding a dark upper edge.\n'
        text.name='START HERE v024 | Painted world trailer';text.clear();text.write(value)
s.render.filepath=str(R/'renders/world_v016/WTSC_Painted_World_4K_v024.mp4');s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
out=R/'renders/world_v016/inspection_v024';out.mkdir(exist_ok=True)
s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
for name,f in [('01_village',1),('02_woods',721),('03_school',1057),('04_camp',1417),('05_battlefield',1777),('06_title',2305)]:
    s.frame_set(f);s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);print('V024_REVIEW',name,f,flush=True)
