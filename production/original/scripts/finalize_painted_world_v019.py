import bpy,json
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE')
s=bpy.context.scene;assert s.name=='WTSC_PAINTED_WORLD_4K_100S_v018'
target=R/'shots/world/WTSC_Painted_World_Trailer_v019.blend';assert not target.exists()
s.name='WTSC_PAINTED_WORLD_4K_100S_v019'
changed=[]
for m in bpy.data.materials:
    if not m.use_nodes or not any(n.type=='BSDF_TRANSPARENT' for n in m.node_tree.nodes):continue
    # GP and its close ground contact layers need a depth-writing alpha method.
    # Distant fading cards and smoke use sorted alpha to avoid black GP overlap artifacts.
    close=m.name.startswith(('v012 |','v014 |','v015 |')) or m.name in ['v016 | Registered painted earth','v016 | Near bank charcoal paint']
    m.surface_render_method='DITHERED' if close else 'BLENDED'
    changed.append({'material':m.name,'method':m.surface_render_method})
for text in bpy.data.texts:
    if text.name.startswith('START HERE v018'):
        value=text.as_string().replace('v018','v019')+'\nFinal alpha separation: depth-writing DITHERED for GP painted fill and close ground/contact cards; BLENDED for distant fading regional paintings and smoke.\n'
        text.name='START HERE v019 | Painted world trailer';text.clear();text.write(value)
s['alpha_repair']='Depth-writing close character/ground paint; BLENDED distant cards and smoke.'
s.render.filepath=str(R/'renders/world_v016/WTSC_Painted_World_4K_v019.mp4');s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
(R/'notes/world_v016/alpha_final_v019.json').write_text(json.dumps(changed,indent=2))
out=R/'renders/world_v016/inspection_v019';out.mkdir(exist_ok=True)
s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
for name,f in [('01_village',1),('02_woods',721),('03_school',1057),('04_camp',1417),('05_battlefield',1777),('06_title',2305)]:
    s.frame_set(f);s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);print('V019_REVIEW',name,f,flush=True)
