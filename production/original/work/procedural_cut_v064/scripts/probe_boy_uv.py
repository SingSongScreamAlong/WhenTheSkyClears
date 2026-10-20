import bpy,json,numpy as np
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE');O=R/'work/procedural_cut_v064'
bpy.ops.wm.open_mainfile(filepath=str(R/'work/color_arc_v063/native/WTSC_Shared_Color_To_Charcoal_v063.blend'),load_ui=False,use_scripts=False)
ob=bpy.data.objects['V044 BOY | head'];mesh=ob.data
out=dict(object=ob.name,uv_layers=[u.name for u in mesh.uv_layers],active_uv=mesh.uv_layers.active.name,materials=[m.name if m else None for m in mesh.materials],object_materials=[s.material.name if s.material else None for s in ob.material_slots],maps=[])
(O/'evidence/BOY_UV_PROBE.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
src=next((uv for uv in mesh.uv_layers if 'original' in uv.name.lower()),None)
assert src
X=np.array([[v.uv.x,v.uv.y,1.] for v in src.data])
for uv in mesh.uv_layers:
 Y=np.array([[v.uv.x,v.uv.y] for v in uv.data]);A=np.linalg.lstsq(X,Y,rcond=None)[0];err=np.abs(X@A-Y)
 out['maps'].append(dict(from_uv=src.name,to_uv=uv.name,affine_output_rows=A.T.tolist(),max_residual=float(err.max()),source_min=X[:,:2].min(axis=0).tolist(),source_max=X[:,:2].max(axis=0).tolist()))
(O/'evidence/BOY_UV_PROBE.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
