"""Reuse the project's proven Scene/Sound master so native Blender exports include music."""
import bpy,json
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE')
world=bpy.context.scene;assert world.name=='WTSC_PAINTED_WORLD_EDITABLE_v028'
target=R/'shots/world/WTSC_Painted_World_Editable_v029.blend';assert not target.exists()
for strip in list(world.sequence_editor.strips):
    if strip.type=='SOUND':world.sequence_editor.strips.remove(strip)
world.render.use_sequencer=False;world.render.ffmpeg.audio_codec='NONE';world.name='WTSC_WORLD_EDIT_v029'
master=bpy.data.scenes.new('WTSC_MASTER_4K_100S_v029')
master.render.resolution_x=3840;master.render.resolution_y=2160;master.render.resolution_percentage=100
master.render.fps=24;master.render.fps_base=1;master.frame_start=1;master.frame_end=2400
master.view_settings.view_transform='Standard';master.view_settings.look='None'
master.render.use_sequencer=True;master.render.use_compositing=False;master.render.dither_intensity=0
master.render.image_settings.media_type='VIDEO';master.render.ffmpeg.format='MPEG4';master.render.ffmpeg.codec='H264';master.render.ffmpeg.constant_rate_factor='HIGH';master.render.ffmpeg.ffmpeg_preset='REALTIME';master.render.ffmpeg.audio_codec='AAC';master.render.ffmpeg.audio_bitrate=320;master.render.ffmpeg.audio_mixrate=48000
master.render.filepath='//../../renders/world_v016/WTSC_Painted_World_Native_Edit_v029.mp4'
seq=master.sequence_editor_create();picture=seq.strips.new_scene('PICTURE | editable painted world camera',world,channel=2,frame_start=1);picture.scene_input='CAMERA'
sound=seq.strips.new_sound('MUSIC | supplied 100s WAV',str(R/'edit/When_The_Sky_Clears_Trailer_Music_100s.wav'),channel=1,frame_start=1);sound.sound.pack();sound.sound.filepath='//../../edit/When_The_Sky_Clears_Trailer_Music_100s.wav'
for f,v in [(1,1),(2161,1),(2400,0)]:sound.volume=v;sound.keyframe_insert('volume',frame=f)
if master.animation_data:
    for layer in master.animation_data.action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    for k in curve.keyframe_points:k.interpolation='LINEAR'
for marker in world.timeline_markers:master.timeline_markers.new(marker.name,frame=marker.frame)
master['edit_world_in_scene']=world.name;master['picture_source']='Native Scene strip; editable 3D/2.5D scene, not a movie';master['scope']='World pass with held painterly children, not finished character performance'
assert picture.frame_final_duration==2400 and sound.frame_final_duration==2400
for text in bpy.data.texts:
    if text.name.startswith('CURRENT EDITABLE v028'):
        text.name='CURRENT EDITABLE v029 | World and native music master'
        text.write('\nNATIVE EDIT MASTER v029\nEdit sets, GP and camera in WTSC_WORLD_EDIT_v029 (opens by default). For native picture+music export select WTSC_MASTER_4K_100S_v029: one actual Scene strip and the supplied packed WAV, with its last 10-second fade. This replaces the world-only export, which produced a silent AAC track with sequencing disabled. Exact externally muxed 4K movie source v027 is preserved; world visuals remain unchanged.\n')
bpy.context.window.scene=world;world.frame_set(1);master.frame_set(1);bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
report={'editable':str(target),'world_scene':world.name,'native_export_scene':master.name,'picture_strip_scene':picture.scene.name,'picture_frames':picture.frame_final_duration,'sound_frames':sound.frame_final_duration,'sound_packed':bool(sound.sound.packed_file),'visual_change_from_v027':False,'reason':'World-only use_sequencer=False export produced a silent AAC stream; native Scene+Sound master follows the proven existing project workflow.'}
(R/'notes/world_v016/native_edit_master_v029.json').write_text(json.dumps(report,indent=2));print('NATIVE_EDIT_MASTER_SAVED',json.dumps(report),flush=True)
# Verification only, not saved: render one second from a known non-silent music section.
bpy.context.window.scene=master;master.frame_start=241;master.frame_end=264;master.render.resolution_percentage=10;world.render.resolution_percentage=10;master.render.filepath=str(R/'renders/world_v016/native_audio_check_v029.mp4');master.frame_set(241)
bpy.ops.render.render(animation=True,scene=master.name)
