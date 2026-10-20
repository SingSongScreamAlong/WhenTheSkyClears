"""Extract only existing painted A006 head pixels with a dark-safe matte.

This preserves source painting; it does not create or trace a new head contour.
"""

from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

root = Path(__file__).resolve().parents[1]
source = Image.open(root.parent / "boy_reference_adaptation_v065" / "reference" / "A_v053_frame006.png").convert("RGB")
rgb = np.asarray(source, dtype=np.float32)
bg = np.median(rgb[:, 300:380, :], axis=1)[:, None, :]
distance = np.max(np.abs(rgb - bg), axis=2)
alpha = np.clip((distance - 20) / 16, 0, 1)
region = Image.new("L", (660, 720))
ImageDraw.Draw(region).polygon([
    (429,161),(441,119),(458,104),(493,99),(521,107),
    (548,130),(563,158),(552,184),(531,203),(511,216),
    (485,220),(459,204),(437,187),
], fill=255)
region = region.filter(ImageFilter.GaussianBlur(1.0))
alpha = np.minimum(alpha, np.asarray(region)/255)
# The source antialias includes light studio pixels on its outermost edge.
# One-pixel matte contraction avoids a pale rim over the film's darker scenery.
alpha = np.asarray(Image.fromarray((alpha*255).astype("uint8")).filter(ImageFilter.MinFilter(3)), dtype=np.float32)/255
# Remove the gray studio's contribution from semi-transparent edge pixels.
denom = np.maximum(alpha[..., None], .05)
decontaminated = np.clip((rgb - (1-alpha[..., None])*bg)/denom, 0, 255)
decontaminated = np.minimum(decontaminated, rgb)
rgba = np.concatenate((decontaminated, alpha[..., None]*255), axis=2).astype("uint8")
cutout = Image.fromarray(rgba, "RGBA")
moved = Image.new("RGBA", (660,720))
moved.alpha_composite(cutout, (-7, 5))
dest = root / "reference" / "Retained_A006_Painted_Head_Dark_Safe_v066.png"
dest.parent.mkdir(parents=True, exist_ok=True)
moved.save(dest)
print(dest)
