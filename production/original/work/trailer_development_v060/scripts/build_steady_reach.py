import bpy,json,runpy,hashlib
from pathlib import Path
O=Path(r'WTSC_LOCAL_WORKSPACE\work\trailer_development_v060')
P=O/'reference/PRESERVED_STEADY_PAIR_v047.blend';H='29a4d9f794187602af43f7349f2b01c1019f39cba9f1d1278b966b78d1770103'
assert hashlib.sha256(P.read_bytes()).hexdigest()==H
bpy.ops.wm.open_mainfile(filepath=str(P),load_ui=False,use_scripts=False)
s=bpy.data.scenes['V047 | STEADY ORDINARY WALK | no stumble baseline'];bpy.context.window.scene=s
r=runpy.run_path(str(O/'scripts/paired_reach_steady.py'))['apply'](s)
s.name='V060 | STEADY PAIR | first hand contact';s.frame_end=151;s.frame_set(1)
(O/'evidence/STEADY_REACH_BUILD.json').write_text(json.dumps(r,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(O/'native/WTSC_Steady_Paired_Reach_v060.blend'),compress=True)
s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=2;s.eevee.taa_render_samples=24;s.render.image_settings.file_format='PNG'
for f in [1,25,40,55,94,150]:
 s.frame_set(f);s.render.filepath=str(O/f'previews/steady_reach_{f:03d}.png');bpy.ops.render.render(write_still=True,scene=s.name)
assert hashlib.sha256(P.read_bytes()).hexdigest()==H
print('STEADY_REACH_NATIVE_READY',flush=True)
