import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'work/first_danger_conform_v065'
S=R/'work/color_arc_v063/native/WTSC_Shared_Color_To_Charcoal_v063.blend'
bpy.ops.wm.open_mainfile(filepath=str(S),load_ui=False,use_scripts=False)
s=bpy.data.scenes['WTSC_SHARED_COLOR_TO_CHARCOAL_v063'];m=bpy.data.scenes['WTSC_FIRST_DANGER_TITLE_CHECK_v060'];bpy.context.window.scene=s
def curves(a):
 return [f for l in a.layers for st in l.strips for b in st.channelbags for f in b.fcurves] if a else []
def ani(o):
 a=o.animation_data.action if o.animation_data else None
 return {'name':a.name if a else None,'curves':[{'path':f.data_path,'index':f.array_index,'range':[min((k.co.x for k in f.keyframe_points),default=0),max((k.co.x for k in f.keyframe_points),default=0)],'extrapolation':f.extrapolation,'modifiers':[x.type for x in f.modifiers]} for f in curves(a)]}
root=bpy.data.objects['V047 | shared travel | steady .73125mps']
samples=[]
for g in [913,936,937,957,981,1033,1056,1057,1080]:
 s.frame_set(g);m.frame_set(g);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
 samples.append({'frame':g,'root':list(root.matrix_world.translation),'cam':list(s.camera.matrix_world.translation),'actors':[{'name':o.name,'location':list(o.evaluated_get(dg).matrix_world.translation)} for o in root.children_recursive if o.type=='ARMATURE']})
rows={'source_sha':hashlib.sha256(S.read_bytes()).hexdigest(),'root_animation':ani(root),'camera_animation':ani(s.camera),'samples':samples,
 'scene_names':[x.name for x in bpy.data.scenes],
 'title_objects':[{'name':o.name,'type':o.type,'location':list(o.location),'scale':list(o.scale),'body':o.data.body if o.type=='FONT' else None,'size':o.data.size if o.type=='FONT' else None,'animation':ani(o)} for o in m.objects],
 'title_nodes':[{'name':n.name,'type':n.bl_idname,'inputs':[(i.name,str(i.default_value) if hasattr(i,'default_value') else None) for i in n.inputs],'scene':n.scene.name if n.type=='R_LAYERS' and n.scene else None} for n in m.compositing_node_group.nodes],
 'root_children':[{'name':o.name,'type':o.type,'hide':o.hide_render,'parent':o.parent.name if o.parent else None,'shape_keys':len(o.data.shape_keys.key_blocks) if o.type=='MESH' and o.data.shape_keys else 0} for o in root.children_recursive]}
(O/'evidence/SOURCE_INSPECTION.json').write_text(json.dumps(rows,indent=2))
print('SOURCE_INSPECTED',len(s.objects),len(root.children_recursive))
