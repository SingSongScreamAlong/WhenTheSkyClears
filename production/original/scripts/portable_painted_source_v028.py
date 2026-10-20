"""Portable editable checkpoint; exact movie-render source v027 remains immutable."""
import bpy,json,hashlib
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE')
s=bpy.context.scene;assert s.name=='WTSC_PAINTED_WORLD_4K_100S_v027'
target=R/'shots/world/WTSC_Painted_World_Editable_v028.blend';assert not target.exists()
sound=next(st for st in s.sequence_editor.strips if st.type=='SOUND')
sound.sound.pack()
s.render.ffmpeg.audio_codec='AAC';s.render.ffmpeg.audio_bitrate=320;s.render.ffmpeg.audio_mixrate=48000
s['status']='Current animated painted world checkpoint. See delivery manifest for movie validation.'
s['approval']='Painterly direction liked; no final art or motion approval inferred.'
s['scope']='100-second animated world; near-age painterly GP pair held and translated intact.'
s['exact_movie_render_source']='WTSC_Painted_World_Trailer_v027.blend'
s.name='WTSC_PAINTED_WORLD_EDITABLE_v028'
s.render.filepath='//../../renders/world_v016/WTSC_Painted_World_4K_Edit_v028.mp4'
for text in bpy.data.texts:
    if text.name.startswith('CURRENT v027'):
        value=text.as_string()+'\nPORTABLE EDITABLE v028: visual scene unchanged from exact movie source v027. User WAV is packed and AAC audio export is enabled. Source metadata and export/audio packaging only; all geometry, materials, camera/GP/environment keys remain unchanged. Exact movie-render source is retained separately.\n'
        text.name='CURRENT EDITABLE v028 | Painted world';text.clear();text.write(value)
bpy.ops.file.pack_all()
s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
report={'editable':str(target),'exact_render_source':str(R/'shots/world/WTSC_Painted_World_Trailer_v027.blend'),'visual_change':False,'changed_fields':['Scene name/status/export filepath','Packed supplied WAV','AAC audio export enabled','Current source notes'],'sound_packed':bool(sound.sound.packed_file),'image_files_unpacked':[im.name for im in bpy.data.images if im.source=='FILE' and not im.packed_file],'audio_codec':s.render.ffmpeg.audio_codec,'render_resolution':[s.render.resolution_x,s.render.resolution_y],'frame_range':[s.frame_start,s.frame_end]}
assert report['sound_packed'] and not report['image_files_unpacked']
(R/'notes/world_v016/portable_editable_v028.json').write_text(json.dumps(report,indent=2))
print('PORTABLE_EDITABLE_SAVED',json.dumps(report),flush=True)
# Low-resolution one-second native audio export smoke check; source stays at UHD/100 seconds.
s.render.resolution_percentage=10;s.frame_start=1;s.frame_end=24;s.render.filepath=str(R/'renders/world_v016/native_audio_check_v028.mp4')
bpy.ops.render.render(animation=True)
