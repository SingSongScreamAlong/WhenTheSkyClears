import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Readability_Working_View_v034.blend'),load_ui=False,use_scripts=False);S=bpy.context.scene;S.frame_set(20);bpy.data.collections['V034 | DIAGNOSTIC joint and cloth guides'].hide_render=True;bpy.data.collections['V034 | DIAGNOSTIC hand xray overlay'].hide_render=True
def mat(name,c):
    m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();em=n.new('ShaderNodeEmission');em.inputs['Color'].default_value=(*c,1);out=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(em.outputs[0],out.inputs[0]);return m
for s,c in [('near',(.90,.015,.30)),('far',(.015,.45,.80))]:bpy.data.objects['V007_BOY | articulated drawn hand '+s].material_slots[0].material=mat('V034 occlusion test '+s,c)
coat=bpy.data.objects['V025 | COAT drawings | editable GP'];near=bpy.data.objects['V024 continuous near trouser drawing'];far=bpy.data.objects['V024 continuous far trouser drawing'];states=[('NO_COAT',[coat]),('NO_NEAR_TROUSER',[near]),('NO_COAT_OR_NEAR_TROUSER',[coat,near]),('NO_COAT_OR_TROUSERS',[coat,near,far])];S.camera=bpy.data.objects['V024 | CLOSE portrait'];S.render.resolution_x=480;S.render.resolution_y=720;S.render.resolution_percentage=100;S.render.threads_mode='FIXED';S.render.threads=2
for name,objects in states:
    for o in [coat,near,far]:o.hide_render=False
    for o in objects:o.hide_render=True
    folder=P/'previews'/('OCCLUDER_'+name);folder.mkdir(exist_ok=True);S.render.filepath=str(folder/'0020.png');bpy.ops.render.render(write_still=True)
print('V034_TARGETED_OCCLUDER_STILLS_DONE',flush=True)
