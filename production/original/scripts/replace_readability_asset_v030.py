import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(r'WTSC_LOCAL_WORKSPACE');sys.path.insert(0,str(R/'scripts'))
from high_crown_native_v030 import apply_high_crown
s=bpy.context.scene;assert s.name=='WTSC_PAINTED_WORLD_4K_100S_v030'
asset=apply_high_crown(s,R);trees=[s.objects[n] for n in asset['objects']]
for f in list(range(1,301))+list(range(1873,2401)):
    s.frame_set(f);bpy.context.view_layer.update()
    for o in trees:
        # The original wide tree bounds (±4.58) conservatively contain new X
        # including signed wind. Check the taller new Z extent separately.
        xx=[world_to_camera_view(s,s.camera,o.matrix_world@Vector((x,0,z))).x for x in [-4.58,4.58] for z in [0,8]]
        assert max(xx)<0 or min(xx)>1,(f,o.name,xx)
for text in bpy.data.texts:
    if text.name.startswith('CURRENT v030'):
        text.write('\nFinal foreground solution uses a new GPT-painted high-crown oak asset with a naturally bare lower trunk. Native source aspect ratio is preserved; no stretched crown or bark.\n')
s.frame_set(1);target=R/'shots/world/WTSC_Painted_World_Trailer_v030.blend';bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
p=R/'notes/world_v016/readability_and_reuse_v030.json';report=json.loads(p.read_text());report['source_sha256']=hashlib.sha256(target.read_bytes()).hexdigest();report['changed_objects']=asset['objects'];report['change']='New purpose-painted high-crown oak; source aspect ratio preserved, no warping';report['new_asset']=asset;p.write_text(json.dumps(report,indent=2));print('FINAL_READABILITY_ASSET',json.dumps(report),flush=True)
out=R/'renders/world_v016/inspection_v030_final';out.mkdir(exist_ok=True);s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
for name,f in [('01_Woods',769),('02_School',1057),('03_Camp',1417)]:s.frame_set(f);s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
