import bpy,json,hashlib
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE');m=bpy.data.scenes['WTSC_MASTER_4K_106S_v038'];w=bpy.data.scenes['WTSC_WORLD_CORRECTED_v037'];e=bpy.data.scenes['WTSC_FULL_FILM_KNOCKOUT_v037']
assert (m.render.resolution_x,m.render.resolution_y,m.render.resolution_percentage,m.render.fps,m.frame_start,m.frame_end)==(3840,2160,100,24,1,2544)
assert m.render.use_sequencer and m.render.ffmpeg.audio_codec=='AAC'
picture=next(s for s in m.sequence_editor.strips if s.type=='SCENE');sound=next(s for s in m.sequence_editor.strips if s.type=='SOUND');assert picture.scene==e and picture.frame_final_duration==2544 and sound.frame_final_end==2401 and sound.sound.packed_file
volumes=[]
for f in [1,2161,2281,2400,2401]:m.frame_set(f);volumes.append([f,sound.volume])
assert abs(volumes[2][1]-.5)<1e-5 and 0<volumes[3][1]<.005 and volumes[-1][1]==0
images={};fonts={}
def collect(nt):
 if not nt:return
 for n in nt.nodes:
  if n.type=='TEX_IMAGE' and n.image and n.image.source=='FILE':images[n.image.name]=n.image
  if n.type=='GROUP':collect(n.node_tree)
for ob in w.objects:
 if hasattr(ob.data,'materials'):
  for mat in ob.data.materials:
   if mat:collect(mat.node_tree)
for s in [w,e]:
 for ob in s.objects:
  if ob.type=='FONT':fonts[ob.data.font.name]=ob.data.font
assert all(i.packed_file for i in images.values())
assert all(f.packed_file or f.filepath=='<builtin>' for f in fonts.values())
assert not any(n.bl_idname=='CompositorNodeImage' for n in e.compositing_node_group.nodes)
report={'editable':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'master_scene':m.name,'frames':2544,'seconds':106,'output':[3840,2160,24],'picture_scene_strip':picture.scene.name,'music_packed':True,'sound_volume_samples':volumes,'used_images_packed':[{'name':i.name,'pixels':list(i.size)} for i in images.values()],'used_fonts_packed':[{'name':f.name,'path':f.filepath} for f in fonts.values()],'picture_cache_movie_dependency':False,'versioned_native_paths':{'world':w.render.filepath,'picture':e.render.filepath,'master':m.render.filepath},'only_authoring_companion_changes':'Precise100s native audio fade boundary, packed fonts, versioned output paths; picture remains same immutable037 source.'}
(R/'notes/world_v016/portable_readback_v038.json').write_text(json.dumps(report,indent=2));print('EDITABLE_REOPEN_VERIFIED',json.dumps({'images':len(images),'fonts':len(fonts),'volumes':volumes,'frames':2544}),flush=True)
