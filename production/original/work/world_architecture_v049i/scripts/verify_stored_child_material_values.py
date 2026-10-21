import bpy,json,hashlib
from pathlib import Path
O=Path(r'WTSC_LOCAL_USER\Documents\Codex\2026-10-16\task\world_architecture_v049');R=Path(r'WTSC_LOCAL_WORKSPACE')
def value(v):
 if isinstance(v,(str,float,int,bool)) or v is None:return v
 if isinstance(v,bpy.types.ID):return [v.bl_rna.identifier,v.name]
 try:return [value(x) for x in v]
 except TypeError:return str(v)
def md(m):
 if not m:return None
 r={'name':m.name,'diffuse':value(m.diffuse_color)};gp=getattr(m,'grease_pencil',None)
 if gp:r['gp']={k:value(getattr(gp,k,None)) for k in ['color','fill_color','show_stroke','show_fill','mode','stroke_style','fill_style']}
 if m.node_tree:
  r['nodes']=[]
  for n in m.node_tree.nodes:
   q={'name':n.name,'type':n.bl_idname,'inputs':[(a.name,value(a.default_value)) for a in n.inputs if hasattr(a,'default_value')],'outputs':[(a.name,value(a.default_value)) for a in n.outputs if hasattr(a,'default_value')]}
   if n.type=='TEX_IMAGE':q['image']=n.image.name if n.image else None;q['extension']=n.extension;q['interpolation']=n.interpolation
   if hasattr(n,'color_ramp'):q['ramp']=[(a.position,value(a.color)) for a in n.color_ramp.elements]
   r['nodes'].append(q)
  r['links']=[(a.from_node.name,a.from_socket.name,a.to_node.name,a.to_socket.name) for a in m.node_tree.links]
 return hashlib.sha256(json.dumps(r,sort_keys=True).encode()).hexdigest()
def read(p,scene):
 bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False);s=bpy.data.scenes[scene];bpy.context.window.scene=s;s.frame_set(1);result={}
 for o in s.objects:
  a=o;chosen=False
  while a:
   if a.name=='v016 | CHILDREN | held painterly near-age pair':chosen=True;break
   a=a.parent
  if chosen and o.data and hasattr(o.data,'materials'):result[o.name]=[md(m) for m in o.data.materials]
 return result
base=read(R/'work/world_art_v048d/WTSC_World_Art_Checkpoint_v048d.blend','WTSC_WORLD_ART_v048d_OPEN_DIAGNOSTIC')
final=read(R/'work/world_architecture_v049i/WTSC_School_Window_Depth_Proof_v049i.blend','WTSC_SCHOOL_WINDOW_DEPTH_v049i_OPEN_DIAGNOSTIC');assert len(base)==14 and base==final
r={'source':'preserved v048d','target':'delivered v049i','actual_socket_input_output_color_values_compared':True,'gp_stroke_fill_colors_compared':True,'protected_object_material_sets':len(base),'all_equal':base==final,'digests':base}
(O/'STORED_CHILD_MATERIAL_VALUE_CHECK_v049i.json').write_text(json.dumps(r,indent=2));print('STORED_CHILD_MATERIAL_VALUES_IDENTICAL',len(base),flush=True)
