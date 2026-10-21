import bpy,json,hashlib
from pathlib import Path
O=Path(__file__).parent;P=Path(r'WTSC_LOCAL_WORKSPACE\work\world_minimum_v058\WTSC_World_Development_v058_Packed.blend')
hash_before=hashlib.sha256(P.read_bytes()).hexdigest();assert hash_before=='13c2aee075315131eac6f85d9d726b766051a84edffa961f4ec38ecf7029a890'
bpy.ops.wm.open_mainfile(filepath=str(P),load_ui=False,use_scripts=False)
s=bpy.data.scenes['WTSC_WORLD_FOREGROUND_v058d'];assert len(s.objects)==430;assert len(bpy.data.actions)==41;assert (s.frame_start,s.frame_end,s.render.fps)==(1,2400,24)
master=bpy.data.scenes['WTSC_MASTER_4K_106S_v040'];assert (master.frame_start,master.frame_end,master.render.fps)==(1,2544,24)
assert all(im.packed_file for im in bpy.data.images if im.source=='FILE' and im.type!='RENDER_RESULT')
paths={sc.name:sc.render.filepath for sc in bpy.data.scenes};print('DELIVERY_RENDER_PATHS',json.dumps(paths),flush=True)
assert all(sc.render.filepath.replace(chr(92),'/').startswith('//renders_v058/') for sc in bpy.data.scenes)
assert hashlib.sha256(P.read_bytes()).hexdigest()==hash_before
(O/'DELIVERED_NATIVE_OPEN_VERIFIED.json').write_text(json.dumps({'exact_project_file':str(P),'sha256':hash_before,'opened_successfully_in_blender':True,'active_world_objects':len(s.objects),'actions':len(bpy.data.actions),'all_file_images_packed':True,'world_frames':[1,2400],'master_frames':[1,2544],'fps':24,'native_file_unchanged':True,'rendered_or_saved_by_this_check':False},indent=2));print('DELIVERED_NATIVE_COLD_OPEN_OK',flush=True)
