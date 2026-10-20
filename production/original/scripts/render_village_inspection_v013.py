"""Three inspection renders from v013 in a separate Blender process.

Never writes the source .blend or original review PNG. Adds only diagnostic
camera/bounds/labels in memory, then saves a separately named inspection copy.
"""
import bpy
import hashlib
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(r"WTSC_LOCAL_WORKSPACE")
SOURCE = ROOT / "shots/world/WTSC_Village_Still_Review_v013.blend"
ORIGINAL_PNG = ROOT / "renders/village_lookdev/Village_Still_v013_4K.png"
OUT = ROOT / "renders/village_lookdev/inspection_v013"
NOTES = ROOT / "notes/village_lookdev"
EXPECTED = {
    SOURCE: "107541346f126bf52076c0e2c28cff4d9bf29b36ee79ac810aa0d5f28fe4a606",
    ORIGINAL_PNG: "c6141948c343c16d48e38c71b077119e07e941cfadc7550e25119ee6462474ee",
}


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    assert Path(bpy.data.filepath) == SOURCE
    for path, expected in EXPECTED.items():
        assert digest(path) == expected, path
    OUT.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    assert scene.name == "WTSC_VILLAGE_STILL_v013"
    assert scene.frame_start == scene.frame_end == 1
    original_camera = scene.camera
    original_pose = [list(row) for row in original_camera.matrix_world]
    original_lens = original_camera.data.lens
    original_objects = list(scene.objects)
    assert len(original_objects) == 6
    assert len([o for o in original_objects if o.type == "MESH"]) == 4
    assert len([o for o in original_objects if o.type == "GREASEPENCIL"]) == 1
    tools = bpy.data.collections.new("INSPECTION ONLY | camera bounds labels grid")
    scene.collection.children.link(tools)
    scene.render.resolution_x = 3840
    scene.render.resolution_y = 2160
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.frame_set(1)
    products = []

    def detail(name, filename, zoom, nx, ny, description):
        camera = original_camera.copy()
        camera.data = original_camera.data.copy()
        camera.name = "INSPECT | " + name
        tools.objects.link(camera)
        camera.data.lens = original_lens * zoom
        camera.data.shift_x = (nx - .5) * zoom
        camera.data.shift_y = (.5 - ny) * zoom * 9 / 16
        scene.camera = camera
        scene.render.filepath = str(OUT / filename)
        assert not Path(scene.render.filepath).exists()
        bpy.ops.render.render(write_still=True, scene=scene.name)
        products.append({
            "file": scene.render.filepath, "dimensions": [3840, 2160],
            "provenance": "New native Blender camera render of existing v013 assets; not a PNG crop",
            "shows": description,
            "camera": {"location": list(camera.location), "lens_mm": camera.data.lens,
                       "shift_x": camera.data.shift_x, "shift_y": camera.data.shift_y},
        })

    detail("Children and path", "01_Children_Contact_Native_4K.png", 3, .35, .73,
           "Held pure-black editable GP children, hand connection, shoe shapes and relationship to the painted path. This does not prove planted animated feet or gait.")
    detail("Bakery detail", "02_Bakery_Detail_Native_4K.png", 2.05, .70, .64,
           "Actual painted bakery facade, warm window, plaster, foliage and foreground overlap. Details live in a 1672x941 bitmap, not modeled window/roof geometry.")

    # Inspection geometry starts only after the two unchanged-asset detail renders.
    camera_data = bpy.data.cameras.new("INSPECT | Oblique orthographic camera")
    overview = bpy.data.objects.new("INSPECT | Oblique camera", camera_data)
    tools.objects.link(overview)
    overview.location = (-52, -58, 36)
    target = Vector((0, 14, 3))
    overview.rotation_euler = (target - overview.location).to_track_quat("-Z", "Y").to_euler()
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = 88
    camera_data.clip_end = 400
    scene.camera = overview
    scene.world = scene.world.copy()
    scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.018, .025, .035, 1)
    scene.world.node_tree.nodes["Background"].inputs[1].default_value = 1

    def material(name, color):
        mat = bpy.data.materials.new("INSPECT | " + name)
        mat.use_nodes = True
        nt = mat.node_tree
        nt.nodes.clear()
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        emit = nt.nodes.new("ShaderNodeEmission")
        emit.inputs[0].default_value = (*color, 1)
        nt.links.new(emit.outputs[0], out.inputs[0])
        return mat

    palette = [(0.12, .65, 1), (1, .55, .10), (.12, .9, .8),
               (.55, .95, .22), (.95, .18, .65), (1, .22, .15)]
    mats = [material(str(i + 1), color) for i, color in enumerate(palette)]
    white = material("Legend", (.8, .87, .94))
    muted = material("Muted legend", (.35, .45, .55))
    grid_mat = material("Diagnostic grid", (.045, .065, .085))

    def line(name, points, mat, radius=.035):
        curve = bpy.data.curves.new("INSPECT | " + name, "CURVE")
        curve.dimensions = "3D"
        curve.bevel_depth = radius
        curve.bevel_resolution = 0
        spline = curve.splines.new("POLY")
        spline.points.add(len(points) - 1)
        for p, co in zip(spline.points, points):
            p.co = (*co, 1)
        obj = bpy.data.objects.new("INSPECT | " + name, curve)
        tools.objects.link(obj)
        curve.materials.append(mat)
        return obj

    def text(name, body, location, size, mat):
        data = bpy.data.curves.new("INSPECT | " + name, "FONT")
        data.body = body
        data.size = size
        data.extrude = 0
        obj = bpy.data.objects.new("INSPECT | " + name, data)
        tools.objects.link(obj)
        obj.location = location
        obj.rotation_euler = overview.rotation_euler
        data.materials.append(mat)
        return obj

    def overlay(name, body, nx, ny, size, mat):
        span = camera_data.ortho_scale
        offset = Vector(((nx - .5) * span, (ny - .5) * span * 9 / 16, -8))
        pos = overview.location + overview.rotation_euler.to_quaternion() @ offset
        return text(name, body, pos, size, mat)

    mesh_names = ["v013 | Rear countryside", "v013 | Painted village",
                  "v013 | Walking path", "v013 | Oak frame and near bank"]
    stage = []
    bpy.context.view_layer.update()
    for idx, name in enumerate(mesh_names):
        obj = scene.objects[name]
        verts = [obj.matrix_world @ v.co for v in obj.data.vertices]
        xmin, xmax = min(v.x for v in verts), max(v.x for v in verts)
        zmin, zmax = min(v.z for v in verts), max(v.z for v in verts)
        y = obj.location.y - .02
        corners = [(xmin, y, zmin), (xmax, y, zmin), (xmax, y, zmax),
                   (xmin, y, zmax), (xmin, y, zmin)]
        line("Actual plane bounds " + str(idx + 1), corners, mats[idx], .055)
        text("Plane number " + str(idx + 1), str(idx + 1), (xmin - .8, y - .25, zmax + .3), 1.15, mats[idx])
        stage.append({"number": idx + 1, "object": name, "actual_y": obj.location.y,
                      "source": obj.get("source_asset"), "corners": corners[:4]})
    pair = next(o for o in original_objects if o.type == "GREASEPENCIL")
    corners = [pair.matrix_world @ Vector(v) for v in pair.bound_box]
    px = min(v.x for v in corners) - .16
    pxx = max(v.x for v in corners) + .16
    pz = min(v.z for v in corners) - .10
    pzz = max(v.z for v in corners) + .12
    py = min(v.y for v in corners) - .08
    line("GP drawing bounds 5", [(px, py, pz), (pxx, py, pz), (pxx, py, pzz),
                                  (px, py, pzz), (px, py, pz)], mats[4], .045)
    text("GP number 5", "5", (px - .7, py, pzz + .2), .9, mats[4])

    # Review camera is a real existing scene object; render a schematic wire marker
    # and frustum from its actual matrix and camera.data.view_frame, not a new set asset.
    origin = original_camera.matrix_world.translation.copy()
    frustum = []
    for corner in original_camera.data.view_frame(scene=scene):
        frustum.append(original_camera.matrix_world @ (corner * (8 / abs(corner.z))))
    line("Actual review-camera frustum perimeter", frustum + frustum[:1], mats[5], .04)
    for i, endpoint in enumerate(frustum):
        line("Actual camera ray " + str(i), [origin, endpoint], mats[5], .035)
    line("Camera marker", [origin + Vector((-.55, 0, -.38)), origin + Vector((.55, 0, -.38)),
                           origin + Vector((.55, 0, .38)), origin + Vector((-.55, 0, .38)),
                           origin + Vector((-.55, 0, -.38))], mats[5], .065)
    text("Camera number 6", "6", origin + Vector((-.9, -.2, 1)), 1, mats[5])
    for x in range(-25, 26, 5):
        line("Grid X " + str(x), [(x, -22, -10), (x, 47, -10)], grid_mat, .012)
    for y in range(-20, 46, 5):
        line("Grid Y " + str(y), [(-25, y, -10), (25, y, -10)], grid_mat, .012)
    overlay("Title", "ACTUAL BLENDER SCENE / OBLIQUE DEPTH INSPECTION", .025, .94, .92, white)
    overlay("Subtitle", "v013 assets unchanged | Diagnostic camera, wires, numbers and grid added only in this inspection copy", .025, .905, .51, muted)
    labels = ["1  Rear countryside   Y +40", "2  Painted village     Y +12",
              "3  Walking path        Y +2", "4  Near oak / bank     Y -5",
              "5  Grease Pencil pair  Y -0.36", "6  Review camera       Y -16"]
    for idx, label in enumerate(labels):
        col = idx % 3
        row = idx // 3
        overlay("Legend " + str(idx + 1), label, .025 + col * .325, .13 - row * .04, .56, mats[idx])
    overlay("Construction note", "FOUR FLAT IMAGE PLANES / THREE BITMAPS + NATIVE GP DRAWING. No modeled buildings behind the paintings.", .025, .035, .49, white)
    scene.render.filepath = str(OUT / "03_Oblique_Depths_Diagnostic_Native_4K.png")
    assert not Path(scene.render.filepath).exists()
    bpy.ops.render.render(write_still=True, scene=scene.name)
    products.append({
        "file": scene.render.filepath, "dimensions": [3840, 2160],
        "provenance": "Native Blender render from an added oblique diagnostic camera; actual v013 objects, with explicitly labeled inspection annotations",
        "shows": "Four physically separated image planes, native GP pair and original review-camera marker/frustum. Demonstrates layer spacing and flat construction; not a production frame or proof of approved scrolling.",
        "stage": stage, "diagnostic_camera": list(overview.location),
        "diagnostic_additions": "Colored plane/GP bounds, numbered text, schematic review-camera frustum, coordinate grid and legend",
    })
    assert [list(row) for row in original_camera.matrix_world] == original_pose
    assert original_camera.data.lens == original_lens
    scene["inspection_only"] = "Extra still views; still approval and exact approved reference remain unresolved. No scrolling/acting."
    scene.render.filepath = str(OUT / "03_Oblique_Depths_Diagnostic_Native_4K.png")
    copy_path = ROOT / "shots/world/WTSC_Village_Inspection_v013.blend"
    assert not copy_path.exists()
    bpy.ops.wm.save_as_mainfile(filepath=str(copy_path))
    for path, expected in EXPECTED.items():
        assert digest(path) == expected, path
    report = {
        "source": str(SOURCE), "source_sha256": EXPECTED[SOURCE],
        "original_review_png": str(ORIGINAL_PNG), "original_review_png_sha256": EXPECTED[ORIGINAL_PNG],
        "original_source_and_review_png_preserved": True,
        "original_camera_pose_and_lens_preserved": True,
        "inspection_copy": str(copy_path), "blender": bpy.app.version_string,
        "views": products, "imagegen_used": False,
        "new_modeled_set_assets": False, "character_pose_changed": False,
        "scrolling_started": False, "approval": "Still approval pending",
        "reference": "Provisional handoff reference; exact approved ink-and-wash image remains unavailable",
        "paint_source_sizes": [[1672, 941]] * 3,
    }
    (NOTES / "inspection_views_v013.json").write_text(json.dumps(report, indent=2))
    print("INSPECTION_COMPLETE", json.dumps(report), flush=True)


main()
