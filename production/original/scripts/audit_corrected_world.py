import bpy,json,hashlib,struct,sys
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE')
portable='--portable' in sys.argv
scene_name='WTSC_WORLD_EDIT_v031' if portable else 'WTSC_PAINTED_WORLD_4K_100S_v030'
version='v031' if portable else 'v030'
bpy.context.window.scene=bpy.data.scenes[scene_name]
code=(R/'scripts/audit_world_motion_v026.py').read_text().replace("assert s.name=='WTSC_PAINTED_WORLD_4K_100S_v026'",f"assert s.name=='{scene_name}'").replace('native_motion_audit_v026.json',f'native_motion_audit_{version}.json')
exec(compile(code,'audit_corrected_native_world','exec'))
path=R/f'notes/world_v016/native_motion_audit_{version}.json';report=json.loads(path.read_text());world=bpy.context.scene
trees=[]
for o in sorted([o for o in world.objects if o.name.startswith('v030 | High crown foreground oak ')],key=lambda o:o.name):
    shape=[]
    for key in o.data.shape_keys.key_blocks:
        blob=b''.join(struct.pack('<3f',*p.co) for p in key.data);shape.append({'name':key.name,'coordinates_sha256':hashlib.sha256(blob).hexdigest()})
    uvblob=b''.join(struct.pack('<2f',*p.uv) for p in o.data.uv_layers.active.data)
    mat=o.data.materials[0];tex=next(n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE')
    trees.append({'name':o.name,'location':list(o.location),'scale':list(o.scale),'rotation':list(o.rotation_euler),'shape_keys':shape,'uv_sha256':hashlib.sha256(uvblob).hexdigest(),'drivers':[{'path':d.data_path,'expression':d.driver.expression} for d in o.data.shape_keys.animation_data.drivers],'paint_pixels':list(tex.image.size),'paint_sha256':hashlib.sha256(bytes(tex.image.packed_file.data)).hexdigest()})
assert len(trees)==4;report['high_crown_tree_fingerprints']=trees;path.write_text(json.dumps(report,indent=2))
if portable:
    old=json.loads((R/'notes/world_v016/native_motion_audit_v030.json').read_text())
    assert old['frame_samples']==report['frame_samples']
    assert old['smoke_anchors']==report['smoke_anchors']
    assert old['high_crown_tree_fingerprints']==trees
    master=bpy.data.scenes['WTSC_MASTER_4K_100S_v031'];bpy.context.window.scene=master
    sound=next(st for st in master.sequence_editor.strips if st.type=='SOUND');picture=next(st for st in master.sequence_editor.strips if st.type=='SCENE')
    values={}
    for f in [1,2161,2281,2400]:master.frame_set(f);values[str(f)]=sound.volume
    assert abs(values['2161']-1)<1e-6 and .45<values['2281']<.55 and values['2400']==0
    assert sound.sound.packed_file and picture.scene==world
    assert all(im.packed_file for im in bpy.data.images if im.source=='FILE')
    assert [master.render.resolution_x,master.render.resolution_y,master.render.resolution_percentage,master.render.fps,master.frame_start,master.frame_end]==[3840,2160,100,24,1,2400]
    audio=json.loads((R/'notes/world_v016/native_audio_verified_v031.json').read_text());assert audio['native_master_audio_present']
    p={'editable':bpy.data.filepath,'editable_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'exact_render_source':old['source'],'exact_render_source_sha256':old['source_sha256'],'world_samples_identical_to_v030':True,'tree_geometry_uv_paint_and_wind_identical':True,'world_scene':world.name,'master_scene':master.name,'master_range':[1,2400],'master_resolution':[3840,2160],'fps':24,'picture_strip_frames':picture.frame_final_duration,'sound_strip_frames':sound.frame_final_duration,'music_packed':True,'all_file_images_packed':True,'native_audio_export_checked':audio,'master_fade_volumes':values,'visual_change':False,'known_limits':'Technical persistence and motion-coherence proof, not artistic approval.'}
    (R/'notes/world_v016/portable_reopen_v031.json').write_text(json.dumps(p,indent=2));print('CORRECTED_PORTABLE_REOPEN_PASSED',json.dumps(p),flush=True)
else:print('CORRECTED_EXACT_SOURCE_AUDIT_PASSED',len(trees),flush=True)
