import bpy,json
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE');O=R/'work'/'production_review_v059'
bpy.ops.wm.open_mainfile(filepath=str(R/'shots/world/WTSC_Open_Battlefield_Refinement_v048a.blend'),load_ui=False,use_scripts=False)
d={'scenes':[],'collections':[],'texts':[],'objects':[]}
for s in bpy.data.scenes:d['scenes'].append({'name':s.name,'camera':s.camera.name if s.camera else None,'objects':len(s.objects)})
for c in bpy.data.collections:
 if any(q in c.name.lower() for q in ['pair','v007','recover','v047','v048','child','v043','v046']):
  d['collections'].append({'name':c.name,'objects':len(c.all_objects),'children':[x.name for x in c.children]})
for t in bpy.data.texts:d['texts'].append({'name':t.name,'size':len(t.as_string())})
s=next(s for s in bpy.data.scenes if 'REFINEMENT' in s.name and s.camera);bpy.context.window.scene=s;s.frame_set(1901)
for ob in s.objects:
 if any(q in ob.name.lower() for q in ['v007','v047','v048','boy','girl','control','root','hand','wrist','foot','shoe']):
  d['objects'].append({'name':ob.name,'type':ob.type,'location':list(ob.location),'world':list(ob.matrix_world.translation),'dimensions':list(ob.dimensions),'hide_render':ob.hide_render,'parent':ob.parent.name if ob.parent else None,'collections':[x.name for x in ob.users_collection],'custom':{k:str(ob[k])[:500] for k in ob.keys()},'drivers':[{'path':f.data_path,'expression':f.driver.expression} for f in ob.animation_data.drivers] if ob.animation_data else []})
(O/'motion_inspection.json').write_text(json.dumps(d,indent=2))
print(json.dumps({k:d[k] for k in ['scenes','collections','texts']},indent=2),flush=True)
