import bpy,json,math
from pathlib import Path
O=Path(r'WTSC_LOCAL_WORKSPACE\work\procedural_cut_v064')
b=json.loads((O/'evidence/FULL_CUT_BUILD.json').read_text());bpy.ops.wm.open_mainfile(filepath=b['native'],load_ui=False,use_scripts=False)
w=bpy.data.scenes[b['world_scene']];bpy.context.window.scene=w;c=bpy.data.objects[b['controller']];mat=bpy.data.materials[b['color_material']['material']];mix=mat.node_tree.nodes[b['color_material']['mix_node']];sat=mat.node_tree.nodes[b['color_material']['procedural_saturation_node']]
rows=[]
for f in list(range(1,41))+list(range(2270,2311)):
 w.frame_set(f);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();u=max(0,min(1,(f-1)/(24*96)));expected=u*u*(3-2*u)
 ec=c.evaluated_get(dg);em=mat.evaluated_get(dg)
 rows.append(dict(frame=f,expected=expected,original=c[b['property']],evaluated=ec[b['property']],mix=mix.inputs[0].default_value,evaluated_mix=em.node_tree.nodes[b['color_material']['mix_node']].inputs[0].default_value,saturation=sat.inputs['Saturation'].default_value))
out=dict(rows=rows,max_original_error=max(abs(r['original']-r['expected']) for r in rows),max_evaluated_error=max(abs(r['evaluated']-r['expected']) for r in rows),max_mix_error=max(abs(r['mix']-r['expected']) for r in rows))
(O/'evidence/FLOAT_DRIVER_PRECISION.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='rows'}),flush=True)
