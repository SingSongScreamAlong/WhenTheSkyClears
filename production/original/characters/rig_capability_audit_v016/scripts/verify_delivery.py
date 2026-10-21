import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1]
def pts(o):
 bpy.context.view_layer.update();e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());return [e.matrix_world@v.co for v in e.data.vertices]
def err(rigs):
 a=[]
 for r in rigs:
  w=r['character']
  for side in ['near','far']:
   for n,t in [('shin','ANKLE_'),('forearm','WRIST_')]:
    target=bpy.data.objects[w+' | '+t+side];a.append((r.matrix_world@r.pose.bones[n+'_'+side].tail-target.matrix_world.translation).length)
 return max(a)
def gap(r):
 leg=next(o for o in r.children if o.get('v007_role')=='drawn_leg' and o.name.endswith('near'));hand=next(o for o in r.children if o.get('v007_role')=='drawn_hand' and o.name.endswith('near'));vs=pts(leg);t=((vs[20]+vs[21])-(vs[12]+vs[13])).normalized();t.y=0;t.normalize();n=Vector((-t.z,0,t.x));return min((p-vs[17]).dot(n) for p in pts(hand)[:8])
report={}
def drivers():
 return {o.name:[fc.data_path for fc in o.animation_data.drivers] for o in bpy.context.scene.objects if o.animation_data and o.animation_data.drivers}
bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Painted_Rig_Capability_v016.blend'),load_ui=False,use_scripts=False)
expected=drivers();report['expected_object_control_drivers']=expected
bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Painted_Rig_Control_Asset_v016.blend'),load_ui=False,use_scripts=False)
S=bpy.context.scene;pack=bpy.data.collections['WTSC_PAINTED_RIG_CAPABILITY_v016'];rigs=[o for o in pack.all_objects if o.type=='ARMATURE'];boots=[o for o in pack.all_objects if o.get('v007_role')=='support_boot'];limbs=[o for o in pack.all_objects if o.get('v007_role') in ['drawn_leg','drawn_arm','drawn_cuff']]
base={o.name:pts(o) for o in [*boots,*limbs]}
for r in rigs:
 c=bpy.data.objects[r['character']+' | HIP'];c.location+=Vector((.012,0,-.015))
bpy.context.view_layer.update()
report['unkeyed_control_asset']={'actions_in_file':len(bpy.data.actions),'all16_native_edit_responses_m':{o.name:max((a-b).length for a,b in zip(base[o.name],pts(o))) for o in limbs},'max_boot_drift_m':max(max((a-b).length for a,b in zip(base[o.name],pts(o))) for o in boots),'max_IK_error_m':err(rigs),'embedded_scripts_enabled':False}
report['unkeyed_control_asset']['control_drivers_preserved']=drivers()==expected
bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Painted_Rig_Live_Diagnostic_v016.blend'),load_ui=False,use_scripts=False)
S=bpy.context.scene;rigs=[o for o in S.objects if o.type=='ARMATURE'];boots=[o for o in S.objects if o.get('v007_role')=='support_boot'];rows=[];plant_base={}
for f in range(1,97):
 S.frame_set(f);bpy.context.view_layer.update();section=(f-1)//24
 if f in [1,49]:plant_base={o.name:pts(o) for o in boots}
 rows.append({'frame':f,'max_IK_error_m':err(rigs),'min_boot_world_z_m':min(min(v.z for v in pts(o)) for o in boots),'max_planted_boot_drift_m':max(max((a-b).length for a,b in zip(plant_base[o.name],pts(o))) for o in boots) if section in [0,2] else None,'brace_projected_gap_m':{r['character']:gap(r) for r in rigs} if section==2 else None})
report['fresh_saved_live_all96_frames']=rows
report['live_control_drivers_preserved']=drivers()==expected
report['technical_only_pass']=(report['unkeyed_control_asset']['actions_in_file']==0 and report['unkeyed_control_asset']['control_drivers_preserved'] and report['live_control_drivers_preserved'] and max(a['max_IK_error_m'] for a in rows)<.0001 and min(a['min_boot_world_z_m'] for a in rows)>-1e-6 and all(v is None or 0<=min(v.values())<=max(v.values())<.002 for v in [a['brace_projected_gap_m'] for a in rows]))
(P/'evidence/delivery_native_verification.json').write_text(json.dumps(report,indent=2))
# Actual-production camera and original pair gap on the simple diagnostic
# stage. Material/light/environment matching is deliberately not claimed.
info=json.loads((P/'evidence/actual_v046_camera.json').read_text());cam=S.camera;cam.data.type=info['type'];cam.data.lens=info['lens'];cam.data.sensor_width=info['sensor_width'];cam.data.sensor_fit=info['sensor_fit'];cam.data.shift_x=info['shift_x'];cam.data.shift_y=info['shift_y'];cam.matrix_world=Matrix(info['relative_to_pair_root'])
for r in rigs:r.delta_location.x=.22 if r['character']=='BOY' else -.22
for f in range(1,97):
 S.frame_set(f);S.render.filepath=str(P/f'previews/MATCHED_SHOT/{f:04d}.png');bpy.ops.render.render(write_still=True)
# Visible-paint clearance masks at the core .8m pair test. These never modify
# the character materials or saved native file.
bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Painted_Rig_Capability_v016.blend'),load_ui=False,use_scripts=False)
S=bpy.context.scene;S.frame_set(221);S.render.film_transparent=True;S.render.image_settings.color_mode='RGBA'
allmeshes=[o for o in S.objects if o.type=='MESH'];rigs={o['character']:o for o in S.objects if o.type=='ARMATURE'}
for part in ['head','offer_hand']:
 for w,r in rigs.items():
  for o in allmeshes:o.hide_render=True
  selected=[o for o in r.children if o.type=='MESH' and (('original head' in o.name) if part=='head' else (o.get('v007_role')=='drawn_hand' and o.name.endswith('far' if w=='BOY' else 'near')))]
  for o in selected:o.hide_render=False
  S.render.filepath=str(P/f'previews/clearance_{part}_{w}.png');bpy.ops.render.render(write_still=True)
print('V016_DELIVERY_FRESH_NATIVE_PASS',report['technical_only_pass'],'MAX_IK',max(a['max_IK_error_m'] for a in rows))
