import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
O=Path(r'WTSC_LOCAL_USER\Documents\Codex\2026-10-16\task\world_architecture_v049')
R=Path(r'WTSC_LOCAL_WORKSPACE')
SRC=R/'work/world_art_v048d/WTSC_World_Art_Checkpoint_v048d.blend'
PRE=O/'WTSC_Registered_School_Depth_v049c.blend'
OUT=O/'WTSC_Registered_School_Depth_v049d.blend'
assert not OUT.exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def actions():
 out={}
 for a in bpy.data.actions:
  rows=[]
  for l in a.layers:
   for st in l.strips:
    for bag in st.channelbags:
     for f in bag.fcurves:rows.append((f.data_path,f.array_index,[(tuple(k.co),tuple(k.handle_left),tuple(k.handle_right),k.interpolation) for k in f.keyframe_points]))
  out[a.name]=sha_bytes(repr(rows))
 return out
def sha_bytes(v):return hashlib.sha256(v.encode()).hexdigest()
def objects():
 d={}
 for o in bpy.data.objects:
  if o.name.startswith('v049 |'):continue
  q={'type':o.type,'parent':o.parent.name if o.parent else None,'matrix':[list(r) for r in o.matrix_basis],'hide_render':o.hide_render}
  if o.type=='MESH':q['geometry']=sha_bytes(repr(([tuple(v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])))
  if o.type=='FONT':q['text']=[o.data.body,o.data.font.name,o.data.size]
  d[o.name]=q
 return d
def prepare(s):
 bpy.context.window.scene=s;s.render.engine='BLENDER_EEVEE';s.render.resolution_x=3840;s.render.resolution_y=2160;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=2;s.render.use_sequencer=False;s.eevee.taa_render_samples=32;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.dither_intensity=0
def camera_samples(s):
 r=[]
 for f in [241,1201,1225,1249,1849,2400]:
  s.frame_set(f);bpy.context.view_layer.update();r.append({'frame':f,'camera':s.camera.name,'matrix':[list(x) for x in s.camera.matrix_world],'lens':s.camera.data.lens,'shift':[s.camera.data.shift_x,s.camera.data.shift_y]})
 return r
bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False,use_scripts=False);s=bpy.data.scenes['WTSC_WORLD_ART_v048d_OPEN_DIAGNOSTIC'];prepare(s);s.frame_set(1)
base=objects();acts=actions();timing=sorted((q.frame_start,q.frame_end,q.render.fps) for q in bpy.data.scenes);cameras=camera_samples(s)
(O/'native_4k_before').mkdir(exist_ok=True)
for f in [1201,1225,1249]:
 s.frame_set(f);s.render.filepath=str(O/'native_4k_before'/f'WTSC_v048d_School_{f}_4K.png');bpy.ops.render.render(write_still=True,scene=s.name);print('ARCH_BEFORE_4K',f,flush=True)
bpy.ops.wm.open_mainfile(filepath=str(PRE),load_ui=False,use_scripts=False);s=bpy.data.scenes['WTSC_REGISTERED_SCHOOL_DEPTH_v049c_OPEN_DIAGNOSTIC'];prepare(s)
# Preserve low-value source-painted variation inside the room; cap the surviving
# pane highlights to the dark room range so they do not repeat behind the glass.
room=bpy.data.materials['v049 | registered original painted stone front'].copy();room.name='v049 | recessed room | source-painted shadow variation'
nt=room.node_tree
emissions=[n for n in nt.nodes if n.type=='EMISSION' and n.inputs[0].is_linked]
assert emissions
for em in emissions:
 old=em.inputs[0].links[0].from_socket;n=nt.nodes.new('ShaderNodeVectorMath');n.operation='MINIMUM';n.inputs[1].default_value=(.018,.023,.025);nt.links.new(old,n.inputs[0]);nt.links.new(n.outputs[0],em.inputs[0])
