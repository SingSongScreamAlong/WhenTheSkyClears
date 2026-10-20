import bpy,json,hashlib
from pathlib import Path
O=Path(r'WTSC_LOCAL_USER\Documents\Codex\2026-10-16\task\world_architecture_v049')
R=Path(r'WTSC_LOCAL_WORKSPACE')
SRC=R/'work/world_art_v048d/WTSC_World_Art_Checkpoint_v048d.blend'
OUT=O/'WTSC_Registered_School_Depth_v049e.blend';assert not OUT.exists()
def digest(m):
 if not m or not m.node_tree:return None
 nt=m.node_tree;rows=[]
 for n in nt.nodes:
  inp=[]
  for v in n.inputs:
   if not hasattr(v,'default_value'):continue
   q=v.default_value
   try:q=list(q)
   except TypeError:pass
   inp.append((v.name,q))
  rows.append((n.name,n.bl_idname,inp,[(a.from_node.name,a.from_socket.name,a.to_node.name,a.to_socket.name) for a in nt.links if a.to_node==n],n.image.name if n.type=='TEX_IMAGE' and n.image else None))
 return hashlib.sha256(repr(rows).encode()).hexdigest()
def child_materials(s):
 return {o.name:[(m.name,digest(m)) for m in o.data.materials if m] for o in s.objects if o.type=='MESH' and any(k in o.name.lower() for k in ['boy','girl','child','v007'])}
def prep(s):
 bpy.context.window.scene=s;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=2;s.eevee.taa_render_samples=32;s.render.use_sequencer=False;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.dither_intensity=0
bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False,use_scripts=False);s=bpy.data.scenes['WTSC_WORLD_ART_v048d_OPEN_DIAGNOSTIC'];prep(s);protected=child_materials(s)
s.frame_set(1297);s.render.filepath=str(O/'native_4k_before/WTSC_v048d_School_1297_4K.png');bpy.ops.render.render(write_still=True,scene=s.name)
bpy.ops.wm.open_mainfile(filepath=str(O/'WTSC_Registered_School_Depth_v049d.blend'),load_ui=False,use_scripts=False);s=bpy.data.scenes['WTSC_REGISTERED_SCHOOL_DEPTH_v049d_OPEN_DIAGNOSTIC'];prep(s)
removed=[]
for o in list(bpy.data.objects):
 if o.name.startswith('v049 |') and any(k in o.name for k in ['jamb block','arch voussoir','fracture flake','rubble block']):removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
room=bpy.data.materials['v049 | recessed room | source-painted shadow variation']
nt=room.node_tree
for n in list(nt.nodes):
 if n.type=='VECT_MATH' and n.operation=='MINIMUM':
  # Compress the old interior paint into a dark value range without clipping
  # every source pixel to one constant color.
  n.operation='MULTIPLY';n.inputs[1].default_value=(.17,.17,.17)
  cap=nt.nodes.new('ShaderNodeVectorMath');cap.operation='MINIMUM';cap.inputs[1].default_value=(.022,.024,.025)
  targets=[l.to_socket for l in n.outputs[0].links]
  nt.links.new(n.outputs[0],cap.inputs[0])
  for target in targets:nt.links.new(cap.outputs[0],target)
assert protected==child_materials(s)
s.name='WTSC_REGISTERED_SCHOOL_DEPTH_v049e_OPEN_DIAGNOSTIC';s['v049e_review']='Removed34 diagrammatic stone/flaked/rubble overlays after native4K inspection. Continuous source-painted wall retained.35 fixed native pieces give selected window/outer damaged-edge depth. High-resolution facade painting remains unmet.'
s.frame_set(1225);bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
for f in [1201,1225,1249,1297]:
 s.frame_set(f);s.render.filepath=str(O/'native_4k_after'/f'WTSC_v049e_School_{f}_4K.png');bpy.ops.render.render(write_still=True,scene=s.name);print('CLEAN_DEPTH_4K',f,flush=True)
# Cold reopen proves final saved state rather than only the render-session state.
bpy.ops.wm.open_mainfile(filepath=str(OUT),load_ui=False,use_scripts=False);s=bpy.data.scenes['WTSC_REGISTERED_SCHOOL_DEPTH_v049e_OPEN_DIAGNOSTIC'];bpy.context.window.scene=s
new=[o for o in s.objects if o.name.startswith('v049 |')];assert all(not o.animation_data for o in new)
unpacked=[im.name for im in bpy.data.images if im.source=='FILE' and not im.packed_file];missing_audio=[a.name for a in bpy.data.sounds if not a.packed_file and not Path(bpy.path.abspath(a.filepath)).exists()]
assert not unpacked and not missing_audio;assert child_materials(s)==protected
report=json.loads((O/'ARCHITECTURE_VERIFICATION_v049d.json').read_text());report.update({'native':str(OUT),'native_sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'new_objects_without_actions':len(new),'removed_after_4K_QA':removed,'actual_4K_frames':[1201,1225,1249,1297],'source_unchanged':hashlib.sha256(SRC.read_bytes()).hexdigest()=='fe3270155538a44cb08ef3ee2c37f25461d292d5a9f10f4d2406e65822df3e5a','cold_reopen_pass':True,'protected_character_object_material_sets':len(protected),'protected_character_material_nodes_unchanged':True,'unpacked_images':unpacked,'missing_audio':missing_audio,'frame_handlers':len(bpy.app.handlers.frame_change_post),'render_dimensions':[s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage],'created_objects':len(new),'status':'PARTIAL DEPTH PROOF; continuous wall restored after4K QA; original source softness unresolved'})
assert report['source_unchanged'];(O/'ARCHITECTURE_VERIFICATION_v049e.json').write_text(json.dumps(report,indent=2));print('CLEAN_FINAL',report['native_sha256'],len(new),len(protected),flush=True)
