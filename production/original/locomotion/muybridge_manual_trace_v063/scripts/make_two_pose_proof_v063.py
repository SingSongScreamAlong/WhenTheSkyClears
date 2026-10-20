"""Proof two manually authored poses using the actual Blender GP render alphas."""

import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).resolve().parents[1]
prior = root.parent / "muybridge_manual_trace_v062"
source6_path = prior / "reference" / "phase06_source_crop.png"
source8_path = root / "reference" / "phase08_source_crop.png"
render6_path = prior / "previews" / "phase06_native_trace_rgba_v062.png"
render8_path = root / "previews" / "phase08_native_trace_rgba_v063.png"
source6 = Image.open(source6_path).convert("RGB").resize((620, 1176), Image.Resampling.LANCZOS)
source8 = Image.open(source8_path).convert("RGB").resize((620, 1176), Image.Resampling.LANCZOS)
render6 = Image.open(render6_path).convert("RGBA")
render8 = Image.open(render8_path).convert("RGBA")
assert source6.size == source8.size == render6.size == render8.size == (620, 1176)


def overlay(source, render):
    layer = Image.new("RGBA", source.size, (8, 238, 231, 0))
    layer.putalpha(render.getchannel("A").point(lambda value: round(value * 0.72)))
    return Image.alpha_composite(source.convert("RGBA"), layer).convert("RGB")


def on_paper(render):
    paper = Image.new("RGBA", render.size, (239, 235, 224, 255))
    return Image.alpha_composite(paper, render).convert("RGB")


font_path = Path(r"C:\Windows\Fonts\arial.ttf")
font = ImageFont.truetype(str(font_path), 22) if font_path.exists() else ImageFont.load_default()
small = ImageFont.truetype(str(font_path), 15) if font_path.exists() else ImageFont.load_default()


def sheet(name, panels, titles, footer):
    canvas = Image.new("RGB", (20 + len(panels)*640, 1296), (238, 233, 218))
    draw = ImageDraw.Draw(canvas)
    for i, (panel, title) in enumerate(zip(panels, titles)):
        x = 20 + i*640
        canvas.paste(panel, (x, 72))
        draw.text((x, 22), title, fill=(36, 35, 32), font=font)
        draw.rectangle((x-1, 71, x+620, 1249), outline=(87, 83, 74), width=1)
    draw.text((20, 1258), footer, fill=(56, 53, 48), font=small)
    path = root / "previews" / name
    canvas.save(path, optimize=True)
    return path


phase8 = sheet(
    "Phase08_Source_Native_Overlay_v063.png",
    (source8, on_paper(render8), overlay(source8, render8)),
    ("SOURCE PHOTO - PHASE 8", "EDITABLE GP RENDER", "SOURCE + GP OVERLAY"),
    "The overlay is composited from actual Blender render alpha at exactly 2x source-crop registration.",
)
pair = sheet(
    "Phase06_Phase08_Source_Overlays_v063.png",
    (source6, overlay(source6, render6), source8, overlay(source8, render8)),
    ("PHASE 6 SOURCE", "PHASE 6 GP OVERLAY", "PHASE 8 SOURCE", "PHASE 8 GP OVERLAY"),
    "Same 310 x 588 crop, camera, scale and 2x panel registration. Each pose was authored separately.",
)

# Also preserve a compact one-source-pixel-to-one-proof-pixel pair for silhouette judgment.
small_canvas = Image.new("RGB", (660, 650), (238, 233, 218))
small_draw = ImageDraw.Draw(small_canvas)
for i, (source, render, title) in enumerate(((source6, render6, "PHASE 6"), (source8, render8, "PHASE 8"))):
    x = 10 + i*325
    small_canvas.paste(overlay(source, render).resize((310,588), Image.Resampling.LANCZOS), (x, 38))
    small_draw.text((x, 10), title, fill=(36,35,32), font=small)
small_path = root / "previews" / "Phase06_Phase08_At_Source_Scale_v063.png"
small_canvas.save(small_path, optimize=True)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


report = {
    "phase06_source_sha256": sha(source6_path),
    "phase08_source_sha256": sha(source8_path),
    "phase06_native_render_sha256": sha(render6_path),
    "phase08_native_render_sha256": sha(render8_path),
    "phase08_contact_sheet": str(phase8),
    "two_pose_proof": str(pair),
    "source_scale_proof": str(small_path),
    "proof_sha256": {p.name: sha(p) for p in (phase8, pair, small_path)},
    "source_crop_size": [310, 588],
    "render_size": [620, 1176],
    "phase06_alpha_bbox": render6.getchannel("A").getbbox(),
    "phase08_alpha_bbox": render8.getchannel("A").getbbox(),
    "method": "actual Blender Grease Pencil render alpha composited on source; no image tracing",
}
(root / "evidence" / "TWO_POSE_PROOF_v063.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print("TWO_POSE_PROOF_V063", json.dumps(report))
