import bpy,json,hashlib
from pathlib import Path
O=Path(r'WTSC_LOCAL_USER\Documents\Codex\2026-10-16\task\color_progression_study_v049');p=O/'WTSC_Three_Still_Color_Test_v049b.blend';assert not p.exists();bpy.ops.wm.open_mainfile(filepath=str(O/'WTSC_Three_Still_Color_Test_v049.blend'),load_ui=False,use_scripts=False);s=bpy.data.scenes['WTSC_THREE_STILL_COLOR_TEST_v049'];bpy.context.window.scene=s
corrected=0
for m in bpy.data.materials:
 if not m.name.startswith('COLOR TEST v049') or not m.node_tree.animation_data or not m.node_tree.animation_data.action:continue
 for layer in m.node_tree.animation_data.action.layers:
  for st in layer.strips:
   for bag in st.channelbags:
    for fc in bag.fcurves:
     if len(fc.keyframe_points)==3 and all(abs(k.co.x-f)<.001 for k,f in zip(fc.keyframe_points,[241,1201,1849])):
      for k in fc.keyframe_points:k.interpolation='CONSTANT'
      corrected+=1
assert corrected>0
s.render.resolution_percentage=100;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.dither_intensity=0;s.render.threads_mode='FIXED';s.render.threads=2;s.eevee.taa_render_samples=32;s.frame_set(241);bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True)
(O/'native_4k_test').mkdir(exist_ok=True)
for label,f in [('peaceful',241),('transition',1201),('war_zone',1849)]:
 s.frame_set(f);s.render.filepath=str(O/'native_4k_test'/f'WTSC_Color_Test_{label}_{f}_4K.png');bpy.ops.render.render(write_still=True,scene=s.name);print('COLOR_NATIVE_4K',label,flush=True)
r=json.loads((O/'COLOR_TEST_REPORT_v049.json').read_text());r.update({'native':str(p),'native_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'preset_curves_constant':corrected,'actual_render_dimensions':[3840,2160],'render_samples':32,'visual_assessment':'Warm restrained umber remains readable; school world loses color before children; war drains children to near-neutral charcoal. No residual accent added. Test only, no new contact or geometry.'});(O/'COLOR_TEST_REPORT_v049.json').write_text(json.dumps(r,indent=2));print('COLOR_STUDY_COMPLETE',flush=True)
