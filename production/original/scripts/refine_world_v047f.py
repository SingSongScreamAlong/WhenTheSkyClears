"""The remaining repeat row belongs to the path paint, behind the foreground bank."""
import bpy,json,hashlib
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];N=R/'notes/improvement_v047';prior=json.loads((N/'build_v047d.json').read_text())
source=Path(bpy.data.filepath);assert hashlib.sha256(source.read_bytes()).hexdigest()==prior['sha256']
out=R/'shots/world/WTSC_Open_Battlefield_Refinement_v047f.blend';assert not out.exists()
s=bpy.data.scenes[prior['world_scene']];m=bpy.data.scenes[prior['master_scene']];bpy.context.window.scene=s;s.frame_set(1901);bpy.context.view_layer.update()
path=s.objects['v020 | Walking path | continuous blended paint'];mat=path.data.materials[0].copy();mat.name='v047f | quieter lower path paint with fixed projection';path.data.materials[0]=mat;nt=mat.node_tree
uv=path.data.uv_layers.new(name='v047f | fixed lower path projection1901')
for loop in path.data.loops:
 p=world_to_camera_view(s,s.camera,path.matrix_world@path.data.vertices[loop.vertex_index].co)
 uv.data[loop.index].uv=(p.x,p.y)
node=nt.nodes.new('ShaderNodeUVMap');node.uv_map=uv.name
tex=nt.nodes.new('ShaderNodeTexImage');tex.name='v047f | new lower path original paint only';tex.image=bpy.data.images.get('Foreground_Bank_Paintover_v047.png');assert tex.image;tex.extension='EXTEND';nt.links.new(node.outputs[0],tex.inputs[0])
sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(node.outputs[0],sep.inputs[0])
def ramp(value,a,b,c,d):
 n=nt.nodes.new('ShaderNodeMapRange');n.clamp=True;n.interpolation_type='SMOOTHERSTEP';nt.links.new(value,n.inputs[0])
 for name,v in [('From Min',a),('From Max',b),('To Min',c),('To Max',d)]:n.inputs[name].default_value=v
 return n.outputs[0]
def mul(a,b):
 n=nt.nodes.new('ShaderNodeMath');n.operation='MULTIPLY';nt.links.new(a,n.inputs[0]);nt.links.new(b,n.inputs[1]);return n.outputs[0]
fac=mul(ramp(sep.outputs['X'],0,.08,0,1),ramp(sep.outputs['X'],.92,1,1,0))
fac=mul(fac,ramp(sep.outputs['Y'],.14,.175,0,1));fac=mul(fac,ramp(sep.outputs['Y'],.248,.271,1,0))
receiver=nt.nodes['v041 DORMANT | source-bound local warmth'];target=receiver.inputs[6];old=target.links[0].from_socket
mix=nt.nodes.new('ShaderNodeMixRGB');mix.name='v047f | lower path plant-repeat replacement'
nt.links.new(fac,mix.inputs[0]);nt.links.new(old,mix.inputs[1]);nt.links.new(tex.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],target)
path['v047f_scope']='Fixed bank-context repaint sampled below feet, replacing repeated lower path plants; RGB only. Original geometry/alpha/physical light receiver retained. No new generated character pixels sampled.'
s.name='WTSC_OPEN_BATTLEFIELD_REFINEMENT_v047f';m.name='WTSC_OPEN_5S_REFINEMENT_MASTER_v047f'
report=dict(prior);report.update({'native':str(out),'world_scene':s.name,'master_scene':m.name,
 'world_iteration_review':'v047d improved bank soil. v047e edge matte did not address the repeat row because it is also in the lower path painting. v047f replaces that bounded lower path RGB band while preserving foot contact/geometry/alpha.',
 'lower_path_repaint':{'object':path.name,'fixed_reference_frame':1901,'image_uv_y_band':[.14,.175,.248,.271],
   'alpha_changed':False,'geometry_changed':False,'light_receiver_retained':True},
 'artistic_acceptance':False,'full_trailer_propagated':False})
text=bpy.data.texts.new('CURRENT v047f | Ground-layer review correction');text.write(json.dumps(report,indent=2))
bpy.context.window.scene=m;m.frame_set(1901);bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report['sha256']=hashlib.sha256(out.read_bytes()).hexdigest();(N/'build_v047f.json').write_text(json.dumps(report,indent=2))
print('V047F_NATIVE_BUILT',str(out),flush=True)
