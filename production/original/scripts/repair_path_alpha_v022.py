import bpy
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE')
s=bpy.context.scene;assert s.name=='WTSC_PAINTED_WORLD_4K_100S_v021'
target=R/'shots/world/WTSC_Painted_World_Trailer_v022.blend';assert not target.exists()
s.name='WTSC_PAINTED_WORLD_4K_100S_v022'
m=bpy.data.materials['v020 | Path continuous painted earth blend'];nt=m.node_tree
sep=next(n for n in nt.nodes if n.type=='SEPXYZ')
path=next(n for n in nt.nodes if n.type=='TEX_IMAGE' and 'Path_Detail' in n.image.name)
clean=nt.nodes.new('ShaderNodeMapRange');clean.clamp=True;clean.inputs['From Min'].default_value=.07;clean.inputs['From Max'].default_value=.95;nt.links.new(path.outputs['Alpha'],clean.inputs[0])
fill=nt.nodes.new('ShaderNodeMapRange');fill.clamp=True;fill.interpolation_type='SMOOTHERSTEP';fill.inputs['From Min'].default_value=-.21;fill.inputs['From Max'].default_value=-.05;fill.inputs['To Min'].default_value=1;fill.inputs['To Max'].default_value=0;nt.links.new(sep.outputs['Z'],fill.inputs[0])
alpha=nt.nodes.new('ShaderNodeMath');alpha.operation='MAXIMUM';nt.links.new(clean.outputs[0],alpha.inputs[0]);nt.links.new(fill.outputs[0],alpha.inputs[1])
mix=next(n for n in nt.nodes if n.type=='MIX_SHADER');nt.links.new(alpha.outputs[0],mix.inputs[0])
for text in bpy.data.texts:
    if text.name.startswith('START HERE v021'):
        value=text.as_string().replace('v021','v022')+'\nPath alpha retains transparent upper grass/sky pixels. Opaque underpainting fills only below the painted path band, with no black upper strip.\n'
        text.name='START HERE v022 | Painted world trailer';text.clear();text.write(value)
s.render.filepath=str(R/'renders/world_v016/WTSC_Painted_World_4K_v022.mp4');s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
out=R/'renders/world_v016/inspection_v022';out.mkdir(exist_ok=True)
s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
for name,f in [('01_village',1),('02_woods',721),('03_school',1057),('04_camp',1417),('05_battlefield',1777),('06_title',2305)]:
    s.frame_set(f);s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);print('V022_REVIEW',name,f,flush=True)
