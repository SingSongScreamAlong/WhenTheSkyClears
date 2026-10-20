"""Bounded isolated preview, after checking production has no active render jobs."""
import bpy,sys,json,time,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]
s=bpy.data.scenes['FX_MOTION_v002 | real shot plate + animated native FX'];bpy.context.window.scene=s
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=32;s.render.threads_mode='FIXED';s.render.threads=2
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.fps=24
s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
if hasattr(s.render,'compositor_device'):s.render.compositor_device='GPU'
root=bpy.data.objects['FXv002 | fixed ground origin and controls']
# The ignition uses a cropped portion of the painted lower core. Feather its
# upper UV boundary so it never reveals a straight rectangular crop edge.
mat=bpy.data.materials['FXv002 | fast pale-hot core flash'];nt=mat.node_tree
if not nt.nodes.get('FXv002 ignition tip falloff'):
 uv=next(n for n in nt.nodes if n.type=='TEX_COORD');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(uv.outputs['UV'],sep.inputs[0])
 cap=nt.nodes.new('ShaderNodeMapRange');cap.name='FXv002 ignition tip falloff';cap.clamp=True;cap.interpolation_type='SMOOTHERSTEP';cap.inputs['From Min'].default_value=.18;cap.inputs['From Max'].default_value=.29;cap.inputs['To Min'].default_value=1;cap.inputs['To Max'].default_value=0;nt.links.new(sep.outputs['Y'],cap.inputs[0])
 out=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL');mix=out.inputs[0].links[0].from_node;old=mix.inputs[0].links[0].from_socket
 mul=nt.nodes.new('ShaderNodeMath');mul.operation='MULTIPLY';nt.links.new(old,mul.inputs[0]);nt.links.new(cap.outputs[0],mul.inputs[1]);nt.links.new(mul.outputs[0],mix.inputs[0])
# Small soft fill replaces the diffuse environment contribution used by Cycles
# on the solid fragments; it does not relight the held environment plate.
ld=bpy.data.lights.new('FXv002 GPU proof | cool soft fragment fill','AREA');ld.energy=20;ld.color=(.44,.55,.70);ld.shape='DISK';ld.size=4
lo=bpy.data.objects.new(ld.name,ld);s.collection.objects.link(lo);lo.location=root.location+Vector((-2,-4,5));lo.rotation_euler=((root.location+Vector((0,0,.7)))-lo.location).to_track_quat('-Z','Y').to_euler()
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];mode=args[0] if args else 'keys'
folder=P/'previews/motion_frames_gpu_v002';folder.mkdir(exist_ok=True)
report={'mode':mode,'blender':bpy.app.version_string,'renderer':s.render.engine,'samples':32,'cpu_threads':2,'pixels':[1920,1080],'fps':24,'held_scene_source_frame':1825,'frames':[],'source_files_modified':False,'compositor_device':str(getattr(s.render,'compositor_device','runtime default'))}
started=time.perf_counter()
if mode=='motion':
 s.frame_start=1795;s.frame_end=1890;s.render.filepath=str(folder)+'/'
 print('FX_GPU_MOTION_START',json.dumps(report),flush=True);bpy.ops.render.render(animation=True,scene=s.name)
else:
 for frame in [1814,1825,1870]:
  s.frame_set(frame);s.render.filepath=str(P/f'previews/GPU_key_{frame}_v002.png');begin=time.perf_counter();bpy.ops.render.render(write_still=True,scene=s.name)
  report['frames'].append({'frame':frame,'age':root['age'],'seconds':time.perf_counter()-begin,'root':list(root.matrix_world.translation)})
 s.frame_set(1825);bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_FX_GPU_Preview_v002.blend'),compress=True)
 bpy.data.libraries.write(str(P/'native/WTSC_Hero_Eruption_Collection_v002a.blend'),{bpy.data.collections['FXv002 | Detailed painterly ground eruption']},fake_user=True,compress=True)
report['elapsed_seconds']=time.perf_counter()-started
(P/'evidence'/f'gpu_{mode}_render_v002.json').write_text(json.dumps(report,indent=2));print('FX_GPU_PREVIEW_COMPLETE',json.dumps(report),flush=True)
