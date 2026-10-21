"""Bundle the one-pose review without copying or altering any earlier version."""

from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

root = Path(__file__).resolve().parents[1]
relative = [
    "ONE_POSE_CORRECTION_REVIEW_v066.txt",
    "native/Boy_Phase08_Manual_Painted_Contour_Correction_v066.blend",
    "previews/Boy_Phase08_Native_Correction_v066.png",
    "previews/Boy_Phase08_A_Before_After_Matched_v066.png",
    "reference/Retained_A006_Painted_Head_Dark_Safe_v066.png",
    "evidence/PHASE08_NATIVE_BUILD_v066.json",
    "evidence/PHASE08_COLD_OPEN_v066.json",
    "evidence/Phase08_Cold_Open_Render_v066.png",
    "scripts/pose8_spec_v066.py",
    "scripts/build_native_v066.py",
    "scripts/refine_retained_head_v066.py",
    "scripts/make_matched_board_v066.py",
    "scripts/readback_v066.py",
]
out = root / "Boy_Phase08_One_Pose_Correction_v066.zip"
with ZipFile(out, "w", ZIP_DEFLATED, compresslevel=7) as z:
    for name in relative:
        path = root / name
        if not path.is_file():
            raise FileNotFoundError(path)
        z.write(path, name)
with ZipFile(out) as z:
    assert z.testzip() is None
print(out, out.stat().st_size)
