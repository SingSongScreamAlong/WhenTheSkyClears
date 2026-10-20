from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];s=(ROOT/'locomotion/steady_walk_baseline_v047/scripts/verify_paint_and_clothing.py').read_text()
s=s.replace("old=BASE/'native/WTSC_Age10_Painted_Outfit_Restoration_v046.blend'","old=ROOT/'locomotion/steady_walk_baseline_v047/native/WTSC_Steady_Ordinary_Walk_v047.blend'")
s=s.replace("new=P/'native/WTSC_Steady_Ordinary_Walk_v047.blend'","new=P/'native/WTSC_Connected_Weight_Loading_v048.blend'")
s=s.replace('V047 | STEADY ORDINARY WALK | no stumble baseline','V048 | CONNECTED WEIGHT LOADING | ordinary walk').replace('source_v046_sha256','source_v047_sha256').replace('V047_ORIGINAL','V048_ORIGINAL')
exec(compile(s,'same_paint_and_clothing_check_v048','exec'),globals())
