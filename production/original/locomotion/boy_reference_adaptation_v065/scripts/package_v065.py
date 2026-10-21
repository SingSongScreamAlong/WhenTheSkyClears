"""Package only the isolated, reviewable two-pose proof."""

from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

root = Path(__file__).resolve().parents[1]
files = [
    root / "TWO_POSE_ADAPTATION_REVIEW_v065.txt",
    root / "native" / "Boy_Phase06_Point_Authored_Redraw_v065.blend",
    root / "native" / "Boy_Phase08_Point_Authored_Redraw_v065.blend",
    root / "previews" / "Boy_Two_Pose_Reference_Adaptation_Review_v065.png",
    root / "previews" / "Boy_Phase06_Native_Redraw_v065.png",
    root / "previews" / "Boy_Phase08_Native_Redraw_v065.png",
    root / "previews" / "Boy_Phase06_Retained_Head_Trial_v065.png",
    root / "previews" / "Boy_Phase08_Retained_Head_Trial_v065.png",
    root / "evidence" / "TWO_POSE_COLD_OPEN_v065.json",
    root / "evidence" / "BOY_PHASE06_NATIVE_BUILD_v065.json",
    root / "evidence" / "BOY_PHASE08_NATIVE_BUILD_v065.json",
    root / "scripts" / "pose_specs.py",
    root / "scripts" / "build_native_pose_v065.py",
    root / "scripts" / "make_review_board_v065.py",
    root / "scripts" / "readback_native_v065.py",
    root / "scripts" / "retained_head_trial_v065.py",
]
out = root / "Boy_Two_Pose_Reference_Adaptation_Proof_v065.zip"
with ZipFile(out, "w", ZIP_DEFLATED, compresslevel=7) as z:
    for path in files:
        if not path.exists():
            raise FileNotFoundError(path)
        z.write(path, arcname=path.relative_to(root))
print(out, out.stat().st_size)
