import bpy,json
from pathlib import Path
ROOT=Path(r'WTSC_LOCAL_WORKSPACE')
assert bpy.data.filepath.endswith('WTSC_Living_World_Editable_v011.blend')
world=bpy.data.scenes['WTSC_WORLD_FIRST_4K'];bpy.context.window.scene=world
world.render.image_settings.media_type='IMAGE';world.render.image_settings.file_format='PNG';world.render.resolution_percentage=100
for name,frame in [('Village',1),('Woods',865),('School',1249)]:
    world.frame_set(frame);world.render.filepath=str(ROOT/f'renders/living_world/Editable_{name}_v011_4K.png');bpy.ops.render.render(write_still=True)
world.frame_set(1);world.render.filepath='//../../renders/living_world/still_'
print(json.dumps({'source':bpy.data.filepath,'review_frames':['Village','Woods','School'],'resolution':[3840,2160]}))
