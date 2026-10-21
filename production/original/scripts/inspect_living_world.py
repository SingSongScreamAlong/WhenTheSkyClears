import bpy,json,hashlib
from pathlib import Path
ROOT=Path(r'WTSC_LOCAL_WORKSPACE')
world=bpy.data.scenes['WTSC_WORLD_FIRST_4K'];master=bpy.data.scenes['WTSC_MASTER_4K_100S'];bpy.context.window.scene=world
version='v011' if bpy.data.filepath.endswith('WTSC_Living_World_Editable_v011.blend') else 'v010'
assert bpy.data.filepath.endswith(('WTSC_Living_World_v010.blend','WTSC_Living_World_Editable_v011.blend'))
pair=bpy.data.objects['GP_Pair_STATIC_world_scale']
pair_channels=[f.data_path for l in pair.animation_data.action.layers for s in l.strips for b in s.channelbags for f in b.fcurves]
assert set(pair_channels)=={'location'}
assert [f.frame_number for l in pair.data.layers for f in l.frames]==[1]
assert not [o for o in world.objects if o.type=='ARMATURE']
root=bpy.data.collections['20 | LIVING WORLD dimensional sets'];visible=[o for o in root.all_objects if not o.hide_render]
assert len([o for o in visible if o.type=='CURVE'])==(27 if version=='v011' else 5)
proof=[]
for frame in [1,121,1489]:
    world.frame_set(frame);bpy.context.view_layer.update()
    row={'frame':frame,'shape_keys':{},'paper':list(bpy.data.objects['LW Paper tumbling 00'].location),'chimney':list(bpy.data.objects['LW Chimney rising soft smoke 0'].location)}
    for obj in visible:
        data=getattr(obj,'data',None);keys=getattr(data,'shape_keys',None)
        if keys:
            row['shape_keys'][obj.name]=float(keys.key_blocks[1].value)
            if keys.animation_data:
                assert all(d.is_valid for d in keys.animation_data.drivers),obj.name
    proof.append(row)
assert proof[0]['shape_keys']!=proof[1]['shape_keys'] and proof[0]['paper']!=proof[1]['paper']
assert proof[0]['chimney']!=proof[1]['chimney']
images=[i for i in bpy.data.images if i.name!='Render Result'];assert all(i.packed_file for i in images)
sound=next(s for s in master.sequence_editor.strips if s.type=='SOUND');assert sound.sound.packed_file
bpy.context.window.scene=master;volumes={}
for frame in [2161,2401]:master.frame_set(frame);bpy.context.view_layer.update();volumes[str(frame)]=sound.volume
assert volumes=={'2161':1.0,'2401':0.0}
master.frame_set(1);world.frame_set(1);bpy.context.window.scene=world
assert master.render.resolution_x==3840 and master.render.resolution_y==2160 and master.render.resolution_percentage==100
assert master.render.fps==24 and master.frame_end-master.frame_start+1==2400
report={'file':bpy.data.filepath,'blender':bpy.app.version_string,'source_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
 'resolution':[3840,2160],'fps':24,'frames':2400,'seconds':100,'visible_dimensional_objects':len(visible),
 'native_curve_objects':[o.name for o in visible if o.type=='CURVE'],
 'new_mesh_vertices':sum(len(o.data.vertices) for o in visible if o.type=='MESH'),
 'new_mesh_polygons':sum(len(o.data.polygons) for o in visible if o.type=='MESH'),
 'asset_roots':[o.name for o in visible if o.name.startswith('ASSET |')],
 'ambient_motion_readback':proof,'packed_images':len(images),
 'audio_packed_sha256':hashlib.sha256(sound.sound.packed_file.data).hexdigest(),'audio_volume':volumes,
 'held_GP_frames':[1],'pair_channels':pair_channels,'artistic_status':'Production iteration; no final artistic or character-performance approval.'}
(ROOT/f'notes/living_world/native_reopen_{version}.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='ambient_motion_readback'}))
