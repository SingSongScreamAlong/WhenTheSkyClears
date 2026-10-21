import bpy,json
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE')
world=bpy.data.scenes['WTSC_WORLD_EDIT_v031'];master=bpy.data.scenes['WTSC_MASTER_4K_100S_v031']
for text in bpy.data.texts:
    if text.name.startswith('CURRENT EDITABLE v031'):
        value=text.as_string().replace('All art created through GPT imagegen, with files and prompts retained in sets/ and notes/.','Raster paint assets were generated through GPT imagegen, with files and prompts retained in sets/ and notes/. Native GP, vector/mesh effects and title geometry were authored in Blender; the title uses the packed local Arial Black font.')
        text.clear();text.write(value)
bpy.context.window.scene=world;world.frame_set(1);master.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'shots/world/WTSC_Painted_World_Editable_v031.blend'),compress=True)
bpy.context.window.scene=master;world.render.resolution_percentage=10;master.render.resolution_percentage=10;master.frame_set(2400);master.render.image_settings.media_type='IMAGE';master.render.image_settings.file_format='PNG';master.render.image_settings.color_mode='RGB';master.render.filepath=str(R/'renders/world_v016/native_master_last_frame_v031.png')
bpy.ops.render.render(write_still=True,scene=master.name)

