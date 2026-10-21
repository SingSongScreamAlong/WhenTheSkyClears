"""One native layered 4K look-development still; no animation or old-file edits."""
import bpy
import json
import math
from pathlib import Path
from mathutils import Matrix

ROOT = Path(r"WTSC_LOCAL_WORKSPACE")
ART = ROOT / "sets/village_lookdev/v012"
NOTES = ROOT / "notes/village_lookdev"


def main():
    source_path = bpy.data.filepath
    expected = str(ROOT / "shots/world/WTSC_Living_World_Editable_v011.blend")
    assert Path(source_path) == Path(expected), source_path
    previous_scene = bpy.context.window.scene
    assert "WTSC_VILLAGE_STILL_v012" not in bpy.data.scenes
    scene = bpy.data.scenes.new("WTSC_VILLAGE_STILL_v012")
    bpy.context.window.scene = scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 3840
    scene.render.resolution_y = 2160
    scene.render.resolution_percentage = 100
    scene.render.fps = 24
    scene.frame_start = scene.frame_end = 1
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"
    scene.render.image_settings.compression = 25
    scene.render.filepath = str(ROOT / "renders/village_lookdev/Village_Still_v012_4K.png")
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    if hasattr(scene, "eevee"):
        scene.eevee.taa_render_samples = 64
    scene.world = bpy.data.worlds.new("v012 | black outside plate")
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)
    scene.world.node_tree.nodes["Background"].inputs[1].default_value = 0

    def collection(name):
        c = bpy.data.collections.new("v012 | " + name)
        scene.collection.children.link(c)
        return c

    rear = collection("01 Rear landscape")
    middle = collection("02 Village middle distance")
    ground = collection("03 Walking ground behind children")
    children = collection("04 Flat black GP children")
    foreground = collection("05 Near framing")
    cameras = collection("06 Camera")

    cam_data = bpy.data.cameras.new("v012 | Side-on 50mm")
    cam = bpy.data.objects.new("v012 | Review camera", cam_data)
    cameras.objects.link(cam)
    cam.location = (0, -16, 3)
    cam.rotation_euler = (math.pi / 2, 0, 0)
    cam_data.lens = 50
    cam_data.sensor_width = 36
    cam_data.sensor_fit = "HORIZONTAL"
    cam_data.clip_end = 300
    scene.camera = cam

    def image_plane(name, filename, y, owner, mask=None, darken=False):
        path = ART / filename
        assert path.is_file(), path
        # Reuse Blender's actual native image-as-mesh-plane importer and UVs.
        result = bpy.ops.image.import_as_mesh_planes(
            filepath=str(path), directory=str(path.parent) + "/",
            files=[{"name": path.name}], relative=False, use_transparency=True)
        assert "FINISHED" in result, result
        obj = bpy.context.object
        obj.name = "v012 | " + name
        for old in list(obj.users_collection):
            old.objects.unlink(obj)
        owner.objects.link(obj)
        xs = [v.co.x for v in obj.data.vertices]
        ys = [v.co.y for v in obj.data.vertices]
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        dx, dy = max(xs) - min(xs), max(ys) - min(ys)
        width = (y + 16) * .72
        height = width * 9 / 16
        for v in obj.data.vertices:
            v.co = ((v.co.x - cx) / dx * width, (v.co.y - cy) / dy * height, 0)
        obj.location = (0, y, 3)
        obj.rotation_mode = "XYZ"
        obj.rotation_euler = (math.pi / 2, 0, 0)
        obj.scale = (1, 1, 1)
        mat = obj.data.materials[0].copy()
        mat.name = "v012 | Painted material | " + name
        obj.data.materials[0] = mat
        nt = mat.node_tree
        texture = next(n for n in nt.nodes if n.type == "TEX_IMAGE")
        image = texture.image
        for n in list(nt.nodes):
            if n != texture:
                nt.nodes.remove(n)
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        transparent = nt.nodes.new("ShaderNodeBsdfTransparent")
        emit = nt.nodes.new("ShaderNodeEmission")
        mix = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(transparent.outputs[0], mix.inputs[1])
        nt.links.new(emit.outputs[0], mix.inputs[2])
        nt.links.new(mix.outputs[0], out.inputs[0])
        uv = nt.nodes.new("ShaderNodeTexCoord")
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(uv.outputs["UV"], sep.inputs[0])
        color = texture.outputs["Color"]
        if darken:
            ramp = nt.nodes.new("ShaderNodeValToRGB")
            ramp.label = "Designed foreground value grouping; path stays light"
            ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
            for idx, (pos, val) in enumerate([(0, .18), (.075, .24), (.105, .7),
                                              (.14, .95), (.19, .85), (.25, .18), (1, .18)]):
                el = ramp.color_ramp.elements[0] if idx == 0 else ramp.color_ramp.elements.new(pos)
                el.position = pos
                el.color = (val, val, val, 1)
            nt.links.new(sep.outputs["Y"], ramp.inputs[0])
            multiply = nt.nodes.new("ShaderNodeMixRGB")
            multiply.blend_type = "MULTIPLY"
            multiply.inputs[0].default_value = 1
            nt.links.new(color, multiply.inputs[1])
            nt.links.new(ramp.outputs[0], multiply.inputs[2])
            color = multiply.outputs[0]
        nt.links.new(color, emit.inputs[0])
        alpha = texture.outputs["Alpha"]
        if mask:
            lower = nt.nodes.new("ShaderNodeMath")
            lower.operation = "LESS_THAN"
            lower.inputs[1].default_value = .25
            nt.links.new(sep.outputs["Y"], lower.inputs[0])
            mask_value = lower.outputs[0]
            if mask == "near":
                upper = nt.nodes.new("ShaderNodeMath")
                upper.operation = "SUBTRACT"
                upper.inputs[0].default_value = 1
                nt.links.new(lower.outputs[0], upper.inputs[1])
                footer = nt.nodes.new("ShaderNodeMath")
                footer.operation = "LESS_THAN"
                footer.inputs[1].default_value = .075
                nt.links.new(sep.outputs["Y"], footer.inputs[0])
                union = nt.nodes.new("ShaderNodeMath")
                union.operation = "MAXIMUM"
                nt.links.new(upper.outputs[0], union.inputs[0])
                nt.links.new(footer.outputs[0], union.inputs[1])
                mask_value = union.outputs[0]
            multiply_alpha = nt.nodes.new("ShaderNodeMath")
            multiply_alpha.operation = "MULTIPLY"
            nt.links.new(alpha, multiply_alpha.inputs[0])
            nt.links.new(mask_value, multiply_alpha.inputs[1])
            alpha = multiply_alpha.outputs[0]
        nt.links.new(alpha, mix.inputs[0])
        mat.surface_render_method = "DITHERED"
        texture.extension = "CLIP"
        texture.interpolation = "Linear"
        image.pack()
        obj["source_asset"] = str(path.relative_to(ROOT))
        obj["depth_role"] = name
        obj["art_approval"] = "PROVISIONAL; still-frame review pending"
        return obj

    image_plane("Rear countryside", "Rear_Countryside.png", 40, rear)
    image_plane("Painted village", "Village_Middle.png", 12, middle)
    image_plane("Walking path", "Foreground_Ground.png", 2, ground, "ground", True)
    image_plane("Oak frame and near bank", "Foreground_Ground.png", -5, foreground, "near", True)

    source_pair = bpy.data.objects["GP_Pair_STATIC_world_scale"]
    pair = source_pair.copy()
    pair.data = source_pair.data.copy()
    pair.name = "v012 | CHILDREN | held editable GP black silhouettes"
    children.objects.link(pair)
    pair.parent = None
    pair.matrix_world = Matrix.Identity(4)
    pair.animation_data_clear()
    pair.data.animation_data_clear()
    for idx, old_mat in enumerate(list(pair.data.materials)):
        mat = old_mat.copy()
        mat.name = "v012 | Pure black ink | " + str(idx)
        gp = mat.grease_pencil
        gp.color = (0, 0, 0, 1)
        gp.fill_color = (0, 0, 0, 1)
        gp.show_stroke = False
        gp.show_fill = True
        pair.data.materials[idx] = mat
    for layer in pair.data.layers:
        layer.use_lights = False
        layer.opacity = 1
    view_width = (16 - .36) * .72
    view_height = view_width * 9 / 16
    pair.location = ((.35 - .5) * view_width, 0, 3 + (.5 - .84) * view_height)
    pair.hide_render = False
    pair.hide_viewport = False
    pair.hide_set(False)
    pair["performance"] = "Held drawing only; gait and acting remain deferred"
    pair["design_approval"] = "Existing provisional pair; no redesign approval inferred"
    pair["render_style"] = "Pure black; light-independent; no 3D shading or rim light"
    scene["project"] = "When the Sky Clears"
    scene["scope"] = "ONE STILL FRAME ONLY; no scrolling test or full trailer render"
    scene["approval"] = "PROVISIONAL still direction. Await Conrad's still-frame approval before five-second scrolling test."
    scene["reference_status"] = "Approved ink-and-wash text found; preceding approved image pixels unavailable. Handoff source/image1.png inspected as provisional atmosphere reference."
    scene.frame_set(1)
    bpy.context.view_layer.update()
    note = bpy.data.texts.new("START HERE | v012 still review")
    note.write("ONE representative 4K village still. Original v010/v011 sources and movies preserved.\n"
               "Four independent painted depth planes using three built-in GPT imagegen sources, plus editable native GP children.\n"
               "Only frame 1 exists in this scene. No gait, acting, scrolling or full-length render is approved by this still.\n"
               "Exact approved ink-and-wash image could not be retrieved; this direction remains provisional.\n"
               "Paint rasters are 1672 x 941; the native composite render is 3840 x 2160. This is not native 4K source painting.\n"
               "After still approval: FIVE-second scrolling review, then wait for scrolling approval before any new 100-second render.\n")
    output = ROOT / "shots/world/WTSC_Village_Still_Review_v012.blend"
    assert not output.exists(), output
    # Write only the review scene and its dependencies; original scene/file stays intact.
    bpy.data.libraries.write(str(output), {scene, note}, path_remap="RELATIVE", fake_user=True, compress=True)
    evidence = {
        "source_preserved": source_path,
        "output": str(output),
        "scene": scene.name,
        "resolution": [3840, 2160],
        "frame_range": [scene.frame_start, scene.frame_end],
        "objects": [{"name": o.name, "type": o.type, "location": list(o.location),
                     "dimensions": list(o.dimensions)} for o in scene.objects],
        "images": [{"name": im.name, "size": list(im.size), "packed": bool(im.packed_file)}
                   for im in bpy.data.images if im.filepath and "village_lookdev" in im.filepath],
        "animation": "None; review frame only",
        "approval": "Pending still-frame review",
    }
    (NOTES / "native_assembly_v012.json").write_text(json.dumps(evidence, indent=2))
    bpy.context.window.scene = previous_scene
    print(json.dumps(evidence))


main()
