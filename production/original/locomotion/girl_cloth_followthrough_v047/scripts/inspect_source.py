import bpy,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];FILE=ROOT/'locomotion/painted_outfit_restoration_v046/native/WTSC_Age10_Painted_Outfit_Restoration_v046.blend';before=hashlib.sha256(FILE.read_bytes()).hexdigest();assert before=='e993540280bc60ff5fcc1dafe316f7c8457c5c8750a1110b8f6e307a865d005d';bpy.ops.wm.open_mainfile(filepath=str(FILE),load_ui=False,use_scripts=False);S=bpy.data.scenes['V046 | AGE10 BONES | restored painted clothing'];bpy.context.window.scene=S
report={'source_sha256':before,'meshes':[]}
for o in bpy.data.objects:
 if o.type!='MESH' or o.hide_render or not (o.name.startswith('V044 GIRL') or o.name.startswith('V046 GIRL')):continue
 q={'name':o.name,'vertex_count':len(o.data.vertices),'face_count':len(o.data.polygons),'role':o.get('proportion_role',o.get('wardrobe_role')),'origin':list(o.location),'modifiers':[(m.type,m.name) for m in o.modifiers],'uv_layers':[u.name for u in o.data.uv_layers],'materials':[m.name for m in o.data.materials],'x_range':[min(v.co.x for v in o.data.vertices),max(v.co.x for v in o.data.vertices)],'z_range':[min(v.co.z for v in o.data.vertices),max(v.co.z for v in o.data.vertices)]}
 if o.get('proportion_role')=='head':
  u=o.data.uv_layers[0];q['uv_by_vertex']={}
  for lp in o.data.loops:q['uv_by_vertex'][lp.vertex_index]=list(u.data[lp.index].uv)
  q['verts']=[list(v.co) for v in o.data.vertices]
 report['meshes'].append(q)
assert hashlib.sha256(FILE.read_bytes()).hexdigest()==before;(P/'evidence/SOURCE_INSPECTION.json').write_text(json.dumps(report,indent=2));print(json.dumps([{k:v for k,v in o.items() if k not in ['uv_by_vertex','verts']} for o in report['meshes']],indent=2))
