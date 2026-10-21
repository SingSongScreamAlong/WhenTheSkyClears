"""Independent pixel decode, alpha and preservation checks; no image edits."""
from pathlib import Path
import hashlib
import json
from PIL import Image
import numpy as np

root = Path(__file__).resolve().parents[1]
expected = {
    "shots/world/WTSC_Living_World_v010.blend": "dedb85194afa2776e5bd0ca8bcbdd16f45e34ad47095a06dd2e03ba10adc6560",
    "shots/world/WTSC_Living_World_Editable_v011.blend": "13ab34cf37953f6fa8ce12ce3a70c7202547b7f144770399e5d3bd7f5ac409e4",
    "renders/living_world/WTSC_Living_World_4K_v010.mp4": "bd4da200c33b40a89e80312215d75d597f63cf28318493758ee7ef114037029a",
}
preserved = []
for name, sha in expected.items():
    path = root / name
    with path.open("rb") as f:
        actual = hashlib.file_digest(f, "sha256").hexdigest()
    assert actual == sha, name
    preserved.append({"path": name, "sha256": actual, "unchanged": True})
path = root / "renders/village_lookdev/Village_Still_v013_4K.png"
with Image.open(path) as image:
    image.load()
    assert image.size == (3840, 2160)
    arr = np.asarray(image.convert("RGB"))
    # Bound the two known GP children and verify their solid black rendered interior.
    crop = arr[int(.60*2160):int(.85*2160), int(.28*3840):int(.42*3840)]
    black = np.all(crop == 0, axis=2)
    assert int(black.sum()) > 10000
paint = []
for name in ("Rear_Countryside.png", "Village_Middle.png", "Foreground_Ground.png"):
    with Image.open(root / "sets/village_lookdev/v012" / name) as image:
        image.load()
        alpha = np.asarray(image.convert("RGBA"))[:, :, 3]
        if name != "Rear_Countryside.png":
            assert alpha.min() == 0 and alpha.max() == 255
        paint.append({"file": name, "size": list(image.size), "mode": image.mode,
                      "alpha_range": [int(alpha.min()), int(alpha.max())]})
result = {"review_png": str(path), "size": [3840, 2160], "decode_ok": True,
          "solid_black_child_pixels_in_review_region": int(black.sum()),
          "paint_sources": paint, "preserved_original_deliverables": preserved,
          "approval": "Pending; technical validation does not approve art or scrolling"}
(root / "notes/village_lookdev/media_verification_v013.json").write_text(json.dumps(result, indent=2))
print(json.dumps(result))
