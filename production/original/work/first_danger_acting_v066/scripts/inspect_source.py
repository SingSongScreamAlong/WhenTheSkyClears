import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'work/first_danger_acting_v066'
for d in ['evidence','native','previews','renders']:(O/d).mkdir(parents=True,exist_ok=True)
S=R/'work/first_danger_conform_v065/native/WTSC_First_Danger_Conformed_v065f.blend'
bpy.ops.wm.open_mainfile(filepath=str(S),load_ui=False,use_scripts=False)
w=bpy.data.scenes['WTSC_FIRST_DANGER_WORLD_v065'];bpy.context.window.scene=w;w.frame_set(937);bpy.context.view_layer.update()
rigs={who:bpy.data.objects['V044 '+who+' | estimated joint centres'] for who in ['BOY','GIRL']}
report={'source':str(S),'sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'rigs':{},'actors':[]}
for who,r in rigs.items():
 report['rigs'][who]={'matrix_world':[list(v) for v in r.matrix_world],'location':list(r.location),'parent':r.parent.name,'bones':{b.name:{'head':list(b.head_local),'tail':list(b.tail_local),'length':b.length} for b in r.data.bones},'poses':{b.name:{'head':list(b.head),'tail':list(b.tail)} for b in r.pose.bones}}
for o in w.objects:
 if o.type=='MESH' and (o.parent in rigs.values() or (o.parent and o.parent.name in [r.name for r in rigs.values()])):
  report['actors'].append({'name':o.name,'hidden':o.hide_render,'parent':o.parent.name,'parent_type':o.parent_type,'parent_bone':o.parent_bone,'verts':len(o.data.vertices),'props':dict(o.items()),'groups':[(g.name,sum(1 for v in o.data.vertices if any(q.group==g.index for q in v.groups))) for g in o.vertex_groups],'modifiers':[{'name':m.name,'type':m.type,'object':getattr(getattr(m,'object',None),'name',None)} for m in o.modifiers], 'shape_count':len(o.data.shape_keys.key_blocks) if o.data.shape_keys else 0,'matrix_local':[list(row) for row in o.matrix_local]})
(O/'evidence/SOURCE_INSPECTION.json').write_text(json.dumps(report,indent=2,default=str))
print(json.dumps(report,indent=2,default=str))
