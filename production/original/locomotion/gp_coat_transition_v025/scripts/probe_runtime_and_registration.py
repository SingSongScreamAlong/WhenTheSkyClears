import bpy,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'reference/PRESERVED_WALK_v024.blend'),load_ui=False,use_scripts=False)
def props(x):
    if hasattr(x,'bl_rna'):return [{'id':p.identifier,'type':p.type,'readonly':p.is_readonly} for p in x.bl_rna.properties]
    return [{'id':n,'value':str(getattr(x,n))[:180]} for n in dir(x) if not n.startswith('_')]
gp=bpy.data.grease_pencils.new('V025 runtime probe');ob=bpy.data.objects.new('V025 runtime probe',gp);bpy.context.scene.collection.objects.link(ob)
layer=gp.layers.new('probe',set_active=True);frame=layer.frames.new(1);drawing=frame.drawing;drawing.add_strokes([4]);stroke=drawing.strokes[0]
mat=bpy.data.materials.new('V025 probe');bpy.data.materials.create_gpencil_data(mat);ob.data.materials.append(mat)
report={'version':bpy.app.version_string,'build_hash':bpy.app.build_hash.decode(),'object_type':ob.type,'data_rna':gp.bl_rna.identifier,'frame_rna':frame.bl_rna.identifier,'drawing_rna':drawing.bl_rna.identifier,'drawing_properties':props(drawing),'stroke_properties':props(stroke),'point_properties':props(stroke.points[0]),'layer_properties':props(layer),'material_properties':props(mat.grease_pencil),'has_object_modifiers':hasattr(ob,'modifiers'),'grease_pencil_operators':[n for n in dir(bpy.ops.grease_pencil) if any(k in n for k in ['interpol','stroke','material'])]}
body=bpy.data.objects['LOCO_BOY | PAINT body'];rig=body.parent
report['body']={'matrix_world':[list(v) for v in body.matrix_world],'vertices':len(body.data.vertices),'materials':[m.name for m in body.data.materials],'bounds_base':list(map(list,body.bound_box)),'rig':rig.name,'bones':{n:{'rest_head':list(rig.data.bones[n].head_local),'rest_tail':list(rig.data.bones[n].tail_local)} for n in ['pelvis','chest','head','thigh_near','shin_near']}}
samples=[]
for f in [17,19.25,21,23,25.25,27,29]:
    bpy.context.scene.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();e=body.evaluated_get(bpy.context.evaluated_depsgraph_get())
    samples.append({'frame':f,'root':list(rig.parent.location),'bones':{n:{'head':list(rig.matrix_world@rig.pose.bones[n].head),'tail':list(rig.matrix_world@rig.pose.bones[n].tail)} for n in ['pelvis','chest','head','upper_arm_near','upper_arm_far','thigh_near','shin_near','foot_near']},'body_vertices':[list(e.matrix_world@v.co) for v in e.data.vertices],'uv_by_loop':[list(u.uv) for u in body.data.uv_layers.active.data],'polygons':[list(p.vertices) for p in body.data.polygons]})
report['registration_samples']=samples
(P/'evidence/RUNTIME_API_AND_REGISTRATION.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ['registration_samples','body']},indent=2))
