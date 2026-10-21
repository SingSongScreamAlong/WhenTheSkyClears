import bpy
import hashlib
import json
from pathlib import Path
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
rows=[]
for label, rel, scene_name in [
    ('full_v040', 'shots/world/WTSC_Painted_World_Full_Trailer_Editable_v040.blend', 'WTSC_WORLD_CORRECTED_v040'),
    ('world_v058', 'work/world_minimum_v058/WTSC_World_Development_v058_Packed.blend', 'WTSC_WORLD_FOREGROUND_v058d'),
    ('color_v063', 'work/color_arc_v063/native/WTSC_Shared_Color_To_Charcoal_v063.blend', 'WTSC_SHARED_COLOR_TO_CHARCOAL_v063')]:
    p=ROOT/rel
    h=hashlib.sha256(p.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
    scene=bpy.data.scenes[scene_name]
    bpy.context.window.scene=scene
    samples=[]
    for f in [1,936,937,981,1056,1057,2400]:
        scene.frame_set(f)
        bpy.context.view_layer.update()
        camera=scene.camera.evaluated_get(bpy.context.evaluated_depsgraph_get())
        samples.append({'frame':f,'camera_location':list(camera.matrix_world.translation),
                        'camera_matrix':[list(r) for r in camera.matrix_world],
                        'ortho_scale':camera.data.ortho_scale})
    rows.append({'label':label,'scene':scene_name,'samples':samples,'source_unchanged':h==hashlib.sha256(p.read_bytes()).hexdigest()})
(OUT/'camera_travel_samples.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print('TRAVEL_AUDIT_COMPLETE')
