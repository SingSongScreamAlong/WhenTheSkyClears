import bpy,json,hashlib
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE');w=bpy.data.scenes['WTSC_WORLD_CORRECTED_v039'];root=w.objects['v036 | Camp hearth | fixed emitter'];changed=[]
for mat in bpy.data.materials:
 if not mat.name.startswith('v039') or not mat.node_tree:continue
 nt=mat.node_tree
 for n in nt.nodes:
  if n.type!='VALUE' or not any(s in n.name for s in ['coherent fire beat','source-connected actor beat']):continue
  curve=next((f for f in nt.animation_data.drivers if f.data_path==n.outputs[0].path_from_id('default_value')),None)
  if not curve:continue
  d=curve.driver;v=d.variables.new();v.name='power';v.type='SINGLE_PROP';v.targets[0].id=root;v.targets[0].data_path='["light_power"]';d.expression='v*power/420';changed.append({'material':mat.name,'node':n.name})
bpy.context.window.scene=w;w.frame_set(1609);bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
p=R/'notes/world_v016/camp_paint_language_v039.json';r=json.loads(p.read_text());r['sha256']=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest();r['physical_power_linked_receivers']=changed;p.write_text(json.dumps(r,indent=2));print('PHYSICAL_POWER_RECEIVERS_LINKED',len(changed),flush=True)
