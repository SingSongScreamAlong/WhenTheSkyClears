import bpy,json,hashlib,struct
from mathutils import Vector
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
R=Path(r'WTSC_LOCAL_WORKSPACE')
w=bpy.data.scenes['WTSC_WORLD_CENTERED_v034'];m=bpy.data.scenes['WTSC_MASTER_4K_103S_v034'];e=bpy.data.scenes['WTSC_KNOCKOUT_ENDING_v034'];bpy.context.window.scene=w
pair=next(o for o in w.objects if o.type=='GREASEPENCIL');oldcam=next(o for o in w.objects if o.type=='CAMERA' and abs(o.data.lens-50)<.001)
src_center=(.34999988973140717,.26261744648218155);rows=[];drawings=[]
for f in [1,1249,1681,1968]:
 w.frame_set(f);bpy.context.view_layer.update();positions=pair.data.layers[0].frames[0].drawing.attributes['position'].data
 drawings.append(hashlib.sha256(b''.join(struct.pack('fff',*p.vector) for p in positions)).hexdigest())
 p=[world_to_camera_view(w,w.camera,pair.matrix_world@p.vector) for p in positions];cx=(min(v.x for v in p)+max(v.x for v in p))/2;cy=(min(v.y for v in p)+max(v.y for v in p))/2
 assert abs(cx-.5)<1e-5 and abs(cy-.5)<1e-5
 errors=[]
 if f<=1681:
  for dx in [-4,0,4]:
   for y in [0,2,20,180]:
    for z in [0,3,8]:
     point=Vector((oldcam.location.x+dx,y,z));a=world_to_camera_view(w,oldcam,point);b=world_to_camera_view(w,w.camera,point)
     errors.extend([abs(b.x-(2*(a.x-src_center[0])+.5))*3840,abs(b.y-(2*(a.y-src_center[1])+.5))*2160])
  assert max(errors)<.03,max(errors)
 rows.append({'frame':f,'pair_center':[cx,cy],'world_projection_vs_original_2x_crop_max_pixel_error':max(errors) if errors else None})
assert len(set(drawings))==1 and sum(len(l.frames) for l in pair.data.layers)==1
strips=[{'type':s.type,'name':s.name,'start':s.frame_final_start,'end_exclusive':s.frame_final_end,'scene':s.scene.name if s.type=='SCENE' else None} for s in m.sequence_editor.strips]
assert any(s['start']==1 and s['end_exclusive']==1969 and s['scene']==w.name for s in strips)
assert any(s['start']==1969 and s['end_exclusive']==2473 and s['scene']==e.name for s in strips)
sound=next(s for s in m.sequence_editor.strips if s.type=='SOUND');volumes=[]
for f in [1,1968,1969,2161,2281,2400]:m.frame_set(f);volumes.append([f,sound.volume])
assert all(abs(v-1)<1e-6 for f,v in volumes if f<=2161) and abs(volumes[-1][1])<1e-6
report={'source':bpy.data.filepath,'source_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'native_projection_checks':rows,'cached_crop_integer_rounding_error_pixels_y':.507368803024292,'held_drawing_sha256':drawings[0],'held_drawing_frames':1,'native_master_strips':strips,'native_master_sound_volume':volumes,'sound_packed':bool(sound.sound.packed_file),'render_output':[m.render.resolution_x,m.render.resolution_y,m.render.fps,m.frame_start,m.frame_end],'linked_movie':[i.filepath for i in bpy.data.images if i.source=='MOVIE'],'legacy_title_hidden':bpy.data.collections['v016 | 07 Monumental title terrain'].hide_render,'limitation':'0–70 cached crop effective1080; native70–82 UHD; ending cached fill effective1080. At82 deliberate cut to initially black knockout, clean52–70 world replay inside glyphs; exact pair center and scale preserved.'}
(R/'notes/world_v016/complete_native_audit_v034.json').write_text(json.dumps(report,indent=2));print('COMPLETE_NATIVE_AUDIT_PASSED',json.dumps(rows),flush=True)
