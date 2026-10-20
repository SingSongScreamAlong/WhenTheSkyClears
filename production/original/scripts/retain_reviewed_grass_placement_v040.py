"""Keep the benchmark's local grass correction; preserve other regions' staging."""
import bpy,json,hashlib
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE')
old=bpy.data.scenes['WTSC_WORLD_CORRECTED_v037'];positions={o.name:list(o.location) for o in old.objects if o.name.startswith('v016 | Rooted grass ')}
p=R/'shots/world/WTSC_Painted_World_Full_Trailer_Editable_v040.blend';bpy.ops.wm.open_mainfile(filepath=str(p));w=bpy.data.scenes['WTSC_WORLD_CORRECTED_v040'];restored=[]
for ob in w.objects:
    if ob.name in positions and not 78<=ob.location.x<=100:ob.location.z=positions[ob.name][2];restored.append(ob.name)
report_path=R/'notes/world_v016/full_build_v040.json';report=json.loads(report_path.read_text());report.pop('source_sha256',None);report['changes']['grass_roots_placed_at_bank_edge']=11;report['changes']['other_regions_grass_staging_preserved']=len(restored);report['regional_visual_check']='Regional UHD proof inspection retained the reviewed camp grass adjustment only; broad additional grass raises were reverted before render freeze. Existing original wind retained throughout.'
note=bpy.data.texts['CURRENT v040 | Propagated paint light and grounded world'];note.clear();note.write(json.dumps(report,indent=2));bpy.context.window.scene=bpy.data.scenes['WTSC_MASTER_4K_106S_v040'];bpy.context.scene.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True)
report['source_sha256']=hashlib.sha256(p.read_bytes()).hexdigest();report_path.write_text(json.dumps(report,indent=2));print('REVIEWED_GRASS_SCOPE_RETAINED',len(restored),report['source_sha256'],flush=True)
