import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(P/'reference/PREFERRED_MOVEMENT_v028.blend'),load_ui=False,use_scripts=False);S=bpy.context.scene;rig=bpy.data.objects['LOCO_BOY | RIG'];B=json.loads((P/'reference/ORIGINAL_BOY_BOOT_PIVOTS_v018.json').read_text());out={}
for f in [1,4,11,13,17,20,27,29,32]:
    S.frame_set(f);bpy.context.view_layer.update();row={}
    for s in ['near','far']:
        pants=bpy.data.objects['V024 continuous '+s+' trouser drawing'];e=pants.evaluated_get(bpy.context.evaluated_depsgraph_get());E=sum((e.matrix_world@v.co for v in e.data.vertices[-7:]),Vector())/7;F=rig.matrix_world@rig.pose.bones['foot_'+s].matrix;R=F.to_3x3()@Matrix(B[s]['flat_bone']).to_3x3().inverted();a=math.atan2(R[0][2],R[0][0]);rel=Matrix.Rotation(-a,4,'Y')@(E-F.translation);row[s]={'cuff_endpoint_world':list(E),'relative_to_flat_shoe_ankle':list(rel)}
    out[f]=row
(P/'evidence/ORIGINAL_CUFF_TO_SHOE_RELATION.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
