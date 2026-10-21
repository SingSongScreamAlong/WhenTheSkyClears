"""Finish the same compact test with the existing original paint, not a flat flame icon."""
import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parents[1];s=bpy.data.scenes['FXv011 | compact brief impact low dust'];bpy.context.window.scene=s;r=bpy.data.objects['FXv011 | fixed impact anchor and controls'];c=bpy.data.collections['FXv011 | COMPACT IMPACT | brief flash small debris low dust']
for name in ['FXv011 | compact2to3frame flash','FXv011 | small pale core']:
    o=bpy.data.objects.get(name)
    if o:bpy.data.objects.remove(o,do_unlink=True)
im=bpy.data.images.load(str(P.parent/'benchmark_v002/assets/Hero_Explosion_Paint_v002.png'),check_existing=True);im.alpha_mode='STRAIGHT';im.pack()
me=bpy.data.meshes.new('FXv011 | compact original painted flash');me.from_pydata([(-.23,-.14,0),(.23,-.14,0),(.23,-.14,.44),(-.23,-.14,.44)],[],[(0,1,2,3)]);me.update();uv=me.uv_layers.new(name='Original paint unwarped')
for l,xy in zip(me.loops,[(0,0),(1,0),(1,1),(0,1)]):uv.data[l.index].uv=xy
m=bpy.data.materials.new('FXv011 | original painted flash brief exposure');m.use_nodes=True;m.surface_render_method='DITHERED';nt=m.node_tree;nt.nodes.clear();tex=nt.nodes.new('ShaderNodeTexImage');tex.image=im;hs=nt.nodes.new('ShaderNodeHueSaturation');hs.inputs['Saturation'].default_value=.6;hs.inputs['Value'].default_value=1.0;nt.links.new(tex.outputs['Color'],hs.inputs['Color']);em=nt.nodes.new('ShaderNodeEmission');em.inputs['Strength'].default_value=1.8;nt.links.new(hs.outputs[0],em.inputs[0]);a=nt.nodes.new('ShaderNodeMath');a.operation='MULTIPLY';nt.links.new(tex.outputs['Alpha'],a.inputs[0]);f=a.inputs[1].driver_add('default_value');f.driver.type='SCRIPTED';f.driver.expression='I*max(0,min(1,(3-t)/1.5)) if 0<=t<3 else 0'
for name,key in [('t','age'),('I','intensity')]:v=f.driver.variables.new();v.name=name;v.type='SINGLE_PROP';v.targets[0].id=r;v.targets[0].data_path='["'+key+'"]'
tr=nt.nodes.new('ShaderNodeBsdfTransparent');mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(a.outputs[0],mix.inputs[0]);nt.links.new(tr.outputs[0],mix.inputs[1]);nt.links.new(em.outputs[0],mix.inputs[2]);out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(mix.outputs[0],out.inputs[0]);me.materials.append(m);o=bpy.data.objects.new('FXv011 | compact original painted flash',me);c.objects.link(o);o.parent=r
r['flash_finish']='Original project-owned painted flash, unwarped fixed canvas, only ages0-2; no continuing smoke/card growth.'
s.frame_set(7);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Compact_Impact_Proof_v011.blend'),compress=True)
(P/'evidence/painted_flash_finish.json').write_text(json.dumps({'reason':'Initial actual keys exposed a flat flame-icon look. Finish the same test with existing original paint while keeping its compact timing and small event size.','new_art':False,'source_image':str(im.filepath),'flash_frames_relative':[0,2],'canvas_metres':[.46,.44],'animated_cloud_scaling':False,'dust_and_debris_changed':False},indent=2));print('COMPACT_PAINTED_FLASH_FINISHED',flush=True)
