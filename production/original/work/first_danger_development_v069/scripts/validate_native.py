import bpy,json,hashlib,sys
from pathlib import Path
O=Path(__file__).resolve().parents[1];B=json.loads((O/'evidence/BUILD.json').read_text());P=Path(B['native']);H=hashlib.sha256(P.read_bytes()).hexdigest();assert H==B['native_sha256']
bpy.ops.wm.open_mainfile(filepath=B['source'],load_ui=False,use_scripts=False);S=bpy.data.scenes['WTSC_FIRST_DANGER_ROUGH_WORLD_v068'];bpy.context.window.scene=S;cams={}
for g in range(913,1081):S.frame_set(g);bpy.context.view_layer.update();cams[g]=[float(x) for r in S.camera.matrix_world for x in r]
bpy.ops.wm.open_mainfile(filepath=str(P),load_ui=False,use_scripts=False);S=bpy.data.scenes[B['world_scene']];bpy.context.window.scene=S
names=set(B['body_objects']);heads=set(B['head_objects']);rows=[];maxcam=0
rigs=[bpy.data.objects['V044 '+w+' | estimated joint centres'] for w in ['BOY','GIRL']]
for g in range(913,1081):
 S.frame_set(g);bpy.context.view_layer.update();body=[o for o in S.objects if o.name in names and not o.hide_render];hs=[o for o in S.objects if o.name in heads and not o.hide_render]
 assert len(body)==2 and len(hs)==2 and all(o['drawing_frame']==g for o in body+hs)
 assert {o['character'] for o in body}=={'BOY','GIRL'} and {o['character'] for o in hs}=={'BOY','GIRL'}
 assert all(o.hide_render for o in S.objects if o.parent in rigs)
 assert not any(not o.hide_render and o.name.startswith('V068 ') for o in S.objects)
 actual=[float(x) for r in S.camera.matrix_world for x in r];maxcam=max(maxcam,max(abs(a-b) for a,b in zip(actual,cams[g])))
 rows.append({'frame':g,'body':[o.name for o in body],'heads':[{'name':o.name,'column':o['atlas_column']} for o in hs]})
assert maxcam<1e-7
assert all(hashlib.sha256(bpy.data.images[n].packed_file.data).hexdigest()==h for n,h in B['original_painting_hashes'].items())
atlas=bpy.data.images['V069 | generated painted head-angle atlas | RGBA'];assert atlas.packed_file and hashlib.sha256(atlas.packed_file.data).hexdigest()==B['atlas_sha256']
assert hashlib.sha256(Path(B['source']).read_bytes()).hexdigest()==B['source_sha256']
assert (S.render.resolution_x,S.render.resolution_y,S.render.fps)==(3840,2160,24)
assert len(list((O/'drawings').glob('*.svg')))==336
positions={};drift=[];floor=[];grip=[]
for row in B['rows']:
 g=row['frame'];ps=row['children']
 for w,p in ps.items():
  ob=bpy.data.objects[f'V069 {w} | body drawing G{g:04d}']
  for side,fm in p['feet'].items():
   if not fm['contact']:continue
   group=ob.vertex_groups['boots | '+side];vs=[v for v in ob.data.vertices if any(a.group==group.index for a in v.groups)];x=(min(v.co.x for v in vs)+max(v.co.x for v in vs))/2;floor.append(min(v.co.z for v in vs));key=(w,side,fm['plant'])
   if key in positions:drift.append(abs(x-positions[key]))
   positions[key]=x
 if g>=995:
  a=ps['BOY'];b=ps['GIRL'];dx=a['wrist_near'][0]+a['offset']-b['wrist_near'][0]-b['offset'];dz=a['wrist_near'][1]-b['wrist_near'][1];grip.append((dx*dx+dz*dz)**.5)
assert max(drift,default=0)<2e-6 and max(abs(v) for v in floor)<.003
assert max(grip)-min(grip)<1e-5 and .08<min(grip)<.11
report={'passed':True,'native':str(P),'native_sha256':H,'source_unchanged':True,'original_packed_paintings_unchanged':True,'new_head_atlas_packed_and_identical_to_workspace_copy':True,'camera_max_difference':maxcam,'production_frames_checked':168,'body_drawings_per_child':168,'exposure':'One native drawing per production frame at24fps','source_svg_exports':336,'visible_old_rough_drawings':0,'max_stance_drawing_sole_drift_m':max(drift,default=0),'stance_floor_extent_m':[min(floor),max(floor)],'coupled_wrist_gap_m':[min(grip),max(grip)],'native_resolution':[3840,2160],'head_angles':'New built-in-imagegen reference-led studies; actual alpha retained; no ghost-face crossfading.','frames':rows,'artistic_acceptance':False,'scope':'Isolated seven seconds only. Not full-trailer integration or final craft approval.'}
(O/'evidence/COLD_VALIDATION.json').write_text(json.dumps(report,indent=2));print('V069_COLD_VALIDATION_PASSED',flush=True)
