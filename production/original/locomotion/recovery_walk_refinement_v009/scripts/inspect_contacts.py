import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_v009_Matched_Review_Copy.blend'),load_ui=False);s=bpy.context.scene
rows=[]
for o in s.objects:
 if o.name.startswith('v041 sole contact |'):
  row={'name':o.name,'parent':o.parent.name if o.parent else None,'hide':o.hide_render,'props':{k:str(o[k]) for k in o.keys()},'constraints':[(c.name,c.type) for c in o.constraints],'drivers':[]}
  if o.animation_data:
   row['drivers']=[{'path':fc.data_path,'index':fc.array_index,'expr':fc.driver.expression,'vars':[{'name':v.name,'type':v.type,'targets':[{'id':t.id.name if t.id else None,'bone':t.bone_target,'path':t.data_path} for t in v.targets]} for v in fc.driver.variables]} for fc in o.animation_data.drivers]
  rows.append(row)
(P/'evidence/external_contact_probe.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows),flush=True)
