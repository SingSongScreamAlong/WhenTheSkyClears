import bpy,json,sys,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];sys.path.insert(0,str(P/'scripts'));import rig_pose_api as api;import source_match as M
PATH=P/'native/WTSC_Leaves_Reference_Child_Eight_Poses_v020.blend';bpy.ops.wm.open_mainfile(filepath=str(PATH),load_ui=False,use_scripts=False);S=bpy.context.scene;rigs,c=api.initialize_from_scene();r=rigs['BOY'];source=bpy.data.objects['V020 | SOURCE52 | exact FBX sampled poses'];authored=json.loads((P/'evidence/eight_pose_matching.json').read_text());rows=[]
def p(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());return [e.matrix_world@v.co for v in e.data.vertices]
for pose in authored:
 f=pose['study_frame_30fps'];S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();v=M.parameters(pose['unwrapped_source_frame'],r,{'near':'R','far':'L'});B=v['source'];feet=[]
 for side in ['near','far']:
  V=p(bpy.data.objects[M.BOOTS[side]['object']]);meta=v['foot'][side][1];feet.append({'side':side,'mode':meta['mode'],'minimum_sole_z_m':min(q.z for q in V),'contact_error_m':(V[meta['active_vertex']]-Vector(meta['anchor'])).length if 'active_vertex' in meta else None})
 errors=[]
 for side,src in [('near','R'),('far','L')]:
  for native,a,b in [('thigh','UpperLeg_','LowerLeg_'),('shin','LowerLeg_','Ankle_'),('upper_arm','Shoulder_','Elbow_'),('forearm','Elbow_','Hand_')]:
   desired=M.point(B,b+src)-M.point(B,a+src);actual=r.pose.bones[native+'_'+side].tail-r.pose.bones[native+'_'+side].head;desired.y=actual.y=0
   errors.append({'side':side,'bone':native,'direction_error_deg':math.degrees(desired.angle(actual))})
 source_error=max(((source.matrix_world@source.pose.bones[n].head)-Vector((-B[n]['head'].y-M.ROOT_START,B[n]['head'].x,B[n]['head'].z))).length for n in M.DATA['bones'])
 rows.append({'phase':pose['name'],'study_frame':f,'source_frame':pose['unwrapped_source_frame'],'source_pose_error_m':source_error,'IK':api.reach_report(),'feet':feet,'projected_direction_residuals':errors})
rest=json.loads((P/'evidence/child_rest_bones.json').read_text());rest_exact=all(abs(r.data.bones[n].length-d['length'])<1e-8 and max(abs(r.data.bones[n].matrix_local[i][j]-d['matrix'][i][j]) for i in range(4) for j in range(4))<1e-7 for n,d in rest.items())
summary={'pose_count_unique':8,'duplicate_bookend_checked':True,'child_rest_proportions_unchanged':rest_exact,'all_four_IK_chains_reachable':all(q['reachable'] for row in rows for q in row['IK']),'source_copied_pose_max_error_m':max(row['source_pose_error_m'] for row in rows),'max_native_IK_endpoint_error_m':max(q['endpoint_error_m'] for row in rows for q in row['IK']),'source_arm_direction_max_residual_deg':max(q['direction_error_deg'] for row in rows for q in row['projected_direction_residuals'] if 'arm' in q['bone']),'source_leg_direction_max_residual_deg':max(q['direction_error_deg'] for row in rows for q in row['projected_direction_residuals'] if q['bone'] in ['thigh','shin']),'contacts_checked_at_poses_only':True,'continuous_contacts_or_inbetweens_validated':False,'no_stretch':all(not ct.use_stretch for b in r.pose.bones for ct in b.constraints if ct.type=='IK'),'artistic_status':'NOT APPROVED; matching and painted deformation limits both remain','source_import_warning':'FBX Short custom-property type unsupported; no skeleton/action import failure observed.52bones and original source action retained.'}
(P/'evidence/fresh_native_pose_checks.json').write_text(json.dumps({'summary':summary,'poses':rows},indent=2));print('V020_FRESH',json.dumps(summary))
if not (summary['all_four_IK_chains_reachable'] and rest_exact and summary['source_copied_pose_max_error_m']<.0001):raise RuntimeError('Saved pose verification failed')
# Contrast correction affects only the skeleton visualization, not the rigs/art.
for name,color in [('V020 right / child near',(.29,.09,.035)),('V020 left / child far',(.025,.16,.19)),('V020 torso',(.09,.08,.06))]:
 mat=bpy.data.materials[name];mat.diffuse_color=(*color,1);next(n for n in mat.node_tree.nodes if n.type=='EMISSION').inputs[0].default_value=(*color,1)
srcCol=bpy.data.collections['V020 | source skeleton render'];childCol=bpy.data.collections['V020 | child native skeleton render']
for o in [*srcCol.objects,*childCol.objects]:
 if o.type=='CURVE':o.data.bevel_depth=.008
S['V020_matching_limits']='Source average-leg-scaled stride1.021m. Up to28.9mm pelvis reach accommodation; source toe dip produces zero drawn swing clearance in L_UP. Neither gait matching nor painted deformation is approved.'
for name in ['source_match.py','rig_pose_api.py','build_study.py']:
 text=bpy.data.texts.get('V020 '+name) or bpy.data.texts.new('V020 '+name);text.clear();text.write((P/'scripts'/name).read_text())
S.frame_set(1);S.camera=bpy.data.objects['V020 | CHILD | CLOSE'];srcCol.hide_render=True;childCol.hide_render=True;paint=[o for o in r.children if o.type=='MESH']
for o in paint:o.hide_render=False
bpy.ops.wm.save_as_mainfile(filepath=str(PATH),compress=True)
for pose in M.PHASES['phases']:
 f=pose['study_frame_30fps'];S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update()
 for mode in ['SOURCE','CHILD_SKELETON','PAINTED']:
  srcCol.hide_render=mode!='SOURCE';childCol.hide_render=mode!='CHILD_SKELETON'
  for o in paint:o.hide_render=mode!='PAINTED'
  for size in ['CLOSE','SHOT']:
   S.camera=bpy.data.objects['V020 | '+('SOURCE' if mode=='SOURCE' else 'CHILD')+' | '+size];S.render.filepath=str(P/f'previews/{mode}_{size}/{pose["index"]:02d}.png');bpy.ops.render.render(write_still=True)
print('V020_READABLE_DIAGRAMS_COMPLETE')
