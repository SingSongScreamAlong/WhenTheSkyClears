"""Portable final authoring companion; keep immutable v037 render source intact."""
import bpy,json,hashlib
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE');out=R/'shots/world/WTSC_Full_Knockout_Trailer_Editable_v038.blend';assert not out.exists()
render_source=Path(bpy.data.filepath);original_sha=hashlib.sha256(render_source.read_bytes()).hexdigest();m=bpy.data.scenes['WTSC_MASTER_4K_106S_v037'];w=bpy.data.scenes['WTSC_WORLD_CORRECTED_v037'];e=bpy.data.scenes['WTSC_FULL_FILM_KNOCKOUT_v037']
sound=next(s for s in m.sequence_editor.strips if s.type=='SOUND')
# The movie mux uses sample-accurate90–100 fade. Frame2401 is precisely100s,
# and lies at the sound strip's exclusive end. Match that boundary natively.
path=sound.path_from_id('volume')
if m.animation_data and m.animation_data.action:
 for layer in m.animation_data.action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for fc in list(bag.fcurves):
     if fc.data_path==path:bag.fcurves.remove(fc)
for frame,value in [(1,1),(2161,1),(2401,0)]:sound.volume=value;sound.keyframe_insert('volume',frame=frame)
for layer in m.animation_data.action.layers:
 for strip in layer.strips:
  for bag in strip.channelbags:
   for fc in bag.fcurves:
    for k in fc.keyframe_points:k.interpolation='LINEAR'
for font in bpy.data.fonts:
 if font.filepath and font.filepath!='<builtin>' and not font.packed_file:
  try:font.pack()
  except RuntimeError:pass
bpy.ops.file.pack_all();m.name='WTSC_MASTER_4K_106S_v038';m.render.filepath='//../../renders/world_v016/WTSC_Full_Knockout_Native_Edit_v038.mp4'
report={'editable':str(out),'immutable_render_source':str(render_source),'immutable_render_source_sha256':original_sha,'native_export_scene':m.name,'world_scene_unchanged':w.name,'picture_scene_unchanged':e.name,'world_or_typography_change':False,'only_changes':'Native audio fade ends at exact100s frame2401 instead of previous last-picture-frame2400; pack installed editable-embedding fonts for local authoring; clear current note. Movie mux already uses exact90–100.','sound_frames':[sound.frame_final_start,sound.frame_final_end],'fade_keys':[[1,1],[2161,1],[2401,0]],'duration_seconds':106,'resolution':[3840,2160],'fps':24,'frames':2544,'font_scope':'Local authoring companion only; delivered MP4 contains pixels, no font files. WindowsfsType8 inspected for selected fonts.'}
note=bpy.data.texts.new('CURRENT v038 | Final106s native editable master');note.write(json.dumps(report,indent=2));bpy.context.window.scene=m;m.frame_set(1);w.frame_set(1);e.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
assert hashlib.sha256(render_source.read_bytes()).hexdigest()==original_sha
report['editable_sha256']=hashlib.sha256(out.read_bytes()).hexdigest();(R/'notes/world_v016/final_editable_v038.json').write_text(json.dumps(report,indent=2));print('FINAL_EDITABLE_SAVED',json.dumps(report),flush=True)
