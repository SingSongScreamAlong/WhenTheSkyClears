import bpy,json,math,csv,subprocess,os
from pathlib import Path
P=Path(__file__).resolve().parents[1];s=bpy.data.scenes['FXv010 | joined rupture and ground dust'];bpy.context.window.scene=s;r=bpy.data.objects['FXv010 | fixed impact anchor and timing'];o=bpy.data.objects['FXv010 | retimeable finite dust VDB'];folder=P/'previews/retime_h';folder.mkdir(exist_ok=True);rows=[]
for start,frame,name in [(7,20,'baseline'),(107,120,'offset100')]:
    tasks=csv.reader(subprocess.check_output([r'C:\Windows\System32\tasklist.exe','/FI','IMAGENAME eq blender.exe','/FO','CSV','/NH'],text=True,creationflags=subprocess.CREATE_NO_WINDOW).splitlines());others=[int(t[1]) for t in tasks if t and t[0].lower()=='blender.exe' and int(t[1]) not in [39896,os.getpid()]]
    if others:raise RuntimeError('Render deferred for other Blender jobs '+str(others))
    r['start_frame']=float(start);r.update_tag(refresh={'OBJECT'});s.frame_set(frame);bpy.context.view_layer.update();ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());ev.data.grids.load();row={'start':start,'frame':frame,'age':r['age'],'volume_offset':ev.data.frame_offset,'grids_frame':ev.data.grids.frame,'grid_file':ev.data.grids.frame_filepath};rows.append(row);assert row['grid_file'].endswith('fluid_data_0020.vdb'),row;s.render.filepath=str(folder/(name+'.png'));bpy.ops.render.render(write_still=True,scene=s.name)
r['start_frame']=7;r.update_tag(refresh={'OBJECT'});s.frame_set(20);bpy.context.view_layer.update();assert [x['volume_offset'] for x in rows]==[0,-100],rows
(P/'evidence/native_volume_retime_h.json').write_text(json.dumps(rows,indent=2));print('VDB_RETIME_RENDERED',json.dumps(rows),flush=True)
