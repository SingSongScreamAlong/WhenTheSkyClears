import bpy,json,hashlib
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE')
O=Path(r'WTSC_LOCAL_USER\Documents\Codex\2026-10-16\task\world_art_v048');(O/'before').mkdir(exist_ok=True)
src=R/'shots/world/WTSC_Painted_World_Full_Trailer_Editable_v040.blend'
bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False)
s=bpy.data.scenes['WTSC_WORLD_CORRECTED_v040'];bpy.context.window.scene=s
s.render.resolution_x=3840;s.render.resolution_y=2160;s.render.resolution_percentage=25;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.use_sequencer=False;s.render.threads_mode='FIXED';s.render.threads=2
s.eevee.taa_render_samples=16
for f,name in [(241,'peaceful'),(1201,'transition'),(1849,'war_zone')]:
 s.frame_set(f);s.render.filepath=str(O/'before'/f'{name}_{f}_960.png');bpy.ops.render.render(write_still=True,scene=s.name);print('BASELINE_DONE',name,flush=True)
print('SOURCE_UNCHANGED',hashlib.sha256(src.read_bytes()).hexdigest(),flush=True)
