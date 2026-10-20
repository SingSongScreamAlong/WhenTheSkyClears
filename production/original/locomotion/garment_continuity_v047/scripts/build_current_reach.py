import bpy,json,hashlib,runpy,datetime
from pathlib import Path
B=Path(r'WTSC_LOCAL_WORKSPACE\locomotion\garment_continuity_v047');O=B/'current_v046_continuation'
P=O/'native/WTSC_Age10_Garment_Continuity_v047b.blend';H=hashlib.sha256(P.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(P),load_ui=False,use_scripts=False)
s=bpy.data.scenes['V047b | AGE TEN | garment continuity'];bpy.context.window.scene=s
report=json.loads((O/'evidence/GARMENT_NATIVE_REPORT.json').read_text())
report['paired_reach']=runpy.run_path(str(B/'scripts/paired_reach_refined.py'))['apply'](s)
s.name='V047b | AGE TEN | reach and contact';s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'native/WTSC_Age10_Paired_Reach_v047b.blend'))
(O/'evidence/PAIRED_REACH_NATIVE_REPORT.json').write_text(json.dumps(report,indent=2))
s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100
s.render.threads_mode='FIXED';s.render.threads=2;s.render.dither_intensity=0;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.eevee.taa_render_samples=32
for f in [1,25,36,40,45,51,55,72,94]:
 s.frame_set(f);s.render.filepath=str(O/f'previews/reach_{f:02d}.png');bpy.ops.render.render(write_still=True,scene=s.name)
assert hashlib.sha256(P.read_bytes()).hexdigest()==H
print('CURRENT_V046_REFINED_CONTACT_READY',flush=True)
