import bpy,json,hashlib,sys
from pathlib import Path
P=Path(__file__).resolve().parents[1];R=P.parents[1];BASE=R/'characters/rig_capability_audit_v016/native/WTSC_Painted_Rig_Capability_v016.blend'
sys.path.insert(0,str(P/'scripts'));import corrective_geometry as C
bpy.ops.wm.open_mainfile(filepath=str(BASE),load_ui=False,use_scripts=False);S=bpy.context.scene
baseline_hash=hashlib.sha256(BASE.read_bytes()).hexdigest()
pack=bpy.data.collections['WTSC_PAINTED_RIG_CAPABILITY_v016'];rigs={o['character']:o for o in pack.all_objects if o.type=='ARMATURE'};meshes=[o for o in pack.all_objects if o.type=='MESH']
controls={(o.name.split(' | ')[0],o['v016_control']):o for o in pack.all_objects if o.get('v016_control')}
for f in range(1,222,20):
 S.frame_set(f);S.render.filepath=str(P/f'previews/BEFORE/{f:04d}.png');bpy.ops.render.render(write_still=True)
pack.name='WTSC_PAINTED_RIG_CORRECTIVES_v017';helpers=bpy.data.collections.new('V017 | CORRECTIVE CONTOUR TARGETS');pack.children.link(helpers)
for who,rig in rigs.items():
 wrist=controls[who,'WRIST_far'];wrist['FrontLayer']=0.;wrist.id_properties_ui('FrontLayer').update(min=0,max=1,description='Deliberate2D far-arm layer switch:0behind torso;1in front of torso but behind near arm. Key as CONSTANT.')
 hand=next(o for o in meshes if o.parent==rig and o.get('v007_role')=='drawn_hand' and o.name.endswith('far'))
 fc=hand.driver_add('location',1);v=fc.driver.variables.new();v.name='front';v.targets[0].id=wrist;v.targets[0].data_path='["FrontLayer"]';fc.driver.expression='0.024-0.060*max(0,min(1,front))'
 for frame in range(1,222,20):wrist['FrontLayer']=float(frame==201);wrist.keyframe_insert(data_path='["FrontLayer"]',frame=frame)
 for l in wrist.animation_data.action.layers:
  for st in l.strips:
   for bag in st.channelbags:
    for fc in bag.fcurves:
     if fc.data_path=='["FrontLayer"]':
      for k in fc.keyframe_points:k.interpolation='CONSTANT'
report={'baseline':str(BASE),'baseline_sha256':baseline_hash,'IK_chains':8,'limb_cuff_surfaces':16,'arm_correctives':[],'compression_correctives':[],'head_views':'Original v015 right-profile paint retained. Required girl attention turn remains missing matching registered art.','source_interface':'Original v016 controller ABI and8nativeIKchains retained.'}
for o in meshes:
 if o.get('v007_role') in ['drawn_arm','drawn_cuff']:report['arm_correctives'].append(C.arms(o,helpers,controls))
for f in [1,61,161,201]:
 S.frame_set(f);S.render.filepath=str(P/f'previews/AFTER_ARMS_{f:04d}.png');bpy.ops.render.render(write_still=True)
S.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Painted_Rig_Arm_Correctives_v017.blend'),compress=True)
for o in meshes:
 if o.get('v007_role')=='drawn_leg':report['compression_correctives'].append(C.legs(o))
 if o.get('skin_region') in ['body','dress']:report['compression_correctives'].append(C.garment(o,controls))
for rig in rigs.values():
 rig['corrective_revision']='v017 live painted joint/cloth study';rig['motion_status']='Technical control ABI preserved; visual acceptance UNPASSED; performance paused';rig['IK_chain_count']=4
S['corrective_revision']='v017';S['IK_chains_total']=8;S['artistic_acceptance']=False
for name in ['corrective_geometry.py','rig_pose_api.py']:
 t=bpy.data.texts.get(name) or bpy.data.texts.new(name);t.clear();t.write((P/'scripts'/name).read_text())
for f in range(1,222,20):
 S.frame_set(f);S.render.filepath=str(P/f'previews/AFTER/{f:04d}.png');bpy.ops.render.render(write_still=True)
S.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Painted_Rig_Corrective_Board_v017.blend'),compress=True)
for o in pack.all_objects:
 if o.animation_data:
  o.animation_data.action=None
  for tr in list(o.animation_data.nla_tracks):o.animation_data.nla_tracks.remove(tr)
for a in list(bpy.data.actions):bpy.data.actions.remove(a)
S.frame_start=1;S.frame_end=1;S.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Painted_Rig_Control_Asset_v017.blend'),compress=True)
report['baseline_unchanged']=hashlib.sha256(BASE.read_bytes()).hexdigest()==baseline_hash
(P/'evidence/build_report.json').write_text(json.dumps(report,indent=2));print('V017_BUILT',len(report['arm_correctives']),len(report['compression_correctives']))
