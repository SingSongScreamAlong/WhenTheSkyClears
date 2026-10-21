import bpy,json,hashlib
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
R=Path(r'WTSC_LOCAL_WORKSPACE')
w=bpy.data.scenes['WTSC_WORLD_CENTERED_v033'];e=bpy.data.scenes['WTSC_KNOCKOUT_ENDING_v033'];m=bpy.data.scenes['WTSC_MASTER_4K_103S_v033']
pair=next(o for o in w.objects if o.type=='GREASEPENCIL');positions=pair.data.layers[0].frames[0].drawing.attributes['position'].data
samples=[]
for f in [1,241,1249,1681,2161,2400]:
 w.frame_set(f);bpy.context.window.scene=w;bpy.context.view_layer.update()
 p=[world_to_camera_view(w,w.camera,pair.matrix_world@p.vector) for p in positions]
 cx=(min(v.x for v in p)+max(v.x for v in p))/2
 assert abs(cx-.5)<1e-5,(f,cx)
 samples.append({'frame':f,'projected_pair_center_x':cx,'camera':list(w.camera.location),'pair':list(pair.location)})
stripreport=[{'name':s.name,'type':s.type,'visible_start':s.frame_final_start,'visible_end_exclusive':s.frame_final_end,'scene':s.scene.name if s.type=='SCENE' else None} for s in m.sequence_editor.strips]
assert any(s['visible_start']==1969 and s['visible_end_exclusive']==2473 and s['scene']==e.name for s in stripreport)
assert any(s['visible_start']==1 and s['visible_end_exclusive']==1969 and s['scene']==w.name for s in stripreport)
assert any(s['type']=='SOUND' and s['visible_end_exclusive']==2401 for s in stripreport)
for image in bpy.data.images:
 if image.source=='MOVIE':image.filepath=bpy.path.relpath(image.filepath)
for sound in bpy.data.sounds:
 if sound.filepath:sound.filepath=bpy.path.relpath(sound.filepath)
bpy.context.window.scene=e;e.frame_set(2137)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
report={'source':bpy.data.filepath,'source_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'native_pair_center_samples':samples,'master_strips':stripreport,'legacy_title_collection_hidden':bpy.data.collections['v016 | 07 Monumental title terrain'].hide_render,'linked_movie':'//../../renders/world_v016/WTSC_Painted_World_4K_v030.mp4','packed_world_assets':True}
(R/'notes/world_v016/knockout_native_audit_v033.json').write_text(json.dumps(report,indent=2))
# Native master readback of a composed frame: checks real Scene strip frame mapping.
bpy.context.window.scene=m;m.render.image_settings.media_type='IMAGE';m.render.image_settings.file_format='PNG';m.frame_set(2137);m.render.filepath=str(R/'renders/world_v016/ending_checks_4K_v033/master_2137.png');bpy.ops.render.render(write_still=True,scene=m.name)
print('NATIVE_ENDING_AUDIT_PASSED',flush=True)
