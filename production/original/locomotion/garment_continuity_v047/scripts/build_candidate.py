import bpy,json,hashlib,runpy,datetime
from pathlib import Path
O=Path(r'WTSC_LOCAL_WORKSPACE\locomotion\garment_continuity_v047')
P=O/'reference/PRESERVED_v046_INPUT.blend'
H='0bac9af67c64a3a215093033c384c063e3631f6dcf8c3e7b63abe8184c9b5dd9'
assert hashlib.sha256(P.read_bytes()).hexdigest()==H
bpy.ops.wm.open_mainfile(filepath=str(P),load_ui=False,use_scripts=False)
s=bpy.data.scenes['V046 | AGE10 BONES | restored painted clothing'];bpy.context.window.scene=s
report={'input_sha256':H,'built_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
report['coat_uv']=runpy.run_path(str(O/'scripts/fix_coat_uv.py'))['apply'](s)
report['garment_lag']=runpy.run_path(str(O/'scripts/body_followthrough.py'))['apply'](s)
s.name='V047 | AGE TEN | garment continuity'
s['V047_input_sha256']=H
s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'native/WTSC_Age10_Garment_Continuity_v047.blend'))
(O/'evidence/GARMENT_NATIVE_REPORT.json').write_text(json.dumps(report,indent=2))
report['paired_reach']=runpy.run_path(str(O/'scripts/paired_reach.py'))['apply'](s)
s.name='V047 | AGE TEN | reach and contact'
s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'native/WTSC_Age10_Paired_Reach_v047.blend'))
(O/'evidence/PAIRED_REACH_NATIVE_REPORT.json').write_text(json.dumps(report,indent=2))
s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100
s.render.threads_mode='FIXED';s.render.threads=2;s.render.dither_intensity=0
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.eevee.taa_render_samples=32
for f in [1,25,40,55,72,94]:
 s.frame_set(f);s.render.filepath=str(O/f'previews/reach_{f:02d}.png');bpy.ops.render.render(write_still=True,scene=s.name)
assert hashlib.sha256(P.read_bytes()).hexdigest()==H
print('V047_NATIVE_AND_KEY_REVIEW_READY',flush=True)
