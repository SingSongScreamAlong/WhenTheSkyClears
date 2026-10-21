"""Plain motion study. Same geometry/cache; no claim about unseen tutorial animation."""
import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parents[1];s=bpy.data.scenes['FXv010 | joined rupture and ground dust'];bpy.context.window.scene=s;root=bpy.data.objects['FXv010 | fixed impact anchor and timing'];asset=bpy.data.collections['FXv010 | JOINED EARTH RUPTURE and DUST']
mat=bpy.data.materials.new('FXv010 | plain silhouette review');mat.use_nodes=True;nt=mat.node_tree;nt.nodes.clear();tr=nt.nodes.new('ShaderNodeBsdfTransparent');em=nt.nodes.new('ShaderNodeEmission');em.inputs[0].default_value=(.025,.030,.030,1);mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(tr.outputs[0],mix.inputs[1]);nt.links.new(em.outputs[0],mix.inputs[2]);f=mix.inputs[0].driver_add('default_value');f.driver.expression='1 if t>=1 else 0';v=f.driver.variables.new();v.name='t';v.type='SINGLE_PROP';v.targets[0].id=root;v.targets[0].data_path='["age"]';out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(mix.outputs[0],out.inputs[0]);mat.surface_render_method='DITHERED'
for o in asset.all_objects:
    if o.name.startswith('FXv010 | connected crust section'):
        for i in range(len(o.data.materials)):o.data.materials[i]=mat
volume=next(m for m in bpy.data.materials if m.name.startswith('FXv010 | cold ink dust volume'))
for n in volume.node_tree.nodes:
    if n.type=='PRINCIPLED_VOLUME':n.inputs['Color'].default_value=(.025,.030,.030,1)
    if n.type=='MATH' and n.operation=='MULTIPLY_ADD':n.inputs[1].default_value=0;n.inputs[2].default_value=1
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Earth_Plain_Motion_v010h.blend'),compress=True)
print('PLAIN_MOTION_SAME_GEOMETRY_AND_CACHE',flush=True)
