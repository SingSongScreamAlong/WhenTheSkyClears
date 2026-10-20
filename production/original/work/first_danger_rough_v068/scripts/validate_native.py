import bpy,json,hashlib,math,sys
from pathlib import Path
O=Path(__file__).resolve().parents[1];R=O.parents[1];B=json.loads((O/'evidence/BUILD.json').read_text());P=Path(B['native']);H=hashlib.sha256(P.read_bytes()).hexdigest();assert H==B['native_sha256']
# Independent cold reopen, original and candidate cameras sampled at all frames.
bpy.ops.wm.open_mainfile(filepath=B['source'],load_ui=False,use_scripts=False)
S=bpy.data.scenes['WTSC_FIRST_DANGER_ACTING_WORLD_v067'];bpy.context.window.scene=S
cams={}
for g in range(913,1081):
 S.frame_set(g);bpy.context.view_layer.update();cams[g]=[float(v) for row in S.camera.matrix_world for v in row]
bpy.ops.wm.open_mainfile(filepath=str(P),load_ui=False,use_scripts=False)
S=bpy.data.scenes[B['world_scene']];bpy.context.window.scene=S
names=set(B['new_drawing_objects']);old=set(B['hidden_original_objects']);rows=[];maxcamera=0
for g in range(913,1081):
 S.frame_set(g);bpy.context.view_layer.update();visible=[ob for ob in S.objects if ob.name in names and not ob.hide_render]
 assert len(visible)==2 and set(o['character'] for o in visible)=={'BOY','GIRL'}
 assert all(o.hide_render for o in S.objects if o.name in old)
 assert all(o['drawing_frame']==913+((g-913)//2)*2 for o in visible)
 actual=[float(v) for row in S.camera.matrix_world for v in row];maxcamera=max(maxcamera,max(abs(a-b) for a,b in zip(actual,cams[g])))
 rows.append({'frame':g,'visible_drawings':[o.name for o in visible]})
assert maxcamera<1e-7
art={im.name:hashlib.sha256(im.packed_file.data).hexdigest() for im in bpy.data.images if im.packed_file};assert art==B['artwork_hashes']
assert S.render.resolution_x==3840 and S.render.resolution_y==2160 and S.render.fps==24
assert hashlib.sha256(Path(B['source']).read_bytes()).hexdigest()==B['source_sha256']
assert len(list((O/'drawings').glob('*.svg')))==168
positions={};drift=[];clearance=[]
for row in B['rows']:
 for w,p in row['children'].items():
  ob=bpy.data.objects[f'V068 {w} | drawing G{row["frame"]:04d} | flat contour layers']
  for side,fm in p['feet'].items():
   if not fm['contact']:continue
   group=ob.vertex_groups['boots | '+side];vs=[v for v in ob.data.vertices if any(a.group==group.index for a in v.groups)]
   z=min(v.co.z for v in vs);clearance.append(z)
   key=(w,side,fm['plant']);x=(min(v.co.x for v in vs)+max(v.co.x for v in vs))/2
   if key in positions:drift.append(abs(x-positions[key]))
   positions[key]=x
assert max(drift,default=0)<2e-6
assert max(abs(x) for x in clearance)<.003
sys.path.insert(0,str(O/'scripts'));import pose_spec as M
jump={};previous=None;grip=[]
for g in range(913,1081,2):
 pp=M.paired(g)
 if previous:
  for w,p in pp.items():
   for n in ['hip','head','elbow_near','elbow_far','wrist_near','wrist_far']:
    delta=M.length(M.sub(p[n],previous[w][n]));key=w+' '+n;jump[key]=max(delta,jump.get(key,0))
 if g>=995:
  a=M.add(pp['BOY']['wrist_near'],(-.4,0));b=M.add(pp['GIRL']['wrist_near'],(.4,0));grip.append(M.length(M.sub(a,b)))
 previous=pp
assert all(.065<x<.16 for x in grip)
assert max(grip)-min(grip)<1e-5,'Coupled grip opened'
assert min(row['children'][w]['hip'][1] for row in B['rows'] if row['frame']>=1003 for w in ['BOY','GIRL'])>.64,'Outgoing trailing leg collapsed the pelvis'
report={'passed':True,'native':str(P),'native_sha256':H,'source_unchanged':True,'packed_source_paintings_unchanged':True,'source_camera_max_matrix_difference':maxcamera,'production_frames_checked':168,'new_drawing_count':len(names),'drawings_per_child':84,'exposure':'on twos at24fps','source_vector_count':168,'visible_original_characters':0,'native_resolution':[3840,2160],'stance_drawing_sole_max_drift_m':max(drift,default=0),'stance_drawing_floor_extent_m':[min(clearance),max(clearance)],'paired_wrist_gap_after_grip_m':[min(grip),max(grip)],'joint_max_change_per_two_frames_m':jump,'frames':rows,'artistic_acceptance':False,'limitation':'Mechanical/continuity checks only. New rough drawings and likeness require visual review; no final painted finish or Arcane-quality claim.'}
(O/'evidence/COLD_VALIDATION.json').write_text(json.dumps(report,indent=2));print('V068_COLD_CHECKS_PASSED',flush=True)
