"""Test reuse of the approved painted head pixels without changing authored legs.

This is a *retained art* test, not a newly painted head or a rotoscope claim.
Only source frames already in the isolated evidence folder are read.
"""

from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
for phase, frame, dx, dy in ((6, 0, -4, 0), (8, 6, -7, 5)):
    baseline = Image.open(ROOT / "reference" / f"A_v053_frame{frame:03d}.png").convert("RGB")
    pixels = np.asarray(baseline, dtype=np.int16)
    bg = np.median(pixels[:, 300:380, :], axis=1)[:, None, :]
    difference = np.max(np.abs(pixels - bg), axis=2)
    # Feather the difference matte; the manual region keeps all coat pixels out.
    alpha = np.clip((difference - 9) * (255 / 12), 0, 255).astype("uint8")
    region = Image.new("L", (660, 720))
    polygon = [
        (429, 161), (441, 119), (458, 104), (493, 99),
        (521, 107), (548, 130), (563, 158), (552, 184),
        (531, 203), (511, 216), (485, 220), (459, 204), (437, 187),
    ]
    ImageDraw.Draw(region).polygon(polygon, fill=255)
    region = region.filter(ImageFilter.GaussianBlur(2.0))
    alpha = np.minimum(alpha, np.asarray(region))
    retained = baseline.convert("RGBA")
    retained.putalpha(Image.fromarray(alpha))
    # The full-frame transparent image preserves the comparison coordinate frame.
    moved = Image.new("RGBA", (660, 720))
    moved.alpha_composite(retained, (dx, dy))
    retained_path = ROOT / "reference" / f"Retained_Painted_Head_From_A{frame:03d}_For_Phase{phase:02d}_v065.png"
    moved.save(retained_path)

    native = Image.open(ROOT / "previews" / f"Boy_Phase{phase:02d}_Native_Redraw_v065.png").convert("RGBA")
    # Clear the trial's flat head geometry before laying down the retained art.
    # This affects only the diagnostic composite, not the editable native file.
    n = np.array(native)
    n[95:217, 425:570, 3] = 0
    native = Image.fromarray(n, "RGBA")
    panel = Image.new("RGBA", (660, 720), (216, 216, 212, 255))
    panel.alpha_composite(native)
    panel.alpha_composite(moved)
    out = ROOT / "previews" / f"Boy_Phase{phase:02d}_Retained_Head_Trial_v065.png"
    panel.convert("RGB").save(out)
    print(out)
