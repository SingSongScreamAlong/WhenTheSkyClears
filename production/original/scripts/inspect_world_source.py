import bpy,json,hashlib
from pathlib import Path
ROOT=Path(r'WTSC_LOCAL_WORKSPACE')
world=bpy.data.scenes['WTSC_WORLD_FIRST_4K'];master=bpy.data.scenes['WTSC_MASTER_4K_100S']
pair=bpy.data.objects['GP_Pair_STATIC_world_scale']
channels=[]
for layer in pair.animation_data.action.layers:
    for strip in layer.strips:
        for bag in strip.channelbags:channels.extend(f.data_path for f in bag.fcurves)
frames=[f.frame_number for layer in pair.data.layers for f in layer.frames]
images=[]
for image in bpy.data.images:
    if image.name=='Render Result':continue
    images.append({'name':image.name,'size':list(image.size),'packed':bool(image.packed_file),
                   'relative_path':image.filepath,'resolved':bpy.path.abspath(image.filepath)})
sound=next(s for s in master.sequence_editor.strips if s.type=='SOUND')
original_scene=bpy.context.window.scene
bpy.context.window.scene=master
volumes={}
for frame in [1,2161,2401]:
    master.frame_set(frame)
    bpy.context.view_layer.update()
    volumes[str(frame)]=sound.volume
master.frame_set(1);world.frame_set(1)
bpy.context.window.scene=original_scene
report={'source_path':bpy.data.filepath,'blender_version':bpy.app.version_string,
  'startup_scene':original_scene.name,
  'world_scene':world.name,'master_scene':master.name,
  'resolution':[master.render.resolution_x,master.render.resolution_y],
  'resolution_percentage':master.render.resolution_percentage,'fps':master.render.fps,
  'frame_range':[master.frame_start,master.frame_end],'duration_seconds':(master.frame_end-master.frame_start+1)/master.render.fps,
  'world_set_collections':[c.name for c in world.collection.children],
  'native_GP_objects':[o.name for o in world.objects if o.type=='GREASEPENCIL'],
  'armatures_in_world':[o.name for o in world.objects if o.type=='ARMATURE'],
  'pair_held_drawing_frames':frames,'pair_animation_channels':channels,
  'native_picture_strips':[{'name':s.name,'scene':s.scene.name,'frames':s.frame_final_duration} for s in master.sequence_editor.strips if s.type=='SCENE'],
  'audio':{'path':sound.sound.filepath,'packed':bool(sound.sound.packed_file),'packed_bytes':sound.sound.packed_file.size if sound.sound.packed_file else 0,'packed_sha256':hashlib.sha256(sound.sound.packed_file.data).hexdigest() if sound.sound.packed_file else None,'resolved_path':bpy.path.abspath(sound.sound.filepath),'file_exists':Path(bpy.path.abspath(sound.sound.filepath)).is_file(),'frames':sound.frame_final_duration,'volume_keys_readback':volumes},
  'paintings':images,'status':'world and set atmosphere pass; human artistic approval pending'}
assert report['resolution']==[3840,2160] and report['resolution_percentage']==100
assert report['duration_seconds']==100 and report['fps']==24
assert frames==[1] and set(channels)=={'location'}
assert not report['armatures_in_world']
assert len(report['native_picture_strips'])==1 and report['native_picture_strips'][0]['frames']==2400
assert report['audio']['file_exists'] and report['audio']['frames']==2400
assert volumes['2161']==1 and volumes['2401']==0
assert all(i['packed'] for i in images)
if bpy.data.filepath.endswith(('v005.blend','v006.blend')):
    assert report['audio']['packed'] and report['audio']['packed_bytes']>19000000
    assert report['audio']['packed_sha256']==hashlib.sha256((ROOT/'edit/When_The_Sky_Clears_Trailer_Music_100s.wav').read_bytes()).hexdigest()
if bpy.data.filepath.endswith('v006.blend'):
    assert original_scene==world
    assert bpy.data.materials['Battlefield ruin line paint'].surface_render_method=='BLENDED'
    assert bpy.data.materials['Far ruined street dissolves into ash paint'].surface_render_method=='BLENDED'
(ROOT/'notes/world_native_reopen_verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ['paintings','world_set_collections']}))
