import bpy,sys
a=sys.argv[sys.argv.index('--')+1:];s=bpy.data.scenes['WTSC_WORLD_CENTERED_v034'];bpy.context.window.scene=s
s.frame_start=int(a[0]);s.frame_end=int(a[1]);s.render.resolution_percentage=100;s.render.use_sequencer=False
s.render.image_settings.media_type='VIDEO';s.render.ffmpeg.format='MPEG4';s.render.ffmpeg.codec='H264';s.render.ffmpeg.constant_rate_factor='HIGH';s.render.ffmpeg.ffmpeg_preset='GOOD';s.render.ffmpeg.audio_codec='NONE';s.render.filepath=a[2]
bpy.ops.render.render(animation=True,scene=s.name)
print('WORLD_PATCH_COMPLETED',s.frame_start,s.frame_end,flush=True)
