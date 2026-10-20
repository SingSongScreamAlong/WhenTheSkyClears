import bpy
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE');s=bpy.data.scenes['WTSC_OPEN_BATTLEFIELD_MOTION_TRIAL_v042'];bpy.context.window.scene=s;folder=R/'renders/world_v016/integration_v042';folder.mkdir(exist_ok=True);s.render.resolution_percentage=50;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
for frame in [1801,1825,1843,1852,1881,1920]:
    s.frame_set(frame);s.render.filepath=str(folder/f'Motion_Only_{frame}_1080.png');bpy.ops.render.render(write_still=True,scene=s.name)
print('MOTION_ONLY_KEYFRAMES_RENDERED',flush=True)
