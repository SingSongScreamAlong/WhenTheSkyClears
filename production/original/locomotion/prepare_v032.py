from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parent;old=ROOT/'rough_breakdowns_construction_v031';P=ROOT/'balanced_load_and_arm_readability_v032';assert not P.exists()
for d in ['reference','scripts','native','previews','evidence']:(P/d).mkdir(parents=True)
for name in ['PRESERVED_BASELINE_v028.blend','PRESERVED_BASELINE_v030.blend','ORIGINAL_BOY_BOOT_PIVOTS_v018.json']:shutil.copy2(old/'reference'/name,P/'reference'/name)
shutil.copy2(old/'native/WTSC_Rough_Construction_v031.blend',P/'reference/PRESERVED_BASELINE_v031.blend')
for name in ['pose_keys.py','construction_motion.py','draw_construction.py','build_construction.py','render_breakdowns.py','verify_and_render_action.py','encode_construction.py','apply_library_metadata.py','win_ea_compat.py']:
    data=(old/'scripts'/name).read_text(encoding='utf-8-sig').replace('V031','V032').replace('v031','v032');(P/'scripts'/name).write_text(data)
print(P)
