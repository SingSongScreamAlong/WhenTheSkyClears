import bpy
from pathlib import Path
root=Path(r'WTSC_LOCAL_WORKSPACE')
world=bpy.data.scenes['WTSC_WORLD_FIRST_4K'];bpy.context.window.scene=world
world.frame_set(1489)
world.render.image_settings.media_type='IMAGE';world.render.image_settings.file_format='PNG'
world.render.resolution_percentage=100
world.render.filepath=str(root/'renders/world/Battlefield_Corrected_4K_v006.png')
bpy.ops.render.render(write_still=True)
world.frame_set(1);world.render.filepath='//../../renders/world/frames_4k/frame_'
print('Corrected native 4K still complete')
