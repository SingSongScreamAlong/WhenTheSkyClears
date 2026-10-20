import bpy,json,hashlib,struct,runpy,re
from pathlib import Path
from array import array
P=Path(__file__).resolve().parents[1];V10=P.parent/'stumble_polish_continuation_v010';stem=lambda n:re.sub(r'\.\d{3}$','',n)
def geometry_hash(root):
 h=hashlib.sha256()
 for o in sorted([o for o in root.children_recursive if o.type=='MESH'],key=lambda o:stem(o.name)):
  h.update(stem(o.name).encode());me=o.data;arr=array('f',[0.]*(len(me.vertices)*3));me.vertices.foreach_get('co',arr);h.update(arr.tobytes())
  for uv in me.uv_layers:
   for v in uv.data:h.update(struct.pack('ff',*v.uv))
  if me.shape_keys:
   for key in me.shape_keys.key_blocks:
    arr=array('f',[0.]*(len(key.data)*3));key.data.foreach_get('co',arr);h.update(key.name.encode());h.update(arr.tobytes())
 return h.hexdigest()
def snapshot(path,revision,first):
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False);s=bpy.context.scene;root=next(o for o in s.objects if o.get('motion_revision')==revision);rigs={o['character']:o for o in root.children_recursive if o.type=='ARMATURE'};rows=[]
 for local in range(1,169):
  s.frame_set(first+local-1);bpy.context.view_layer.update();row={'bones':{w:{b.name:[list(v) for v in b.matrix] for b in rig.pose.bones} for w,rig in rigs.items()},'root':[list(v) for v in root.matrix_world],'distance':next(o for o in root.children if o.get('loco_role')=='DISTANCE_CURVE').location.x,'camera':[list(v) for v in s.camera.matrix_world] if s.camera else None}
  if first==1801:
   fx=s.objects.get('FXv003 | fixed ground origin and controls');light=s.objects.get('v043 OWNED | Brief eruption light');row['fx']=[fx.get('age'),fx.get('hot_envelope'),light.data.energy]
  rows.append(row)
 return rows,geometry_hash(root)
report={};angle=runpy.run_path(str(P/'scripts/apply_correction.py'))['correction_angle']
for mode,oldpath,newpath,start in [('native',V10/'native/WTSC_Stumble_Polish_Continuation_v010.blend',P/'native/WTSC_Stumble_Polish_Continuation_v010a.blend',1),('matched',V10/'native/WTSC_v010_Matched_Review_Copy.blend',P/'native/WTSC_v010a_Matched_Review_Copy.blend',1801)]:
 old,oldgeo=snapshot(oldpath,'v010_polish_continuation',start);new,newgeo=snapshot(newpath,'v010a_lean_gap_correction',start);assert oldgeo==newgeo,'Native mesh/UV/shape drawing changed'
 errors={'other_bone_matrices':0.,'outside_correction_all_bones':0.,'root':0.,'distance':0.,'camera':0.,'fx_light':0.,'seam120_121_all_bones':0.};changed={}
 for i,(a,b) in enumerate(zip(old,new),1):
  for w,bones in a['bones'].items():
   for name,M in bones.items():
    err=max(abs(M[r][c]-b['bones'][w][name][r][c]) for r in range(4) for c in range(4));allowed=w=='BOY' and name in ['chest','head'] and angle(i)>1e-10
    if not allowed:errors['other_bone_matrices']=max(errors['other_bone_matrices'],err)
    if angle(i)<=1e-10:errors['outside_correction_all_bones']=max(errors['outside_correction_all_bones'],err)
    if i in [120,121]:errors['seam120_121_all_bones']=max(errors['seam120_121_all_bones'],err)
    if err>1e-5:changed.setdefault(str(1800+i),[]).append(w+'/'+name)
  errors['root']=max(errors['root'],max(abs(a['root'][r][c]-b['root'][r][c]) for r in range(4) for c in range(4)));errors['distance']=max(errors['distance'],abs(a['distance']-b['distance']));errors['camera']=max(errors['camera'],max(abs(a['camera'][r][c]-b['camera'][r][c]) for r in range(4) for c in range(4)))
  if mode=='matched':errors['fx_light']=max(errors['fx_light'],max(abs(x-y) for x,y in zip(a['fx'],b['fx'])))
 assert max(errors.values())<1e-5,errors
 report[mode]={'all168_max_errors':errors,'mesh_UV_shape_key_geometry_sha256':newgeo,'geometry_preserved':True,'changed_bones_and_frames':changed}
protected=json.loads((P/'evidence/protected_inputs.json').read_text());report['protected_source_files']={p:hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in protected.items()};assert all(report['protected_source_files'].values())
report['status']='Narrow correction preserved all v010 arms/girl/boots/travel/camera/FX/continuation within float roundoff; only boy chest/head local38..48 intentionally differ. No full movie rendered.'
(P/'evidence/preservation_validation.json').write_text(json.dumps(report,indent=2));print('V010a_PRESERVATION_PASSED',json.dumps(report),flush=True)
