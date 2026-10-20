"""Make the delivered source open on the actual editable world camera.
No geometry, paint, character or timing changes relative to the render source.
"""
import bpy,json,hashlib
from pathlib import Path
ROOT=Path(r'WTSC_LOCAL_WORKSPACE')
world=bpy.data.scenes['WTSC_WORLD_FIRST_4K'];master=bpy.data.scenes['WTSC_MASTER_4K_100S']
world.render.image_settings.media_type='IMAGE';world.render.image_settings.file_format='PNG'
world.render.filepath='//../../renders/world/frames_4k/frame_'
world['paint_package']='10 GPT imagegen set paintings plus one held pair reference; packed sources'
for strip in master.sequence_editor.strips:
    if strip.type=='SOUND':strip.sound.pack()
bpy.context.window.scene=world
world.frame_set(1);master.frame_set(1)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active;space.region_3d.view_perspective='CAMERA'
            space.shading.type='MATERIAL';space.shading.use_scene_world=True;space.shading.use_scene_lights=True
            space.overlay.show_overlays=False
bpy.data.texts['READ ME | WORLD FIRST'].write('\nDelivery source opens on the WORLD camera. Edit set collections here. To render the complete movie with music, choose WTSC_MASTER_4K_100S from the Scene menu, then Render Animation. WORLD has PNG still output; MASTER has UHD H264/AAC movie output.\nThe supplied source music is packed in this blend along with the painted images.\nThe v005 delivery changes only the startup view, still-output settings, audio packing and this note from the v004 movie source; visual content and timing remain the same.\n')
target=ROOT/'shots/world/WTSC_World_First_v005.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(target))
manifest=json.loads((ROOT/'notes/world_asset_manifest.json').read_text())
manifest['native_project']='shots/world/WTSC_World_First_v005.blend'
manifest['movie_render_source']='shots/world/WTSC_World_First_v004.blend'
manifest['delivery_source_change']='Startup world-camera view, PNG still output on world scene, packed source audio, and corrected paint-count note. No picture, geometry, motion or edit changes.'
(ROOT/'notes/world_asset_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('Delivery source saved',str(target))
