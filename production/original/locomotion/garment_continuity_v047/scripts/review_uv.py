import bpy,json,hashlib,runpy
from pathlib import Path
O=Path(r'WTSC_LOCAL_WORKSPACE\locomotion\garment_continuity_v047')
P=O/'reference/PRESERVED_v046_INPUT.blend';bpy.ops.wm.open_mainfile(filepath=str(P),load_ui=False,use_scripts=False);s=bpy.data.scenes['V046 | AGE10 BONES | restored painted clothing'];bpy.context.window.scene=s
report=runpy.run_path(str(O/'scripts/fix_coat_uv.py'))['apply'](s);(O/'evidence/UPPER_COAT_UV_CANDIDATE.json').write_text(json.dumps(report,indent=2))
s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=2;s.render.dither_intensity=0;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.eevee.taa_render_samples=32
for f in [1,9,17,25]:
 s.frame_set(f);s.render.filepath=str(O/f'previews/uv_{f:02d}.png');bpy.ops.render.render(write_still=True,scene=s.name)
print('UPPER_COAT_UV_REVIEW_READY',json.dumps(report),flush=True)
