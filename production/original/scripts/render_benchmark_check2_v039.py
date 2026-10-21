import bpy
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE');w=bpy.data.scenes['WTSC_WORLD_CORRECTED_v039'];e=bpy.data.scenes['WTSC_FULL_FILM_KNOCKOUT_v039']
nt=bpy.data.node_groups.new('TECHNICAL CHECK | same world glow as picture','CompositorNodeTree');nt.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor');rl=nt.nodes.new('CompositorNodeRLayers');rl.scene=w;g=nt.nodes.new('CompositorNodeGlare');source=next(n for n in e.compositing_node_group.nodes if n.bl_idname=='CompositorNodeGlare')
for inp in source.inputs:
 if inp.name!='Image' and hasattr(inp,'default_value'):
  try:g.inputs[inp.name].default_value=inp.default_value
  except (TypeError,ValueError):pass
o=nt.nodes.new('NodeGroupOutput');nt.links.new(rl.outputs['Image'],g.inputs['Image']);nt.links.new(g.outputs['Image'],o.inputs['Image']);w.compositing_node_group=nt
for s,tag in [(w,'world'),(e,'knockout')]:
 bpy.context.window.scene=s;s.render.resolution_percentage=25;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.frame_set(1609);s.render.filepath=str(R/f'renders/world_v016/camp_benchmark_checks_v039/{tag}_1609_960_r2.png');bpy.ops.render.render(write_still=True,scene=s.name)
print('LOW_COST_SECOND_PASS_DONE',flush=True)
