import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(P/'reference/PREFERRED_MOVEMENT_v028.blend'),load_ui=False,use_scripts=False)
S=bpy.context.scene;rig=bpy.data.objects['LOCO_BOY | RIG'];B=json.loads((P/'reference/ORIGINAL_BOY_BOOT_PIVOTS_v018.json').read_text());report={'version':bpy.app.version_string,'source':'PREFERRED_MOVEMENT_v028.blend','no_render_or_native_write':True,'boots':{},'frames':{}}
for side,d in B.items():
    o=bpy.data.objects[d['object']];m=o.data
    report['boots'][side]={'name':o.name,'parent':o.parent.name if o.parent else None,'parent_type':o.parent_type,'parent_bone':o.parent_bone,'matrix_world':[list(r) for r in o.matrix_world],'vertices':len(m.vertices),'faces':len(m.polygons),'modifiers':[{'name':x.name,'type':x.type,'object':x.object.name if hasattr(x,'object') and x.object else None} for x in o.modifiers],'shape_keys':[k.name for k in m.shape_keys.key_blocks] if m.shape_keys else [],'groups':[g.name for g in o.vertex_groups],'uv_layer':m.uv_layers.active.name if m.uv_layers.active else None,'materials':[{'name':ma.name,'images':[{'name':n.image.name,'path':n.image.filepath,'packed':bool(n.image.packed_file)} for n in ma.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]} for ma in m.materials if ma and ma.use_nodes]}
for f in [1,4,11,13,17,20,27,29,32]:
    S.frame_set(f);bpy.context.view_layer.update();row={}
    for side,d in B.items():
        o=bpy.data.objects[d['object']];e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());V=[e.matrix_world@v.co for v in e.data.vertices];bone=rig.matrix_world@rig.pose.bones['foot_'+side].matrix;F=Matrix(d['flat_bone']);R=bone.to_3x3()@F.to_3x3().inverted();a=math.atan2(R[0][2],R[0][0]);A=bone.translation;inv=Matrix.Rotation(-a,4,'Y');N=[inv@(v-A) for v in V];row[side]={'pitch_deg':math.degrees(a),'ankle':list(A),'sole_min_z':min(v.z for v in V),'bounds_x':[min(v.x for v in V),max(v.x for v in V)],'flat_relative_bounds_xz':[[min(v[k] for v in N),max(v[k] for v in N)] for k in [0,2]],'normalized_vertices':[list(v) for v in N]}
    report['frames'][f]=row
for side in B:
    first=report['frames'][1][side]['normalized_vertices'];report['boots'][side]['maximum_nonrigid_change_m']=max(math.dist(v,w) for row in report['frames'].values() for v,w in zip(first,row[side]['normalized_vertices']))
(P/'evidence/ACTUAL_V028_FOOTWEAR_AUDIT.json').write_text(json.dumps(report,indent=2));print(json.dumps({'version':report['version'],'boots':report['boots'],'frame1':{s:{k:v for k,v in d.items() if k!='normalized_vertices'} for s,d in report['frames'][1].items()}},indent=2))
