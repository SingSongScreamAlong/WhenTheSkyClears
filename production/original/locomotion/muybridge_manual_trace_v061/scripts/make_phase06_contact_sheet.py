"""Place source, actual Blender GP render, and its registration overlay side by side."""

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


root = Path(__file__).resolve().parents[1]
source_path = root / "reference" / "phase06_source_crop.png"
native_path = root / "previews" / "phase06_native_trace_rgba.png"
source = Image.open(source_path).convert("RGB").resize((620, 1176), Image.Resampling.LANCZOS)
native = Image.open(native_path).convert("RGBA")
assert native.size == source.size
alpha = native.getchannel("A")

cream = Image.new("RGBA", source.size, (239, 235, 224, 255))
trace_panel = Image.alpha_composite(cream, native).convert("RGB")
cyan = Image.new("RGBA", source.size, (12, 241, 236, 0))
cyan.putalpha(alpha.point(lambda value: round(value * 0.72)))
overlay = Image.alpha_composite(source.convert("RGBA"), cyan).convert("RGB")

width = 1940
height = 1296
sheet = Image.new("RGB", (width, height), (238, 233, 218))
positions = [20, 660, 1300]
for left, panel in zip(positions, (source, trace_panel, overlay)):
    sheet.paste(panel, (left, 72))

font_path = Path(r"C:\Windows\Fonts\arial.ttf")
font = ImageFont.truetype(str(font_path), 22) if font_path.exists() else ImageFont.load_default()
small = ImageFont.truetype(str(font_path), 15) if font_path.exists() else ImageFont.load_default()
d = ImageDraw.Draw(sheet)
for left, title in zip(positions, ("MUYBRIDGE PLATE 2 · PHASE 6", "BLENDER GREASE PENCIL TRACE", "REGISTERED OVERLAY")):
    d.text((left, 22), title, fill=(37, 37, 33), font=font)
    d.rectangle((left - 1, 71, left + 620, 1249), outline=(87, 83, 74), width=1)
d.text((20, 1258), "Source adult anatomy study · manual point-authored contours · original crop 310×588 · cyan uses native-render alpha", fill=(57, 54, 49), font=small)
d.text((1300, 1258), "leading heel and trailing toe both near ground; head detail low contrast", fill=(57, 54, 49), font=small)

out = root / "previews" / "Phase06_Source_Native_Overlay_Contact_v061.png"
sheet.save(out, optimize=True)
report = {
    "source_crop_sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
    "native_render_sha256": hashlib.sha256(native_path.read_bytes()).hexdigest(),
    "contact_sha256": hashlib.sha256(out.read_bytes()).hexdigest(),
    "native_alpha_bbox": alpha.getbbox(),
    "contact_path": str(out),
    "contact_size": sheet.size,
    "uses_actual_native_render": True,
    "overlay_registration": "All panels use source pixel crop scaled exactly 2x; native camera maps 1 source pixel to 2 render pixels.",
}
(root / "evidence" / "PHASE06_CONTACT_SHEET_v061.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print("PHASE06_CONTACT_SHEET", json.dumps(report))
