"""Reuse the same read-only measurement method on the new cold native."""
from pathlib import Path
P=Path(__file__).resolve().parents[1];s=(P/'scripts/diagnose_v046.py').read_text()
s=s.replace("ROOT/'locomotion/painted_outfit_restoration_v046/native/WTSC_Age10_Painted_Outfit_Restoration_v046.blend'","P/'native/WTSC_Steady_Ordinary_Walk_v047.blend'")
s=s.replace("assert sha=='e993540280bc60ff5fcc1dafe316f7c8457c5c8750a1110b8f6e307a865d005d';",'')
s=s.replace("bpy.data.scenes['V046 | AGE10 BONES | restored painted clothing']","bpy.data.scenes['V047 | STEADY ORDINARY WALK | no stumble baseline']").replace('range(249)','range(257)').replace("'samples':249","'samples':257").replace('.8295477722050396','.73125').replace('V046_GAIT_DIAGNOSIS.json','V047_GAIT_DIAGNOSIS.json')
exec(compile(s,'same_method_new_candidate','exec'),globals())
