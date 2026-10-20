import bpy,json,time
from pathlib import Path
P=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Painted_Character_Look_STUDY_v040.blend'),load_ui=False,use_scripts=False);S=bpy.context.scene;S.render.threads_mode='FIXED';S.render.threads=2;S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG';records=[];start=time.time()
for view,cam,size,frames in [('HERO','V024 | CLOSE portrait',(960,1440),[1]),('CLOSE','V024 | CLOSE portrait',(480,720),[1,4,11,20,27,32]),('SHOT','V020 | CHILD | SHOT',(1280,720),[1,20])]:
 S.camera=bpy.data.objects[cam];S.render.resolution_x,S.render.resolution_y=size;folder=P/'previews'/view;folder.mkdir(exist_ok=True)
 for f in frames:
  S.frame_set(f);S.render.filepath=str(folder/f'{f:04d}.png');bpy.ops.render.render(write_still=True);records.append({'view':view,'frame':f,'size':size});print('V040_NATIVE_PROOF',view,f,flush=True)
(P/'evidence/NATIVE_PROOF_RENDER_RECORD.json').write_text(json.dumps({'actual_native_renders':records,'count':len(records),'threads':2,'elapsed_seconds':time.time()-start,'scope':'Painted design transfer study; not production or animation acceptance.'},indent=2))
