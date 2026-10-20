"""Three small staging checks only, not the held integrated-performance deliverable."""
import bpy
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE');s=bpy.data.scenes['WTSC_OPEN_INTEGRATION_GROUNDWORK_v041'];bpy.context.window.scene=s;s.render.resolution_percentage=25;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
for f in [1801,1825,1920]:
    s.frame_set(f);s.render.filepath=str(R/f'renders/world_v016/integration_v041/Groundwork_Only_{f}_960.png');bpy.ops.render.render(write_still=True,scene=s.name)
print('GROUNDWORK_THREE_SMALL_STILLS_DONE_NO_INTEGRATED_RENDER',flush=True)
