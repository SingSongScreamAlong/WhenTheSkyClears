import bpy,json,runpy
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE');O=R/'work/production_review_v059'
bpy.ops.wm.open_mainfile(filepath=str(O/'WTSC_Paired_Recovery_Integration_v059b.blend'),load_ui=False,use_scripts=False)
s=bpy.data.scenes['WTSC_PAIRED_RECOVERY_WORLD_v059b'];bpy.context.window.scene=s
root=next(o for o in s.objects if o.get('motion_revision')=='v007_drawn_pose_corrections')
helper=runpy.run_path(str(O/'correct_pair_v059.py'));report=helper['apply'](s,root)
s.name='WTSC_PAIRED_RECOVERY_WORLD_v059c';s.frame_set(1901)
# Stable near/far ordering for newly interlocking drawings.
girl=bpy.data.objects['v059 GIRL | coherent late-contact hand']
girl.location.y=-0.002
report['girl_hand_depth_offset_m']=-0.002
(O/'contact_correction_v059c.json').write_text(json.dumps(report,indent=2))
s.render.filepath='//review_v059/'
bpy.ops.wm.save_as_mainfile(filepath=str(O/'WTSC_Paired_Recovery_Integration_v059c.blend'),compress=True)
s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=4;s.eevee.taa_render_samples=32;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG'
for f in [1897,1901,1918]:
 s.frame_set(f);s.render.filepath=str(O/f'corrected_{f}.png');bpy.ops.render.render(write_still=True,scene=s.name);print('CORRECTED_KEY',f,flush=True)
print('CONTACT_CANDIDATE_READY',flush=True)
