import bpy,sys,json,math,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];sys.path.insert(0,str(P/'scripts'));import walk_common as W
def digest(x):return hashlib.sha256(json.dumps(x,separators=(',',':'),sort_keys=True).encode()).hexdigest()
def manifest(rig):
 meshes={}
 for o in rig.children:
  if o.type!='MESH':continue
  meshes[o.name]={'vertex_count':len(o.data.vertices),'vertices':digest([list(v.co) for v in o.data.vertices]),'UV':digest([[list(x.uv) for x in l.data] for l in o.data.uv_layers]),'materials':[m.name if m else None for m in o.data.materials],'groups':digest([[(g.group,g.weight) for g in v.groups] for v in o.data.vertices]),'keys':digest({k.name:[list(v.co) for v in k.data] for k in o.data.shape_keys.key_blocks}) if o.data.shape_keys else None}
 return {'meshes':meshes,'bones':{b.name:{'length':b.length,'matrix':[list(x) for x in b.matrix_local]} for b in rig.data.bones},'packed_images':{i.name:hashlib.sha256(bytes(i.packed_file.data)).hexdigest() for i in bpy.data.images if i.packed_file}}
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'characters/rig_correctives_v017/native/WTSC_Painted_Rig_Control_Asset_v017.blend'),load_ui=False,use_scripts=False);W.api.initialize_from_scene();before=manifest(W.api.RIGS['BOY'])
bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Boy_Travelling_Walk_v018.blend'),load_ui=False,use_scripts=False);S=bpy.context.scene;r,c=W.api.initialize_from_scene();rig=r['BOY'];T=rig.parent;recipes=json.loads((P/'evidence/actual_sole_pivots.json').read_text());after=manifest(rig)
art={'before':before,'after':after,'base_mesh_UV_material_weights_shapes_rest_bones_identical':before==after,'scope':'Identity check does not establish attractive deformation in motion.'};(P/'evidence/art_identity.json').write_text(json.dumps(art,indent=2))
times={1+i*.03125 for i in range(1537)}
for side in ['near','far']:
 for C in range(1 if side=='near' else -11,50,24):
  for k in recipes[side]['contacts']:
   t=C+k['from_phase']
   for e in [-.001,0,.001]:
    if 1<=t+e<=49:times.add(t+e)
samples=[];bone_lengths={b.name:b.length for b in rig.data.bones};max_length_error=0;plane={};joint_xyz=[];areas={}
for f in sorted(times):
 S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();row=W.validate(f,rig,recipes);samples.append(row)
 for b in rig.pose.bones:max_length_error=max(max_length_error,abs((b.tail-b.head).length-bone_lengths[b.name]))
 joint_xyz.append({'frame':f,'near_knee':list(rig.pose.bones['shin_near'].head),'far_knee':list(rig.pose.bones['shin_far'].head),'near_elbow':list(rig.pose.bones['forearm_near'].head),'far_elbow':list(rig.pose.bones['forearm_far'].head)})
 for b in rig.pose.bones:
  for ct in b.constraints:
   if ct.type=='IK':plane.setdefault(b.name,set()).add(round(ct.pole_angle,8))
 for o in rig.children:
  if o.type!='MESH':continue
  E=o.evaluated_get(bpy.context.evaluated_depsgraph_get());V=[E.matrix_world@v.co for v in E.data.vertices];counts={'positive':0,'negative':0,'degenerate':0}
  for face in E.data.polygons:
   ids=list(face.vertices);a=sum(V[ids[i]].x*V[ids[(i+1)%len(ids)]].z-V[ids[(i+1)%len(ids)]].x*V[ids[i]].z for i in range(len(ids)))/2
   counts['degenerate' if abs(a)<1e-10 else 'positive' if a>0 else 'negative']+=1
  areas.setdefault(o.name,[]).append({'frame':f,**counts})
(P/'evidence/continuous_contact_validation.json').write_text(json.dumps(samples,indent=2));(P/'evidence/joint_path_samples.json').write_text(json.dumps(joint_xyz,indent=2));(P/'evidence/projected_face_signs.json').write_text(json.dumps(areas,indent=2))
def snap(f):
 S.frame_set(f);bpy.context.view_layer.update();return {o.name:[v-Vector((W.travel(f),0,0)) for v in W.evaluated_points(o)] for o in rig.children if o.type=='MESH'}
