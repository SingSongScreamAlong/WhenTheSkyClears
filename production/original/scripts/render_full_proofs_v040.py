"""Actual native UHD compositor samples before full-film render freeze."""
import bpy,json
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE');e=bpy.data.scenes['WTSC_FULL_FILM_KNOCKOUT_v040'];w=bpy.data.scenes['WTSC_WORLD_CORRECTED_v040'];bpy.context.window.scene=e
folder=R/'renders/world_v016/full_knockout_checks_v040';folder.mkdir(exist_ok=True)
e.render.use_sequencer=False;e.render.resolution_percentage=100;e.render.image_settings.media_type='IMAGE';e.render.image_settings.file_format='PNG';e.render.dither_intensity=0
for frame in [241,841,1201,1609,1921,2161,2401]:
    w.frame_set(frame);e.frame_set(frame);e.render.filepath=str(folder/f'{frame}.png');bpy.ops.render.render(write_still=True,scene=e.name)
print('FULL_V040_NATIVE_UHD_PROOFS_COMPLETED',flush=True)
