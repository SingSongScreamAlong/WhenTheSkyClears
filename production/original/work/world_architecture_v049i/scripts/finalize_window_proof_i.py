import bpy,json,hashlib,math
from pathlib import Path
O=Path(r'WTSC_LOCAL_USER\Documents\Codex\2026-10-16\task\world_architecture_v049');R=Path(r'WTSC_LOCAL_WORKSPACE');SRC=R/'work/world_art_v048d/WTSC_World_Art_Checkpoint_v048d.blend';OUT=O/'WTSC_School_Window_Depth_Proof_v049i.blend';assert not OUT.exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def md(m):
 if not m:return None
 gp=getattr(m,'grease_pencil',None);v={'name':m.name,'diffuse':list(m.diffuse_color)}
 if gp:v['gp']={k:str(getattr(gp,k,None)) for k in ['color','fill_color','show_stroke','show_fill','mode','stroke_style','fill_style']}
 if m.node_tree:
  v['nodes']=[(n.name,n.bl_idname,[(a.name,str(a.default_value)) for a in n.inputs if hasattr(a,'default_value')],n.image.name if n.type=='TEX_IMAGE' and n.image else None) for n in m.node_tree.nodes]
  v['links']=[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links]
 return hashlib.sha256(repr(v).encode()).hexdigest()
def child(s):
 def selected(o):
  while o:
   if o.name=='v016 | CHILDREN | held painterly near-age pair':return True
   o=o.parent
  return False
 return {o.name:[md(m) for m in o.data.materials] for o in s.objects if selected(o) and o.data and hasattr(o.data,'materials')}
def prep(s):
 bpy.context.window.scene=s;s.render.engine='BLENDER_EEVEE';s.render.resolution_x=3840;s.render.resolution_y=2160;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=2;s.eevee.taa_render_samples=32;s.render.use_sequencer=False;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.dither_intensity=0
bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False,use_scripts=False);s=bpy.data.scenes['WTSC_WORLD_ART_v048d_OPEN_DIAGNOSTIC'];bpy.context.window.scene=s;s.frame_set(1);protected=child(s);assert len(protected)>0
bpy.ops.wm.open_mainfile(filepath=str(O/'WTSC_Registered_School_Depth_v049e.blend'),load_ui=False,use_scripts=False);s=bpy.data.scenes['WTSC_REGISTERED_SCHOOL_DEPTH_v049e_OPEN_DIAGNOSTIC'];prep(s)
removed=[]
for o in list(bpy.data.objects):
 if o.name.startswith('v049 |') and ('right-side original foliage' in o.name or 'ruined wall' in o.name or 'deep stone sill' in o.name):removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
paint=bpy.data.materials['v049 | registered original painted stone front'];m=paint.copy();m.name='v049i | continuous original school | selected window aperture only';nt=m.node_tree;out=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL');old=out.inputs[0].links[0].from_socket
def mn(op,a,b):
 n=nt.nodes.new('ShaderNodeMath');n.operation=op
 for i,v in enumerate([a,b]):
  if isinstance(v,(float,int)):n.inputs[i].default_value=v
  else:nt.links.new(v,n.inputs[i])
 return n.outputs[0]
uv=nt.nodes.new('ShaderNodeUVMap');uv.uv_map='Paint UV';sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(uv.outputs[0],sep.inputs[0]);x=mn('MULTIPLY',sep.outputs[0],1672);y=mn('MULTIPLY',mn('SUBTRACT',1,sep.outputs[1]),941)
hole=json.loads((O/'ARCHITECTURE_BUILD_v049c.json').read_text())['window_hole_pixel_polygon'];mask=1.
for (ax,ay),(bx,by) in zip(hole,hole[1:]+hole[:1]):
 dx=bx-ax;dy=by-ay;z=mn('ADD',mn('ADD',mn('MULTIPLY',x,-dy),mn('MULTIPLY',y,dx)),dy*ax-dx*ay);mask=mn('MULTIPLY',mask,mn('GREATER_THAN',z,-.15*math.hypot(dx,dy)))
tr=nt.nodes.new('ShaderNodeBsdfTransparent');mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(mask,mix.inputs[0]);nt.links.new(old,mix.inputs[1]);nt.links.new(tr.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],out.inputs[0]);s.objects['v016 | School | broken windows and plaster'].data.materials[0]=m
s.name='WTSC_SCHOOL_WINDOW_DEPTH_v049i_OPEN_DIAGNOSTIC';s['v049i_scope']='Partial selected-window construction proof only:35cm reveal,62cm backing,thick timber/glass registered to source paint. Rejected ruin return/rear split and diagrammatic masonry overlays removed. Original1672x941 facade remains, high-res painting and full ruin construction unmet. Existing palette and children preserved.'
s.frame_set(1);assert protected==child(s)
s.frame_set(1225);bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
for f in [1201,1225,1249,1297]:
 s.frame_set(f);s.render.filepath=str(O/'native_4k_after'/f'WTSC_v049i_School_{f}_4K.png');bpy.ops.render.render(write_still=True,scene=s.name);print('WINDOW_PROOF_4K',f,flush=True)
bpy.ops.wm.open_mainfile(filepath=str(OUT),load_ui=False,use_scripts=False);s=bpy.data.scenes['WTSC_SCHOOL_WINDOW_DEPTH_v049i_OPEN_DIAGNOSTIC'];bpy.context.window.scene=s;s.frame_set(1);assert protected==child(s)
new=[o for o in s.objects if o.name.startswith('v049 |')];assert len(new)==32 and all(not o.animation_data for o in new)
unpacked=[im.name for im in bpy.data.images if im.source=='FILE' and not im.packed_file];missing_audio=[a.name for a in bpy.data.sounds if not a.packed_file and not Path(bpy.path.abspath(a.filepath)).exists()];assert not unpacked and not missing_audio
q=json.loads((O/'ARCHITECTURE_VERIFICATION_v049e.json').read_text());q.update({'native':str(OUT),'native_sha256':sha(OUT),'created_objects':len(new),'new_objects_without_actions':len(new),'rear_parallax_samples':[],'rear_foliage_depth_m':0,'ruin_return_depth_m':0,'rear_registration_error_4K_pixels':None,'removed_failed_rear_split_and_return':removed,'protected_character_object_material_sets':len(protected),'protected_character_material_nodes_unchanged':True,'protected_character_objects':list(protected),'cold_reopen_pass':True,'source_unchanged':sha(SRC)=='fe3270155538a44cb08ef3ee2c37f25461d292d5a9f10f4d2406e65822df3e5a','unpacked_images':unpacked,'missing_audio':missing_audio,'render_dimensions':[s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage],'status':'PARTIAL WINDOW DEPTH PROOF; high-resolution facade and ruin reconstruction UNMET','limitations':['Original facade remains1672x941. Native contour fitting/extrusion does not supply missing painted surface detail.','Only one selected window gains depth. Failed outer-wall/rear-foliage split and geometric masonry overlays were rejected and removed.','World-fixed bank sampling fix also retained because sourcev048d produced stretched edge columns in adjacent cameras.','Existing v040 held children remain composition witnesses. New character-author rigs/FX and the color progression study were not integrated.','Four matched actual4K before/after stills, not a full-film or normal-speed validation.','Earlier reference-guided image generation failed: AbsolutePathBuf deserialized without a base path. No repeat calls this turn; no generated replacement facade used.']})
assert q['source_unchanged'];(O/'ARCHITECTURE_VERIFICATION_v049i.json').write_text(json.dumps(q,indent=2));print('WINDOW_FINAL_READY',q['native_sha256'],len(protected),flush=True)
