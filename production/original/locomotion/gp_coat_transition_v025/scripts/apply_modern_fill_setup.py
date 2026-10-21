import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parents[1];F=P/'native/WTSC_GP_Coat_Transition_v025.blend';bpy.ops.wm.open_mainfile(filepath=str(F),load_ui=False,use_scripts=False);S=bpy.context.scene;o=bpy.data.objects['V025 | COAT drawings | editable GP']
for l in o.data.layers:
    for f in l.frames:
        d=f.drawing;group=0
        for s in d.strokes:
            if s.cyclic:group+=1;s.fill_id=group;s.hide_stroke=True;s.fill_opacity=1.;s.fill_color=(0,0,0,0)
            else:s.fill_id=0;s.hide_stroke=False
        d.tag_positions_changed()
for m in o.data.materials:
    g=m.grease_pencil;color=g.fill_color if g.show_fill else g.color;m.diffuse_color=color;m.use_nodes=True;n=m.node_tree.nodes;n.clear();lk=m.node_tree.links;out=n.new('ShaderNodeOutputMaterial');em=n.new('ShaderNodeEmission');em.inputs['Color'].default_value=(*color[:3],1);alpha=color[3]
    if 'original packed' in m.name:
        im=n.new('ShaderNodeTexImage');im.image=g.fill_image;tc=n.new('ShaderNodeTexCoord');scale=n.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(.15,.32,1);add=n.new('ShaderNodeVectorMath');add.operation='ADD';add.inputs[1].default_value=(.325,.37,0);lk.new(tc.outputs['UV'],scale.inputs[0]);lk.new(scale.outputs[0],add.inputs[0]);lk.new(add.outputs[0],im.inputs['Vector']);lk.new(im.outputs['Color'],em.inputs['Color']);mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=.55;lk.new(im.outputs['Alpha'],mul.inputs[0]);alpha=mul.outputs[0]
    tr=n.new('ShaderNodeBsdfTransparent');mix=n.new('ShaderNodeMixShader');lk.new(tr.outputs[0],mix.inputs[1]);lk.new(em.outputs[0],mix.inputs[2]);lk.new(mix.outputs[0],out.inputs['Surface'])
    if isinstance(alpha,float):mix.inputs[0].default_value=alpha
    else:lk.new(alpha,mix.inputs[0])
bpy.data.objects['LOCO_BOY | PAINT body'].location.y=-.025
o.data.update_tag();S.frame_set(21);bpy.ops.wm.save_as_mainfile(filepath=str(F),compress=True)
report={'fill_groups_per_frame':max(s.fill_id for s in o.data.layers[0].frames[0].drawing.strokes),'node_materials':len(o.data.materials),'material_properties':[p.identifier for p in o.data.materials[0].bl_rna.properties],'scope':'Actual5.2 native fill groups and shader material test; originalv024 untouched'}
(P/'evidence/MODERN_FILL_SETUP.json').write_text(json.dumps(report,indent=2))
S.camera=bpy.data.objects['V024 | CLOSE portrait'];S.render.resolution_x=400;S.render.resolution_y=600
for f in [21,25]:S.frame_set(f);S.render.filepath=str(P/f'previews/GP_MODERN_FILL_{f:04d}.png');bpy.ops.render.render(write_still=True)
print('V025_MODERN_FILL_CHECK_COMPLETE')
