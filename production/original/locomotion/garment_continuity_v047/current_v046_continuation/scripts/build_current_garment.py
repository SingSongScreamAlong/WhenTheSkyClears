import bpy,json,hashlib,runpy,datetime
from pathlib import Path
B=Path(r'WTSC_LOCAL_WORKSPACE\locomotion\garment_continuity_v047');O=B/'current_v046_continuation'
P=O/'reference/PRESERVED_FINAL_v046_INPUT.blend';H='e993540280bc60ff5fcc1dafe316f7c8457c5c8750a1110b8f6e307a865d005d'
assert hashlib.sha256(P.read_bytes()).hexdigest()==H
bpy.ops.wm.open_mainfile(filepath=str(P),load_ui=False,use_scripts=False)
s=bpy.data.scenes['V046 | AGE10 BONES | restored painted clothing'];bpy.context.window.scene=s
report={'input_sha256':H,'source_modified_utc':'2026-10-18T21:30:20.628944+00:00','built_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'newest_v046_uv_material_depth_origins_preserved':True,'earlier_manual_uv_remap_applied':False}
report['garment_lag']=runpy.run_path(str(B/'scripts/body_followthrough.py'))['apply'](s)
s.name='V047b | AGE TEN | garment continuity';s['V047_final_v046_input_sha256']=H
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(O/'native/WTSC_Age10_Garment_Continuity_v047b.blend'))
(O/'evidence/GARMENT_NATIVE_REPORT.json').write_text(json.dumps(report,indent=2))
s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100
s.render.threads_mode='FIXED';s.render.threads=2;s.render.dither_intensity=0;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.eevee.taa_render_samples=32
for f in [1,9,17,25]:
 s.frame_set(f);s.render.filepath=str(O/f'previews/garment_{f:02d}.png');bpy.ops.render.render(write_still=True,scene=s.name)
assert hashlib.sha256(P.read_bytes()).hexdigest()==H
print('CURRENT_V046_GARMENT_CONTINUATION_READY',flush=True)
