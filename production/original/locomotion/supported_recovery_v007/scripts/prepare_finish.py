from pathlib import Path
P=Path(__file__).resolve().parents[1];R=P.parents[1];s=(R/'locomotion/battlefield_corrections_v006/scripts/finish_review.py').read_text()
s=s.replace('v006','v007').replace('V006','V007').replace('v043','v044').replace('V043','V044')
s=s.replace('renders/world_v016/integration_v044/WTSC_Combined_Open_75_80_4K_v044.mp4','renders/world_v016/integration_v044/WTSC_Drawn_Open_75_80_View_v044.mp4')
s=s.replace('v044 ORIGINAL / EEVEE4K source','v044 BASELINE / EEVEE').replace('v007 DRAWN CORRECTIONS / CPU Cycles proof / MATCHED CAMERA','v007 SUPPORT + LOOK BACK / EEVEE / MATCHED CAMERA')
s=s.replace('renderer differs','SAME EEVEE RENDERER')
s=s.replace('frames=[1,25,31,37,43,47,53,58,71,81,101,120]','frames=[1,31,37,43,47,58,71,81,89,101,110,120]')
s=s.replace('[37,47,58,81,101,120]','[43,47,58,89,101,120]')
s=s.replace('Rounded leg silhouettes now avoid the source angular/hollow lifted-knee shapes; original painting/design retained. Hands visibly open/relax with followthrough; subtle balance/breath/cloth continues after route stop. Deep boy boot overlap and small fingers still merit final-scale review. No cinematic acceptance.','Shot-size and critical-crop review: projected boot/shin paths separate during76.7..77.3; girl stabilizes, turns toward boy and offers her hand; boy braces his thigh, prepares weight forward after stop, reaches and rises visibly. Original sole/shoe/art basis retained. The fast2D head exposure and stylized fingertip clasp remain limited; no cinematic acceptance.')
s=s.replace('Integrated proof is CyclesCPU2sample960x540; v044 original was EEVEE4K. Camera/framing/timing/nativeworld retained, renderer grain/light appearance can differ.','Same production EEVEE renderer and settings, camera/world/FX/light/route; v007 actual render960x540, v044 reference1920x1080 downsampled to960x540. No renderer switch or background replacement.')
(P/'scripts/finish_review.py').write_text(s)
# Correct the inherited evidence key label; the actual comparison already uses
# the v044 native file and its original EEVEE settings.
path=P/'evidence/integrated_comparison.json'
if path.exists():
 import json
 d=json.loads(path.read_text())
 if 'new_foot_world_matrix_max_error_v043' in d:d['new_foot_world_matrix_max_error_v044']=d.pop('new_foot_world_matrix_max_error_v043')
 path.write_text(json.dumps(d,indent=2))
path=P/'scripts/integrated_comparison.py';s=path.read_text().replace('new_foot_world_matrix_max_error_v043','new_foot_world_matrix_max_error_v044');path.write_text(s)
print('V007_MATCHED_EEVEE_FINISH_READY')
