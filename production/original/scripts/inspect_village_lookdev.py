"""Read-only native inspection before the bounded village still revision."""
import bpy
import json
from pathlib import Path


def main():
    root = Path(r"WTSC_LOCAL_WORKSPACE")
    out = root / "notes" / "village_lookdev"
    out.mkdir(parents=True, exist_ok=True)
    pair = bpy.data.objects.get("GP_Pair_STATIC_world_scale")
    result = {
        "file": bpy.data.filepath,
        "blender": bpy.app.version_string,
        "scene": bpy.context.scene.name,
        "scenes": list(bpy.data.scenes.keys()),
        "image_plane_operator": hasattr(bpy.ops.image, "import_as_mesh_planes"),
        "pair": None,
    }
    if pair:
        result["pair"] = {
            "name": pair.name,
            "type": pair.type,
            "location": list(pair.location),
            "dimensions": list(pair.dimensions),
            "scale": list(pair.scale),
            "parent": pair.parent.name if pair.parent else None,
            "layers": [l.name for l in pair.data.layers],
            "materials": [{"name": m.name,
                           "stroke": list(m.grease_pencil.color),
                           "fill": list(m.grease_pencil.fill_color),
                           "show_stroke": m.grease_pencil.show_stroke,
                           "show_fill": m.grease_pencil.show_fill}
                          for m in pair.data.materials if m and m.is_grease_pencil],
        }
    (out / "native_before_v012.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result))


main()
