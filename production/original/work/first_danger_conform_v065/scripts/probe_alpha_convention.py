import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'work/first_danger_conform_v065';build=json.loads((O/'evidence/BUILD.json').read_text());S=Path(build['native'])
bpy.ops.wm.open_mainfile(filepath=str(S),load_ui=False,use_scripts=False)
w=bpy.data.scenes['WTSC_FIRST_DANGER_WORLD_v065'];m=bpy.data.scenes['WTSC_FIRST_DANGER_TITLE_v065'];nt=w.compositing_node_group
nt.nodes['V065 | readable children in foreground of title'].inputs['Straight Alpha'].default_value=True
Q=O/'evidence/alpha_convention_probe';Q.mkdir(exist_ok=True)
for sc in [w,m]:sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.render.threads_mode='FIXED';sc.render.threads=2
for n in nt.nodes:
 if n.type=='OUTPUT_FILE':
  n.mute=n.name not in ['V065 | world export','V065 | visible actor matte']
  if not n.mute:n.directory=str(Q);n.file_name=('world_' if n.name=='V065 | world export' else 'matte_')+'####'
bpy.context.window.scene=w;w.frame_set(913);m.frame_set(913);bpy.context.view_layer.update();w.render.filepath=str(Q/'straight_alpha_final.png');bpy.ops.render.render(write_still=True,scene=w.name)
print('STRAIGHT_ALPHA_PROBE_RENDER_COMPLETE')
