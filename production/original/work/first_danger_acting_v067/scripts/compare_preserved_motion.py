import bpy,json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parents[1];B=json.loads((O/'evidence/BUILD.json').read_text())
frames=[913+i*.5 for i in range(335)];cache={};metrics={'boot_vertex_max_difference_m':0.,'camera_matrix_max_difference':0.,'pelvis_matrix_max_difference':0.}
for index,(path,scene) in enumerate([(B['native'],B['world_scene']),(B['source'],'WTSC_FIRST_DANGER_ACTING_WORLD_v066')]):
 bpy.ops.wm.open_mainfile(filepath=path,load_ui=False,use_scripts=False);S=bpy.data.scenes[scene];bpy.context.window.scene=S
 boots=[o for o in S.objects if o.type=='MESH' and o.get('proportion_role')=='boot' and o.parent and o.parent.name.startswith('V044 ') and not o.hide_render]
 rigs=[o for o in S.objects if o.type=='ARMATURE' and o.name.startswith('V044 ')]
 for g in frames:
  S.frame_set(int(g),subframe=g-int(g));bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
  row={'camera':S.camera.matrix_world.copy(),'boots':{},'pelvis':{r.name:r.evaluated_get(dg).pose.bones['pelvis'].matrix.copy() for r in rigs}}
  for o in boots:
   e=o.evaluated_get(dg);row['boots'][o.name]=[e.matrix_world@v.co for v in e.data.vertices]
  if index==0:cache[g]=row
  else:
   old=cache[g];metrics['camera_matrix_max_difference']=max(metrics['camera_matrix_max_difference'],max(abs(row['camera'][i][j]-old['camera'][i][j]) for i in range(4) for j in range(4)))
   for n,points in row['boots'].items():metrics['boot_vertex_max_difference_m']=max(metrics['boot_vertex_max_difference_m'],max((p-q).length for p,q in zip(points,old['boots'][n])))
   for n,m in row['pelvis'].items():metrics['pelvis_matrix_max_difference']=max(metrics['pelvis_matrix_max_difference'],max(abs(m[i][j]-old['pelvis'][n][i][j]) for i in range(4) for j in range(4)))
out={'samples':len(frames),'metrics':metrics,'passed':all(x<2e-6 for x in metrics.values()),'source_unchanged':hashlib.sha256(Path(B['source']).read_bytes()).hexdigest()==B['source_sha256'],'candidate_unchanged':hashlib.sha256(Path(B['native']).read_bytes()).hexdigest()==B['native_sha256']}
(O/'evidence/PRESERVED_MOTION.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert out['passed'] and out['source_unchanged'] and out['candidate_unchanged']
