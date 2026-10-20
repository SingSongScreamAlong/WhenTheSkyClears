"""Prove all twelve companion crops equal the retained original JPEG pixels."""

import hashlib
import json
from pathlib import Path
from PIL import Image, ImageChops

root = Path(__file__).resolve().parents[1]
original = root.parent / "three_way_walk_test_v057" / "reference" / "Muybridge_Animal_Locomotion_Plate_2_1887.jpg"
expected_sha = "d0178c822beeae7c86f9e780f2fd4f9e6309accc9a8f03b8f4696b01abab1911"
source_sha = hashlib.sha256(original.read_bytes()).hexdigest()
if source_sha != expected_sha:
    raise RuntimeError("Retained original source JPEG hash changed")
source = Image.open(original).convert("RGB")
crop_hashes = {}
for phase in range(1,13):
    rect=(31+(phase-1)*310,32,341+(phase-1)*310,620)
    path=root / "reference" / f"phase{phase:02d}_source_crop.png"
    crop=Image.open(path).convert("RGB")
    if crop.size!=(310,588) or ImageChops.difference(crop,source.crop(rect)).getbbox() is not None:
        raise RuntimeError(f"Source pixels changed in phase {phase}")
    crop_hashes[f"phase{phase:02d}"]=hashlib.sha256(path.read_bytes()).hexdigest()
report={"original_source_sha256":source_sha,"crop_sha256":crop_hashes,"all_exact_pixels_verified":True,"crop_dimensions":[310,588]}
(root / "evidence" / "SOURCE_CROPS_VERIFIED_v064.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps(report))
