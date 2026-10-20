"""Native Blender composite of fresh UHD world, glyph and visible-drawing caches.

The live v065e compositor implements the same masked-world -> original-world mix.
Only the final composite changed after the v065d world workers started. This
reuses their unchanged world render instead of repeating its expensive lighting.
"""
import bpy,json,time,hashlib,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'work/first_danger_conform_v065';BUILD=json.loads((O/'evidence/BUILD.json').read_text());N=Path(BUILD['native']);N_SHA=hashlib.sha256(N.read_bytes()).hexdigest();SOURCE=O/'renders/sequence4K';FG='--foreground' in sys.argv;TAG='FINAL_COMPOSITE_F' if FG else 'FINAL_COMPOSITE';DEST=O/('renders/final_composite4K_F' if FG else 'renders/final_composite4K');DEST.mkdir(exist_ok=True)
if FG:assert (O/'evidence/FOREGROUND_ALPHA_COMPLETE.json').exists()
def input_path(kind,g):return (O/'renders/foreground_alpha4K' if kind=='tree' else SOURCE/kind)/f'{g:04d}.png'
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.data.scenes.new('V065 | exact native pixel-cache composite');bpy.context.window.scene=s
s.render.engine='BLENDER_EEVEE';s.render.resolution_x=3840;s.render.resolution_y=2160;s.render.resolution_percentage=100;s.render.fps=24;s.render.threads_mode='FIXED';s.render.threads=2;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.color_depth='8';s.render.image_settings.compression=15;s.render.dither_intensity=0;s.render.use_compositing=True;s.render.use_sequencer=False;s.eevee.taa_render_samples=1
s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0.;s.view_settings.gamma=1.
cam=bpy.data.objects.new('Cache composite render camera',bpy.data.cameras.new('Cache composite render camera'));s.collection.objects.link(cam);cam.location=(0,0,10);s.camera=cam
nt=bpy.data.node_groups.new('V065 | pixel-cache equivalent of live reveal','CompositorNodeTree');nt.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor');s.compositing_node_group=nt
nodes={}
for kind in ['world','glyph','matte']+(['tree'] if FG else []):nodes[kind]=nt.nodes.new('CompositorNodeImage')
base=nt.nodes.new('ShaderNodeMix');base.data_type='RGBA';base.blend_type='MULTIPLY';base.inputs[0].default_value=1.;base.clamp_factor=True;base.clamp_result=False
nt.links.new(nodes['glyph'].outputs['Image'],base.inputs[6]);nt.links.new(nodes['world'].outputs['Image'],base.inputs[7])
reveal=nt.nodes.new('ShaderNodeMix');reveal.data_type='RGBA';reveal.blend_type='MIX';reveal.clamp_factor=True;reveal.clamp_result=False
factor=nodes['matte'].outputs['Image']
if FG:
 inv=nt.nodes.new('ShaderNodeMath');inv.operation='SUBTRACT';inv.inputs[0].default_value=1.;nt.links.new(nodes['tree'].outputs['Image'],inv.inputs[1]);mul=nt.nodes.new('ShaderNodeMath');mul.operation='MULTIPLY';mul.use_clamp=True;nt.links.new(factor,mul.inputs[0]);nt.links.new(inv.outputs[0],mul.inputs[1]);factor=mul.outputs[0]
nt.links.new(factor,reveal.inputs[0]);nt.links.new(base.outputs[2],reveal.inputs[6]);nt.links.new(nodes['world'].outputs['Image'],reveal.inputs[7]);output=nt.nodes.new('NodeGroupOutput');nt.links.new(reveal.outputs[2],output.inputs[0])
pending=set(range(913,1081));rows=[];began=time.monotonic()
previous=O/f'evidence/{TAG}_PROGRESS.json'
if previous.exists():
 old_progress=json.loads(previous.read_text());assert old_progress['native']==str(N)
 for row in old_progress['rows']:
  assert hashlib.sha256((DEST/f'{row["frame"]:04d}.png').read_bytes()).hexdigest()==row['result_sha256']
  assert all(hashlib.sha256(input_path(kind,row['frame']).read_bytes()).hexdigest()==sha for kind,sha in row['source_image_sha256'].items())
  rows.append(row);pending.remove(row['frame'])
 print('VERIFIED_EXISTING_FINAL_COMPOSITES',len(rows),flush=True)
while pending:
 ready={}
 for path in (O/'evidence').glob('RENDER_MOVIE_*_PROGRESS.json'):
  if path.exists():
   try:
    progress=json.loads(path.read_text())
    for row in progress['rows']:
     if row['frame'] in pending:ready[row['frame']]=row
   except json.JSONDecodeError:pass # Writer is replacing a progress snapshot.
 if not ready:
  assert time.monotonic()-began<2400,'Source UHD workers did not complete within the bounded wait'
  time.sleep(.5);continue
 for g,source_row in sorted(ready.items()):
  # A progress row is emitted only after all native outputs are written.
  files={kind:input_path(kind,g) for kind in nodes}
  assert all(p.exists() for p in files.values())
  source_hashes={kind:hashlib.sha256(p.read_bytes()).hexdigest() for kind,p in files.items()}
  old=[]
  for kind,node in nodes.items():
   if node.image:old.append(node.image)
   image=bpy.data.images.load(str(files[kind]),check_existing=False);image.colorspace_settings.name='sRGB';node.image=image
  for image in old:bpy.data.images.remove(image)
  s.frame_set(g);s.render.filepath=str(DEST/f'{g:04d}.png');bpy.ops.render.render(write_still=True,scene=s.name)
  row={'frame':g,'source_world_native_sha256':BUILD['world_render_native_sha256'],'source_image_sha256':source_hashes,'global_progress':source_row['charcoal_progress'],'result_sha256':hashlib.sha256((DEST/f'{g:04d}.png').read_bytes()).hexdigest()};rows.append(row);pending.remove(g)
  (O/f'evidence/{TAG}_PROGRESS.json').write_text(json.dumps({'completed':len(rows),'total':168,'last_frame':g,'native':str(N),'rows':rows},indent=2));print('V065_FINAL_COMPOSITE',g,len(rows),168,flush=True)
assert hashlib.sha256(N.read_bytes()).hexdigest()==N_SHA
report={'native':str(N),'native_sha256':N_SHA,'native_unchanged':True,'world_render_native':BUILD['world_render_native'],'world_render_native_sha256':BUILD['world_render_native_sha256'],'resolution':[3840,2160],'fps':24,'frames':168,'global_range':[913,1080],'method':'Actual native UHD world/glyph/visible-actor caches, composited in Blender using the live native drawing reveal'+(' and exact foreground-oak alpha' if FG else '')+'. All sRGB pixel caches decode before linear composition; no scaling or interpolation.','rows':sorted(rows,key=lambda r:r['frame'])}
(O/f'evidence/{TAG}_COMPLETE.json').write_text(json.dumps(report,indent=2));print('V065_NATIVE_FINAL_COMPOSITE_COMPLETE',flush=True)
