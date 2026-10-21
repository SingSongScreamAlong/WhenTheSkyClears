"""Same-clock v047/v048 normal-speed comparison, using the proven encoder."""
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];s=(ROOT/'locomotion/steady_walk_baseline_v047/scripts/encode_comparison.py').read_text()
s=s.replace('V047','CURRENT_TOKEN').replace('V046','V047').replace('CURRENT_TOKEN','V048')
s=s.replace("def source(tag,f):return Image.open(V/('frames_'+tag)/('FRAME_%04d.png'%f)).convert('RGB')","def source(tag,f):\n folder=ROOT/'locomotion/steady_walk_baseline_v047/previews/frames_V047' if tag=='V047' else V/'frames_V048'\n return Image.open(folder/('FRAME_%04d.png'%f)).convert('RGB')")
s=s.replace('WTSC_Steady_Walk_v047_NormalSpeed_8Cycles.mp4','WTSC_Weight_Loading_v048_NormalSpeed_8Cycles.mp4').replace('WTSC_v046_vs_v047_Steady_Walk_NormalSpeed.mp4','WTSC_v047_vs_v048_Weight_Loading_NormalSpeed.mp4').replace('WTSC_v046_v047_Matched_Pose_Comparison.png','WTSC_v047_v048_Matched_Loading_Poses.png').replace('ENCODED_LONG_COMPARISON_CONTACT_SHEET_v047.jpg','ENCODED_LONG_COMPARISON_CONTACT_SHEET_v048.jpg')
s=s.replace('v047 | STEADY ORDINARY WALK | NORMAL SPEED','v048 | CONNECTED WEIGHT LOADING | NORMAL SPEED').replace('v046 | PREVIOUS WALK','v047 | QUIET BASELINE').replace('v047 | STEADY ORDINARY BASELINE','v048 | CONNECTED STEP LOADING')
s=s.replace('31-frame cycle, 0.830 m/s | preserved reference','32-frame cycle, 0.731 m/s | preserved reference').replace('32-frame cycle, 0.731 m/s | shorter stride and coordinated transfer','Same pace and phase | knee absorption, drawn-sole rollover and counterbalance').replace('cadence and travel differ intentionally','same cadence, phase and travel')
s=s.replace('Actual v047 native F','Actual v048 native F').replace('Same camera and scale; each version retains its own gait clock and travel','Same camera, scale, gait clock, phase and root travel')
exec(compile(s,'same_encoder_current_loading_candidate','exec'),globals())
