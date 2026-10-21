import bpy,json,time
from pathlib import Path
P=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(P/'reference/PRESERVED_v035.blend'),load_ui=False,use_scripts=False);S=bpy.context.scene;S.render.threads_mode='FIXED';S.render.threads=2;S.render.resolution_percentage=100;t=time.time();records=[]
for view,cam,size in [('CLOSE','V024 | CLOSE portrait',(480,720)),('SHOT','V020 | CHILD | SHOT',(1280,720))]:
 S.camera=bpy.data.objects[cam];S.render.resolution_x,S.render.resolution_y=size;folder=P/'previews'/('BASE_'+view);folder.mkdir(exist_ok=True)
 for f in range(1,64):
  S.frame_set(f);S.render.filepath=str(folder/f'{f:04d}.png');bpy.ops.render.render(write_still=True)
 records.append({'view':view,'size':size,'frames':[1,63]});print('BASELINE_VIEW_COMPLETE',view,round(time.time()-t,1),flush=True)
(P/'evidence/BASELINE_RENDER.json').write_text(json.dumps({'actual_frames':126,'fps':30,'records':records,'elapsed_s':time.time()-t,'threads':2,'scope':'Bounded two-cycle native movement diagnostic; source unchanged.'},indent=2));print('BASELINE_COMPLETE',flush=True)
