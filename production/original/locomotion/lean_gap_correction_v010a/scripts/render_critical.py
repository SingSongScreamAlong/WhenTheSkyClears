import bpy,json
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parents[1];V10=P.parent/'stumble_polish_continuation_v010'
frames=[1837,1840,1841,1842,1843,1844,1845,1846,1847,1848,1849];meta={}
for mode,source in [('v010',V10/'native/WTSC_v010_Matched_Review_Copy.blend'),('v010a',P/'native/WTSC_v010a_Matched_Review_Copy.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
 revision='v010_polish_continuation' if mode=='v010' else 'v010a_lean_gap_correction';root=next(o for o in s.objects if o.get('motion_revision')==revision);rigs={o['character']:o for o in root.children_recursive if o.type=='ARMATURE'}
 heads={w:next(o for o in rig.children if o.type=='MESH' and ('original head and attached braid' in o.name if w=='GIRL' else 'original head' in o.name)) for w,rig in rigs.items()}
 s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=2;s.eevee.taa_render_samples=16;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.use_border=False;folder=P/'previews'/mode;folder.mkdir(exist_ok=True);meta[mode]={}
 for f in frames:
  s.frame_set(f);bpy.context.view_layer.update();meta[mode][str(f)]={}
  for who,ob in heads.items():
   ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();pts=[world_to_camera_view(s,s.camera,ev.matrix_world@v.co) for v in me.vertices];meta[mode][str(f)][who]={'pixels':[[q.x*1920,(1-q.y)*1080] for q in pts],'faces':[list(p.vertices) for p in me.polygons]};ev.to_mesh_clear()
  path=folder/f'{f}.png';s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
(P/'evidence/projected_head_meshes.json').write_text(json.dumps(meta));print('V010a_CRITICAL_STILLS_DONE',flush=True)
