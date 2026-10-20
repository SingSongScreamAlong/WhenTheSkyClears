from pathlib import Path
import json,math
P=Path(__file__).resolve().parents[1];D=json.loads((P/'evidence/fbx_source_inspection.json').read_text());rows=D['samples'];by={r['frame']:r for r in rows}
def extremum(lo,hi,kind):return min((r for r in rows if lo<=r['frame']<=hi),key=lambda r:(1 if kind=='min' else -1)*r['bones']['Hips']['head'][2])['frame']
def passing(lo,hi,s):
 best=[]
 for r in rows:
  if lo<=r['frame']<=hi:
   b=r['bones'];hip=-sum(b['UpperLeg_'+x]['head'][1] for x in ['L','R'])/2;k=-b['LowerLeg_'+s]['head'][1];best.append((abs(k-hip),r['frame']))
 return min(best)[1]
phases=[('R_CONTACT',9.75,'Contact onset estimate: right ankle/toe world-forward position approaches a plateau; toe-up foot settles to flat by12. Heel is not a source joint.'),('R_LOADING',extremum(10,14,'min'),'Hip height minimum following right contact.'),('R_PASSING',passing(16,19,'L'),'Swing left knee passes the projected hip center; this is knee passing, not ankle crossing.'),('R_UP',extremum(17,22,'max'),'Hip height maximum during right support.'),('L_CONTACT',25.75,'Contact onset estimate: left ankle/toe world-forward speed falls sharply; flat forefoot settles by28. Heel is not a source joint.'),('L_LOADING',extremum(26,29,'min'),'Hip height minimum at early left loading; contact and load are nearly coincident in this clip.'),('L_PASSING',passing(2,4,'R')+31,'Next-cycle swing right knee passes projected hip center.'),('L_UP',extremum(3,7,'max')+31,'Next-cycle hip height maximum during left support.')]
stride=-rows[-1]['bones']['Root']['head'][1]+rows[0]['bones']['Root']['head'][1]
out={'source_key_range':D['key_range'],'source_fps':D['fps'],'period_frames':31.,'period_seconds':31/30,'source_root_stride_m':stride,'root_direction':'-worldY mapped to child+X; worldZ retained','phase_definition_limit':'No source heel or skin sole exists. Contact onset is inferred from stationary-foot onset, foot pitch and subsequent flat forefoot. It is not an exact measured heel event.','contact_windows_source_frames':{'R':[9.75,11.],'L':[25.75,27.]},'phases':[{'index':i+1,'name':n,'unwrapped_source_frame':f,'wrapped_source_frame':2+(f-2)%31,'source_seconds_from_first_key':(f-2)/30,'seconds_from_study_contact':(f-9.75)/30,'study_frame_30fps':1+f-9.75,'basis':b} for i,(n,f,b) in enumerate(phases)],'adult_reference_status':'User-supplied Animation Base Locomotion v3; not Mixamo; adult gait is reference only, not approved child acting.'}
(P/'reference/SOURCE_PHASE_TIMING_v020.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
