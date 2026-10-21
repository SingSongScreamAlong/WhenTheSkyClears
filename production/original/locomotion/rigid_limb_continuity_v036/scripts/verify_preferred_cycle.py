import bpy,json,hashlib,math,time
from pathlib import Path
P=Path(__file__).resolve().parents[1];cache={};samples=[1+i/8 for i in range(745)];protected=['PERF_BOY | original head'];report={'scope':'Whole active action-channel comparison plus dense numerical checks across three cycles; not an artistic rating','sample_interval_frames':.125,'samples':len(samples),'source_frames':[1,94],'fps':30,'preferred_source_sha256':hashlib.sha256((P/'reference/PREFERRED_v033.blend').read_bytes()).hexdigest()}
def curves(a):
 if a:
  for l in a.layers:
   for st in l.strips:
    for bag in st.channelbags:yield from bag.fcurves
def fcdata(fc):return (fc.extrapolation,[(tuple(k.co),k.interpolation,tuple(k.handle_left),tuple(k.handle_right)) for k in fc.keyframe_points],[(m.type,getattr(m,'mode_before',None),getattr(m,'mode_after',None)) for m in fc.modifiers])
def actionmap():return {o.name:{(fc.data_path,fc.array_index):fcdata(fc) for fc in curves(o.animation_data.action)} for o in bpy.context.scene.objects if o.animation_data and o.animation_data.action}
def coat():
 o=bpy.data.objects['V025 | COAT drawings | editable GP'];return hashlib.sha256(repr([(f.frame_number,[[(tuple(p.position),p.radius,p.opacity,tuple(p.vertex_color)) for p in st.points] for st in f.drawing.strokes]) for f in o.data.layers[0].frames]).encode()).hexdigest()
def setup(path):
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);S=bpy.context.scene;rig=bpy.data.objects['LOCO_BOY | RIG'];fore=S.view_layers['V025 | original foreground'];controls={o.name:o for o in S.objects if o.get('v016_control')};return S,rig,fore,controls
def frame(S,f):S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update()
def mesh(o,vl):
 vl.update();e=o.evaluated_get(vl.depsgraph);return [e.matrix_world@v.co for v in e.data.vertices]
S,rig,fore,C=setup(P/'reference/PREFERRED_v033.blend');oldactions=actionmap();oldcoat=coat()
for f in samples:
 frame(S,f);fore.update();cache[f]={'root':rig.parent.matrix_world.copy(),'controls':{n:o.matrix_world.copy() for n,o in C.items()},'bones':{b.name:(rig.matrix_world@b.matrix).copy() for b in rig.pose.bones},'shoulders':{s:rig.matrix_world@rig.pose.bones['upper_arm_'+s].head for s in ['near','far']},'head':mesh(bpy.data.objects[protected[0]],fore),'soles':{s:min((bpy.data.objects['V033 | '+s+' | canonical painted shoe'].matrix_world@v.co).z for v in bpy.data.objects['V033 | '+s+' | canonical painted shoe'].data.vertices) for s in ['near','far']}}
S,rig,fore,C=setup(P/'native/WTSC_Limb_Volume_and_Hand_Readability_v036.blend');newactions=actionmap();changes=[]
for name,channels in oldactions.items():
 candidate=newactions.get(name,{})
 for key in set(channels)|set(candidate):
  if channels.get(key)!=candidate.get(key):changes.append({'object':name,'path':key[0],'index':key[1]})
