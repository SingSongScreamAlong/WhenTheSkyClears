import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'work/first_danger_conform_v065';build=json.loads((O/'evidence/BUILD.json').read_text());N=Path(build['native']);H=hashlib.sha256(N.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(N),load_ui=False,use_scripts=False)
w=bpy.data.scenes['WTSC_FIRST_DANGER_WORLD_v065'];m=bpy.data.scenes['WTSC_FIRST_DANGER_TITLE_v065'];master=bpy.data.scenes['WTSC_FIRST_DANGER_REVIEW_MASTER_v065'];ctrl=bpy.data.objects['V065 | both children | global full-cut color time'];oc=bpy.data.scenes.get(build.get('foreground_occlusion_scene',''))
Q=O/'evidence/native_edit_pixels';Q.mkdir(exist_ok=True)
for sc in [w,m,master]+([oc] if oc else []):
 sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.image_settings.media_type='IMAGE';sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGB';sc.render.dither_intensity=0
for nt in bpy.data.node_groups:
 if nt.bl_idname=='CompositorNodeTree':
  for node in nt.nodes:
   if node.type=='OUTPUT_FILE':node.mute=True
rows=[]
for g in [937,1056]:
 for label,sc in [('direct',w),('master',master)]:
  bpy.context.window.scene=w;w.frame_set(g);m.frame_set(g);bpy.context.view_layer.update()
  if oc:oc.frame_set(g)
  bpy.context.window.scene=sc;sc.frame_set(g);bpy.context.view_layer.update();sc.render.filepath=str(Q/f'{label}_{g:04d}.png')
  bpy.ops.render.render(write_still=True,scene=sc.name)
  u=((g-1)/24)/96;expected=3*u*u-2*u*u*u
  rows.append({'frame':g,'render':label,'global_color':ctrl['charcoal_progress'],'expected_color':expected,'color_error':abs(ctrl['charcoal_progress']-expected)})
assert hashlib.sha256(N.read_bytes()).hexdigest()==H
(O/'evidence/NATIVE_EDIT_RENDER.json').write_text(json.dumps({'native_sha256':H,'native_unchanged':True,'resolution':[1280,720],'rows':rows},indent=2));print('NATIVE_EDIT_TEST_RENDERS_COMPLETE',flush=True)
