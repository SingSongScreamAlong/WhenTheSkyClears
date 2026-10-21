import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Live_Limb_Continuity_v036.blend'),load_ui=False,use_scripts=False);S=bpy.context.scene;S.render.threads_mode='FIXED';S.render.threads=2;S.render.resolution_percentage=100
for view,cam,size in [('CLOSE','V024 | CLOSE portrait',(480,720)),('SHOT','V020 | CHILD | SHOT',(1280,720))]:
 S.camera=bpy.data.objects[cam];S.render.resolution_x,S.render.resolution_y=size;p=P/'previews'/('FIRST_'+view);p.mkdir(exist_ok=True)
 for f in [1,4,11,20,27]:S.frame_set(f);S.render.filepath=str(p/f'{f:04d}.png');bpy.ops.render.render(write_still=True)
rig=bpy.data.objects['LOCO_BOY | RIG'];report={}
for side in ['near','far']:
 o=bpy.data.objects['V007_BOY | articulated drawn hand '+side];B=rig.data.bones['hand_'+side].matrix_local.inverted();report[side]={'bone_relative_coords':[list(B@v.co) for v in o.data.vertices],'shape_keys':[k.name for k in o.data.shape_keys.key_blocks],'material':o.material_slots[0].material.name}
o=bpy.data.objects['V033 | near | canonical painted shoe'];report['shoe']={'coords':[list(v.co) for v in o.data.vertices],'polygons':[list(p.vertices) for p in o.data.polygons]};(P/'evidence/HAND_AND_SHOE_GEOMETRY.json').write_text(json.dumps(report,indent=2));print('V036_FIRST_STILLS_COMPLETE',flush=True)
