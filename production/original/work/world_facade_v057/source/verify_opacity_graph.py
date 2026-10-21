import bpy,json,hashlib
from pathlib import Path
O=Path(__file__).parent;SRC=Path(r'WTSC_LOCAL_WORKSPACE\work\world_architecture_v049i\WTSC_School_Window_Depth_Proof_v049i.blend');NEW=O/'WTSC_Continuous_Facade_Source_Lighting_TEST_v057.blend'
def inspect(path):
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);school=bpy.data.objects['v016 | School | broken windows and plaster'];m=school.data.materials[0];nt=m.node_tree;old=[n for n in nt.nodes if n.type=='TEX_IMAGE' and n.image and n.image.name=='School_v001.png'][0]
 def dependency(sock,seen=()):
  if not sock.is_linked:
   try:return repr(list(sock.default_value))
   except:return repr(getattr(sock,'default_value',None))
  l=sock.links[0];n=l.from_node
  if n.name in seen:return ['cycle',n.name]
  props={k:str(getattr(n,k,None)) for k in ['operation','blend_type','interpolation_type','clamp','uv_map'] if hasattr(n,k)}
  if n.type=='TEX_IMAGE':return [n.bl_idname,n.name,l.from_socket.name,n.image.name,props,dependency(n.inputs['Vector'],seen+(n.name,))]
  return [n.bl_idname,n.name,l.from_socket.name,props,[(x.name,dependency(x,seen+(n.name,))) for x in n.inputs if not x.is_unavailable]]
 alpha=[]
 for n in nt.nodes:
  if n.bl_idname=='ShaderNodeMixShader':alpha.append([n.name,dependency(n.inputs[0])])
  if n.bl_idname=='ShaderNodeBsdfPrincipled':alpha.append([n.name,dependency(n.inputs['Alpha'])])
 return {'old_source_alpha_links':sorted((l.to_node.name,l.to_socket.name) for l in old.outputs['Alpha'].links),'opacity_control_dependencies':alpha,'original_color_targets':sorted((l.to_node.name,l.to_socket.name) for l in old.outputs['Color'].links),'unpacked_images':[i.name for i in bpy.data.images if i.source=='FILE' and not i.packed_file]}
a=inspect(SRC);b=inspect(NEW);q={'source':a,'candidate':b,'original_source_alpha_links_equal':a['old_source_alpha_links']==b['old_source_alpha_links'],'opacity_control_dependencies_equal':a['opacity_control_dependencies']==b['opacity_control_dependencies'],'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'native_sha256':hashlib.sha256(NEW.read_bytes()).hexdigest()}
assert q['original_source_alpha_links_equal'] and q['opacity_control_dependencies_equal'] and not b['unpacked_images']
(O/'OPACITY_GRAPH_VERIFICATION.json').write_text(json.dumps(q,indent=2));print('OPACITY_GRAPH_VERIFIED',json.dumps({k:v for k,v in q.items() if k not in ['source','candidate']}))
