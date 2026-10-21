import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parents[1]
s=bpy.data.scenes['WTSC_WORLD_CORRECTED_v037'];bpy.context.window.scene=s;s.frame_set(1825)
rows=[]
for o in s.objects:
 if o.type in {'MESH','GREASEPENCIL'} and (any(k in o.name.lower() for k in ['child','pair','painted','walking','battlefield','ruin','smoke','flame']) or any('Regional painted' in c.name for c in o.users_collection)):
  rows.append({'name':o.name,'type':o.type,'location':list(o.matrix_world.translation),'dimensions':list(o.dimensions),'materials':[(m.name,[(n.name,n.type) for n in m.node_tree.nodes if n.type in {'EMISSION','MIX_SHADER','TEX_IMAGE'}]) for m in o.data.materials if m and m.node_tree]})
report={'camera':{'location':list(s.camera.matrix_world.translation),'rotation':list(s.camera.rotation_euler),'lens':s.camera.data.lens,'shifts':[s.camera.data.shift_x,s.camera.data.shift_y]},'objects':rows}
(P/'evidence/source_objects.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
