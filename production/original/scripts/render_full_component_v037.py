import bpy,sys
from pathlib import Path
a=sys.argv[sys.argv.index('--')+1:];mode,start,end,out=a[0],int(a[1]),int(a[2]),a[3]
if not Path(out).is_absolute():out=str(Path(r'WTSC_LOCAL_WORKSPACE')/out)
version=a[4] if len(a)>4 else '037'
w=bpy.data.scenes['WTSC_WORLD_CORRECTED_v'+version];e=bpy.data.scenes['WTSC_FULL_FILM_KNOCKOUT_v'+version];s=w if mode=='world' else e
nt=bpy.data.node_groups.new('EXPORT COMPONENT | '+mode,'CompositorNodeTree');nt.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor');rl=nt.nodes.new('CompositorNodeRLayers');rl.scene=s;output=nt.nodes.new('NodeGroupOutput')
if mode=='world':
 glare=nt.nodes.new('CompositorNodeGlare');source=next(n for n in e.compositing_node_group.nodes if n.bl_idname=='CompositorNodeGlare')
 for inp in source.inputs:
  if inp.name!='Image' and hasattr(inp,'default_value'):
   try:glare.inputs[inp.name].default_value=inp.default_value
   except (TypeError,ValueError):pass
 nt.links.new(rl.outputs['Image'],glare.inputs['Image']);nt.links.new(glare.outputs['Image'],output.inputs['Image'])
else:
 nt.links.new(rl.outputs['Alpha'],output.inputs['Image']);s.view_settings.view_transform='Raw';s.view_settings.look='None'
s.compositing_node_group=nt;bpy.context.window.scene=s;s.frame_start=start;s.frame_end=end;s.render.resolution_percentage=100;s.render.use_sequencer=False;s.render.use_compositing=True;s.render.filepath=out;s.render.dither_intensity=0
if out.lower().endswith('.png'):
 s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.frame_set(start);bpy.ops.render.render(write_still=True,scene=s.name)
else:
 s.render.image_settings.media_type='VIDEO';s.render.ffmpeg.format='MPEG4';s.render.ffmpeg.codec='H264';s.render.ffmpeg.constant_rate_factor='HIGH' if mode=='world' else 'LOSSLESS';s.render.ffmpeg.ffmpeg_preset='GOOD';s.render.ffmpeg.audio_codec='NONE';bpy.ops.render.render(animation=True,scene=s.name)
print('COMPONENT_COMPLETED',mode,start,end,out,flush=True)
