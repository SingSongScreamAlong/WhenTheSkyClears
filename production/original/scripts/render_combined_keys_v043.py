import bpy
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE');s=bpy.data.scenes['WTSC_OPEN_BATTLEFIELD_COMBINED_TRIAL_v043'];bpy.context.window.scene=s;folder=R/'renders/world_v016/integration_v043';folder.mkdir(exist_ok=True);s.render.resolution_percentage=50;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
for frame in [1801,1825,1830,1843,1852,1881,1920]:
    s.frame_set(frame);s.render.filepath=str(folder/f'Combined_{frame}_1080.png');bpy.ops.render.render(write_still=True,scene=s.name)
print('COMBINED_V043_KEYS_RENDERED',flush=True)
