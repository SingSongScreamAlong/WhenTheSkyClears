"""Material-only correction after full-shot review. Native shape keys stay identical."""
import bpy,json,hashlib,struct,ast
from pathlib import Path
P=Path(__file__).resolve().parents[1];s=bpy.data.scenes['FXv008 | coherent painted proof'];bpy.context.window.scene=s
asset=bpy.data.collections['FXv008 | ONE COHERENT NATIVE BLAST'];root=bpy.data.objects['FXv008 | fixed world impact and controls']
tree=ast.parse((P/'scripts/build_coherent.py').read_text());tree.body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='geometry_hash'];exec(compile(tree,'owned_geometry_hash','exec'),globals())
before=geometry_hash();expected=json.loads((P/'evidence/build_coherent.json').read_text())['geometry_sha256'];assert before==expected
materials=set(m for ob in asset.all_objects if ob.type=='MESH' for m in ob.data.materials)
for m in materials:
    nt=m.node_tree
    if 'rollover shadow' in m.name:
        # The painted source already contains rolled value structure. Do not overlay
        # the silhouette study's explanatory graphic C marks on the final paint.
        node=nt.nodes.get('Same coverage in silhouette and paint');f=node.inputs[1].driver_add('default_value');f.driver.expression='I*.28*(1-P)*max(0,min(1,(92-t)/32)) if t>=2 else 0'
    if 'impulse flash' in m.name:
        tex=next(n for n in nt.nodes if n.type=='TEX_IMAGE');tex.image=bpy.data.images['FXv002 original detailed eruption | packed'];tex.image.pack()
        offset=tex.inputs['Vector'].links[0].from_node;offset.inputs[1].default_value=(.12,0,0);offset.inputs[0].links[0].from_node.inputs[1].default_value=(.76,.30,1)
        emission=next(n for n in nt.nodes if n.type=='EMISSION');warm=emission.inputs['Color'].links[0].from_node;nt.links.new(tex.outputs['Color'],warm.inputs[2])
        alpha=nt.nodes.get('Same coverage in silhouette and paint');feather=alpha.inputs[0].links[0].from_socket;detail=nt.nodes.new('ShaderNodeMath');detail.operation='MULTIPLY';nt.links.new(feather,detail.inputs[0]);nt.links.new(tex.outputs['Alpha'],detail.inputs[1]);nt.links.new(detail.outputs[0],alpha.inputs[0]);continue
    if 'receiver' in m.name:continue
    fill=next(n for n in nt.nodes if n.type=='MIX_RGB' and n.inputs[0].is_linked and n.inputs[0].links[0].from_node.type=='MATH' and n.inputs[0].links[0].from_node.operation=='MULTIPLY')
    coord=next(n for n in nt.nodes if n.type=='TEX_COORD');noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=24;noise.inputs['Detail'].default_value=3.5;noise.inputs['Roughness'].default_value=.75;nt.links.new(coord.outputs['UV'],noise.inputs['Vector']);grain=nt.nodes.new('ShaderNodeValToRGB');grain.name='Dark charcoal grain in pigment gaps';grain.color_ramp.elements[0].color=(.006,.009,.011,1);grain.color_ramp.elements[1].color=(.032,.043,.049,1);nt.links.new(noise.outputs['Fac'],grain.inputs[0]);nt.links.new(grain.outputs[0],fill.inputs[1])
    # Micro edge grain is advected with the same mesh. It is not temporal erosion.
    alpha=nt.nodes.get('Same coverage in silhouette and paint');feather=alpha.inputs[0].links[0].from_socket;edge=nt.nodes.new('ShaderNodeMath');edge.operation='MULTIPLY';nt.links.new(noise.outputs['Fac'],edge.inputs[0]);edge.inputs[1].default_value=.26;lift=nt.nodes.new('ShaderNodeMath');lift.operation='ADD';lift.inputs[1].default_value=.74;nt.links.new(edge.outputs[0],lift.inputs[0]);combine=nt.nodes.new('ShaderNodeMath');combine.operation='MULTIPLY';nt.links.new(feather,combine.inputs[0]);nt.links.new(lift.outputs[0],combine.inputs[1]);nt.links.new(combine.outputs[0],alpha.inputs[0])
after=geometry_hash();assert before==after
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Coherent_Painted_v008b.blend'),compress=True)
helper=bpy.data.node_groups['FXv008 | FX-only restrained bloom over'];bpy.data.libraries.write(str(P/'native/WTSC_Coherent_Append_v008b.blend'),{asset,helper},fake_user=True,compress=True)
(P/'evidence/material_refinement.json').write_text(json.dumps({'geometry_before':before,'geometry_after':after,'same_native_motion':True,'changes':['Removed silhouette-only graphic fold markers from paint','Added advected dark grain to unpainted pigment gaps','Used the original painted ignition lower-detail/alpha for the brief hot flash instead of solid yellow','No time-varying material pose or source image alpha controls the cloud silhouette'],'status':'Material review correction only; render actual corrected proof.'},indent=2));print('MATERIAL_ONLY_REFINEMENT_SAVED',before)
