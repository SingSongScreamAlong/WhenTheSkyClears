import bpy,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];f=ROOT/'locomotion/connected_model_fit_v049/native/WTSC_Connected_Model_Fit_v049.blend';h=hashlib.sha256(f.read_bytes()).hexdigest();assert h=='2f78c5cd86b96d437d97a165b8b61473bcd6c9d1ab284015c229bfb11c6f9a94';bpy.ops.wm.open_mainfile(filepath=str(f),load_ui=False,use_scripts=False);bpy.context.window.scene=bpy.data.scenes['V049 | MODEL FIT AND GROUPED HANDS | v048 motion'];out=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not o.parent or o.parent.type!='ARMATURE':continue
 if o.get('proportion_role')!='head' and o.get('wardrobe_role') not in ['hand','skin']:continue
 mats=[]
 for m in o.data.materials:
  nodes=[{'name':n.name,'type':n.type,'image':n.image.name if n.type=='TEX_IMAGE' and n.image else None,'inputs':[(s.name,str(s.default_value)) for s in n.inputs if hasattr(s,'default_value') and not s.is_linked]} for n in m.node_tree.nodes]
  links=[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links];mats.append({'name':m.name,'nodes':nodes,'links':links})
 out.append({'name':o.name,'role':o.get('proportion_role',o.get('wardrobe_role')),'rig':o.parent.name,'vertices':len(o.data.vertices),'uvs':[l.name for l in o.data.uv_layers],'materials':mats,'visible':not o.hide_render,'properties':{k:v for k,v in o.items() if isinstance(v,(str,float,int))}})
(P/'evidence/SOURCE_FINISH_INSPECTION.json').write_text(json.dumps(out,indent=2));assert hashlib.sha256(f.read_bytes()).hexdigest()==h;print('V050_READ_ONLY_SOURCE_INSPECTION_DONE')
