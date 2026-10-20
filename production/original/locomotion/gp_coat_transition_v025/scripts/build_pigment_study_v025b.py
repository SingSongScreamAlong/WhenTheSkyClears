import bpy,math,json
from pathlib import Path
P=Path(__file__).resolve().parents[1];F=P/'native/WTSC_GP_Coat_Transition_Pigment_Study_v025b.blend';bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_GP_Upper_Loading_v025b.blend'),load_ui=False,use_scripts=False);S=bpy.context.scene;rig=bpy.data.objects['LOCO_BOY | RIG'];coat=bpy.data.objects['V025 | COAT drawings | editable GP']
sampler=bpy.data.objects.new('V025b | pigment space follows chest',None);sampler.parent=rig.parent;bpy.data.collections['V025 | evaluation dependencies'].objects.link(sampler)
for f in range(17,33):
    S.frame_set(f);bpy.context.view_layer.update();H=rig.pose.bones['pelvis'].head;ch=rig.pose.bones['chest'].tail;sampler.location=H;sampler.rotation_euler=(0,math.atan2(ch.x-H.x,ch.z-H.z),0);sampler.keyframe_insert('location',frame=f);sampler.keyframe_insert('rotation_euler',frame=f)
image=bpy.data.images['Pair_Painterly_Near_Age_v015.png']
for idx,m in enumerate(coat.data.materials):
    if idx==6:continue
    n=m.node_tree.nodes;l=m.node_tree.links;em=next(v for v in n if v.type=='EMISSION');base=tuple(em.inputs['Color'].default_value)
    tex=n.new('ShaderNodeTexCoord');tex.object=sampler;sep=n.new('ShaderNodeSeparateXYZ');l.new(tex.outputs['Object'],sep.inputs[0]);axes=[]
    for a,freq,extent,offset in [('X',36,30/1672,600/1672),('Z',32,30/941,1-410/941)]:
        mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=freq;l.new(sep.outputs[a],mul.inputs[0]);ping=n.new('ShaderNodeMath');ping.operation='PINGPONG';ping.inputs[1].default_value=1;l.new(mul.outputs[0],ping.inputs[0]);scale=n.new('ShaderNodeMath');scale.operation='MULTIPLY_ADD';scale.inputs[1].default_value=extent;scale.inputs[2].default_value=offset;l.new(ping.outputs[0],scale.inputs[0]);axes.append(scale.outputs[0])
    uv=n.new('ShaderNodeCombineXYZ');l.new(axes[0],uv.inputs['X']);l.new(axes[1],uv.inputs['Y']);im=n.new('ShaderNodeTexImage');im.image=image;im.interpolation='Linear';l.new(uv.outputs[0],im.inputs['Vector']);gray=n.new('ShaderNodeRGBToBW');l.new(im.outputs['Color'],gray.inputs[0]);ratio=n.new('ShaderNodeMath');ratio.operation='DIVIDE';ratio.inputs[1].default_value=.0111254725;l.new(gray.outputs[0],ratio.inputs[0]);contrast=n.new('ShaderNodeMath');contrast.operation='MULTIPLY_ADD';contrast.inputs[1].default_value=.60;contrast.inputs[2].default_value=.40;l.new(ratio.outputs[0],contrast.inputs[0]);mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1.;mix.inputs[1].default_value=base;l.new(contrast.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],em.inputs['Color'])
coat['V025b_paint']='Original opaque30x30source coat pigment patch, mirrored repeats in chest-attached object space, applied to new GP planes. No original big folds or identity images are remapped over the coat.'
S['V025b_status']='One half-step pigment/contour study; artistic acceptance open';S.frame_set(21);bpy.ops.wm.save_as_mainfile(filepath=str(F),compress=True)
S.camera=bpy.data.objects['V024 | CLOSE portrait'];S.render.resolution_x=400;S.render.resolution_y=600
for f in [21,25]:S.frame_set(f);S.render.filepath=str(P/f'previews/GP_PIGMENT_v025b_{f:04d}.png');bpy.ops.render.render(write_still=True)
(P/'evidence/PIGMENT_STUDY_v025b.json').write_text(json.dumps({'native':str(F),'source_image':image.name,'source_patch_pixels':[600,380,630,410],'mapping':'Mirrored small pigment patch in chest-attached object space; original silhouette/folds not converted','source_v025_preserved':True,'scope':'Same16drawing half-step, no cycle expansion'},indent=2));print('V025B_PIGMENT_STUDY_RENDERED')
