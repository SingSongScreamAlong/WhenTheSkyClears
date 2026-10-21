"""Retimed legacy render for an honest matched-age comparison, effects files only."""
import bpy,json,time
from pathlib import Path
P=Path(__file__).resolve().parents[1]
s=bpy.data.scenes['FX_MOTION_v002 | real shot plate + animated native FX'];bpy.context.window.scene=s
root=bpy.data.objects['FXv002 | fixed ground origin and controls'];root['start_frame']=1824.0;root.update_tag()
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=32;s.render.threads_mode='FIXED';s.render.threads=2
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.fps=24
if hasattr(s.render,'compositor_device'):s.render.compositor_device='GPU'
s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
s.frame_start=1800;s.frame_end=1919;folder=P/'previews/reference_v002a_frames';folder.mkdir(exist_ok=True);s.render.filepath=str(folder)+'/'
started=time.perf_counter();bpy.ops.render.render(animation=True,scene=s.name)
report={'reference':'v002a current GPU proof, old hot/smoke evolution preserved','retiming':'start_frame changed1813 to1824 in memory only for matched event age','frames':[1800,1919],'fps':24,'pixels':[1920,1080],'seconds':time.perf_counter()-started,'source_file_modified':False,'render':'Eevee32samples, GPU compositor, twoCPUthreads'}
(P/'evidence/legacy_reference_render_v003.json').write_text(json.dumps(report,indent=2));print('FX_LEGACY_REFERENCE_COMPLETE',json.dumps(report),flush=True)
