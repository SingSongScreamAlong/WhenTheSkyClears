exec((__import__('pathlib').Path(__file__).parent/'inspect_foreground.py').read_text().split('rows=[]')[0])
for name in ['v020 | Walking path | continuous blended paint','v020 | Foreground bank | continuous blended paint']:
 m=s.objects[name].data.materials[0];print(name,flush=True)
 for n in m.node_tree.nodes:
  if n.type in ['TEX_IMAGE','MATH','MAP_RANGE','COMBXYZ','SEPXYZ','TEX_NOISE'] and not n.name.startswith('v040'):
   print(n.name,n.type,getattr(n,'operation',''),[(i,x.name,list(x.default_value) if hasattr(x,'default_value') and hasattr(x.default_value,'__len__') else getattr(x,'default_value',None),[(l.from_node.name,l.from_socket.name) for l in x.links]) for i,x in enumerate(n.inputs) if not x.hide],flush=True)
