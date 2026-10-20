import bpy,json,time
from pathlib import Path
root=Path(r'WTSC_LOCAL_WORKSPACE')
world=bpy.data.scenes['WTSC_WORLD_FIRST_4K'];bpy.context.window.scene=world
world.render.image_settings.media_type='IMAGE';world.render.image_settings.file_format='PNG'
world.render.resolution_percentage=100
for name,frame in [('Village',1),('Departure',481),('Woods',865),('School',1249),('Camp',1489),('Battlefield',1777),('Title',2281)]:
    world.frame_set(frame);world.render.filepath=str(root/f'renders/living_world/{name}_v009_4K.png')
    start=time.time();bpy.ops.render.render(write_still=True);print(json.dumps({'rendered':name,'frame':frame,'seconds':round(time.time()-start,2)}),flush=True)
world.frame_set(1);world.render.resolution_percentage=100;world.render.filepath='//../../renders/living_world/still_'