s.objects['v049 | window deep room backing'].data.materials[0]=room
s.name='WTSC_REGISTERED_SCHOOL_DEPTH_v049d_OPEN_DIAGNOSTIC'
s['v049d_review']='Bounded physical window/ruin depth proof, traced original glass boundaries and source-painted front/room variation. Source facade remains1672x941; not a new4K painted facade. Bank sample support corrected. No color study, character or production edit.'
s.frame_set(1);after=objects();aacts=actions();assert base==after;assert acts==aacts
assert timing==sorted((q.frame_start,q.frame_end,q.render.fps) for q in bpy.data.scenes)
assert cameras==camera_samples(s)
new=[o for o in s.objects if o.name.startswith('v049 |')];assert all(not o.animation_data for o in new)
parallax=[]
P=lambda x,y,z=10:Vector((65+(x/1672-.5)*22,z,3.29222369194+(.5-y/941)*12.3815793991))
for f in [1201,1225,1249]:
 s.frame_set(f);bpy.context.view_layer.update();front=P(1400,540);back=front.copy();back.y+=.65
 # The rear card has a reference-camera reprojection; use the measured offset
 # relative to center1225 for the same original source point.
 s.frame_set(1225);bpy.context.view_layer.update();cp=s.camera.matrix_world.translation.copy();back=cp+(front-cp)*((front.y-cp.y+.65)/(front.y-cp.y))
 s.frame_set(f);bpy.context.view_layer.update();a=world_to_camera_view(s,s.camera,front);b=world_to_camera_view(s,s.camera,back);parallax.append({'frame':f,'rear_vs_front_horizontal_px_4K':(b.x-a.x)*3840,'rear_vs_front_vertical_px_4K':(b.y-a.y)*2160})
for im in bpy.data.images:
 if im.source=='FILE' and not im.packed_file:im.pack()
unpacked=[im.name for im in bpy.data.images if im.source=='FILE' and not im.packed_file];assert not unpacked
s.frame_set(1225);s.render.filepath=str(O/'native_4k_after/WTSC_v049d_School_1225_4K.png');bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
(O/'native_4k_after').mkdir(exist_ok=True)
for f in [1201,1225,1249]:
 s.frame_set(f);s.render.filepath=str(O/'native_4k_after'/f'WTSC_v049d_School_{f}_4K.png');bpy.ops.render.render(write_still=True,scene=s.name);print('ARCH_AFTER_4K',f,flush=True)
report=json.loads((O/'ARCHITECTURE_BUILD_v049c.json').read_text());report.update({'native':str(OUT),'native_sha256':sha(OUT),'host':bpy.app.version_string,'source_unchanged':sha(SRC)=='fe3270155538a44cb08ef3ee2c37f25461d292d5a9f10f4d2406e65822df3e5a','original_object_geometry_transform_parent_title_visibility_identical':base==after,'original_object_count':len(base),'original_actions_identical':acts==aacts,'original_actions_count':len(acts),'all_original_scene_ranges_fps_identical':True,'camera_samples_identical':cameras,'actual_4K_frames':[1201,1225,1249],'render_dimensions':[3840,2160],'samples':32,'new_objects_without_actions':len(new),'rear_parallax_samples':parallax,'unpacked_images':unpacked,'normal_speed_review':False,'status':'TECHNICAL DEPTH PROOF; visual review pending; high-resolution facade gate remains open','limitations':['Original facade painting remains1672x941; tracing/sharpening existing boundaries does not create missing painted surface detail.','One selected broken window and right damaged-wall/foliage separation only; not full school or ruins reconstruction.','Existing v040 children are a composition witness; no character-author assets or new color study integrated.','Six actual still renders; no full-film render or normal-speed playback review.']})
(O/'ARCHITECTURE_VERIFICATION_v049d.json').write_text(json.dumps(report,indent=2));print('ARCHITECTURE_4K_READY',sha(OUT),flush=True)
