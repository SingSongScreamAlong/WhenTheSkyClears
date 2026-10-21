import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(r'WTSC_LOCAL_WORKSPACE');O=Path(r'WTSC_LOCAL_USER\Documents\Codex\2026-10-16\task\world_art_v048')
SRC=R/'shots/world/WTSC_Painted_World_Full_Trailer_Editable_v040.blend';FINAL=O/'WTSC_World_Art_Checkpoint_v048c.blend';assert not FINAL.exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fingerprint():
 result={}
 for o in bpy.data.objects:
  if o.name.startswith('v048'):continue
  q={'type':o.type,'parent':o.parent.name if o.parent else None,'matrix':[list(v) for v in o.matrix_basis]}
  if o.type=='MESH':q['geometry']=hashlib.sha256(repr(([tuple(v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])).encode()).hexdigest()
  if o.type=='FONT':q['text']=[o.data.body,o.data.font.name,o.data.size]
  result[o.name]=q
 return result
def actions():
 out={}
 for a in bpy.data.actions:
  rows=[]
  for l in a.layers:
   for st in l.strips:
    for bag in st.channelbags:
     for f in bag.fcurves:rows.append((f.data_path,f.array_index,[(tuple(k.co),k.interpolation) for k in f.keyframe_points]))
  out[a.name]=hashlib.sha256(repr(rows).encode()).hexdigest()
 return out
def prepare(s):
 bpy.context.window.scene=s;s.render.engine='BLENDER_EEVEE';s.render.resolution_x=3840;s.render.resolution_y=2160;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=2;s.render.use_sequencer=False;s.eevee.taa_render_samples=32;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.dither_intensity=0
frames=[('peaceful',241),('transition',1201),('war_zone',1849)]
bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False,use_scripts=False);s=bpy.data.scenes['WTSC_WORLD_CORRECTED_v040'];prepare(s);s.frame_set(1);original=fingerprint();original_actions=actions();timing={s.name:[s.frame_start,s.frame_end,s.render.fps] for s in bpy.data.scenes}
(O/'native_4k_before').mkdir(exist_ok=True)
for label,f in frames:
 s.frame_set(f);s.render.filepath=str(O/'native_4k_before'/f'WTSC_v040_{label}_{f}_4K.png');bpy.ops.render.render(write_still=True,scene=s.name);print('NATIVE_4K_BEFORE',label,flush=True)
bpy.ops.wm.open_mainfile(filepath=str(O/'WTSC_World_Art_Branch_v048b.blend'),load_ui=False,use_scripts=False);s=bpy.data.scenes['WTSC_WORLD_CORRECTED_v040'];prepare(s)
# Preserve the rejected experiment separately; remove only its own hidden objects
# from the final reviewable checkpoint.
removed=[]
for o in list(bpy.data.objects):
 if o.name.startswith('v048') and o.hide_render:removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
# Warm loam belongs to the peaceful village; keep winter ash in the war section.
m=bpy.data.materials['v048b | peaceful original painted earth'];nt=m.node_tree;em=next(n for n in nt.nodes if n.type=='EMISSION');old=em.inputs[0].links[0].from_socket;n=nt.nodes.new('ShaderNodeMixRGB');n.blend_type='MULTIPLY';n.inputs[0].default_value=.60;n.inputs[2].default_value=(1.16,1.02,.76,1);nt.links.new(old,n.inputs[1]);nt.links.new(n.outputs[0],em.inputs[0])
s.frame_set(1);after=fingerprint();acts=actions();base_ok=all(after.get(n)==v for n,v in original.items());act_ok=all(acts.get(n)==v for n,v in original_actions.items());assert base_ok and act_ok
timing_ok=timing=={s.name:[s.frame_start,s.frame_end,s.render.fps] for s in bpy.data.scenes};assert timing_ok
new=[o for o in s.objects if o.name.startswith('v048')];assert all(not o.animation_data for o in new)
pan=s.objects['v026 | Countryside panorama | stationary at true depth'];cover=[]
for f in list(range(1,2401,24))+[2400]:
 s.frame_set(f);bpy.context.view_layer.update();v=[world_to_camera_view(s,s.camera,pan.matrix_world@Vector(v)) for v in pan.bound_box];xmin=min(p.x for p in v);xmax=max(p.x for p in v);ymin=min(p.y for p in v);ymax=max(p.y for p in v);cover.append({'frame':f,'covers':xmin<=0 and xmax>=1 and ymin<=0 and ymax>=1,'bounds':[xmin,xmax,ymin,ymax]})
