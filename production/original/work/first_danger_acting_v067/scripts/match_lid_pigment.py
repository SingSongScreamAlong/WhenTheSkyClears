import bpy,json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parents[1];B=json.loads((O/'evidence/BUILD.json').read_text());bpy.ops.wm.open_mainfile(filepath=B['native'],load_ui=False,use_scripts=False)
paint=bpy.data.objects['V044 BOY | head'];uvname=paint.data.uv_layers.active.name
for name in B['new_lid_objects']:
 if 'GIRL' not in name:continue
 o=bpy.data.objects[name];m=paint.data.materials[0].copy();m.name='V067 GIRL | original shared skin pigment | '+('lid line' if 'line' in name else 'lid skin')
 if 'line' in name:
  em=next(n for n in m.node_tree.nodes if n.type=='EMISSION');src=em.inputs[0].links[0].from_socket;node=m.node_tree.nodes.new('ShaderNodeMixRGB');node.blend_type='MULTIPLY';node.inputs[0].default_value=1;node.inputs[2].default_value=(.22,.18,.16,1);m.node_tree.links.new(src,node.inputs[1]);m.node_tree.links.new(node.outputs[0],em.inputs[0])
 o.data.materials[0]=m;o.data.uv_layers.active.name=uvname
 for d in o.data.uv_layers.active.data:d.uv=(330/1254,1-285/1254)
S=bpy.data.scenes[B['world_scene']];bpy.context.window.scene=S;S.frame_set(957);bpy.context.view_layer.update();P=O/'native/WTSC_First_Danger_Acting_v067d.blend';bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True)
B['native']=str(P);B['native_sha256']=hashlib.sha256(P.read_bytes()).hexdigest();B['lid_pigment']='Native lid drawings sample the existing shared skin atlas/cheek pigment and use the original global color shader. The charcoal-only girl source pigment is not used as a skin lid.'
(O/'evidence/BUILD.json').write_text(json.dumps(B,indent=2));print('V067D_MATCHED_LID_PIGMENT_SAVED',flush=True)
