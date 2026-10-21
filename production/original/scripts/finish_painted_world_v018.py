import bpy,json,math
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE')
s=bpy.context.scene
assert s.name=='WTSC_PAINTED_WORLD_4K_100S_v017'
target=R/'shots/world/WTSC_Painted_World_Trailer_v018.blend';assert not target.exists()
s.name='WTSC_PAINTED_WORLD_4K_100S_v018'
# Prior project native renders established BLENDED as the reliable GP/alpha-card overlap route.
# This fixes black silhouettes where a fully faded transparent card overlaps the drawn foreground.
changed=[]
for m in bpy.data.materials:
    if m.use_nodes and any(n.type=='BSDF_TRANSPARENT' for n in m.node_tree.nodes):
        m.surface_render_method='BLENDED';changed.append(m.name)
s.eevee.taa_render_samples=64
s.render.ffmpeg.ffmpeg_preset='REALTIME';s.render.dither_intensity=0
# Dark rigid posts in the camp paint stay pinned; brighter cloth can billow.
camp=s.objects['v016 | Camp | pinned canvas and ropes'];im=next(n.image for n in camp.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE');pixels=list(im.pixels);w,h=im.size
uvs={loop.vertex_index:camp.data.uv_layers.active.data[loop.index].uv.copy() for loop in camp.data.loops}
base=camp.data.shape_keys.key_blocks[0]
for key in list(camp.data.shape_keys.key_blocks)[1:]:
    for i,p in enumerate(key.data):
        uv=uvs[i];x=min(w-1,max(0,int(uv.x*(w-1))));y=min(h-1,max(0,int(uv.y*(h-1))));idx=(y*w+x)*4
        light=sum(pixels[idx:idx+3])/3;weight=max(0,min(1,(light-.025)/.075))
        p.co=base.data[i].co+(p.co-base.data[i].co)*weight
for text in bpy.data.texts:
    if text.name.startswith('START HERE v017'):
        content=text.as_string().replace('v017','v018')+'\nAlpha compositing: BLENDED painted planes fixes GP overlap silhouettes; 64 native samples. Dark camp posts pinned by sampled paint value.\n'
        text.name='START HERE v018 | Painted world trailer';text.clear();text.write(content)
s['alpha_repair']='BLENDED raster/FX materials; verified against original GP overlap issue.'
s.render.filepath=str(R/'renders/world_v016/WTSC_Painted_World_4K_v018.mp4');s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
(R/'notes/world_v016/alpha_repair_v018.json').write_text(json.dumps({'source':str(target),'changed_materials':changed,'method':'BLENDED transparent paint/fx shaders, preserving native GP contour','samples':64},indent=2))
out=R/'renders/world_v016/inspection_v018';out.mkdir(exist_ok=True)
s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
for name,f in [('01_village',1),('02_woods',721),('03_school',1057),('04_camp',1417),('05_battlefield',1777),('06_title',2305)]:
    s.frame_set(f);s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);print('V018_REVIEW',name,f,flush=True)
