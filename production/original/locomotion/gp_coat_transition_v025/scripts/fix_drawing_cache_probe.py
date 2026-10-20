import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parents[1];F=P/'native/WTSC_GP_Coat_Transition_v025.blend';bpy.ops.wm.open_mainfile(filepath=str(F),load_ui=False,use_scripts=False);S=bpy.context.scene;o=bpy.data.objects['V025 | COAT drawings | editable GP']
report={'engine':S.render.engine,'object_hide_render':o.hide_render,'layer':[],'materials':[]}
for l in o.data.layers:
    report['layer'].append({'name':l.name,'opacity':l.opacity,'hide':l.hide,'functions':[n for n in dir(l.frames[0].drawing) if 'tag' in n or 'tri' in n]})
    for f in l.frames:
        d=f.drawing
        if hasattr(d,'tag_positions_changed'):d.tag_positions_changed()
        for s in d.strokes:
            if s.cyclic:
                s.fill_opacity=1.;s.fill_color=o.data.materials[s.material_index].grease_pencil.fill_color
for m in o.data.materials:
    g=m.grease_pencil;report['materials'].append({'name':m.name,'fill':g.show_fill,'stroke':g.show_stroke,'mode':g.mode,'fill_style':g.fill_style,'color':list(g.fill_color),'enum_mode':[(e.identifier,e.name) for e in g.bl_rna.properties['mode'].enum_items]})
o.data.update_tag();S.frame_set(21);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(F),compress=True);S.camera=bpy.data.objects['V024 | CLOSE portrait'];S.render.resolution_x=400;S.render.resolution_y=600;S.render.filepath=str(P/'previews/GP_CACHE_PROBE_0021.png');bpy.ops.render.render(write_still=True)
(P/'evidence/GP_CACHE_AND_MATERIAL_PROBE.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
