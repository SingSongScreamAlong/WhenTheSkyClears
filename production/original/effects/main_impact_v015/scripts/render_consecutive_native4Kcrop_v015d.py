"""25 consecutive original native4K-pixel border renders; no upscaling."""
import bpy,json,time,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];build=json.loads((P/'evidence/build_main_impact_v015d.json').read_text())
assert Path(bpy.data.filepath).resolve()==Path(build['native_context']).resolve()
native_sha=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
s=bpy.data.scenes[build['scene']];bpy.context.window.scene=s
s.render.resolution_x=3840;s.render.resolution_y=2160;s.render.resolution_percentage=100
s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
box=[2200,400,3800,1720]
s.render.use_border=True;s.render.use_crop_to_border=True
s.render.border_min_x=box[0]/3840;s.render.border_max_x=box[2]/3840
s.render.border_min_y=(2160-box[3])/2160;s.render.border_max_y=(2160-box[1])/2160
s.render.threads_mode='FIXED';s.render.threads=2
folder=P/'previews/consecutive_native4Kcrop_v015d';folder.mkdir(parents=True,exist_ok=True)
rows=[]
for frame in range(1824,1849):
    s.frame_set(frame);bpy.context.view_layer.update();s.render.filepath=str(folder/f'{frame:04d}.png')
    t=time.perf_counter();bpy.ops.render.render(write_still=True,scene=s.name)
    rows.append({'frame':frame,'seconds':time.perf_counter()-t,'path':s.render.filepath})
report={'native_full_resolution':[3840,2160],'crop_box_top_left_pixels':box,'expected_crop_size':[1600,1320],
        'fps':24,'frames':list(range(1824,1849)),'frame_count':25,'rows':rows,
        'native_4K_file_unchanged':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()==native_sha,
        'g_source_unchanged':hashlib.sha256(Path(build['source']).read_bytes()).hexdigest()==build['source_sha256'],
        'artistic_acceptance':False,'continuous_speed_playback_observed':False}
(P/'evidence/consecutive_native4Kcrop_v015d.json').write_text(json.dumps(report,indent=2))
print('PAINTED_IMPACT_NATIVE4K_CONSECUTIVE_COMPLETE',json.dumps(report),flush=True)
