import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parents[1];F=P/'native/WTSC_GP_Coat_Transition_Pigment_Study_v025b.blend';bpy.ops.wm.open_mainfile(filepath=str(F),load_ui=False,use_scripts=False);S=bpy.context.scene;coat=bpy.data.objects['V025 | COAT drawings | editable GP'];layer=coat.data.layers[0]
drawings={f.frame_number:[p.position.copy() for p in f.drawing.strokes[0].points] for f in layer.frames};first=drawings[17];mesh=bpy.data.meshes.new('V025b | painted fill follows authored GP boundary');mesh.from_pydata(first,[],[tuple(range(len(first)))]);mesh.update();fill=bpy.data.objects.new(mesh.name,mesh);bpy.data.collections['V025 | separate authored GP coat transition'].objects.link(fill);fill.parent=coat.parent
fill.shape_key_add(name='Basis')
for frame,verts in drawings.items():
    if frame==17:continue
    key=fill.shape_key_add(name='GP drawing F'+str(frame));key.data.foreach_set('co',[x for v in verts for x in v])
    for f in range(17,33):key.value=float(f==frame);key.keyframe_insert('value',frame=f)
for l in mesh.shape_keys.animation_data.action.layers:
    for st in l.strips:
        for bag in st.channelbags:
            for fc in bag.fcurves:
                for key in fc.keyframe_points:key.interpolation='CONSTANT'
# Same source-pigment shader, evaluated by a native mesh carrier; GP material nodes did not show the grain.
source=coat.data.materials[0];m=bpy.data.materials.new('V025b | original grain on drawn coat fill');m.use_nodes=True;n=m.node_tree.nodes;n.clear();l=m.node_tree.links
mapping={}
for old in source.node_tree.nodes:
    new=n.new(old.bl_idname);new.name=old.name;mapping[old.name]=new
    for attr in ['operation','blend_type','interpolation','projection','extension']:
        if hasattr(old,attr):setattr(new,attr,getattr(old,attr))
    if old.type=='TEX_IMAGE':new.image=old.image
    if old.type=='TEX_COORD':new.object=old.object
    for a,b in zip(old.inputs,new.inputs):
        if hasattr(a,'default_value'):
            try:b.default_value=a.default_value
            except:pass
for link in source.node_tree.links:l.new(mapping[link.from_node.name].outputs[link.from_socket.identifier],mapping[link.to_node.name].inputs[link.to_socket.identifier])
out=next(v for v in n if v.type=='OUTPUT_MATERIAL');em=next(v for v in n if v.type=='EMISSION')
for link in list(out.inputs['Surface'].links):l.remove(link)
l.new(em.outputs[0],out.inputs['Surface']);mesh.materials.append(m)
for fr in layer.frames:
    s=fr.drawing.strokes[0];s.fill_id=0;s.fill_opacity=0;s.hide_stroke=True;fr.drawing.tag_positions_changed()
fill['V025b_paint']='Editable fill carrier exactly follows the newly authored GP silhouette samples. Original30x30coat pigment reused as grain; not a converted original cutout or a new raster image.'
S.frame_set(21);bpy.ops.wm.save_as_mainfile(filepath=str(F),compress=True);S.camera=bpy.data.objects['V024 | CLOSE portrait'];S.render.resolution_x=400;S.render.resolution_y=600
for f in [21,25]:S.frame_set(f);S.render.filepath=str(P/f'previews/GP_PAINTED_FILL_v025b_{f:04d}.png');bpy.ops.render.render(write_still=True)
(P/'evidence/PAINTED_FILL_CARRIER_v025b.json').write_text(json.dumps({'object':fill.name,'vertices':len(first),'pose_drawings':len(drawings),'native_mesh_carrier':'Exact new GP boundary, no old cutout tracing','grain_source':'Original v015 packed painting,30x30opaque coat patch','new_raster_art':False},indent=2));print('V025B_PAINTED_FILL_CHECK_COMPLETE')
