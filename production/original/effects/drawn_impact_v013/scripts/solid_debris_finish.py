import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parents[1];s=bpy.data.scenes['FXv013 | drawn expansion and seated contacts'];bpy.context.window.scene=s;changed=[]
for m in bpy.data.materials:
    if not m.name.startswith('FXv013 |') or not any(term in m.name for term in ['chips','soil nicks','contact shadow']):continue
    for n in m.node_tree.nodes:
        if n.bl_idname=='ShaderNodeMapRange':n.inputs['To Min'].default_value=1;n.inputs['To Max'].default_value=1;changed.append(m.name)
assert len(changed)==3,changed
s.frame_set(9);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Drawn_Impact_Painted_v013.blend'),compress=True)
(P/'evidence/solid_debris_finish.json').write_text(json.dumps({'changed_materials':changed,'reason':'Actual side-by-side key review showed opacity grain weakened solid debris. Color pigment retained; opacity grain excluded from chips, soil nicks and contact shadows. Geometry, timing and paths unchanged.'},indent=2));print('SOLID_DEBRIS_FINISH_READY',changed,flush=True)
