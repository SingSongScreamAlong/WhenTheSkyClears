import bpy,time,json
from pathlib import Path
ROOT=Path(r'WTSC_LOCAL_WORKSPACE')
world=bpy.data.scenes['WTSC_WORLD_FIRST_4K'];bpy.context.window.scene=world
mat=bpy.data.materials['LW | Painted Leaves'];assert mat.surface_render_method=='BLENDED'
mat.surface_render_method='DITHERED'
world.render.resolution_percentage=100;world.render.image_settings.media_type='IMAGE';world.render.image_settings.file_format='PNG'
times=[]
for name,frame in [('Village',1),('Woods',865)]:
    world.frame_set(frame);world.render.filepath=str(ROOT/f'renders/living_world/{name}_LeafAlpha_Test_4K.png');start=time.time();bpy.ops.render.render(write_still=True)
    times.append({'name':name,'seconds':time.time()-start})
mat.surface_render_method='BLENDED';world.frame_set(1);world.render.filepath='//../../renders/living_world/still_'
print(json.dumps(times))
