"""Use identical framing, clocks and decode checks as the frozen v049 review."""
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];s=(ROOT/'locomotion/connected_model_fit_v049/scripts/encode_v049_motion.py').read_text()
s=s.replace('V049','CURRENT').replace('V048','V049').replace('CURRENT','V050')
s=s.replace('v049','currenttag').replace('v048','v049').replace('currenttag','v050')
s=s.replace('Model_Fit_v050_Actual_NormalSpeed','Face_Hand_Finish_v050_Actual_NormalSpeed').replace('Model_Fit_SameMotion','Face_Hand_Finish_SameMotion')
s=s.replace('v050 MODEL FIT | ACTUAL NATIVE MOTION | NORMAL SPEED','v050 FACE / HAND FINISH | ACTUAL NATIVE | NORMAL SPEED')
s=s.replace('v049 | BEFORE MODEL FIT','v049 | RECEIVED BASELINE').replace('v050 | FITTED MODEL IN MOTION','v050 | FACE AND RELAXED HAND FINISH')
s=s.replace('Original garment fit, sleeve crown and painted hand grouping','Frozen v049 model and motion | unchanged reference').replace('Refined garment contour, sleeves, forearms and hand grouping','Registered girl face/skin finish and static relaxed hand curl')
s=s.replace("'model_version':'v050' if file==full else 'v049 left, v050 right'","'model_version':'v050 face/hand finish' if file==full else 'v049 left, v050 right'")
s=s.replace('(410,275,880,570)','(410,175,880,570)').replace('(1920,680)','(1920,880)').replace('y=(j//4)*340','y=(j//4)*440').replace('(480,301)','(480,403)')
exec(compile(s,'v050_actual_motion_encoder','exec'),globals())
