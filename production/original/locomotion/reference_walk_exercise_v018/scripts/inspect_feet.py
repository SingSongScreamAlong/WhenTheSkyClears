import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];sys.path.insert(0,str(P/'scripts'));import rig_pose_api as api
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'characters/rig_correctives_v017/native/WTSC_Painted_Rig_Control_Asset_v017.blend'),load_ui=False,use_scripts=False)
r,c=api.initialize_from_scene();rig=r['BOY'];rig.parent.matrix_world=Matrix.Identity(4);rig.matrix_world=Matrix.Identity(4);bpy.context.view_layer.update()
rows={}
for side in ['near','far']:
 ob=next(o for o in rig.children if o.get('v007_role')=='support_boot' and o.name.endswith(side));bone=rig.data.bones['foot_'+side];d=api.FEET['BOY_'+side]
 A=bone.head_local;rot=Matrix.Rotation(d['flatten_angle'],4,'Y');verts=[ob.matrix_local@v.co for v in ob.data.vertices];vv=[rot@(v-A) for v in verts];low=min(v.z for v in vv);flat=Matrix.Translation((0,0,-low))@rot@Matrix.Translation(-A)@bone.matrix_local
 transformed=[flat@bone.matrix_local.inverted()@v for v in verts]
 near=[{'index':i,'xyz':list(v)} for i,v in enumerate(transformed) if v.z<.002]
 rows[side]={'name':ob.name,'object_local_matrix':[list(row) for row in ob.matrix_local],'flat_bone':[list(row) for row in flat],'vertices':[[*v] for v in transformed],'sole_2mm':near,'source_recipe':d}
(P/'evidence/foot_geometry_inspection.json').write_text(json.dumps(rows,indent=2));print(json.dumps({s:{'name':x['name'],'sole_2mm':x['sole_2mm']} for s,x in rows.items()}))
