import bpy,json,hashlib
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE');O=R/'locomotion/garment_continuity_v047'
meta=json.loads((O/'evidence/NATIVE_SOURCE_INSPECTION.json').read_text());P=Path(meta['source']);assert hashlib.sha256(P.read_bytes()).hexdigest()==meta['sha256']
bpy.ops.wm.open_mainfile(filepath=str(P),load_ui=False,use_scripts=False);s=bpy.data.scenes[meta['scene']];bpy.context.window.scene=s
s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=2;s.render.dither_intensity=0;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.eevee.taa_render_samples=32
out=O/'previews/baseline';out.mkdir(parents=True,exist_ok=True)
for f in range(1,64):
 s.frame_set(f);bpy.context.view_layer.update();s.render.filepath=str(out/f'{f:04d}.png');bpy.ops.render.render(write_still=True,scene=s.name)
 if f%16==0:print('BASELINE_FRAME',f,flush=True)
assert hashlib.sha256(P.read_bytes()).hexdigest()==meta['sha256']
(O/'evidence/BASELINE_RENDER_RECORD.json').write_text(json.dumps({'source':str(P),'source_sha256':meta['sha256'],'source_unchanged':True,'frames':[1,63],'fps':30,'size':[1280,720],'note':'Actual native sequential two-cycle render, not a recycled cycle.'},indent=2))
print('BASELINE_READY',flush=True)
