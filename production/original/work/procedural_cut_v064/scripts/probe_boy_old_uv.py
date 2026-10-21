import bpy,json,numpy as np
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE');O=R/'work/procedural_cut_v064'
bpy.ops.wm.open_mainfile(filepath=str(R/'work/color_arc_v063/native/WTSC_Shared_Color_To_Charcoal_v063.blend'),load_ui=False,use_scripts=False)
rows=[]
for ob in bpy.data.objects:
 if ob.type!='MESH' or 'head' not in ob.name.lower() or 'boy' not in ob.name.lower():continue
 mesh=ob.data;vs=np.array([list(v.co) for v in mesh.vertices]);row=dict(name=ob.name,uv_layers=[u.name for u in mesh.uv_layers],bounds=[vs.min(axis=0).tolist(),vs.max(axis=0).tolist()],material=[m.name if m else None for m in mesh.materials],parent=getattr(ob.parent,'name',None),maps=[])
 for uv in mesh.uv_layers:
  X=np.array([[v.uv.x,v.uv.y,1.] for v in uv.data]);Y=np.array([[mesh.vertices[l.vertex_index].co.x,mesh.vertices[l.vertex_index].co.z] for l in mesh.loops]);A=np.linalg.lstsq(X,Y,rcond=None)[0]
  row['maps'].append(dict(uv=uv.name,to_local_xz_affine_rows=A.T.tolist(),max_residual=float(np.abs(X@A-Y).max()),uv_min=X[:,:2].min(axis=0).tolist(),uv_max=X[:,:2].max(axis=0).tolist()))
 rows.append(row)
(O/'evidence/BOY_OLD_UV_PROBE.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows),flush=True)
