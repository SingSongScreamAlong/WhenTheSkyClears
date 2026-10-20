import bpy
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE');w=bpy.data.scenes['WTSC_WORLD_CORRECTED_v039'];e=bpy.data.scenes['WTSC_FULL_FILM_KNOCKOUT_v039']
# Two modest quarter-size technical stills only; no full-quality competing job.
for s,tag in [(w,'world'),(e,'knockout')]:
 bpy.context.window.scene=s;s.render.resolution_percentage=25;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.frame_set(1609);s.render.filepath=str(R/f'renders/world_v016/camp_benchmark_checks_v039/{tag}_1609_960.png');bpy.ops.render.render(write_still=True,scene=s.name)
print('LOW_COST_BENCHMARK_CHECKS_DONE',flush=True)
