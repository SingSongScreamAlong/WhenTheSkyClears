"""Fresh native world sequence at absolute trailer time; no source save."""
import bpy,json,sys,hashlib,time,struct
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE');O=R/'work/procedural_cut_v064'
a=sys.argv[sys.argv.index('--')+1:];start,end=map(int,a[:2]);resume='--resume' in a;build=json.loads((O/'evidence/FULL_CUT_BUILD.json').read_text())
native=Path(build['native']);assert hashlib.sha256(native.read_bytes()).hexdigest()==build['native_sha256']
bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
w=bpy.data.scenes[build['world_scene']];e=bpy.data.scenes[build['picture_scene']];bpy.context.window.scene=w
ctrl=bpy.data.objects[build['controller']]
actor_mat=bpy.data.materials[build['color_material']['material']]
shared_mix=actor_mat.node_tree.nodes[build['color_material']['mix_node']]
pigment=actor_mat.node_tree.nodes[build['color_material']['procedural_saturation_node']]
nt=bpy.data.node_groups.new('V064 | export world with exact native title glow','CompositorNodeTree');nt.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor')
rl=nt.nodes.new('CompositorNodeRLayers');rl.scene=w;glare=nt.nodes.new('CompositorNodeGlare');src=next(n for n in e.compositing_node_group.nodes if n.bl_idname=='CompositorNodeGlare')
for inp in src.inputs:
 if inp.name!='Image' and hasattr(inp,'default_value'):
  try:glare.inputs[inp.name].default_value=inp.default_value
  except (TypeError,ValueError):pass
output=nt.nodes.new('NodeGroupOutput');nt.links.new(rl.outputs['Image'],glare.inputs['Image']);nt.links.new(glare.outputs['Image'],output.inputs['Image']);w.compositing_node_group=nt
w.render.resolution_x=1280;w.render.resolution_y=720;w.render.resolution_percentage=100;w.render.threads_mode='FIXED';w.render.threads=3
w.render.use_sequencer=False;w.render.use_compositing=True;w.render.dither_intensity=0
w.render.image_settings.media_type='IMAGE';w.render.image_settings.file_format='PNG';w.render.image_settings.color_mode='RGB';w.render.image_settings.color_depth='8';w.render.image_settings.compression=15
if hasattr(w,'eevee'):w.eevee.taa_render_samples=32
w.frame_start=start;w.frame_end=end;w.frame_step=1;w.render.filepath=str(O/'previews/world_frames')+'/'
rows=[];resumed_frames=[];began=time.time()
def written(scene,*args):
 f=scene.frame_current;t=(f-1)/24;u=min(1,max(0,t/96));p=ctrl[build['property']];assert abs(p-u*u*(3-2*u))<1.1e-4,(f,p)
 assert abs(shared_mix.inputs[0].default_value-p)<1.1e-4,(f,'shared material',shared_mix.inputs[0].default_value,p)
 assert abs(pigment.inputs['Saturation'].default_value-(1-p))<1.1e-4,(f,'pigment saturation')
 path=O/'previews/world_frames'/f'{f:04d}.png';assert path.is_file()
 rows.append(dict(frame=f,seconds=t,progress=p,mix_progress=shared_mix.inputs[0].default_value,pigment_saturation=pigment.inputs['Saturation'].default_value,rendered_in_session=(f not in resumed_frames),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
 if f%24==0 or f in [start,end]:print('V064_FRAME',f,'RANGE',start,end,'ELAPSED',round(time.time()-began,2),'COLOR',round(p,6),flush=True)
for frame in range(start,end+1):
 w.frame_set(frame);bpy.context.view_layer.update()
 path=O/'previews/world_frames'/f'{frame:04d}.png'
 w.render.filepath=str(path)
 if path.exists():
  assert resume,'Unexpected pre-existing frame'
  with path.open('rb') as stream:header=stream.read(24)
  assert header[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',header[16:24])==(1280,720)
  resumed_frames.append(frame)
 else:bpy.ops.render.render(write_still=True,scene=w.name)
 written(w)
assert [r['frame'] for r in rows]==list(range(start,end+1))
assert hashlib.sha256(native.read_bytes()).hexdigest()==build['native_sha256']
(O/f'evidence/world_worker_{start:04d}_{end:04d}.json').write_text(json.dumps(dict(native_sha256=build['native_sha256'],frames=rows,resolution=[1280,720],samples=32,native_unchanged=True,source_world_frames_fresh=True,all_shared_material_driver_checks_pass=True,driver_numeric_tolerance=1.1e-4,precision_evidence='FLOAT_DRIVER_PRECISION.json: measured maximum9.515e-5 native RNA update error',resumed_existing_frames=resumed_frames,native_driver_replay_for_resumed_frames=True,elapsed=time.time()-began),indent=2))
print('V064_WORLD_WORKER_COMPLETE',start,end,flush=True)
