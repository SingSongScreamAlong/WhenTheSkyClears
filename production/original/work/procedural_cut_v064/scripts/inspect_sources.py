import bpy,json
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE')
out=R/'work/procedural_cut_v064/evidence'
report={}
for key,path in [('color',R/'work/color_arc_v063/native/WTSC_Shared_Color_To_Charcoal_v063.blend'),('world',R/'work/world_minimum_v058/WTSC_World_Development_v058_Packed.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 rows=[]
 for s in bpy.data.scenes:
  if key=='world' and not any(t in s.name for t in ['v058','MASTER','EDIT']):continue
  bpy.context.window.scene=s;s.frame_set(981)
  candidates=[o for o in s.objects if o.type=='GREASEPENCIL' or ('shared travel' in o.name) or ('V047 | painted stage' in o.name) or (o.type=='EMPTY' and any('shared travel' in x.name for x in o.children_recursive))]
  row=dict(scene=s.name,frames=[s.frame_start,s.frame_end],view=s.view_settings.view_transform,camera=None if not s.camera else dict(name=s.camera.name,loc=list(s.camera.location),drivers=[dict(path=f.data_path,expression=f.driver.expression) for f in s.camera.animation_data.drivers] if s.camera.animation_data else []),objects=[])
  for ob in candidates:
   a=ob.animation_data
   row['objects'].append(dict(name=ob.name,type=ob.type,parent=getattr(ob.parent,'name',None),loc=list(ob.location),matrix=[list(x) for x in ob.matrix_world],inverse=[list(x) for x in ob.matrix_parent_inverse],children=[x.name for x in ob.children],constraints=[(c.type,c.name,getattr(getattr(c,'target',None),'name',None)) for c in ob.constraints],actions=None if not a or not a.action else dict(name=a.action.name,range=list(a.action.frame_range),curves=[dict(path=f.data_path,index=f.array_index,count=len(f.keyframe_points),range=list(f.range()),modifiers=[m.type for m in f.modifiers]) for l in a.action.layers for st in l.strips for b in st.channelbags for f in b.fcurves]),nla=[] if not a else [dict(name=t.name,strips=[dict(name=st.name,action=st.action.name,start=st.frame_start,end=st.frame_end,astart=st.action_frame_start,aend=st.action_frame_end,scale=st.scale,repeat=st.repeat) for st in t.strips]) for t in a.nla_tracks]))
  rows.append(row)
 report[key]=rows
(out/'SOURCES_063_058_INSPECTION.json').write_text(json.dumps(report,indent=2))
print('V064_SOURCES_INSPECTION_READY',flush=True)
