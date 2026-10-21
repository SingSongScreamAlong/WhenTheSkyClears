"""Bounded native refinements shared by the v014 still and contact study."""
import bpy
from mathutils import Vector


def ground_contacts(scene, measured_soles=None):
    pair = next(o for o in scene.objects if o.type == "GREASEPENCIL")
    assert not pair.animation_data
    before = list(pair.location)
    pair.location.z -= .075
    # Existing contour measurements: one low sole region for each held shoe.
    soles = [
        ("Boy back forefoot", -.467, .007919, .155),
        ("Boy front sole", -.198, .006335, .175),
        ("Girl back sole", .128, 0, .205),
        ("Girl front heel", .429, .003167, .125),
    ]
    if measured_soles:
        soles = [("Held shoe " + str(i+1), p["x"], p["z"], p["width"]) for i,p in enumerate(measured_soles)]
    collection = bpy.data.collections.new("v014 | Drawn ground contact marks")
    scene.collection.children.link(collection)
    mat = bpy.data.materials.new("v014 | Soft painted contact | ground only")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    uv = nt.nodes.new("ShaderNodeTexCoord")
    dist = nt.nodes.new("ShaderNodeVectorMath")
    dist.operation = "DISTANCE"
    dist.inputs[1].default_value = (.5, .5, 0)
    nt.links.new(uv.outputs["UV"], dist.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.label = "Small contact wash, not a light or shading on the children"
    ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
    for idx, (position, opacity) in enumerate([(0, .70), (.28, .58), (.43, .10), (.5, 0)]):
        el = ramp.color_ramp.elements[0] if idx == 0 else ramp.color_ramp.elements.new(position)
        el.position = position
        el.color = (opacity, opacity, opacity, 1)
    nt.links.new(dist.outputs["Value"], ramp.inputs[0])
    emit = nt.nodes.new("ShaderNodeEmission")
    emit.inputs[0].default_value = (.012, .006, .002, 1)
    transparent = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(ramp.outputs[0], mix.inputs[0])
    nt.links.new(transparent.outputs[0], mix.inputs[1])
    nt.links.new(emit.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs[0])
    mat.surface_render_method = "DITHERED"
    report = []
    for name, x, z, width in soles:
        # 2D painted ground cue immediately behind the drawing, not a simulated
        # cast shadow or evidence of a modeled ground surface.
        center = Vector((pair.location.x + x, -.35, pair.location.z + z - .007))
        h = .025
        coords = [(-width/2, 0, -h/2), (width/2, 0, -h/2),
                  (width/2, 0, h/2), (-width/2, 0, h/2)]
        mesh = bpy.data.meshes.new("v014 | " + name)
        mesh.from_pydata([tuple(center + Vector(p)) for p in coords], [], [(0, 1, 2, 3)])
        uv_layer = mesh.uv_layers.new(name="Contact wash UV")
        for loop, co in zip(uv_layer.data, [(0, 0), (1, 0), (1, 1), (0, 1)]):
            loop.uv = co
        obj = bpy.data.objects.new("v014 | Ground contact | " + name, mesh)
        collection.objects.link(obj)
        mesh.materials.append(mat)
        obj["purpose"] = "Static drawn contact treatment on the painted path. No child shading or animated foot constraint."
        report.append({"shoe": name, "contact_center": list(center), "width_m": width})
    assert all(tuple(m.grease_pencil.fill_color) == (0, 0, 0, 1) for m in pair.data.materials)
    assert all(not layer.use_lights for layer in pair.data.layers)
    return {"pair_location_before": before, "pair_location_after": list(pair.location),
            "vertical_change_m": -.075, "pose_points_changed": False,
            "contact_type": "Four native soft painted ground marks behind the four held soles", "soles": report}


def detail_tile(obj, path, bounds, name, feather=.07):
    """Register a newly painted regional tile inside the existing card material.

    Existing alpha/cutout, mesh, camera and depth remain unchanged.
    """
    mat = obj.data.materials[0]
    nt = mat.node_tree
    original = next(n for n in nt.nodes if n.type == "TEX_IMAGE")
    targets = [link.to_socket for link in list(nt.links)
               if link.from_socket == original.outputs["Color"]]
    image = bpy.data.images.load(str(path), check_existing=False)
    image.pack()
    tile = nt.nodes.new("ShaderNodeTexImage")
    tile.image = image
    tile.name = name
    tile.label = "NEW PAINTED REGION | not an upscaled full plate"
    tile.extension = "EXTEND"
    tile.interpolation = "Linear"
    uv = next(n for n in nt.nodes if n.type == "TEX_COORD")
    sub = nt.nodes.new("ShaderNodeVectorMath")
    sub.operation = "SUBTRACT"
    u0, u1, v0, v1 = bounds
    sub.inputs[1].default_value = (u0, v0, 0)
    nt.links.new(uv.outputs["UV"], sub.inputs[0])
    scale = nt.nodes.new("ShaderNodeVectorMath")
    scale.operation = "MULTIPLY"
    scale.inputs[1].default_value = (1/(u1-u0), 1/(v1-v0), 1)
    nt.links.new(sub.outputs["Vector"], scale.inputs[0])
    nt.links.new(scale.outputs["Vector"], tile.inputs["Vector"])
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(scale.outputs["Vector"], sep.inputs[0])
    mins = []
    for channel in ["X", "Y"]:
        inv = nt.nodes.new("ShaderNodeMath")
        inv.operation = "SUBTRACT"
        inv.inputs[0].default_value = 1
        nt.links.new(sep.outputs[channel], inv.inputs[1])
        minimum = nt.nodes.new("ShaderNodeMath")
        minimum.operation = "MINIMUM"
        nt.links.new(sep.outputs[channel], minimum.inputs[0])
        nt.links.new(inv.outputs[0], minimum.inputs[1])
        mins.append(minimum.outputs[0])
    edge = nt.nodes.new("ShaderNodeMath")
    edge.operation = "MINIMUM"
    nt.links.new(mins[0], edge.inputs[0])
    nt.links.new(mins[1], edge.inputs[1])
    fade = nt.nodes.new("ShaderNodeMapRange")
    fade.clamp = True
    fade.interpolation_type = "SMOOTHERSTEP"
    fade.inputs["From Min"].default_value = 0
    fade.inputs["From Max"].default_value = feather
    nt.links.new(edge.outputs[0], fade.inputs["Value"])
    alpha = nt.nodes.new("ShaderNodeMath")
    alpha.operation = "MULTIPLY"
    nt.links.new(fade.outputs[0], alpha.inputs[0])
    nt.links.new(tile.outputs["Alpha"], alpha.inputs[1])
    mix = nt.nodes.new("ShaderNodeMixRGB")
    mix.blend_type = "MIX"
    mix.label = "Regional paint registration with feathered edges"
    nt.links.new(alpha.outputs[0], mix.inputs[0])
    nt.links.new(original.outputs["Color"], mix.inputs[1])
    nt.links.new(tile.outputs["Color"], mix.inputs[2])
    for socket in targets:
        nt.links.new(mix.outputs[0], socket)
    obj["detail_tile"] = str(path)
    obj["detail_tile_source_pixels"] = list(image.size)
    obj["detail_tile_uv_bounds"] = list(bounds)
    return {"object": obj.name, "tile": str(path), "new_painted_pixels": list(image.size),
            "original_full_plate_pixels": list(original.image.size), "uv_bounds": list(bounds),
            "old_region_pixels": [(u1-u0)*original.image.size[0], (v1-v0)*original.image.size[1]],
            "registration": "Native material UV mapping into existing card; original image alpha retained", "feather": feather}
