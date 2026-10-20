import bpy,json,hashlib,datetime
from pathlib import Path
O=Path(r'WTSC_LOCAL_WORKSPACE\work\production_look_v061');native=O/'native/WTSC_Physical_Ink_Wash_Forest_v061.blend';sha=hashlib.sha256(native.read_bytes()).hexdigest()
valid=json.loads((O/'evidence/FLAT_STAGE_NATIVE_VALIDATION.json').read_text());assert valid['all_checks_pass'] and valid['native_sha256']==sha
bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
s=bpy.data.scenes['WTSC_INK_WASH_DEPTH_v061'];bpy.context.window.scene=s
P=O/'previews/frames';P.mkdir(exist_ok=True)
s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=4
if hasattr(s,'eevee'):s.eevee.taa_render_samples=64
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
rows=[]
for g in range(937,1057):
 s.frame_set(g);s.render.filepath=str(P/('%04d.png'%g));bpy.ops.render.render(write_still=True,scene=s.name)
 rows.append({'frame':g,'camera':list(s.camera.matrix_world.translation),'root':list(bpy.data.objects['V047 | shared travel | steady .73125mps'].matrix_world.translation),'sha256':hashlib.sha256((P/('%04d.png'%g)).read_bytes()).hexdigest()})
 print('V061_FRAME',g,flush=True)
s.frame_set(981);s.render.resolution_x=3840;s.render.resolution_y=2160;s.render.filepath=str(O/'previews/Native_Contact_4K_v061.png');bpy.ops.render.render(write_still=True,scene=s.name)
# An explicit alternate lateral angle is a depth witness, never an inserted trailer frame.
s.render.resolution_x=1280;s.render.resolution_y=720;cam=s.camera;cam.animation_data_clear();cam.location.x+=.65;cam.location.y+=.35;s.render.filepath=str(O/'previews/Lateral_Depth_Witness_v061.png');bpy.ops.render.render(write_still=True,scene=s.name)
assert hashlib.sha256(native.read_bytes()).hexdigest()==sha
(O/'evidence/NATIVE_SEQUENCE_RENDER.json').write_text(json.dumps({'rendered_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'native_sha256':sha,'native_unchanged':True,'frames':120,'range':[937,1056],'fps':24,'resolution':[1280,720],'rows':rows,'witness_4K':'Native_Contact_4K_v061.png','lateral_witness':'Lateral_Depth_Witness_v061.png'},indent=2))
print('V061_COMPLETE_NATIVE_SEQUENCE_READY',flush=True)
