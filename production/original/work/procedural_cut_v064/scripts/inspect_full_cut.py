import bpy,json,hashlib
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE')
out=R/'work/procedural_cut_v064/evidence'
src=R/'shots/world/WTSC_Painted_World_Full_Trailer_Editable_v040.blend'
bpy.ops.wm.open_mainfile(filepath=str(src))
def curves(id):
 a=id.animation_data
 if not a or not a.action:return []
 return [dict(path=f.data_path,index=f.array_index,keys=[(round(k.co.x,4),round(k.co.y,4)) for k in f.keyframe_points]) for l in a.action.layers for s in l.strips for b in s.channelbags for f in b.fcurves]
report=dict(source=str(src),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),scenes=[])
for s in bpy.data.scenes:
 if not any(t in s.name for t in ['v040','v063']):continue
 bpy.context.window.scene=s;s.frame_set(981);bpy.context.view_layer.update()
 actors=[o for o in s.objects if o.type=='GREASEPENCIL' or any(t in o.name.lower() for t in ['pair','boy','girl','charcoal','paint fill'])]
 report['scenes'].append(dict(name=s.name,frames=[s.frame_start,s.frame_end],fps=s.render.fps,res=[s.render.resolution_x,s.render.resolution_y],camera=None if not s.camera else dict(name=s.camera.name,matrix=[list(x) for x in s.camera.matrix_world],lens=s.camera.data.lens,shift=[s.camera.data.shift_x,s.camera.data.shift_y],curves=curves(s.camera)),compositor=None if not s.compositing_node_group else [dict(name=n.name,type=n.type,scene=getattr(getattr(n,'scene',None),'name',None)) for n in s.compositing_node_group.nodes],actors=[dict(name=o.name,type=o.type,parent=None if not o.parent else o.parent.name,matrix=[list(x) for x in o.matrix_world],local=[list(x) for x in o.matrix_basis],hidden=o.hide_render,collection=[c.name for c in o.users_collection],curves=curves(o),materials=[dict(name=m.name,nodes=[] if not m.node_tree else [dict(name=n.name,type=n.type,image=getattr(getattr(n,'image',None),'name',None)) for n in m.node_tree.nodes]) for m in o.data.materials if m] if hasattr(o.data,'materials') else []) for o in actors]))
(out/'FULL_CUT_INSPECTION.json').write_text(json.dumps(report,indent=2))
print('V064_FULL_CUT_INSPECTION_READY',flush=True)
