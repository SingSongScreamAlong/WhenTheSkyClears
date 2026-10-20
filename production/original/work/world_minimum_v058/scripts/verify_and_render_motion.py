import bpy,json,hashlib
from pathlib import Path
O=Path(__file__).parent
SOURCE=Path(r'WTSC_LOCAL_WORKSPACE\work\world_facade_v057\WTSC_Continuous_Painterly_Facade_Proof_v057.blend')
FINAL=O/'WTSC_World_Foreground_Development_v058d.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def action_dna():
 d={}
 for a in bpy.data.actions:
  rows=[]
  for l in a.layers:
   for st in l.strips:
    for bag in st.channelbags:
     for f in bag.fcurves:rows.append((f.data_path,f.array_index,[(tuple(k.co),tuple(k.handle_left),tuple(k.handle_right),k.interpolation) for k in f.keyframe_points]))
  d[a.name]=hashlib.sha256(repr(rows).encode()).hexdigest()
 return d
def snapshot(scene_name):
 s=bpy.data.scenes[scene_name];bpy.context.window.scene=s;s.frame_set(1537);bpy.context.view_layer.update()
 objs={}
 for ob in s.objects:
  row={'type':ob.type,'parent':ob.parent.name if ob.parent else None,'matrix_local':[list(x) for x in ob.matrix_local]}
  if ob.type=='MESH':row['geometry']=hashlib.sha256(repr(([tuple(v.co) for v in ob.data.vertices],[tuple(p.vertices) for p in ob.data.polygons],{u.name:[tuple(v.uv) for v in u.data] for u in ob.data.uv_layers})).encode()).hexdigest()
  objs[ob.name]=row
 cameras={}
 for f in [1,241,601,961,1201,1537,1849,2161,2377,2400]:
  s.frame_set(f);bpy.context.view_layer.update();cameras[str(f)]=[list(v) for v in s.camera.matrix_world]
 return {'objects':objs,'actions':action_dna(),'cameras':cameras,'timing':[s.frame_start,s.frame_end,s.render.fps,s.render.resolution_x,s.render.resolution_y],'images':{im.name:list(im.size) for im in bpy.data.images if im.type!='RENDER_RESULT'}}
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False);old=snapshot('WTSC_CONTINUOUS_FACADE_SOURCE_LIGHTING_v057_TEST')
bpy.ops.wm.open_mainfile(filepath=str(FINAL),load_ui=False,use_scripts=False);new=snapshot('WTSC_WORLD_FOREGROUND_v058d')
checks={'object_names_identical':old['objects'].keys()==new['objects'].keys(),'geometry_uv_local_transforms_parenting_identical':old['objects']==new['objects'],'actions_identical':old['actions']==new['actions'],'camera_samples_identical':old['cameras']==new['cameras'],'world_timing_resolution_identical':old['timing']==new['timing'],'image_dimensions_identical':old['images']==new['images'],'file_images_packed':all(im.packed_file for im in bpy.data.images if im.source=='FILE' and im.type!='RENDER_RESULT'),'source_hash_preserved':sha(SOURCE)=='87c897b5ccc178b1288f5d614eeaa34d642b8e8ac2c239bcd2ab50a79569361a'}
(O/'COLD_REOPEN_VERIFICATION_v058d.json').write_text(json.dumps({'checks':checks,'original_objects':len(old['objects']),'original_actions':len(old['actions']),'source_sha256':sha(SOURCE),'final_sha256':sha(FINAL),'source_timing':old['timing'],'changed_scope':'Path lower RGB material and disabled 105 old needle-grass visibility only; no mesh/UV/action/camera/character changes'},indent=2))
assert all(checks.values()),checks
intervals=[('village',241),('camp',1537),('ruins',2161)]
for variant,pth,sn in [('before',SOURCE,'WTSC_CONTINUOUS_FACADE_SOURCE_LIGHTING_v057_TEST'),('after',FINAL,'WTSC_WORLD_FOREGROUND_v058d')]:
 bpy.ops.wm.open_mainfile(filepath=str(pth),load_ui=False,use_scripts=False);s=bpy.data.scenes[sn];bpy.context.window.scene=s
 s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=2;s.render.use_sequencer=False;s.render.dither_intensity=0;s.eevee.taa_render_samples=32;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG'
 for label,start in intervals:
  folder=O/'motion'/variant/label;folder.mkdir(parents=True,exist_ok=True)
  for f in range(start,start+48):
   s.frame_set(f);s.render.filepath=str(folder/f'{f:04d}.png');bpy.ops.render.render(write_still=True,scene=s.name)
  print('MOTION_SEGMENT',variant,label,flush=True)
 if variant=='after':
  s.render.resolution_x=3840;s.render.resolution_y=2160
  folder=O/'native_4k';folder.mkdir(exist_ok=True)
  for f in [241,1537,2161]:
   s.frame_set(f);s.render.filepath=str(folder/f'AFTER_{f:04d}_4K.png');bpy.ops.render.render(write_still=True,scene=s.name);print('NATIVE_4K',f,flush=True)
(O/'MOTION_RENDER_RECORD.json').write_text(json.dumps({'intervals':intervals,'frames_each':48,'fps':24,'before_and_after':True,'total_native_small_frames':288,'resolution':[1280,720],'three_4k_after_frames':[241,1537,2161],'final_sha_unchanged':sha(FINAL)==json.loads((O/'COLD_REOPEN_VERIFICATION_v058d.json').read_text())['final_sha256'],'source_sha_unchanged':sha(SOURCE)=='87c897b5ccc178b1288f5d614eeaa34d642b8e8ac2c239bcd2ab50a79569361a'},indent=2))
print('MOTION_AND_4K_READY',flush=True)
