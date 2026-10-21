import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];s=bpy.data.scenes['WTSC_OPEN_BATTLEFIELD_REFINEMENT_v047c'];bpy.context.window.scene=s;s.frame_set(1901);bpy.context.view_layer.update()
ob=s.objects['v020 | Foreground bank | continuous blended paint'];points=[ob.matrix_world@v.co for v in ob.data.vertices];mat=ob.data.materials[0]
result={'object':ob.name,'vertices':len(points),'polygons':len(ob.data.polygons),
 'bounds':[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)],
 'materials':[m.name for m in ob.data.materials],
 'nodes':[{'name':n.name,'type':n.type,'image':n.image.name if n.type=='TEX_IMAGE' and n.image else None} for n in mat.node_tree.nodes],
 'links':[[l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name] for l in mat.node_tree.links]}
(R/'notes/improvement_v047/bank_inspection.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result),flush=True)
