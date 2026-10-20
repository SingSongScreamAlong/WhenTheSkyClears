import bpy,json,hashlib
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE')
world=bpy.data.scenes['WTSC_WORLD_EDIT_v029'];master=bpy.data.scenes['WTSC_MASTER_4K_100S_v029']
bpy.context.window.scene=world
code=(R/'scripts/audit_world_motion_v026.py').read_text().replace("assert s.name=='WTSC_PAINTED_WORLD_4K_100S_v026'","assert s.name=='WTSC_WORLD_EDIT_v029'").replace('native_motion_audit_v026.json','native_motion_audit_v029.json')
exec(compile(code,'audit_world_motion_v029','exec'))
old=json.loads((R/'notes/world_v016/native_motion_audit_v027.json').read_text());new=json.loads((R/'notes/world_v016/native_motion_audit_v029.json').read_text())
assert old['frame_samples']==new['frame_samples'],'World camera/drawing/coherence samples changed'
assert old['smoke_anchors']==new['smoke_anchors'],'Smoke attachments changed'
assert new['native_output']==[3840,2160,100,24,1,2400]
bpy.context.window.scene=master
sound=next(st for st in master.sequence_editor.strips if st.type=='SOUND');picture=next(st for st in master.sequence_editor.strips if st.type=='SCENE')
volumes={}
for f in [1,2161,2281,2400]:master.frame_set(f);volumes[str(f)]=sound.volume
assert abs(volumes['2161']-1)<1e-6 and 0.45<volumes['2281']<.55 and volumes['2400']==0
assert sound.sound.packed_file and picture.scene==world
assert all(im.packed_file for im in bpy.data.images if im.source=='FILE')
assert master.render.resolution_x==3840 and master.render.resolution_y==2160 and master.render.resolution_percentage==100
assert master.frame_start==1 and master.frame_end==2400 and master.render.fps==24
audio=json.loads((R/'notes/world_v016/native_audio_verified_v029.json').read_text());assert audio['native_master_audio_present']
report={'editable':bpy.data.filepath,'editable_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'exact_render_source':old['source'],'exact_render_source_sha256':old['source_sha256'],'world_samples_identical_to_v027':True,'smoke_anchors_identical':True,'world_scene':world.name,'master_scene':master.name,'master_range':[master.frame_start,master.frame_end],'master_resolution':[3840,2160],'fps':24,'picture_strip_frames':picture.frame_final_duration,'sound_strip_frames':sound.frame_final_duration,'music_packed':True,'all_file_images_packed':True,'native_audio_export_checked':audio,'master_fade_volumes':volumes,'visual_change':False,'known_limits':'Technical persistence/audio/package checks; not artistic approval.'}
(R/'notes/world_v016/portable_reopen_v029.json').write_text(json.dumps(report,indent=2));print('PORTABLE_REOPEN_PASSED',json.dumps(report),flush=True)
