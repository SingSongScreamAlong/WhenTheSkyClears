import bpy,json,hashlib
from pathlib import Path
O=Path(r'WTSC_LOCAL_USER\Documents\Codex\2026-10-16\task\world_architecture_v049');out=O/'WTSC_Registered_School_Depth_v049b.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(O/'WTSC_Registered_School_Depth_v049.blend'),load_ui=False,use_scripts=False);s=bpy.data.scenes['WTSC_REGISTERED_SCHOOL_DEPTH_v049_OPEN_DIAGNOSTIC'];bpy.context.window.scene=s
paint=bpy.data.materials['v049 | registered original painted stone front'];faces=[]
for o in s.objects:
 if o.type=='MESH' and o.name.startswith('v049 |') and any(k in o.name for k in ['glass fragment','timber mullion','arch sash']):o.data.materials[0]=paint;faces.append(o.name)
# Keep spatial masks fixed, but fit their whole support into valid source pixels.
# EXTEND previously repeated the last image column outside0..1 at adjacent views.
fixed=[]
for m in bpy.data.materials:
 if not m.use_nodes:continue
 for t in list(m.node_tree.nodes):
  if t.type!='TEX_IMAGE' or not t.image or t.image.name!='Foreground_Bank_Paintover_v047.png' or not t.inputs[0].is_linked:continue
  nt=m.node_tree;old=t.inputs[0].links[0].from_socket;sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(old,sep.inputs[0]);x=nt.nodes.new('ShaderNodeMath');x.operation='MULTIPLY_ADD';x.inputs[1].default_value=.99/1.48;x.inputs[2].default_value=.005+.24*.99/1.48;nt.links.new(sep.outputs[0],x.inputs[0]);vec=nt.nodes.new('ShaderNodeCombineXYZ');nt.links.new(x.outputs[0],vec.inputs[0]);nt.links.new(sep.outputs[1],vec.inputs[1]);nt.links.new(sep.outputs[2],vec.inputs[2]);nt.links.new(vec.outputs[0],t.inputs[0]);fixed.append({'material':m.name,'node':t.name})
s.name='WTSC_REGISTERED_SCHOOL_DEPTH_v049b_OPEN_DIAGNOSTIC';s['v049b_refinement']='Source paint retained on front glass/wood faces; native thickness/recess preserved. World-fixed bank sampler remapped into valid image columns; no palette study merged.';s.render.resolution_percentage=100;s.eevee.taa_render_samples=32;s.frame_set(1225);bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(O/'after_preview_b').mkdir(exist_ok=True);s.render.resolution_percentage=25;s.eevee.taa_render_samples=16
for f in [1201,1225,1249]:
 s.frame_set(f);s.render.filepath=str(O/'after_preview_b'/f'After_{f}_960.png');bpy.ops.render.render(write_still=True,scene=s.name);print('PAINTED_DEPTH_PREVIEW',f,flush=True)
r=json.loads((O/'ARCHITECTURE_BUILD_v049.json').read_text());r.update({'native':str(out),'native_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'front_face_paint_reused':faces,'bank_valid_sample_remaps':fixed,'bank_mapping':'Raw support u=-.24..1.24 maps to source u=.005...995; static spatial masks unchanged.','rejected':'Uniform glass/wood front pigments looked too diagrammatic and were replaced with registered original painted fronts.'});(O/'ARCHITECTURE_BUILD_v049b.json').write_text(json.dumps(r,indent=2))
