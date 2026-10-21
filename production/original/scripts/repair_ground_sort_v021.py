import bpy
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE')
s=bpy.context.scene;assert s.name=='WTSC_PAINTED_WORLD_4K_100S_v020'
s.name='WTSC_PAINTED_WORLD_4K_100S_v021'
target=R/'shots/world/WTSC_Painted_World_Trailer_v021.blend';assert not target.exists()
for o in s.objects:
    if not o.name.startswith('v020 | '):continue
    y=o.data.vertices[0].co.y
    for p in o.data.vertices:p.co.y-=y
    o.location.y=y
    o.data.materials[0].surface_render_method='BLENDED'
    o['alpha_sort']='Correct local origin at actual layer depth; sorted alpha avoids GP black overlap.'
for text in bpy.data.texts:
    if text.name.startswith('START HERE v020'):
        value=text.as_string().replace('v020','v021')+'\nContinuous painted ground uses correctly placed object origins and BLENDED alpha to preserve ground contact and feathered edges.\n'
        text.name='START HERE v021 | Painted world trailer';text.clear();text.write(value)
s.render.filepath=str(R/'renders/world_v016/WTSC_Painted_World_4K_v021.mp4');s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
out=R/'renders/world_v016/inspection_v021';out.mkdir(exist_ok=True)
s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
for name,f in [('01_village',1),('02_woods',721),('03_school',1057),('04_camp',1417),('05_battlefield',1777),('06_title',2305)]:
    s.frame_set(f);s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);print('V021_REVIEW',name,f,flush=True)
