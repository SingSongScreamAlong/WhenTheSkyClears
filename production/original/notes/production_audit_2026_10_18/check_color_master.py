import bpy
import hashlib
import json
from pathlib import Path
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
SOURCE = ROOT / 'work/color_arc_v063/native/WTSC_Shared_Color_To_Charcoal_v063.blend'
before = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE), load_ui=False, use_scripts=False)
world = bpy.data.scenes['WTSC_SHARED_COLOR_TO_CHARCOAL_v063']
edit = bpy.data.scenes['WTSC_FIRST_DANGER_EDIT_v060']
for scene in [world, edit]:
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.threads_mode = 'FIXED'
    scene.render.threads = 2
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.film_transparent = False
for label, scene in [('world', world), ('edit', edit), ('edit_standard', edit)]:
    if label == 'edit_standard':
        scene.view_settings.view_transform = 'Standard'
    for dep in bpy.data.scenes:
        if dep.name.startswith('WTSC_'):
            dep.frame_set(981)
    bpy.context.window.scene = scene
    scene.frame_set(981)
    bpy.context.view_layer.update()
    scene.render.filepath = str(OUT / f'v063_{label}_981.png')
    bpy.ops.render.render(write_still=True, scene=scene.name)
    if label == 'edit_standard':
        scene.view_settings.view_transform = 'AgX'
shape = bpy.data.shape_keys.get('Key.053')
owners = []
if shape:
    for ob in bpy.data.objects:
        if getattr(ob.data, 'shape_keys', None) == shape:
            owners.append({'object': ob.name, 'hide_render': ob.hide_render,
                           'scenes': [s.name for s in ob.users_scene]})
(OUT / 'color_master_check.json').write_text(json.dumps({
    'world_view': world.view_settings.view_transform, 'edit_view': edit.view_settings.view_transform,
    'world_sequencer_space': world.sequencer_colorspace_settings.name,
    'edit_sequencer_space': edit.sequencer_colorspace_settings.name,
    'missing_driver_owner_users': shape.users if shape else None,
    'missing_driver_owner_objects': owners,
    'source_unchanged': hashlib.sha256(SOURCE.read_bytes()).hexdigest() == before,
    'scope': 'Actual 1280x720 render of world and native edit at G981; changes in RAM only.'
}, indent=2), encoding='utf-8')
print('COLOR_MASTER_CHECK_COMPLETE', flush=True)
