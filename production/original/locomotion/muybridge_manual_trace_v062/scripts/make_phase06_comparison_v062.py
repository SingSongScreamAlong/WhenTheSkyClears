"""Compare source, v061 trace, and v062 trace using real Blender render alpha."""

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont


root = Path(__file__).resolve().parents[1]
source_path = root / "reference" / "phase06_source_crop.png"
before_path = root.parent / "muybridge_manual_trace_v061" / "previews" / "phase06_native_trace_rgba.png"
after_path = root / "previews" / "phase06_native_trace_rgba_v062.png"
source = Image.open(source_path).convert("RGB").resize((620, 1176), Image.Resampling.LANCZOS)
before = Image.open(before_path).convert("RGBA")
after = Image.open(after_path).convert("RGBA")
assert source.size == before.size == after.size
before_alpha = before.getchannel("A")
after_alpha = after.getchannel("A")


def overlay(base, alpha, color):
    layer = Image.new("RGBA", base.size, (*color, 0))
    layer.putalpha(alpha.point(lambda value: round(value * 0.72)))
    return Image.alpha_composite(base.convert("RGBA"), layer).convert("RGB")


paper = Image.new("RGBA", source.size, (239, 235, 224, 255))
native = Image.alpha_composite(paper, after).convert("RGB")
before_overlay = overlay(source, before_alpha, (245, 135, 45))
after_overlay = overlay(source, after_alpha, (8, 238, 231))
font_path = Path(r"C:\Windows\Fonts\arial.ttf")
font = ImageFont.truetype(str(font_path), 22) if font_path.exists() else ImageFont.load_default()
small = ImageFont.truetype(str(font_path), 15) if font_path.exists() else ImageFont.load_default()


def make_sheet(name, panels, titles, footer):
    width = 20 + len(panels) * 640
    sheet = Image.new("RGB", (width, 1296), (238, 233, 218))
    draw = ImageDraw.Draw(sheet)
    for index, (panel, title) in enumerate(zip(panels, titles)):
        x = 20 + index * 640
        sheet.paste(panel, (x, 72))
        draw.text((x, 22), title, fill=(36, 35, 32), font=font)
        draw.rectangle((x-1, 71, x+620, 1249), outline=(87, 83, 74), width=1)
    draw.text((20, 1258), footer, fill=(56, 53, 48), font=small)
    out = root / "previews" / name
    sheet.save(out, optimize=True)
    return out


comparison = make_sheet(
    "Phase06_Source_Before_After_v062.png",
    (source, before_overlay, after_overlay),
    ("MUYBRIDGE SOURCE · PHASE 6", "BEFORE v061 · ORANGE", "REVISED v062 · CYAN"),
    "Both overlays use alpha from the actual Blender Grease Pencil renders at identical 2× source registration.",
)
native_sheet = make_sheet(
    "Phase06_Source_Native_Overlay_v062.png",
    (source, native, after_overlay),
    ("MUYBRIDGE SOURCE · PHASE 6", "REVISED BLENDER GP RENDER", "REVISED SOURCE OVERLAY"),
    "Second manual contour pass: no automatic tracing, synthesized anatomy or child-proportion adaptation.",
)

report = {
    "source_crop_sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
    "before_render_sha256": hashlib.sha256(before_path.read_bytes()).hexdigest(),
    "after_render_sha256": hashlib.sha256(after_path.read_bytes()).hexdigest(),
    "comparison_path": str(comparison),
    "comparison_sha256": hashlib.sha256(comparison.read_bytes()).hexdigest(),
    "native_sheet_path": str(native_sheet),
    "native_sheet_sha256": hashlib.sha256(native_sheet.read_bytes()).hexdigest(),
    "before_alpha_bbox": before_alpha.getbbox(),
    "after_alpha_bbox": after_alpha.getbbox(),
    "changed_render_pixels_bbox": ImageChops.difference(before_alpha, after_alpha).getbbox(),
    "registration": "identical source crop, 2x panel scale, and Blender 620x1176 orthographic camera",
}
(root / "evidence" / "PHASE06_COMPARISON_v062.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print("PHASE06_COMPARISON_V062", json.dumps(report))
