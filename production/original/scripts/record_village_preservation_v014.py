from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parents[1]
names = [
    "shots/world/WTSC_Living_World_v010.blend",
    "shots/world/WTSC_Living_World_Editable_v011.blend",
    "renders/living_world/WTSC_Living_World_4K_v010.mp4",
    "shots/world/WTSC_Village_Still_Review_v013.blend",
    "renders/village_lookdev/Village_Still_v013_4K.png",
    "shots/world/WTSC_Village_Inspection_v013.blend",
] + [str(p.relative_to(root)).replace("\\", "/") for p in sorted((root / "renders/village_lookdev/inspection_v013").glob("*.png"))]
files = []
for name in names:
    p = root / name
    with p.open("rb") as f:
        sha = hashlib.file_digest(f, "sha256").hexdigest()
    files.append({"path": name, "bytes": p.stat().st_size, "sha256": sha})
target = root / "notes/village_lookdev/preservation_before_v014.json"
assert not target.exists()
target.write_text(json.dumps(files, indent=2))
print(json.dumps(files))
