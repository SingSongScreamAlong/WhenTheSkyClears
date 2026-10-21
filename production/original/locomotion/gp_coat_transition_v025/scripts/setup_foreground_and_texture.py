import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parents[1];F=P/'native/WTSC_GP_Coat_Transition_v025.blend';bpy.ops.wm.open_mainfile(filepath=str(F),load_ui=False,use_scripts=False);S=bpy.context.scene
fg=bpy.data.collections.new('V025 | retained foreground identity');S.collection.children.link(fg);deps=bpy.data.collections.new('V025 | evaluation dependencies');S.collection.children.link(deps)
fore=['LOCO_BOY | PAINT body','PERF_BOY | original head','V007_BOY | articulated drawn hand near','V007_BOY | drawn skin near','V007_BOY | drawn sleeve near','V007_BOY | drawn source gray cuff near']
for name in fore:
    o=bpy.data.objects[name]
    for c in list(o.users_collection):c.objects.unlink(o)
    fg.objects.link(o)
for o in list(S.objects):
    if o.type not in ['MESH','GREASEPENCIL'] and o.name not in deps.objects:deps.objects.link(o)
base=S.view_layers[0];base.name='V025 | coat and lower body';front=S.view_layers.new('V025 | original foreground')
for child in base.layer_collection.children:
    if child.name==fg.name:child.exclude=True
for child in front.layer_collection.children:
    if child.name not in [fg.name,deps.name]:child.exclude=True
S.render.film_transparent=True
g=bpy.data.node_groups.new('V025 | GP under original foreground | native composite','CompositorNodeTree');g.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor');S.compositing_node_group=g;n=g.nodes;l=g.links
a=n.new('CompositorNodeRLayers');a.layer=base.name;b=n.new('CompositorNodeRLayers');b.layer=front.name;over=n.new('CompositorNodeAlphaOver');over.inputs['Factor'].default_value=1.;l.new(a.outputs['Image'],over.inputs['Background']);l.new(b.outputs['Image'],over.inputs['Foreground']);out=n.new('NodeGroupOutput');l.new(over.outputs['Image'],out.inputs['Image'])
# Remove the misregistered full-image wash for the first authored-shape review.
# Original charcoal colour/identity is retained elsewhere; new panels remain a rough paint study.
coat=bpy.data.objects['V025 | COAT drawings | editable GP']
for layer in coat.data.layers:
    for f in layer.frames:
        for s in f.drawing.strokes:
            if s.material_index==6:s.fill_id=0;s.hide_stroke=True;s.fill_opacity=0.;s.fill_color=(0,0,0,0)
        f.drawing.tag_positions_changed()
coat['V025_pigment_status']='Misregistered full-image wash disabled; original source remains packed. Native authored contour/wash-plane study, no completed repaint claim.'
S.frame_set(21);S.camera=bpy.data.objects['V024 | CLOSE portrait'];S.render.resolution_x=400;S.render.resolution_y=600;bpy.ops.wm.save_as_mainfile(filepath=str(F),compress=True)
for f in [21,25]:S.frame_set(f);S.render.filepath=str(P/f'previews/GP_FOREGROUND_FIXED_{f:04d}.png');bpy.ops.render.render(write_still=True)
(P/'evidence/FOREGROUND_COMPOSITE_SETUP.json').write_text(json.dumps({'foreground_objects':fore,'base_layer':base.name,'foreground_layer':front.name,'native_compositor':g.name,'texture_wash_disabled':True,'reason':'Review authored contour/volume without misregistered raster wash; preserve original foreground alpha/painting through a separate native layer'},indent=2))
print('V025_FOREGROUND_CHECK_COMPLETE')
