"""Cold-open contact, actual-bone garment registration and source integrity checks."""
import bpy, json, hashlib, ast, math, csv
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];BASE=ROOT/'locomotion/age10_animation_retarget_v045'
source=(BASE/'scripts/check_and_render_proof.py').read_text().split("S.render.resolution_x=1280")[0]
source=source.replace("FILE=P/'native/WTSC_Age10_Walk_Retarget_Proof_v045.blend'","FILE=P/'native/WTSC_Age10_Painted_Outfit_Restoration_v046.blend'")
source=source.replace("bpy.data.scenes['V045 | AGE TEN | RETARGET AFTER STATIC SCALE']","bpy.data.scenes['V046 | AGE10 BONES | restored painted clothing']")
source=source.replace("P/'evidence/PREFERRED_EIGHTH_FRAME_REFERENCE.json'","BASE/'evidence/PREFERRED_EIGHTH_FRAME_REFERENCE.json'").replace("P/'evidence/RETARGET_BUILD.json'","BASE/'evidence/RETARGET_BUILD.json'").replace("P/'scripts/build_retarget.py'","BASE/'scripts/build_retarget.py'")
exec(compile(source,'v045_verified_contact_test_adapted_for_v046','exec'),globals())
assert all(passed.values()),passed
assert all(v<1e-6 for v in loop.values()),loop
build46=json.loads((P/'evidence/OUTFIT_RESTORATION_BUILD.json').read_text())
tree=ast.parse((P/'scripts/build_outfits.py').read_text());tree.body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['actionhash','rounded','smooth']];exec(compile(tree,'wardrobe_pure_functions','exec'),globals())
for who,r in RIGS.items():
 protected=build46['protected_rigs'][who]
 assert actionhash(r.animation_data.action)==protected['action_hash']
 for b in r.data.bones:
  assert list(b.head_local)==protected['bones'][b.name]['head']
  assert list(b.tail_local)==protected['bones'][b.name]['tail']
C=bpy.data.collections['V046 | restored original painted wardrobe'];cloth=[o for o in C.objects if o.get('wardrobe_role') in ['sleeve','leg']]
errors={o.name:0. for o in cloth};seams={o.name:0. for o in C.objects if o.get('wardrobe_role')=='skin'}
for i in range(249):
 f=1+i/8;S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
 for o in cloth:
  r=o.parent;ev=r.evaluated_get(dg);side=o.name.split()[-1];kind=o['wardrobe_role'];rows=49 if kind=='sleeve' else 65
  n1=('upper_arm_' if kind=='sleeve' else 'thigh_')+side;n2=('forearm_' if kind=='sleeve' else 'shin_')+side
  b1=ev.pose.bones[n1];b2=ev.pose.bones[n2];l1=r.data.bones[n1].length;total=l1+r.data.bones[n2].length
  start=-.008 if kind=='sleeve' else -.025;end=l1+.027 if kind=='sleeve' else total-.030;rounding=.018 if kind=='sleeve' else .022
  oe=o.evaluated_get(dg);to_r=ev.matrix_world.inverted()@oe.matrix_world
  for k in range(rows):
   t=k/(rows-1);d=start+(end-start)*t;expect,_=rounded(b1.head,b1.tail,b2.tail,l1,d,rounding)
   if kind=='leg':
    w=smooth((d-(total-.095))/.065);rest=Vector((0,0,r.data.bones[n1].head_local.z-d));bound=ev.pose.bones['foot_'+side].matrix@r.data.bones['foot_'+side].matrix_local.inverted()@rest;expect=expect.lerp(bound,w)
   actual=to_r@oe.data.vertices[k*9+4].co;err=math.hypot(actual.x-expect.x,actual.z-expect.z);errors[o.name]=max(errors[o.name],err)
 # Verify the two native skin/hand pieces overlap around the actual wrist.
 for o in C.objects:
  if o.get('wardrobe_role')!='skin':continue
  r=o.parent;side=o.name.split()[-1];ev=r.evaluated_get(dg);oe=o.evaluated_get(dg);to_r=ev.matrix_world.inverted()@oe.matrix_world;wrist=ev.pose.bones['hand_'+side].head
  a=to_r@oe.data.vertices[31*9+4].co;b=to_r@oe.data.vertices[32*9+4].co
  # Last two skin rows must reach beyond the wrist into the painted hand.
  handdir=(ev.pose.bones['hand_'+side].tail-wrist).normalized();reach=max((a-wrist).dot(handdir),(b-wrist).dot(handdir));seams[o.name]=max(seams[o.name],max(0,.004-reach))
assert max(errors.values())<.0005,errors
assert max(seams.values())<.001,seams
images=[i for i in bpy.data.images if i.source=='FILE' and i.users];unpacked=[i.name for i in images if not i.packed_file];assert not unpacked,unpacked
assert hashlib.sha256(FILE.read_bytes()).hexdigest()==before
assert hashlib.sha256(Path(build46['source']).read_bytes()).hexdigest()==build46['source_sha256']
report2={'native_sha256':before,'native_unchanged':True,'source_unchanged':True,'actual_rig_bones_and_actions_match_build':True,'garment_samples':249,'garment_frame_range':[1,32],'sample_step_frames':.125,'max_actual_bone_garment_axis_registration_error_m':errors,'limit_m':.0005,'wrist_overlap_deficiency_m':seams,'all_used_file_images_packed':True,'file_image_count':len(images),'original_image_pixels_edited':False,'visual_caveat':'Geometric conformity and texture packing are technical checks. Separate rendered image review is needed to judge clothing appearance and animation.'}
(P/'evidence/COLD_GARMENT_VALIDATION.json').write_text(json.dumps(report2,indent=2))
with (P/'evidence/TRAVEL_CURVE_v046.csv').open('w',newline='') as h:
 w=csv.writer(h);w.writerow(['source_frame_30fps','seconds_since_first_frame','shared_root_travel_m','passing_world_translation_m','camera_follow_m'])
 for i in range(745):
  f=1+i/8;w.writerow([f,(f-1)/30,D(f),-D(f),D(f)])
print('V046_COLD_GARMENTS_CONTACTS_PASS',json.dumps({'garment_axis_max_m':max(errors.values()),'wrist_deficiency_max_m':max(seams.values()),'native_unchanged':True}),flush=True)
