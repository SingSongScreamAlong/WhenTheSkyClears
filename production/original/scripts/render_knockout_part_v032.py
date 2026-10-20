import bpy,sys
from pathlib import Path
a=sys.argv[sys.argv.index('--')+1:];start,end,out=int(a[0]),int(a[1]),a[2]
s=bpy.data.scenes['WTSC_KNOCKOUT_ENDING_v032'];bpy.context.window.scene=s
s.frame_start=start;s.frame_end=end;s.render.resolution_percentage=100;s.render.use_sequencer=False
s.render.image_settings.media_type='VIDEO';s.render.ffmpeg.format='MPEG4';s.render.ffmpeg.codec='H264';s.render.ffmpeg.constant_rate_factor='HIGH';s.render.ffmpeg.ffmpeg_preset='GOOD';s.render.ffmpeg.audio_codec='NONE';s.render.filepath=out
bpy.ops.render.render(animation=True,scene=s.name)
print('ENDING_PART_COMPLETED',start,end,out,flush=True)
