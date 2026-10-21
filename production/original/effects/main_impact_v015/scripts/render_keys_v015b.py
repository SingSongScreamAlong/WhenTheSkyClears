"""Render isolated main-impact native4K keys after explicit GPU coordination."""
import bpy, sys, json, time, hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1]
report_path=P/'evidence/build_main_impact_v015b.json'
build=json.loads(report_path.read_text())
assert Path(bpy.data.filepath).resolve()==Path(build['native_context']).resolve()
s=bpy.data.scenes[build['scene']]
bpy.context.window.scene=s
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
frames=[int(x) for x in args[0].split(',')] if args else [1823,1824,1825,1826,1828,1830,1833,1837,1842,1850,1860,1873,1892,1920]
folder=P/'previews/native4K_keys_v015b';folder.mkdir(parents=True,exist_ok=True)
s.render.resolution_x=3840;s.render.resolution_y=2160;s.render.resolution_percentage=100
s.render.image_settings.media_type='IMAGE'
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
s.render.use_border=False;s.render.use_crop_to_border=False
s.render.threads_mode='FIXED';s.render.threads=2
native_sha=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
rows=[]
for frame in frames:
    path=folder/f'{frame:04d}.png'
    start=time.perf_counter();s.frame_set(frame);bpy.context.view_layer.update()
    s.render.filepath=str(path);bpy.ops.render.render(write_still=True,scene=s.name)
    rows.append({'frame':frame,'path':str(path),'seconds':time.perf_counter()-start,
                 'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
report={'frames':frames,'native_resolution':[3840,2160],'rows':rows,
        'native_unchanged':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()==native_sha,
        'preserved_v047g_unchanged':hashlib.sha256(Path(build['source']).read_bytes()).hexdigest()==build['source_sha256'],
        'visual_review_performed':False,'artistic_acceptance':False}
(P/'evidence/render_keys_v015b.json').write_text(json.dumps(report,indent=2))
print('MAIN_IMPACT_KEYS_COMPLETE',json.dumps(report),flush=True)
