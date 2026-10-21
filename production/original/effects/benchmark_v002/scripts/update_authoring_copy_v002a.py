import bpy
from pathlib import Path
P=Path(__file__).resolve().parents[1]
m=bpy.data.materials['FXv002 | fast pale-hot core flash'];nt=m.node_tree
if not nt.nodes.get('FXv002 ignition tip falloff'):
 uv=next(n for n in nt.nodes if n.type=='TEX_COORD');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(uv.outputs['UV'],sep.inputs[0])
 cap=nt.nodes.new('ShaderNodeMapRange');cap.name='FXv002 ignition tip falloff';cap.clamp=True;cap.interpolation_type='SMOOTHERSTEP';cap.inputs['From Min'].default_value=.18;cap.inputs['From Max'].default_value=.29;cap.inputs['To Min'].default_value=1;cap.inputs['To Max'].default_value=0;nt.links.new(sep.outputs['Y'],cap.inputs[0])
 out=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL');mix=out.inputs[0].links[0].from_node;old=mix.inputs[0].links[0].from_socket
 mul=nt.nodes.new('ShaderNodeMath');mul.operation='MULTIPLY';nt.links.new(old,mul.inputs[0]);nt.links.new(cap.outputs[0],mul.inputs[1]);nt.links.new(mul.outputs[0],mix.inputs[0])
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_FX_Shot_Proof_v002a.blend'),compress=True)
print('V002A_AUTHORING_COPY_SAVED_NO_PRODUCTION_WRITE',flush=True)
