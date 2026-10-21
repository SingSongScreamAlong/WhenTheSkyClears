import bpy,json
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE')
e=bpy.data.scenes['WTSC_KNOCKOUT_ENDING_v032'];bpy.context.window.scene=e
e.render.resolution_percentage=100;e.render.image_settings.media_type='IMAGE';e.render.image_settings.file_format='PNG'
for f in [2033,2137,2257,2400,2401]:
 e.frame_set(f);e.render.filepath=str(R/f'renders/world_v016/ending_checks_4K_v032/{f}.png');bpy.ops.render.render(write_still=True,scene=e.name)
# Actual mask pixels for independent outside-letter verification.
nt=e.compositing_node_group;output=next(n for n in nt.nodes if n.type=='GROUP_OUTPUT');rl=next(n for n in nt.nodes if n.bl_idname=='CompositorNodeRLayers')
nt.links.new(rl.outputs['Alpha'],output.inputs['Image']);e.frame_set(2137);e.render.filepath=str(R/'renders/world_v016/ending_checks_4K_v032/mask_2137.png');bpy.ops.render.render(write_still=True,scene=e.name)
print('CHECKS_DONE',flush=True)
