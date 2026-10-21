import bpy,json,hashlib,numpy as np,math
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1]
old=ROOT/'locomotion/coat_fluidity_v051/native/WTSC_Controlled_Fluid_Coat_v051.blend';new=P/'native/WTSC_Support_Linked_Upper_Body_v052.blend'
hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (old,new)}

def fc(a):
 return {(f.data_path,f.array_index):hashlib.sha256(repr(([(tuple(k.co),k.interpolation) for k in f.keyframe_points],[(m.type,m.mode_before,m.mode_after) for m in f.modifiers if m.type=='CYCLES'])).encode()).hexdigest() for l in a.layers for st in l.strips for b in st.channelbags for f in b.fcurves}
def ah(a):return hashlib.sha256(repr(fc(a)).encode()).hexdigest()
def snapshot():
 r={w:bpy.data.objects['V044 '+w+' | estimated joint centres'] for w in ('BOY','GIRL')};C=bpy.data.collections['V046 | restored original painted wardrobe']
 parts={o.name:o for o in bpy.context.scene.objects if o.type=='MESH' and o.parent in r.values()}
 return {'rig_action_names':{w:x.animation_data.action.name for w,x in r.items()},'actions':{a.name:ah(a) for a in bpy.data.actions},'rig_fcurves':{w:fc(x.animation_data.action) for w,x in r.items()},'root_fcurves':fc(bpy.data.objects['V048 | shared travel | steady .73125mps'].animation_data.action),'camera_fcurves':fc(bpy.context.scene.camera.animation_data.action),'bones':{w:{b.name:(tuple(b.head_local),tuple(b.tail_local),b.parent.name if b.parent else None) for b in x.data.bones} for w,x in r.items()},'geometry':{n:hashlib.sha256(repr([tuple(v.co) for v in o.data.vertices]).encode()).hexdigest() for n,o in parts.items() if o.get('wardrobe_role')!='sleeve'},'uv_mat_weight':{n:hashlib.sha256(repr({'uv':{u.name:[tuple(x.uv) for x in u.data] for u in o.data.uv_layers},'mat':[m.name for m in o.data.materials],'weights':[(v.index,[(g.group,g.weight) for g in v.groups]) for v in o.data.vertices]}).encode()).hexdigest() for n,o in parts.items()},'packed_images':{i.name:hashlib.sha256(i.packed_file.data).hexdigest() for i in bpy.data.images if i.packed_file},'coat_keys':{o.name:[(k.name,hashlib.sha256(repr([tuple(p.co) for p in k.data]).encode()).hexdigest()) for k in o.data.shape_keys.key_blocks] for o in C.objects if o.get('wardrobe_role')=='body' and o.data.shape_keys}}
def measure():
 dg=bpy.context.evaluated_depsgraph_get();r=[bpy.data.objects['V044 '+w+' | estimated joint centres'] for w in ('BOY','GIRL')]
 boots=[o for o in bpy.context.scene.objects if o.parent in r and o.get('proportion_role')=='boot']
 points=np.array([list(e.matrix_world@v.co) for o in boots for e in [o.evaluated_get(dg)] for v in e.data.vertices])
 others={}
 for who,rig in zip(('BOY','GIRL'),r):
  pose=rig.evaluated_get(dg).pose.bones
  def angle(b):
   v=b.tail-b.head;return math.degrees(math.atan2(v.x,-v.z))
  others[who]={'pelvis_head':list(pose['pelvis'].head),'pelvis_tail':list(pose['pelvis'].tail),'chest_degrees':math.degrees(math.atan2((pose['chest'].tail-pose['chest'].head).x,(pose['chest'].tail-pose['chest'].head).z)),'near_elbow_flex_degrees':angle(pose['forearm_near'])-angle(pose['upper_arm_near']),'far_elbow_flex_degrees':angle(pose['forearm_far'])-angle(pose['upper_arm_far'])}
 return points,others