base=snap(1);loop=[]
for f in [25,49]:
 d=snap(f);loop.append({'frame':f,'world_displacement_m':W.travel(f),'relative_mesh_error_m':max((a-b).length for n in base for a,b in zip(base[n],d[n]))})
allfeet=[v for row in samples for v in row['feet'].values()];reach=[x for row in samples for x in row['reach']]
summary={'sample_count':len(samples),'sampling':'1/32 frame plus either side of native contact mode changes','all_reachable':all(r['reachable'] for r in reach),'max_IK_endpoint_error_m':max(r['endpoint_error_m'] for r in reach),'minimum_reach_margin_m':min(r['max_reach_m']-r['distance_m'] for r in reach),'max_fixed_contact_error_m':max(v.get('active_contact_error_m',0) for v in allfeet),'minimum_sole_height_m':min(v['minimum_sole_z_m'] for v in allfeet),'max_swing_clearance_error_m':max(v['clearance_error_m'] for v in allfeet if v['mode']=='SWING'),'max_goal_error_m':max(v['ankle_goal_error_m'] for v in allfeet),'max_bone_length_change_m':max_length_error,'IK_planes':{k:list(v) for k,v in plane.items()},'no_IK_branch_switches':all(len(v)==1 for v in plane.values()),'all_mesh_values_finite':all(r['finite_meshes'] for r in samples),'art_identity':before==after,'loop':loop,'stretch_disabled':all(not ct.use_stretch for b in rig.pose.bones for ct in b.constraints if ct.type=='IK'),'frame_handlers':len(bpy.app.handlers.frame_change_pre)+len(bpy.app.handlers.frame_change_post),'technical_status':'PASS_PENDING_THRESHOLDS','visual_status':'UNPASSED; technical results are not artistic approval'}
passed=summary['all_reachable'] and summary['max_fixed_contact_error_m']<.0001 and summary['minimum_sole_height_m']>-.0001 and summary['max_swing_clearance_error_m']<.0001 and summary['max_bone_length_change_m']<.0001 and summary['no_IK_branch_switches'] and summary['all_mesh_values_finite'] and summary['art_identity'] and summary['stretch_disabled'] and max(x['relative_mesh_error_m'] for x in loop)<.0001
summary['technical_status']='PASS' if passed else 'FAIL';(P/'evidence/validation_summary.json').write_text(json.dumps(summary,indent=2));print('V018_VALIDATION',json.dumps(summary))
if not passed:raise RuntimeError('Continuous technical gate failed; do not render/publish as passed.')
col=bpy.data.collections['V018 | WORLD_CONTACTS_AND_MARKERS'];matched=bpy.data.objects.new('V018 | v046 MATCHED SIZE | follows travel',bpy.data.cameras.new('V018 original100mm matched'));col.objects.link(matched);matched.parent=T
camera=json.loads((ROOT/'characters/rig_capability_audit_v016/evidence/actual_v046_camera.json').read_text());print('CAMERA_KEYS',list(camera))
matched.matrix_basis=Matrix(((1,0,0,1.7280044556),(0,-4.371e-8,-1,-16),(0,1,-4.371e-8,2.2799263),(0,0,0,1)));matched.data.type='PERSP';matched.data.lens=100;matched.data.sensor_width=36;matched.data.sensor_fit='HORIZONTAL';matched.data.shift_x=-.3000002205;matched.data.shift_y=-.2670553327
inspection=S.camera;W.ensure_placement();S.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Boy_Travelling_Walk_v018.blend'),compress=True)
for label,cam in [('SMOOTH',inspection),('MATCHED',matched)]:
 (P/'previews'/label).mkdir(exist_ok=True);S.camera=cam
 for f in range(1,49):
  S.frame_set(f);S.render.filepath=str(P/f'previews/{label}/{f:04d}.png');bpy.ops.render.render(write_still=True)
print('V018_VALIDATED_AND_RENDERED')
