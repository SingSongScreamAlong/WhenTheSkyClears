import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'work/first_danger_conform_v065';build=json.loads((O/'evidence/BUILD.json').read_text());bpy.ops.wm.open_mainfile(filepath=build['native'],load_ui=False,use_scripts=False)
w=bpy.data.scenes['WTSC_FIRST_DANGER_WORLD_v065'];bpy.context.window.scene=w;w.frame_set(1065);bpy.context.view_layer.update()
rows=[]
for ob in w.objects:
 if ob.type!='MESH' or ob.hide_render:continue
 images=[]
 for slot in ob.material_slots:
  if slot.material and slot.material.node_tree:
   images.extend(n.image.name for n in slot.material.node_tree.nodes if n.type=='TEX_IMAGE' and n.image)
 if any('Oak' in x or 'Tree' in x for x in images) or any(x in ob.name.lower() for x in ['oak','trunk','foreground tree']):
  rows.append({'name':ob.name,'images':images,'location':list(ob.matrix_world.translation),'parent':ob.parent.name if ob.parent else None})
(O/'evidence/FOREGROUND_OBJECTS.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
