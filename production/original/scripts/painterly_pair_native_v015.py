"""Native editable GP outline plus registered, vector-clipped painted fill."""
import bpy
import json


def apply_painterly_pair(scene, root):
    recipe = json.loads((root / "characters/Pair_Painterly_Near_Age_Vector_v015.json").read_text())
    pair = next(o for o in scene.objects if o.type == "GREASEPENCIL")
    drawing = pair.data.layers[0].frames[0].drawing
    if len(drawing.attributes["cyclic"].data) > 1:
        drawing.remove_strokes(indices=list(range(1, len(drawing.attributes["cyclic"].data))))
    points = recipe["points"]
    drawing.resize_strokes(sizes=[len(points)], indices=[0])
    drawing.attributes["position"].data.foreach_set("vector", [c for p in points for c in p])
    drawing.attributes["opacity"].data.foreach_set("value", [1.] * len(points))
    drawing.attributes["radius"].data.foreach_set("value", [.0005] * len(points))
    drawing.attributes["cyclic"].data[0].value = True
    drawing.attributes["fill_id"].data[0].value = 0
    drawing.attributes["material_index"].data[0].value = 0
    drawing.tag_positions_changed()
    pair.data.layers[0].name = "HELD | near-age painted children | native vector boundary"
    pair["style"] = "Near-black charcoal paint, restrained gray detail, tiny nonglowing off-white eye marks"
    pair["proportions"] = "Near same age; boy 1.45m, girl approximately 1.37m in this drawing"
    pair["performance"] = "Held pose; no gait or acting animation, per explicit user reply"
    pair["painted_fill"] = "Registered bitmap fill clipped to matching vector polygon, parented to native GP boundary"
    mesh = bpy.data.meshes.new("v015 | Matched painted fill vector mask")
    mesh.from_pydata([(p[0], -.362, p[2]) for p in points], [], [tuple(range(len(points)))])
    uv = mesh.uv_layers.new(name="Registered original painted drawing")
    for loop, co in zip(uv.data, recipe["uv"]):
        loop.uv = co
    obj = bpy.data.objects.new("v015 | Near-black painted fill | GP vector clipped", mesh)
    pair.users_collection[0].objects.link(obj)
    obj.parent = pair
    image = bpy.data.images.load(recipe["source"], check_existing=False)
    image.pack()
    mat = bpy.data.materials.new("v015 | Subtle charcoal painting and soft white eyes")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = image
    tex.extension = "CLIP"
    gray = nt.nodes.new("ShaderNodeHueSaturation")
    gray.inputs["Saturation"].default_value = 0
    gray.inputs["Value"].default_value = .80
    nt.links.new(tex.outputs["Color"], gray.inputs["Color"])
    emit = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(gray.outputs[0], emit.inputs[0])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(tex.outputs["Alpha"], mix.inputs[0])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(emit.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs[0])
    mat.surface_render_method = "DITHERED"
    mesh.materials.append(mat)
    obj["purpose"] = "Paint inside the editable GP silhouette. This mesh is a flat vector mask, not a modeled 3D child."
    return recipe
