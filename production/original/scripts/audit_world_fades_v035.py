import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(r'WTSC_LOCAL_WORKSPACE');s=bpy.data.scenes['WTSC_WORLD_CENTERED_v034'];bpy.context.window.scene=s
def curves(id):
 out=[]
 if id.animation_data:
  if id.animation_data.action:
   for layer in id.animation_data.action.layers:
    for strip in layer.strips:
     for bag in strip.channelbags:out.extend(bag.fcurves)
  out.extend(id.animation_data.drivers)
 return out
def ancestors(socket,seen=None):
 seen=set() if seen is None else seen
 for link in socket.links:
  node=link.from_node
  if node.name in seen:continue
  seen.add(node.name)
  for inp in node.inputs:ancestors(inp,seen)
 return seen
materials=[]
for m in bpy.data.materials:
 users=[o.name for o in s.objects if o.type=='MESH' and m in list(o.data.materials)]
 if not users or not m.node_tree:continue
 nt=m.node_tree;alpha=set()
 for n in nt.nodes:
  if n.type=='MIX_SHADER':alpha|=ancestors(n.inputs[0])
 rows=[]
 for f in curves(nt):
  keypts=[[float(k.co.x),float(k.co.y)] for k in f.keyframe_points]
  nodename=next((n.name for n in nt.nodes if f.data_path.startswith(n.path_from_id())),None)
  rows.append({'path':f.data_path,'node':nodename,'affects_alpha':nodename in alpha,'keys':keypts,'driver':f.driver.expression if f.driver else None})
 if rows:materials.append({'material':m.name,'users':users,'alpha_ancestor_nodes':sorted(alpha),'animation':rows})
objects=[]
for o in s.objects:
 rows=[{'path':f.data_path,'index':f.array_index,'keys':[[float(k.co.x),float(k.co.y)] for k in f.keyframe_points],'driver':f.driver.expression if f.driver else None} for f in curves(o) if any(v in f.data_path for v in ['hide','color','scale','location'])]
 if rows:objects.append({'name':o.name,'animation':rows})
sets=[]
for o in s.objects:
 if o.type=='MESH' and any('Regional painted sets' in c.name for c in o.users_collection):
  s.frame_set(1057);b=[o.matrix_world@Vector(v) for v in o.bound_box]
  sets.append({'name':o.name,'location':list(o.location),'bounds_xz':[min(v.x for v in b),max(v.x for v in b),min(v.z for v in b),max(v.z for v in b)],'materials':[m.name for m in o.data.materials],'hide_render':o.hide_render,'parent':o.parent.name if o.parent else None})
report={'source':bpy.data.filepath,'materials_with_animation':materials,'object_visibility_and_transforms':objects,'regional_sets':sets,'world_nodes':[(n.name,n.type) for n in s.world.node_tree.nodes] if s.world and s.world.node_tree else [],'collections':[{'name':c.name,'hide_render':c.hide_render} for c in bpy.data.collections if c.hide_render]}
(R/'notes/world_v016/fade_audit_before_v035.json').write_text(json.dumps(report,indent=2))
summary=[{'material':m['material'],'users':m['users'],'alpha_animation':[a for a in m['animation'] if a['affects_alpha']]} for m in materials if any(a['affects_alpha'] for a in m['animation'])]
print('NATIVE_ALPHA_ANIMATION',json.dumps(summary),flush=True);print('REGIONAL_SETS',json.dumps(sets),flush=True)
