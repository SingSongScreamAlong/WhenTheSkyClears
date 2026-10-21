import bpy,json,time
from pathlib import Path
P=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Neck_Collar_Connection_Candidate_v041.blend'),load_ui=False,use_scripts=False);S=bpy.context.scene;S.render.threads_mode='FIXED';S.render.threads=2;S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG';start=time.time();records=[]
for view,cam,size in [('CLOSE','V024 | CLOSE portrait',(480,720)),('SHOT','V020 | CHILD | SHOT',(1280,720))]:
 S.camera=bpy.data.objects[cam];S.render.resolution_x,S.render.resolution_y=size;folder=P/'previews'/('CANDIDATE_'+view)
 for f in range(1,64):
  out=folder/f'{f:04d}.png';reused=out.exists()
  if not reused:S.frame_set(f);S.render.filepath=str(out);bpy.ops.render.render(write_still=True)
  records.append({'view':view,'frame':f,'size':size,'same_final_proof_reused':reused});print('V041_MOTION',view,f,round(time.time()-start,1),flush=True)
(P/'evidence/MOTION_RENDER_RECORD.json').write_text(json.dumps({'records':records,'unique_native_frames':len(records),'source_range':[1,63],'fps':30,'threads':2,'elapsed_seconds':time.time()-start,'scope':'Two actual native cycles plus closing pose, fixed preferred movement; no production/world render.'},indent=2));print('V041_MOTION_COMPLETE',flush=True)
