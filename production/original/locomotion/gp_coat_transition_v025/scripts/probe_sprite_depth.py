import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_GP_Coat_Transition_v025.blend'),load_ui=False,use_scripts=False);S=bpy.context.scene;S.frame_set(21);bpy.context.view_layer.update();rig=bpy.data.objects['LOCO_BOY | RIG'];out=[]
for o in rig.children:
    if o.type!='MESH':continue
    e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());out.append({'name':o.name,'y_range':[min((e.matrix_world@v.co).y for v in e.data.vertices),max((e.matrix_world@v.co).y for v in e.data.vertices)] if len(e.data.vertices) else [],'materials':[{'name':m.name,'render_method':m.surface_render_method,'use_nodes':m.use_nodes,'images':[(n.name,n.image.name,list(n.image.size)) for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]} for m in o.data.materials if m]})
(P/'evidence/SPRITE_DEPTH_PROBE.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
