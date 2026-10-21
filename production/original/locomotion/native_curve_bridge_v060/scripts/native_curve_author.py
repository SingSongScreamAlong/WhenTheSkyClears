"""Task-local Blender Grease Pencil stroke authoring operator.

This uses Blender's editable drawing API. It does not synthesize pointer events,
install an add-on, or change the DCC-CUA provider. Register for one Blender
session with register(), and unregister() before reuse if needed.
"""

import json
import math

import bpy


class WTSC_OT_add_native_curve(bpy.types.Operator):
    bl_idname = "wtsc.add_native_curve"
    bl_label = "Add Isolated Native Curve"
    bl_description = "Author one editable Grease Pencil stroke from explicit coordinates"
    bl_options = {"REGISTER", "UNDO"}

    points_json: bpy.props.StringProperty(name="Points JSON")
    base_radius: bpy.props.FloatProperty(name="Base Radius", default=0.045, min=0.001, max=0.3)

    @classmethod
    def poll(cls, context):
        obj = context.view_layer.objects.active
        return bool(obj and obj.type == "GREASEPENCIL" and obj.data.layers.active)

    def execute(self, context):
        try:
            raw = json.loads(self.points_json)
            if not isinstance(raw, list) or not 2 <= len(raw) <= 4096:
                raise ValueError("points must be a list of 2 to 4096 samples")
            positions = []
            for sample in raw:
                if not isinstance(sample, (list, tuple)) or len(sample) != 3:
                    raise ValueError("every sample must contain x, y, z")
                coords = tuple(float(value) for value in sample)
                if not all(math.isfinite(value) and abs(value) <= 10000 for value in coords):
                    raise ValueError("sample coordinates must be finite and bounded")
                positions.append(coords)
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}

        obj = context.view_layer.objects.active
        layer = obj.data.layers.active
        frame = layer.current_frame()
        if frame is None:
            frame = layer.frames.new(context.scene.frame_current)
        drawing = frame.drawing
        old_count = len(drawing.strokes)
        drawing.add_strokes([len(positions)])
        stroke = drawing.strokes[old_count]
        stroke.material_index = 0
        for point, coords in zip(stroke.points, positions):
            point.position = coords
            point.radius = self.base_radius
            point.opacity = 1.0
        if hasattr(drawing, "tag_positions_changed"):
            drawing.tag_positions_changed()
        obj.data.update_tag()
        return {"FINISHED"}


def register():
    bpy.utils.register_class(WTSC_OT_add_native_curve)


def unregister():
    bpy.utils.unregister_class(WTSC_OT_add_native_curve)
