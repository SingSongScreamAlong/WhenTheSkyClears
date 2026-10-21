"""Keep comparison images available inside the two isolated native studies."""

import bpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "muybridge_source_sequence_v064" / "reference"
for phase, aframe in ((6, 0), (8, 6)):
    blend = ROOT / "native" / f"Boy_Phase{phase:02d}_Point_Authored_Redraw_v065.blend"
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    for path in (
        SOURCE / f"phase{phase:02d}_source_crop.png",
        ROOT / "reference" / f"A_v053_frame{aframe:03d}.png",
    ):
        img = bpy.data.images.load(str(path), check_existing=True)
        img.pack()
        img.use_fake_user = True
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(blend), compress=True)
    print("PACKED", blend)
