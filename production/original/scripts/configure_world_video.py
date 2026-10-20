import bpy,json
from pathlib import Path
ROOT=Path(r'WTSC_LOCAL_WORKSPACE')
s=bpy.context.scene
assert s.name=='WTSC_WORLD_FIRST_4K'
s.frame_set(1)
s.render.image_settings.media_type='VIDEO'
assert s.render.image_settings.file_format=='FFMPEG'
s.render.ffmpeg.format='MPEG4';s.render.ffmpeg.codec='H264'
s.render.ffmpeg.constant_rate_factor='HIGH';s.render.ffmpeg.ffmpeg_preset='REALTIME'
s.render.ffmpeg.audio_codec='AAC';s.render.ffmpeg.audio_bitrate=320;s.render.ffmpeg.audio_mixrate=48000
s.render.filepath='//../../renders/world/WTSC_World_Atmosphere_4K_v003.mp4'
s['render_method']='Native Blender FFmpeg animation; typed background renderer accepts PNG/EXR only'
s.render.dither_intensity=0
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'shots/world/WTSC_World_First_v003.blend'))
print(json.dumps({'format':s.render.image_settings.file_format,'media':s.render.image_settings.media_type,'size':[s.render.resolution_x,s.render.resolution_y],'fps':s.render.fps,'frames':[s.frame_start,s.frame_end],'path':s.render.filepath,'audio_codec':s.render.ffmpeg.audio_codec}))
