import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'work/first_danger_conform_v065';build=json.loads((O/'evidence/BUILD.json').read_text());S=Path(build['native']);N=O/'native/WTSC_First_Danger_Conformed_v065d.blend';assert not N.exists()
bpy.ops.wm.open_mainfile(filepath=str(S),load_ui=False,use_scripts=False)
w=bpy.data.scenes['WTSC_FIRST_DANGER_WORLD_v065']
for n in w.compositing_node_group.nodes:
 if n.type=='R_LAYERS' and n.scene is None:n.scene=w
bpy.context.window.scene=w;w.frame_set(981);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(N),compress=True)
build['previous_world_graph_draft']=str(S);build['native']=str(N);build['native_sha256']=hashlib.sha256(N.read_bytes()).hexdigest();build['self_layer_binding']='World Render Layers explicitly references the world; a None binding changed with the font render context and was rejected.'
(O/'evidence/BUILD.json').write_text(json.dumps(build,indent=2));print('V065D_SELF_LAYER_BOUND')
