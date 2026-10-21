import bpy
from pathlib import Path
root=Path(r'WTSC_LOCAL_WORKSPACE')
scene=bpy.data.scenes['WTSC_WORLD_FIRST_4K']
bpy.context.window.scene=scene
scene.frame_set(1489)
scene.render.resolution_percentage=25
scene.render.image_settings.media_type='IMAGE'
scene.render.image_settings.file_format='PNG'
pair=bpy.data.objects['GP_Pair_STATIC_world_scale']
pair.hide_render=True
scene.render.filepath=str(root/'renders/world/test_no_gp.png')
bpy.ops.render.render(write_still=True)
pair.hide_render=False
materials=[m for m in bpy.data.materials if any('Battlefield_v001' in n.image.name for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image)]
for m in materials:m.surface_render_method='BLENDED'
scene.render.filepath=str(root/'renders/world/test_blended.png')
bpy.ops.render.render(write_still=True)
for m in materials:m.surface_render_method='DITHERED'
scene.render.resolution_percentage=100
scene.frame_set(1)
print('Done composite diagnosis')
