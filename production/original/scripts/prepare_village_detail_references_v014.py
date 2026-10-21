"""Native Blender UV-region reference renders; source files are read-only.

These small crops contain only original painting samples, not new detail.
"""
import bpy
import json
import math
from pathlib import Path

ROOT = Path(r"WTSC_LOCAL_WORKSPACE")
OUT = ROOT / "sets/village_lookdev/v014/reference_crops"
OUT.mkdir(parents=True, exist_ok=True)
original = bpy.context.scene
recipes = [
    {"name": "Bakery", "object": "v013 | Painted village", "uv": [.325, .68, .13, .67], "size": [594, 508]},
    {"name": "Path", "object": "v013 | Walking path", "uv": [.25, .46, .06, .22], "size": [352, 152]},
]
for recipe in recipes:
    scene = bpy.data.scenes.new("REFERENCE ONLY | " + recipe["name"])
    bpy.context.window.scene = scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x, scene.render.resolution_y = recipe["size"]
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = True
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    source = original.objects[recipe["object"]]
    obj = source.copy()
    obj.data = source.data.copy()
    scene.collection.objects.link(obj)
    mat = source.data.materials[0].copy()
    obj.data.materials[0] = mat
    nt = mat.node_tree
    texture = next(n for n in nt.nodes if n.type == "TEX_IMAGE")
    emission = next(n for n in nt.nodes if n.type == "EMISSION")
    mix = next(n for n in nt.nodes if n.type == "MIX_SHADER")
    nt.links.new(texture.outputs["Color"], emission.inputs[0])
    nt.links.new(texture.outputs["Alpha"], mix.inputs[0])
    u0, u1, v0, v1 = recipe["uv"]
    width = source.dimensions.x
    height = source.dimensions.y  # Plane-local dimensions: local Y maps to world Z.
    center_x = source.location.x + ((u0 + u1) / 2 - .5) * width
    center_z = source.location.z + ((v0 + v1) / 2 - .5) * height
    camera_data = bpy.data.cameras.new("REFERENCE | region camera")
    camera = bpy.data.objects.new("REFERENCE | region camera", camera_data)
    scene.collection.objects.link(camera)
    camera.location = (center_x, source.location.y - 20, center_z)
    camera.rotation_euler = (math.pi / 2, 0, 0)
    camera_data.type = "ORTHO"
    camera_data.sensor_fit = "HORIZONTAL"
    camera_data.ortho_scale = width * (u1 - u0)
    scene.camera = camera
    recipe["reference_file"] = str(OUT / (recipe["name"] + "_Original_Region.png"))
    recipe["original_source_size"] = list(texture.image.size)
    recipe["original_region_pixels"] = [(u1 - u0) * texture.image.size[0], (v1 - v0) * texture.image.size[1]]
    recipe["provenance"] = "Native Blender orthographic render sampling original bitmap region. No new detail and no sharpening. Reference input only."
    scene.render.filepath = recipe["reference_file"]
    assert not Path(scene.render.filepath).exists()
    bpy.ops.render.render(write_still=True, scene=scene.name)
(ROOT / "notes/village_lookdev/detail_regions_v014.json").write_text(json.dumps(recipes, indent=2))
print("ORIGINAL_REGION_REFERENCES_COMPLETE", json.dumps(recipes))
