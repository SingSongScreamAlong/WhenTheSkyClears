import bpy,json,hashlib
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE')
assert Path(bpy.data.filepath).name=='WTSC_Full_Knockout_Trailer_Editable_v038.blend'
w=bpy.data.scenes['WTSC_WORLD_CORRECTED_v037'];e=bpy.data.scenes['WTSC_FULL_FILM_KNOCKOUT_v037'];m=bpy.data.scenes['WTSC_MASTER_4K_106S_v038']
w.render.filepath='//../../renders/world_v016/WTSC_Corrected_World_Native_v038.mp4';e.render.filepath='//../../renders/world_v016/WTSC_Full_Knockout_Picture_Native_v038.mp4'
bpy.context.window.scene=m;m.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
p=R/'notes/world_v016/final_editable_v038.json';report=json.loads(p.read_text());report['editable_sha256']=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest();report['native_output_paths']={'world':w.render.filepath,'picture':e.render.filepath,'master':m.render.filepath};report['path_scope']='Versioned default exports avoid overwriting earlier world/movie files.';p.write_text(json.dumps(report,indent=2));print('VERSIONED_NATIVE_PATHS_SAVED',flush=True)
