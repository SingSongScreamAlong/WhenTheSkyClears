"""Read-only native data inspection. Never save a blend or render."""
import bpy,json,hashlib,re
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1]
CASES={
 'boy_v041':ROOT/'locomotion/neck_collar_connection_v041/native/WTSC_Neck_Collar_Connection_Candidate_v041.blend',
 'pair_v007':ROOT/'locomotion/supported_recovery_v007/native/WTSC_Supported_Recovery_v007.blend',
 'world_v046':ROOT/'shots/world/WTSC_Open_Battlefield_Supported_Trial_v046.blend',
 'world_v058':ROOT/'work/world_minimum_v058/WTSC_World_Development_v058_Packed.blend'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bbox(V):return [[min(v[i] for v in V),max(v[i] for v in V)] for i in range(3)]
def props(o):
 out={}
 for k in o.keys():
  if k=='_RNA_UI':continue
  v=o[k]
  if isinstance(v,(str,float,int,bool)):out[k]=v
 return out
def parentchain(o):
 a=[]
 while o:a.append({'name':o.name,'location':list(o.location),'scale':list(o.scale),'world_translation':list(o.matrix_world.translation),'world_scale':list(o.matrix_world.to_scale())});o=o.parent
 return a
def obrecord(o):
 r={'name':o.name,'type':o.type,'hide_render':o.hide_render,'parent':o.parent.name if o.parent else None,'location':list(o.location),'scale':list(o.scale),'world_scale':list(o.matrix_world.to_scale()),'world_translation':list(o.matrix_world.translation),'dimensions':list(o.dimensions),'properties':props(o),'collections':[c.name for c in o.users_collection]}
 if o.type in ['MESH','GREASEPENCIL','CURVE','FONT']:
  r['world_bbox_geometry_canvas_not_painted_occupancy']=bbox([o.matrix_world@Vector(v) for v in o.bound_box])
 if o.type=='MESH':r['vertices']=len(o.data.vertices);r['materials']=[s.material.name if s.material else None for s in o.material_slots]
 return r
out={'blender':bpy.app.version_string,'build_hash':bpy.app.build_hash.decode(),'read_only':True,'no_native_save':True,'cases':{}}
for label,path in CASES.items():
 before=sha(path);bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 if label=='world_v046':bpy.context.window.scene=bpy.data.scenes['WTSC_OPEN_SUPPORTED_RECOVERY_TRIAL_v046']
 S=bpy.context.scene
 r={'source':str(path),'sha256_before':before,'active_scene':S.name,'all_scenes':[s.name for s in bpy.data.scenes],'saved_frame':S.frame_current,'fps':S.render.fps,'unit_system':S.unit_settings.system,'scale_length':S.unit_settings.scale_length,'scene_properties':props(S),'rigs':[],'frames':{},'architecture_objects':[],'ground_objects':[],'object_inventory':[{'name':o.name,'type':o.type,'hide_render':o.hide_render,'dimensions':list(o.dimensions),'location':list(o.matrix_world.translation),'properties':{k:v for k,v in props(o).items() if len(str(v))<500}} for o in S.objects]}
 for o in S.objects:
  if o.type=='ARMATURE' and any(x in o.name for x in ['LOCO_BOY','LOCO_GIRL']):
   q=obrecord(o);q['parent_chain']=parentchain(o);q['rest_bones']={b.name:{'length':b.length,'head':list(b.head_local),'tail':list(b.tail_local)} for b in o.data.bones};r['rigs'].append(q)
  if o.type in ['MESH','GREASEPENCIL','EMPTY'] and re.search('door|facade|bakery|school|house|building',o.name,re.I):r['architecture_objects'].append(obrecord(o))
  if o.type=='MESH' and re.search('ground|road|path|floor|contact|sole',o.name,re.I):r['ground_objects'].append(obrecord(o))
 frames=[1,20] if label=='boy_v041' else [1,120] if label=='pair_v007' else [1801,1844,1920] if label=='world_v046' else [241,1201,1537,1844,2161]
 for f in frames:
  S.frame_set(f);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();cam=S.camera;fr={'camera':obrecord(cam) if cam else None,'rigs':[],'ground_raycast_Y0':[]}
  if cam:fr['camera'].update({'lens':cam.data.lens,'type':cam.data.type,'ortho_scale':cam.data.ortho_scale,'sensor_width':cam.data.sensor_width,'sensor_fit':cam.data.sensor_fit,'shift':[cam.data.shift_x,cam.data.shift_y]})
  for o in S.objects:
   if o.type=='ARMATURE' and any(x in o.name for x in ['LOCO_BOY','LOCO_GIRL']):
    e=o.evaluated_get(dg);fr['rigs'].append({'name':o.name,'hide_render':o.hide_render,'world_translation':list(e.matrix_world.translation),'world_scale':list(e.matrix_world.to_scale()),'pose_bones_world':{b.name:{'head':list(e.matrix_world@b.head),'tail':list(e.matrix_world@b.tail),'scale':list(b.scale),'length_world':(e.matrix_world@(b.tail-b.head)).length if False else ((e.matrix_world@b.tail)-(e.matrix_world@b.head)).length} for b in e.pose.bones if re.search('pelvis|chest|head|upper_arm|forearm|hand|thigh|shin|foot',b.name)}})
  # Test only named ground meshes, not foreground paintings/architecture. These
  # rays establish geometry height, not the visually painted contact line.
  xs=set(round(x['world_translation'][0],4) for x in fr['rigs'])
  if label=='world_v058' and cam:xs.add(round(cam.matrix_world.translation.x-1.7,4))
  for x in sorted(xs):
   hits=[]
   for o in S.objects:
    if o.type!='MESH' or o.hide_render or not re.search('ground top|walking path|road|ground.*physical|contact ground|ground strip',o.name,re.I):continue
    e=o.evaluated_get(dg);inv=e.matrix_world.inverted();start=inv@Vector((x,0,20));direction=(inv.to_3x3()@Vector((0,0,-1))).normalized()
    try:hit,co,no,index=e.ray_cast(start,direction,distance=1000)
    except (RuntimeError,ValueError):continue
    if hit:hits.append({'object':o.name,'world_hit':list(e.matrix_world@co),'face':index})
   fr['ground_raycast_Y0'].append({'x':x,'hits':hits})
  r['frames'][str(f)]=fr
 r['sha256_after']=sha(path);assert r['sha256_after']==before;r['source_unchanged']=True;out['cases'][label]=r;print('READ_ONLY_METADATA_COMPLETE',label,'RIGS',len(r['rigs']),'ARCH',len(r['architecture_objects']),'GROUND',len(r['ground_objects']),flush=True)
(P/'evidence/BOTH_CHARACTERS_AND_WORLD_NATIVE.json').write_text(json.dumps(out,indent=2));print('AUDIT_ALL_COMPLETE_NO_SAVES_NO_RENDERS',flush=True)
