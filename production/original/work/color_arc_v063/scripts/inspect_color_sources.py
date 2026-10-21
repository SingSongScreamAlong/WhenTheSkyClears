import bpy,json
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE');O=R/'work/color_arc_v063'
bpy.ops.wm.open_mainfile(filepath=str(R/'work/continuity_restore_v062/native/WTSC_Painted_Continuity_Restored_v062.blend'),load_ui=False,use_scripts=False)
s=bpy.data.scenes['WTSC_PAINTED_CONTINUITY_RESTORED_v062'];bpy.context.window.scene=s;s.frame_set(981)
root=bpy.data.objects['V047 | shared travel | steady .73125mps']
def row(o):
 return {'name':o.name,'roles':dict(o.items()),'uv':[l.name for l in o.data.uv_layers],'mats':[slot.material.name if slot.material else None for slot in o.material_slots]}
r={'target':[row(o) for o in root.children_recursive if o.type=='MESH' and 'GIRL' in o.name and not o.hide_render]}
src=R/'locomotion/face_hand_finish_v050/native/WTSC_Face_Hand_Finish_v050.blend'
with bpy.data.libraries.load(str(src),link=False) as (a,b):
 r['available_materials']=[n for n in a.materials if 'V050 GIRL' in n];b.materials=r['available_materials']
r['imported']=[{'name':m.name,'mode':m.surface_render_method,'uvmaps':[(n.name,n.uv_map) for n in m.node_tree.nodes if n.type=='UVMAP'],'images':[(n.name,n.image.name) for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]} for m in b.materials]
(O/'evidence/COLOR_SOURCE_INSPECTION.json').write_text(json.dumps(r,indent=2,default=str));print('COLOR_SOURCE_INSPECTION_READY',flush=True)