assert all(x['covers'] for x in cover)
# Check persistent structure alpha dependencies, rather than mistaking RGB grades
# or retained fire animation for building dissolves.
def ancestors(sock,seen=None):
 seen=set() if seen is None else seen
 for l in sock.links:
  n=l.from_node
  if n.name in seen:continue
  seen.add(n.name)
  for inp in n.inputs:ancestors(inp,seen)
 return seen
alpha_issues=[]
for o in s.objects:
 if o.type!='MESH' or not any(k in o.name for k in ['Village continues','Woods |','School | broken','Camp | pinned','Battlefield | broken','Ruins | distant']):continue
 for m in o.data.materials:
  if not m or not m.node_tree:continue
  nt=m.node_tree;alpha=set()
  for n in nt.nodes:
   if n.type=='MIX_SHADER':alpha|=ancestors(n.inputs[0])
  if nt.animation_data:
   curves=list(nt.animation_data.drivers)
   a=nt.animation_data.action
   if a:
    for l in a.layers:
     for st in l.strips:
      for bag in st.channelbags:curves+=list(bag.fcurves)
   for fc in curves:
    if any(fc.data_path.startswith(nt.nodes[n].path_from_id()) for n in alpha):alpha_issues.append({'object':o.name,'path':fc.data_path})
assert not alpha_issues
s.name='WTSC_WORLD_ART_v048c_OPEN_DIAGNOSTIC';s['v048_final']='Partial world art checkpoint. Native original title/edit scenes retained; this open diagnostic bypasses the title mask only for art review. No character or FX changes.'
s.frame_set(1849);s.render.filepath=str(O/'native_4k_after/WTSC_v048c_war_zone_1849_4K.png');bpy.ops.wm.save_as_mainfile(filepath=str(FINAL),compress=True)
(O/'native_4k_after').mkdir(exist_ok=True)
for label,f in frames:
 s.frame_set(f);s.render.filepath=str(O/'native_4k_after'/f'WTSC_v048c_{label}_{f}_4K.png');bpy.ops.render.render(write_still=True,scene=s.name);print('NATIVE_4K_AFTER',label,flush=True)
sources=[SRC,R/'shots/world/WTSC_Open_Battlefield_Refinement_v047g.blend',R/'shots/world/WTSC_Open_Battlefield_Supported_Trial_v046.blend',R/'characters/rig_correctives_v017/native/WTSC_Painted_Rig_Control_Asset_v017.blend',R/'locomotion/reference_walk_exercise_v018/native/WTSC_Boy_Travelling_Walk_v018.blend']
report={'native':str(FINAL),'native_sha256':sha(FINAL),'host':bpy.app.version_string,'world_scene':s.name,'render_dimensions':[3840,2160],'render_samples':32,'threads':2,'original_object_geometry_transforms_parents_and_titles_identical':base_ok,'original_actions_identical':act_ok,'original_frame_ranges_fps_identical':timing_ok,'original_object_count':len(original),'retained_new_objects':len(new),'rejected_first_pass_objects_removed':len(removed),'fixed_new_art_without_actions':True,'panorama_coverage_samples':len(cover),'all_panorama_samples_cover_frame':all(x['covers'] for x in cover),'persistent_structure_alpha_animation_issues':alpha_issues,'coverage':cover,'sources_sha256':{str(p):sha(p) for p in sources},'limits':['Full route silhouette/timing retained from v040, not latest character work. v047g was inspected and only its existing earth painting was reused.','Peaceful/transition/war are diagnostic open world stills; title mask unchanged in retained full-film/edit scenes.','Bank and lower path pixels are world-fixed registered paint, with spatial feathered ground joins; architecture has no alpha animation.','Original sub-4K raster paintings remain the main architecture source; authored native fine linework and local material fields supplement them.','No normal-speed film review, no full-film render, no character/FX advancement, not Arcane-level acceptance.']}
(O/'FINAL_VERIFICATION_v048c.json').write_text(json.dumps(report,indent=2));print('V048C_COMPLETE',json.dumps({k:v for k,v in report.items() if k not in ['coverage','sources_sha256','limits']}),flush=True)
