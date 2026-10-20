import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parents[1];S=bpy.context.scene;g=bpy.data.node_groups.new('V025 probe','CompositorNodeTree');S.compositing_node_group=g;g.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor')
out={'available':[n for n in dir(bpy.types) if any(s in n for s in ['AlphaOver','Premul','RLayers'])],'nodes':{}}
for kind in ['CompositorNodeRLayers','CompositorNodeAlphaOver','CompositorNodePremulKey','ShaderNodeMix','NodeGroupOutput']:
    try:
        n=g.nodes.new(kind);out['nodes'][kind]={'inputs':[(i.name,i.identifier,i.bl_idname) for i in n.inputs],'outputs':[(i.name,i.identifier,i.bl_idname) for i in n.outputs],'properties':[p.identifier for p in n.bl_rna.properties]}
    except Exception as e:out['nodes'][kind]={'error':str(e)}
(P/'evidence/COMPOSITOR_RUNTIME_API.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