unexpected=[r for r in changes if not (r['object']==rig.name and 'forearm_' in r['path'] and 'pole_angle' in r['path'])]
errors={k:0. for k in ['root_matrix','all_control_world_matrices','non_arm_bone_world_matrices','shoulder_path_m','head_vertex_m','hand_bone_world_matrices','sole_min_z_change_m','arm_IK_wrist_endpoint_m']};rows=[]
def me(A,B):return max(abs(A[a][b]-B[a][b]) for a in range(4) for b in range(4))
for f in samples:
 frame(S,f);fore.update();r=cache[f];errors['root_matrix']=max(errors['root_matrix'],me(rig.parent.matrix_world,r['root']))
 for n,M in r['controls'].items():errors['all_control_world_matrices']=max(errors['all_control_world_matrices'],me(C[n].matrix_world,M))
 for b in rig.pose.bones:
  W=rig.matrix_world@b.matrix
  if not b.name.startswith(('upper_arm_','forearm_')):errors['non_arm_bone_world_matrices']=max(errors['non_arm_bone_world_matrices'],me(W,r['bones'][b.name]))
  if b.name.startswith('hand_'):errors['hand_bone_world_matrices']=max(errors['hand_bone_world_matrices'],me(W,r['bones'][b.name]))
 errors['head_vertex_m']=max(errors['head_vertex_m'],max((a-b).length for a,b in zip(mesh(bpy.data.objects[protected[0]],fore),r['head'])))
 for side in ['near','far']:
  errors['shoulder_path_m']=max(errors['shoulder_path_m'],(rig.matrix_world@rig.pose.bones['upper_arm_'+side].head-r['shoulders'][side]).length);ob=bpy.data.objects['V033 | '+side+' | canonical painted shoe'];z=min((ob.matrix_world@v.co).z for v in ob.data.vertices);errors['sole_min_z_change_m']=max(errors['sole_min_z_change_m'],abs(z-r['soles'][side]));W=C['BOY | WRIST_'+side].matrix_world.translation;E=rig.matrix_world@rig.pose.bones['forearm_'+side].tail;errors['arm_IK_wrist_endpoint_m']=max(errors['arm_IK_wrist_endpoint_m'],(W-E).length)
 if f in [1,11,20,27,31,31.5,32,62,62.5,63,93,93.5,94]:rows.append({'frame':f,'root_world_x_m':rig.parent.matrix_world.translation.x,'near_wrist_world':list(C['BOY | WRIST_near'].matrix_world.translation),'far_wrist_world':list(C['BOY | WRIST_far'].matrix_world.translation)})
report.update({'active_object_action_count':len(oldactions),'changed_active_channels':changes,'unexpected_channel_changes':unexpected,'exact_control_action_preservation':not any(r['object']!=rig.name for r in changes),'allowed_rig_change':'v035 copied/renamed the rig Action and refit only forearm IK pole-angle channels for the intentionally changed upper/forearm rest split. This is not an unchanged whole arm skeleton claim.','original_GP_coat_drawing_hash_unchanged':oldcoat==coat(),'errors':errors,'wrap_and_selected_checks':rows,'hand_geometry_exception':'v035 far-hand depth offset2mm and v036 thumb clearance up to3.64mm/local values are intentional shape changes; wrist paths, hand matrices, scale and timing match preferred source.','shoe_geometry_exception':'Only non-support upper-canvas vertices move up to a few millimetres; one shared design retained, sole geometry and shoe object trajectories unchanged.','images':[{'name':i.name,'packed':bool(i.packed_file)} for i in bpy.data.images if i.type=='IMAGE'],'observation_limit':'Dense samples are finite numerical checks. Exact action-channel equality establishes preservation of the authored controls; limb shape/rig refits are separately disclosed. Actual normal-speed visual review remains necessary.'})
(P/'evidence/PREFERRED_WHOLE_CYCLE_PRESERVATION.json').write_text(json.dumps(report,indent=2));assert not unexpected and report['original_GP_coat_drawing_hash_unchanged'];assert max(errors.values())<.00002,errors
S.render.threads_mode='FIXED';S.render.threads=2;S.render.resolution_percentage=100
for view,cam,size in [('CLOSE','V024 | CLOSE portrait',(480,720)),('SHOT','V020 | CHILD | SHOT',(1280,720))]:
 S.camera=bpy.data.objects[cam];S.render.resolution_x,S.render.resolution_y=size;p=P/'previews'/('PROOF_'+view);p.mkdir(exist_ok=True)
 for f in [1,4,11,20,27]:S.frame_set(f);S.render.filepath=str(p/f'{f:04d}.png');bpy.ops.render.render(write_still=True)
print('V036_PREFERRED_PRESERVATION_AND_PROOF_COMPLETE',json.dumps({'errors':errors,'unexpected':unexpected,'active_channels_changed':changes}),flush=True)
