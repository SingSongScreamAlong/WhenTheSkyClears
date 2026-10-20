import bpy,json
from pathlib import Path
ROOT=Path(r'WTSC_LOCAL_WORKSPACE')
world=bpy.data.scenes['WTSC_WORLD_FIRST_4K']
world.render.compositor_device='GPU'
if world.sequence_editor:
    for strip in list(world.sequence_editor.strips):
        if strip.type=='SOUND':world.sequence_editor.strips.remove(strip)
world.render.use_sequencer=False
master=bpy.data.scenes.new('WTSC_MASTER_4K_100S')
master.render.resolution_x=3840;master.render.resolution_y=2160;master.render.resolution_percentage=100
master.render.fps=24;master.render.fps_base=1;master.frame_start=1;master.frame_end=2400
master.view_settings.view_transform='Standard';master.view_settings.look='None'
master.render.use_sequencer=True;master.render.use_compositing=False;master.render.dither_intensity=0
master.render.image_settings.media_type='VIDEO'
master.render.ffmpeg.format='MPEG4';master.render.ffmpeg.codec='H264';master.render.ffmpeg.constant_rate_factor='HIGH';master.render.ffmpeg.ffmpeg_preset='REALTIME'
master.render.ffmpeg.audio_codec='AAC';master.render.ffmpeg.audio_bitrate=320;master.render.ffmpeg.audio_mixrate=48000
master.render.filepath='//../../renders/world/WTSC_World_Atmosphere_4K_v004.mp4'
seq=master.sequence_editor_create()
picture=seq.strips.new_scene('WORLD | continuous route from native scene',world,channel=2,frame_start=1)
picture.scene_input='CAMERA'
sound=seq.strips.new_sound('MUSIC | supplied 100-second source',str(ROOT/'edit/When_The_Sky_Clears_Trailer_Music_100s.wav'),channel=1,frame_start=1)
sound.sound.filepath='//../../edit/When_The_Sky_Clears_Trailer_Music_100s.wav'
sound.volume=1;sound.keyframe_insert('volume',frame=2161);sound.volume=0;sound.keyframe_insert('volume',frame=2401)
if master.animation_data and master.animation_data.action:
    for layer in master.animation_data.action.layers:
        for st in layer.strips:
            for bag in st.channelbags:
                for fc in bag.fcurves:
                    for k in fc.keyframe_points:k.interpolation='LINEAR'
for marker in world.timeline_markers:master.timeline_markers.new(marker.name,frame=marker.frame)
master['status']='Provisional world/atmosphere pass; static vector pair; not final performance'
master['edit_world_in_scene']='WTSC_WORLD_FIRST_4K'
master['duration_seconds']=100
master['picture_source']='Native scene strip, not a flattened source movie'
master['audio_source']='User supplied WAV; volume fade frames 2161 to 2401'
assert picture.frame_final_duration==2400
assert sound.frame_final_duration==2400
bpy.context.window.scene=master
master.frame_set(1);world.frame_set(1)
bpy.data.texts['READ ME | WORLD FIRST'].write('\nNative master update\nWTSC_MASTER_4K_100S contains a native Scene strip of the world plus the supplied WAV and fade. Select WTSC_WORLD_FIRST_4K to edit the sets and camera.\n')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'shots/world/WTSC_World_First_v004.blend'))
print(json.dumps({'scene':master.name,'picture_frames':picture.frame_final_duration,'audio_frames':sound.frame_final_duration,'native_source_scene':picture.scene.name,'fps':master.render.fps,'size':[master.render.resolution_x,master.render.resolution_y]}))
