import bpy,json
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE')
s=bpy.context.scene;assert s.name=='WTSC_PAINTED_WORLD_4K_100S_v026';s.name='WTSC_PAINTED_WORLD_4K_100S_v027'
target=R/'shots/world/WTSC_Painted_World_Trailer_v027.blend';assert not target.exists()
changed=[];seen=set()
for o in s.objects:
    if not o.name.startswith(('v016 | Woods |','v025 | Far woods continuation','v016 | Village continues |','v016 | School |','v016 | Camp |','v016 | Battlefield |','v016 | Ruins |')):continue
    m=o.data.materials[0]
    if m.name in seen:continue
    seen.add(m.name);nt=m.node_tree;uv=next(n for n in nt.nodes if n.type=='TEX_COORD');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(uv.outputs['UV'],sep.inputs[0]);r=nt.nodes.new('ShaderNodeMapRange');r.clamp=True;r.interpolation_type='SMOOTHERSTEP'
    baseline=float(o.get('paint_baseline',.835));root=1-baseline;r.inputs['From Min'].default_value=root-.024;r.inputs['From Max'].default_value=root+.032;nt.links.new(sep.outputs['Y'],r.inputs[0]);mix=next(n for n in nt.nodes if n.type=='MIX_SHADER');old=mix.inputs[0].links[0].from_socket;mul=nt.nodes.new('ShaderNodeMath');mul.operation='MULTIPLY';nt.links.new(old,mul.inputs[0]);nt.links.new(r.outputs[0],mul.inputs[1]);nt.links.new(mul.outputs[0],mix.inputs[0]);changed.append({'material':m.name,'root_uv':root,'feather_uv':[root-.024,root+.032]})
for text in bpy.data.texts:
    if text.name.startswith('CURRENT v026'):
        value=text.as_string().replace('v026','v027')+'\nRegional tree/building ground edges receive a small native alpha feather into the continuous ground, avoiding a rectangular root-line join.\n'
        text.name='CURRENT v027 | Painted world trailer and motion corrections';text.clear();text.write(value)
s.render.filepath=str(R/'renders/world_v016/WTSC_Painted_World_4K_v027.mp4');s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
(R/'notes/world_v016/root_feathers_v027.json').write_text(json.dumps(changed,indent=2))
out=R/'renders/world_v016/inspection_v027';out.mkdir(exist_ok=True)
s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
for name,f in [('01_village',1),('02_woods',721),('03_school',1057),('04_camp',1417),('05_battlefield',1777),('06_title',2305)]:
    s.frame_set(f);s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);print('V027_REVIEW',name,f,flush=True)
