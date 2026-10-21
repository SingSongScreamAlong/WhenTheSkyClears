import bpy
import json

data = bpy.data.grease_pencils.new("BrushInputScratch")
obj = bpy.data.objects.new("BrushInputScratch", data)
bpy.context.scene.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
layer = data.layers.new("Input Test", set_active=True)
frame = layer.frames.new(1)
drawing = frame.drawing

report = {
    "version": bpy.app.version_string,
    "background": bpy.app.background,
    "window": bool(bpy.context.window),
    "screen": bool(bpy.context.screen),
    "area": str(bpy.context.area.type) if bpy.context.area else None,
    "gp_data_type": data.bl_rna.identifier,
    "drawing_methods": [n for n in dir(drawing) if n in ("add_strokes", "remove_strokes", "resize_strokes", "strokes")],
    "strokes_type": str(type(drawing.strokes)),
    "stroke_collection_methods": [n for n in dir(drawing.strokes) if not n.startswith("_")],
    "gpencil_paint_tool_settings": bool(bpy.context.tool_settings.gpencil_paint),
    "brushes": [(b.name, b.use_paint_grease_pencil) for b in bpy.data.brushes],
    "brush_operator_poll_before_mode": bpy.ops.grease_pencil.brush_stroke.poll(),
}
try:
    bpy.ops.object.mode_set(mode="PAINT_GREASE_PENCIL")
    report["paint_mode"] = obj.mode
    report["brush_operator_poll_after_mode"] = bpy.ops.grease_pencil.brush_stroke.poll()
    report["paint_brush"] = getattr(bpy.context.tool_settings.gpencil_paint.brush, "name", None)
    report["screen_areas"] = [(a.type, a.width, a.height, [(r.type, r.width, r.height) for r in a.regions]) for a in bpy.context.screen.areas]
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            region = next((r for r in area.regions if r.type == "WINDOW"), None)
            if region:
                with bpy.context.temp_override(window=bpy.context.window, area=area, region=region):
                    report["brush_operator_poll_view3d_override"] = bpy.ops.grease_pencil.brush_stroke.poll()
                    report["override_mode"] = bpy.context.mode
            break
except Exception as exc:
    report["paint_mode_error"] = repr(exc)

print("GP_INSPECTION_JSON", json.dumps(report, default=str))
