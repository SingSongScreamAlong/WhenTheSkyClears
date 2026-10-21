"""Remove the remaining old leaf border using the new painted bank's upper-edge matte."""
import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];N=R/'notes/improvement_v047';prior=json.loads((N/'build_v047d.json').read_text())
source=Path(bpy.data.filepath);assert hashlib.sha256(source.read_bytes()).hexdigest()==prior['sha256']
out=R/'shots/world/WTSC_Open_Battlefield_Refinement_v047e.blend';assert not out.exists()
s=bpy.data.scenes[prior['world_scene']];m=bpy.data.scenes[prior['master_scene']];bpy.context.window.scene=s
bank=s.objects[prior['foreground']['object']];nt=bank.data.materials[0].node_tree
tex=nt.nodes['v047 | new original bank paint only'];mix=nt.nodes['v047 | fixed ground paint mask; event light downstream']
fac=mix.inputs[0].links[0].from_socket
for node in nt.nodes:
 if node.type=='MAP_RANGE' and abs(node.inputs['From Min'].default_value-.215)<1e-5 and abs(node.inputs['From Max'].default_value-.26)<1e-5:
  node.inputs['From Min'].default_value=.285;node.inputs['From Max'].default_value=.31
  break
else:raise RuntimeError('Missing bounded foreground RGB mask')
uv=next(n for n in nt.nodes if n.type=='UVMAP' and n.uv_map=='v047 | fixed bank projection from1901')
separate=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(uv.outputs[0],separate.inputs[0])
luma=nt.nodes.new('ShaderNodeRGBToBW');nt.links.new(tex.outputs['Color'],luma.inputs[0])
def ramp(value,a,b,c,d):
 n=nt.nodes.new('ShaderNodeMapRange');n.clamp=True;n.interpolation_type='SMOOTHERSTEP';nt.links.new(value,n.inputs[0])
 for name,v in [('From Min',a),('From Max',b),('To Min',c),('To Max',d)]:n.inputs[name].default_value=v
 return n.outputs[0]
def calc(op,a,b):
 n=nt.nodes.new('ShaderNodeMath');n.operation=op
 for i,x in enumerate([a,b]):
  if isinstance(x,(int,float)):n.inputs[i].default_value=x
  else:nt.links.new(x,n.inputs[i])
 return n.outputs[0]
key=ramp(luma.outputs[0],.12,.28,1,0)
edge=ramp(separate.outputs['Y'],.19,.24,0,1)
cut=calc('MULTIPLY',fac,calc('MULTIPLY',edge,calc('SUBTRACT',1,key)))
shader=next(n for n in nt.nodes if n.type=='MIX_SHADER')
original=shader.inputs[0].links[0].from_socket
nt.links.new(calc('MULTIPLY',original,calc('SUBTRACT',1,cut)),shader.inputs[0])
bank['v047e_edge_scope']='Original procedural bank alpha multiplied by a bounded new-paint upper-edge matte. Old repeated leaf silhouettes are cut where new paint shows pale path. No source image pixels altered; native bank geometry and static projection retained.'
s.name='WTSC_OPEN_BATTLEFIELD_REFINEMENT_v047e';m.name='WTSC_OPEN_5S_REFINEMENT_MASTER_v047e'
report=dict(prior);report.update({'native':str(out),'world_scene':s.name,'master_scene':m.name,
 'world_iteration_review':'v047d improved lower soil but retained the old repeated leaf row. v047e extends the ground RGB replacement and derives a bounded upper-edge matte from the new paint.',
 'artistic_acceptance':False,'full_trailer_propagated':False})
report['foreground']['alpha_change']='Bounded top-edge luminance matte in the new paint patch; retains original procedural alpha elsewhere.'
text=bpy.data.texts.new('CURRENT v047e | Foreground review correction');text.write(json.dumps(report,indent=2))
bpy.context.window.scene=m;m.frame_set(1901);bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report['sha256']=hashlib.sha256(out.read_bytes()).hexdigest();(N/'build_v047e.json').write_text(json.dumps(report,indent=2))
print('V047E_NATIVE_BUILT',str(out),flush=True)
