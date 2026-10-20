import bpy,json,hashlib
from pathlib import Path
O=Path(r'WTSC_LOCAL_WORKSPACE\work\production_review_v059');P=O/'WTSC_Production_Benchmark_v059.blend'
bpy.ops.wm.open_mainfile(filepath=str(P),load_ui=False,use_scripts=False)
s=bpy.data.scenes['WTSC_RECOVERY_WORLD_v059'];m=bpy.data.scenes['WTSC_5S_REVIEW_MASTER_v059'];t=bpy.data.scenes['WTSC_TITLE_VISIBILITY_REVIEW_v059']
m.view_settings.view_transform=s.view_settings.view_transform;m.view_settings.look=s.view_settings.look;m.view_settings.exposure=s.view_settings.exposure;m.view_settings.gamma=s.view_settings.gamma;m.render.dither_intensity=s.render.dither_intensity
bpy.context.window.scene=s;s.frame_set(1901)
bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True)
sha=hashlib.sha256(P.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(P),load_ui=False,use_scripts=False)
s=bpy.data.scenes['WTSC_RECOVERY_WORLD_v059'];m=bpy.data.scenes['WTSC_5S_REVIEW_MASTER_v059'];t=bpy.data.scenes['WTSC_TITLE_VISIBILITY_REVIEW_v059']
checks={'native_master_view_matches_world':m.view_settings.view_transform==s.view_settings.view_transform,'master_120_frames':m.frame_end-m.frame_start+1==120}
for sc in [s,m,t]:
 sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.render.threads_mode='FIXED';sc.render.threads=4;sc.eevee.taa_render_samples=32;sc.render.image_settings.media_type='IMAGE';sc.render.image_settings.file_format='PNG'
bpy.context.window.scene=m;m.frame_set(101);bpy.context.view_layer.update();m.render.filepath=str(O/'native_master_frame101.png');bpy.ops.render.render(write_still=True,scene=m.name)
rows=[]
for f in [1844,1901,1918]:
 bpy.context.window.scene=s;s.frame_set(f);bpy.context.view_layer.update()
 bpy.context.window.scene=t;t.frame_set(f);bpy.context.view_layer.update()
 rows.append({'frame':f,'glyph_location':list(t.objects['v037 | Entire film | WHEN THE SKY CLEARS'].matrix_world.translation)})
 t.render.filepath=str(O/f'title_corrected_clock_{f}.png');bpy.ops.render.render(write_still=True,scene=t.name)
 print('CORRECT_TITLE_FRAME',f,flush=True)
(O/'final_package_verification.json').write_text(json.dumps({'checks':checks,'file_sha256':sha,'title_clock_samples':rows,'reason':'Matched native review master to source Standard view transform; separately active title scene and world evaluated at each exact frame. Earlier three title_visibility files had stale glyph evaluation and are superseded by title_corrected_clock outputs.'},indent=2))
assert all(checks.values())
print('FINAL_PACKAGE_CHECKED',flush=True)
