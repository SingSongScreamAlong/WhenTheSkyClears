"""Adapt the verified phase-6 native author/readback to the matching phase-8 crop."""

from pathlib import Path

root = Path(__file__).resolve().parents[1]
prior = root.parent / "muybridge_manual_trace_v062" / "scripts"

author = (prior / "build_manual_trace_phase06_v062.py").read_text(encoding="utf-8")
for old, new in (
    ("phase06", "phase08"),
    ("Phase06", "Phase08"),
    ("PHASE06", "PHASE08"),
    ("Phase 06", "Phase 08"),
    ("v062", "v063"),
    ("V062", "V063"),
    ("second manually specified Muybridge contours", "contrasting manually specified phase-8 contours"),
    ('obj["source_phase"] = 6', 'obj["source_phase"] = 8'),
    ('"phase": 6', '"phase": 8'),
    ('"1581,32,1891,620"', '"2201,32,2511,620"'),
):
    author = author.replace(old, new)
author = author.replace(
    'bpy.ops.wm.save_as_mainfile(filepath=str(native_path), compress=True)',
    'bpy.context.preferences.filepaths.save_version = 0\n'
    'bpy.ops.wm.save_as_mainfile(filepath=str(native_path), compress=True)',
)
(root / "scripts" / "build_manual_trace_phase08_v063.py").write_text(author, encoding="utf-8")

reader = (prior / "readback_manual_trace_phase06_v062.py").read_text(encoding="utf-8")
for old, new in (
    ("phase06", "phase08"),
    ("Phase06", "Phase08"),
    ("PHASE06", "PHASE08"),
    ("Phase 06", "Phase 08"),
    ("v062", "v063"),
    ("V062", "V063"),
):
    reader = reader.replace(old, new)
(root / "scripts" / "readback_manual_trace_phase08_v063.py").write_text(reader, encoding="utf-8")
