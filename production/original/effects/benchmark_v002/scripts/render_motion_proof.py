import bpy,json,time
from pathlib import Path
P=Path(__file__).resolve().parents[1]
s=bpy.data.scenes['FX_MOTION_v002 | real shot plate + animated native FX'];bpy.context.window.scene=s
s.render.resolution_percentage=100;s.cycles.samples=8;s.cycles.use_denoising=True;s.cycles.use_animated_seed=False;s.cycles.seed=22017;s.render.threads_mode='FIXED';s.render.threads=2
if hasattr(s.render,'compositor_device'):s.render.compositor_device='CPU'
s.cycles.max_bounces=1;s.cycles.diffuse_bounces=1;s.cycles.glossy_bounces=0;s.cycles.transmission_bounces=0;s.cycles.transparent_max_bounces=6
# Keep the original paint and native mesh flow. The tiny4D per-ray texture warp
# is unnecessary for this proof and expensive on two CPU threads. Billboards
# emit visible color; the separate point light provides physical illumination.
for m in bpy.data.materials:
 if not m.node_tree or not m.name.startswith('FXv002 |'):continue
 if hasattr(m.cycles,'emission_sampling'):m.cycles.emission_sampling='NONE'
 uv=next((n for n in m.node_tree.nodes if n.type=='TEX_COORD'),None)
 if uv:
  for n in m.node_tree.nodes:
   if n.type=='TEX_IMAGE':m.node_tree.links.new(uv.outputs['UV'],n.inputs['Vector'])
# Reopen only the proof's actual dependencies, rather than retaining all source
# world scenes/materials in memory. Preserve full output size; trace only the
# region containing the eruption, dust and airborne debris.
s.render.use_border=True;s.render.use_crop_to_border=False
s.render.border_min_x=.50;s.render.border_max_x=1.;s.render.border_min_y=.20;s.render.border_max_y=.97
minimal=P/'native/WTSC_FX_Motion_Minimal_v002.blend'
bpy.data.libraries.write(str(minimal),{s},fake_user=True,compress=True)
bpy.ops.wm.open_mainfile(filepath=str(minimal),load_ui=False)
s=bpy.data.scenes['FX_MOTION_v002 | real shot plate + animated native FX'];bpy.context.window.scene=s
s.frame_start=1795;s.frame_end=1890;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
folder=P/'previews/motion_frames';folder.mkdir(exist_ok=True);s.render.filepath=str(folder)+'/'
root=bpy.data.objects['FXv002 | fixed ground origin and controls'];rows=[]
for f in [1795,1813,1814,1817,1825,1840,1870,1890]:
 s.frame_set(f);bpy.context.view_layer.update();rows.append({'frame':f,'age':root['age'],'root':list(root.matrix_world.translation)})
(P/'evidence/motion_plan.json').write_text(json.dumps({'frames':[1795,1890],'fps':24,'seconds':4,'pixels':[1920,1080],'renderer':'Cycles CPU two threads;8samples;fixed sampling seed','held_scene_plate':True,'original_camera_and_characters':'Frozen at source frame1825 for this FX evaluation; no production scene change','root_samples':rows},indent=2))
print('FX_ACTUAL_MOTION_PROOF_START',flush=True);bpy.ops.render.render(animation=True,scene=s.name);print('FX_ACTUAL_MOTION_PROOF_COMPLETE',flush=True)
