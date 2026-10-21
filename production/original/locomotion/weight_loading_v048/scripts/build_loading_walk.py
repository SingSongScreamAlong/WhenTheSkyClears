"""Materialize the planned support-loading changes through the preserved v047 engine."""
import sys,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'scripts'))
import motion_spec as M
support=json.loads((P/'evidence/SUPPORT_GEOMETRY.json').read_text());M.configure(support['characters'])
engine=P/'scripts/authoring_engine_from_v047.py';s=engine.read_text().replace('V047','V048')
s=s.replace("SRC=BASE/'native/WTSC_Age10_Painted_Outfit_Restoration_v046.blend'","SRC=ROOT/'locomotion/steady_walk_baseline_v047/native/WTSC_Steady_Ordinary_Walk_v047.blend'")
s=s.replace('e993540280bc60ff5fcc1dafe316f7c8457c5c8750a1110b8f6e307a865d005d','29a4d9f794187602af43f7349f2b01c1019f39cba9f1d1278b966b78d1770103')
s=s.replace("bpy.data.scenes['V046 | AGE10 BONES | restored painted clothing']","bpy.data.scenes['V047 | STEADY ORDINARY WALK | no stumble baseline']")
s=s.replace("bpy.data.collections['V046 | AGE10 PAIR | restored painted outfits']","bpy.data.collections['V047 | AGE10 PAIR | steady ordinary walk']")
s=s.replace("bpy.data.objects['V045 | shared travel | new stride90percent']","bpy.data.objects['V047 | shared travel | steady .73125mps']")
s=s.replace('V048 | STEADY ORDINARY WALK | no stumble baseline','V048 | CONNECTED WEIGHT LOADING | ordinary walk').replace('V048 | AGE10 PAIR | steady ordinary walk','V048 | AGE10 PAIR | connected weight loading')
s=s.replace('WTSC_Steady_Ordinary_Walk_v047.blend','WTSC_Connected_Weight_Loading_v048.blend')
# Restore source path after replacing the output filename above.
s=s.replace("SRC=ROOT/'locomotion/steady_walk_baseline_v047/native/WTSC_Connected_Weight_Loading_v048.blend'","SRC=ROOT/'locomotion/steady_walk_baseline_v047/native/WTSC_Steady_Ordinary_Walk_v047.blend'")
start=s.index('def angle(q):');end=s.index('def ik(H,A,l1,l2):')
s=s[:start]+'''def angle(q):return M.angle(q)
def support_geometry(who,beta):
 z,p,x,inds=M.support_geometry(who,beta);return z,Vector(p),x,inds
def stance(g,who,side,q=None):
 a,beta,meta=M.stance(g,who,side,q);return Vector(a),beta,meta
def foot(g,who,side):
 a,beta,meta=M.foot(g,who,side);return Vector(a),beta,meta
'''+s[end:]
lines=s.splitlines();matches=[i for i,l in enumerate(lines) if l.startswith('  g=f+PHASE[who];phi=')];assert len(matches)==1
lines[matches[0]]='''  g=f+PHASE[who];phi=math.tau*(g-1)/PERIOD;t=TARGET[who];hip=Vector(M.hip(g,who));p=M.posture(g,who)
  a=math.radians(p['pelvis_degrees']);pelvis_dir=Vector((math.sin(a),0,math.cos(a)));lean=p['chest_degrees'];a=math.radians(lean);chest_dir=Vector((math.sin(a),0,math.cos(a)));waist=hip+pelvis_dir*r.data.bones['pelvis'].length;shoulder=waist+chest_dir*r.data.bones['chest'].length;headbase=shoulder+chest_dir*(r.data.bones['head'].head_local.z-t['estimated_shoulder_joint_z_m']);headangle=p['head_degrees'];a=math.radians(headangle);head_dir=Vector((math.sin(a),0,math.cos(a)))
  setbone(r,'pelvis',hip,waist,f);setbone(r,'chest',waist,shoulder,f);setbone(r,'head',headbase,headbase+head_dir*t['vertical_head_m'],f)'''
s='\n'.join(lines)
s=s.replace("for o in bpy.data.collections['V045 | review-only fixed metric ground'].objects:o.hide_render=True","for name in ['V045 | review-only fixed metric ground','V047 | review-only fixed ground']:\n for o in bpy.data.collections[name].objects:o.hide_render=True")
s=s.replace("'hip_vertical_peak_to_peak_m':.026","'hip_vertical_peak_to_peak_m':.0215").replace("'torso_lean_degrees_boy':[1.45,2.15]","'torso_lean_degrees_boy':[1.4,2.75]").replace("'torso_lean_degrees_girl':[1.85,2.55]","'torso_lean_degrees_girl':[1.82,2.97]").replace("'head_pitch_peak_to_peak_degrees':.30","'head_pitch_peak_to_peak_degrees':.40").replace("'heel_strike_toe_up_degrees':8","'heel_strike_toe_up_degrees':12").replace("'toe_off_degrees':-18","'toe_off_degrees':-26").replace("'swing_max_authored_sole_clearance_m':.045","'swing_max_authored_sole_clearance_m':.040")
s=s.replace('STEADY_WALK_BUILD.json','LOADING_WALK_BUILD.json')
s=s.replace('Ordinary steady baseline candidate responding to drunk-stumbling feedback. No new cloth/braid embellishment. v046 paintings and age-ten rest bones retained; new even32-frame gait, quiet torso/pelvis/head, smaller foot roll and coherent reciprocal arms.','Connected weight-loading candidate responding to2/10 v047 feedback. Same speed/cadence and painted appearance. Landing knee accepts load while heel settles over4.5frames; earlier heel rise and swing clearance prevent trailing-knee snap-straight. Restrained torso counterbalance; no cloth/braid embellishment.')
s=s.replace('S.frame_start=1;S.frame_end=257;',"S['V048_loading_spec']='Original age-ten rest anatomy and painting preserved. Same .78m/32frame travel. Loading foot placement .185m;21.5mm pelvis range. See motion_spec.py and guide.';S.frame_start=1;S.frame_end=257;")
exec(compile(s,'preserved_engine_with_v048_loading_spec','exec'),globals())
report=json.loads((P/'evidence/LOADING_WALK_BUILD.json').read_text());report.update({'v048_spec_sha256':hashlib.sha256((P/'scripts/motion_spec.py').read_bytes()).hexdigest(),'preserved_authoring_engine_sha256':hashlib.sha256(engine.read_bytes()).hexdigest(),'same_speed_and_cadence_as_v047':True,'landing_offset_local_m':M.LANDING_X,'loading_roll_source_frames':4.5,'heel_rise_start_source_phase':10.5,'swing_clearance_peak_fraction':.28,'planned_support_path':json.loads((P/'evidence/LOADING_PATH_PLAN.json').read_text())['summary'],'scope':'Support-linked knee absorption and restrained upper-body counterbalance. No generalized bob/sway, new artwork, cloth or braid motion.'});(P/'evidence/LOADING_WALK_BUILD.json').write_text(json.dumps(report,indent=2));print('V048_LOADING_BUILD_COMPLETE',flush=True)