reference=[];changes={w:{'chest':[],'near_elbow':[],'far_elbow':[]} for w in ('BOY','GIRL')};newseries={w:{'near':[],'far':[]} for w in ('BOY','GIRL')};bootmax=0.;pelvismax=0.
for tag,path,scene in [('old',old,'V051 | BOY COAT FLUIDITY | exact v050 gait'),('new',new,'V052 | SUPPORT LINKED UPPER BODY | v051 contacts')]:
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);S=bpy.data.scenes[scene];bpy.context.window.scene=S;snap=snapshot()
 if tag=='old':before=snap
 else:
  assert snap['root_fcurves']==before['root_fcurves'] and snap['camera_fcurves']==before['camera_fcurves']
  assert snap['bones']==before['bones'] and snap['geometry']==before['geometry'] and snap['uv_mat_weight']==before['uv_mat_weight'] and snap['packed_images']==before['packed_images'] and snap['coat_keys']==before['coat_keys']
  for name,h in before['actions'].items():
   if name in before['rig_action_names'].values():continue
   assert snap['actions'][name]==h,name
  for w in ('BOY','GIRL'):
   a=before['rig_fcurves'][w];b=snap['rig_fcurves'][w]
   assert a.keys()==b.keys()
   for k,h in a.items():
    if any(x in k[0] for x in ('pose.bones["pelvis"]','pose.bones["thigh_','pose.bones["shin_','pose.bones["foot_')):assert b[k]==h,(w,k)
 for i in range(129):
  f=1+i/4;S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();boot,other=measure()
  if tag=='old':reference.append((boot,other))
  else:
   bootmax=max(bootmax,float(np.max(np.linalg.norm(boot-reference[i][0],axis=1))))
   for w in ('BOY','GIRL'):
    b=reference[i][1][w];a=other[w];pelvismax=max(pelvismax,float(np.linalg.norm(np.array(a['pelvis_head'])-b['pelvis_head'])),float(np.linalg.norm(np.array(a['pelvis_tail'])-b['pelvis_tail'])))
    for key,label in [('chest_degrees','chest'),('near_elbow_flex_degrees','near_elbow'),('far_elbow_flex_degrees','far_elbow')]:changes[w][label].append(a[key]-b[key])
    newseries[w]['near'].append(a['near_elbow_flex_degrees']);newseries[w]['far'].append(a['far_elbow_flex_degrees'])
assert bootmax<1e-7 and pelvismax<1e-7,(bootmax,pelvismax)
assert any(max(abs(x) for x in changes[w]['chest'])>.2 for w in changes)
assert all(max(abs(x) for x in changes[w]['chest'])<2 for w in changes),changes
assert all(hashlib.sha256(Path(path).read_bytes()).hexdigest()==h for path,h in hashes.items())
correlations={}
for w in ('BOY','GIRL'):
 a=[r[1][w]['near_elbow_flex_degrees'] for r in reference[:128]];b=[r[1][w]['far_elbow_flex_degrees'] for r in reference[:128]]
 correlations[w]={'old_near_far_elbow':float(np.corrcoef(a,b)[0,1]),'new_near_far_elbow':float(np.corrcoef(newseries[w]['near'][:128],newseries[w]['far'][:128])[0,1])}
report={'source_hashes':hashes,'cold_reopen_passed':True,'root_camera_leg_pelvis_fcurves_exact':True,'rest_bones_non_sleeve_geometry_coat_keys_uv_weights_materials_packed_images_exact':True,'sampled_quarter_frames':129,'maximum_boot_vertex_difference_m':bootmax,'maximum_pelvis_endpoint_difference_m':pelvismax,'difference_ranges_degrees':{w:{k:[min(v),max(v)] for k,v in values.items()} for w,values in changes.items()},'elbow_timing_correlations':correlations,'technical_vs_art':'No new contact error. This does not establish natural acting.'}
(P/'evidence/COLD_CHECK.json').write_text(json.dumps(report,indent=2));print('V052_COLD_CONTACT_AND_SOURCE_CHECK_PASS',bootmax,pelvismax,report['difference_ranges_degrees'])
