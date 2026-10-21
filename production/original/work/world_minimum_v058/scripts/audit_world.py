import bpy,json,hashlib
from pathlib import Path
O=Path(__file__).parent;O.mkdir(exist_ok=True)
SRC=Path(r'WTSC_LOCAL_WORKSPACE\work\world_facade_v057\WTSC_Continuous_Painterly_Facade_Proof_v057.blend')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SRC)=='87c897b5ccc178b1288f5d614eeaa34d642b8e8ac2c239bcd2ab50a79569361a'
bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False,use_scripts=False);s=bpy.data.scenes['WTSC_CONTINUOUS_FACADE_SOURCE_LIGHTING_v057_TEST'];bpy.context.window.scene=s
s.render.engine='BLENDER_EEVEE';s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=2;s.eevee.taa_render_samples=32;s.render.use_sequencer=False;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.dither_intensity=0
rows=[]
for f in [241,601,961,1201,1537,1849,2161,2377]:
 s.frame_set(f);bpy.context.view_layer.update();s.render.filepath=str(O/f'AUDIT_{f:04d}.png');bpy.ops.render.render(write_still=True,scene=s.name);rows.append({'frame':f,'seconds':(f-1)/24,'file':s.render.filepath,'camera':[list(x) for x in s.camera.matrix_world]});print('AUDIT_FRAME',f,flush=True)
data={'source':str(SRC),'source_sha256':sha(SRC),'source_unchanged':sha(SRC)=='87c897b5ccc178b1288f5d614eeaa34d642b8e8ac2c239bcd2ab50a79569361a','resolution':[1280,720],'rows':rows,'objects':[{'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None} for o in s.objects]}
(O/'WORLD_AUDIT_RENDER_RECORD.json').write_text(json.dumps(data,indent=2));print('WORLD_AUDIT_READY',flush=True)
