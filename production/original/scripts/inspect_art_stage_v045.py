"""Read-only view of the v044 painted layers for an art-only copy."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(r'WTSC_LOCAL_WORKSPACE');p=Path(bpy.data.filepath);sha=hashlib.sha256(p.read_bytes()).hexdigest();assert sha=='6d661eaa07198d44c40db1abf936c9ffd42d1db8c4c12e4ca18149a2b0379593';s=bpy.data.scenes['WTSC_OPEN_BATTLEFIELD_DRAWN_TRIAL_v044'];bpy.context.window.scene=s;s.frame_set(1849);bpy.context.view_layer.update();rows=[]
for o in s.objects:
 if o.type!='MESH' or o.hide_render or any(c.hide_render for c in o.users_collection):continue
 points=[world_to_camera_view(s,s.camera,o.matrix_world@Vector(v)) for v in o.bound_box];box=[min(v.x for v in points),max(v.x for v in points),min(v.y for v in points),max(v.y for v in points)]
 if box[0]>1 or box[1]<0 or box[2]>1 or box[3]<0 or max(box[1]-box[0],box[3]-box[2])<.13:continue
 mats=[]
 for mat in o.data.materials:
  if not mat:continue
  mats.append({'name':mat.name,'images':[{'name':n.image.name,'size':list(n.image.size)} for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image] if mat.node_tree else [],'nodes':[{'name':n.name,'type':n.bl_idname,'operation':getattr(n,'operation',None),'inputs':{i.name:([*i.default_value] if hasattr(i.default_value,'__len__') and not isinstance(i.default_value,str) else i.default_value) for i in n.inputs if hasattr(i,'default_value') and not i.is_linked}} for n in mat.node_tree.nodes] if mat.node_tree and any(t in o.name for t in ['continuous blended','broken village','distant ash']) else []})
 rows.append({'object':o.name,'location':list(o.matrix_world.translation),'dimensions':list(o.dimensions),'screen_bounds':box,'collections':[c.name for c in o.users_collection],'materials':mats})
report={'source':str(p),'sha256':sha,'frame':1849,'objects':rows,'lights':[{'name':o.name,'type':o.data.type,'color':list(o.data.color),'energy':o.data.energy,'rotation':list(o.rotation_euler)} for o in s.objects if o.type=='LIGHT' and not o.hide_render]};(R/'notes/world_v016/art_stage_inspection_v045.json').write_text(json.dumps(report,indent=2));assert hashlib.sha256(p.read_bytes()).hexdigest()==sha
print('V045_ART_STAGE',json.dumps([{'name':r['object'],'location':r['location'],'bounds':r['screen_bounds'],'materials':[m['name'] for m in r['materials']]} for r in rows]),flush=True)
