import bpy,json,time
from pathlib import Path
P=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Painted_Character_Look_STUDY_v040.blend'),load_ui=False,use_scripts=False);S=bpy.context.scene;S.render.threads_mode='FIXED';S.render.threads=2;S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG';records=[];start=time.time()
for view,cam,size in [('CLOSE','V024 | CLOSE portrait',(480,720)),('SHOT','V020 | CHILD | SHOT',(1280,720))]:
 S.camera=bpy.data.objects[cam];S.render.resolution_x,S.render.resolution_y=size;folder=P/'previews'/view;folder.mkdir(exist_ok=True)
 for f in range(1,95):
  out=folder/f'{f:04d}.png';reused=out.exists()
  if not reused:S.frame_set(f);S.render.filepath=str(out);bpy.ops.render.render(write_still=True)
  records.append({'view':view,'frame':f,'size':size,'same_native_pose_proof_reused':reused});print('V040_MOTION',view,f,round(time.time()-start,1),flush=True)
(P/'evidence/MOTION_RENDER_RECORD.json').write_text(json.dumps({'records':records,'total_native_images':len(records),'threads':2,'elapsed_seconds':time.time()-start,'scope':'Actual isolated painted character motion; original body/cloth/root clock, three native cycles plus closing bookend. Not an AI-generated animation.'},indent=2));print('V040_MOTION_COMPLETE',flush=True)
