import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Painted_Rig_Corrective_Board_v017.blend'),load_ui=False,use_scripts=False);S=bpy.context.scene;S.frame_set(201);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();out=[]
for r in [o for o in S.objects if o.type=='ARMATURE']:
 for o in r.children:
  if o.type=='MESH':
   e=o.evaluated_get(dg);p=[r.matrix_world.inverted()@e.matrix_world@v.co for v in e.data.vertices];out.append({'who':r['character'],'mesh':o.name,'Y':[min(v.y for v in p),max(v.y for v in p)],'FrontLayer':bpy.data.objects[r['character']+' | WRIST_far'].get('FrontLayer')})
(P/'evidence/layer_inspection.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
