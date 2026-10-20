import bpy,json,time,sys
from pathlib import Path
P=Path(__file__).resolve().parents[1];mode=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'proof';start=time.time();records=[]
bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Full_Color_Coat_Continuity_Rough_v039.blend'),load_ui=False,use_scripts=False);S=bpy.context.scene;S.render.threads_mode='FIXED';S.render.threads=2;S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGBA'
for view,cam,size,frames in [('CLOSE','V024 | CLOSE portrait',(480,720),[1,4,8,11,13,17,20,24,27,31,32]),('SHOT','V020 | CHILD | SHOT',(1280,720),[1,4,11,20,27,32])]:
 S.camera=bpy.data.objects[cam];S.render.resolution_x,S.render.resolution_y=size;dest=P/'previews'/view;dest.mkdir(exist_ok=True)
 for f in frames if mode=='proof' else range(1,95):
  out=dest/f'{f:04d}.png'
  if mode!='proof' and out.exists():records.append({'view':view,'frame':f,'file':str(out.relative_to(P)),'reused_same_native_frame_and_camera_proof':True});continue
  S.frame_set(f);S.render.filepath=str(out);bpy.ops.render.render(write_still=True);records.append({'view':view,'frame':f,'file':str(out.relative_to(P)),'size':size,'reused_same_native_frame_and_camera_proof':False});print('V039_RENDER',mode,view,f,round(time.time()-start,1),flush=True)
report={'scope':'Actual native isolated coat continuity review. Body and full-color palette unchanged. No production or world render.','mode':mode,'frames':records,'threads':2,'fps':30,'source_cycle':[1,32],'period':31,'native_frame_range':[1,94] if mode!='proof' else None,'elapsed_seconds':time.time()-start};(P/f'evidence/{mode.upper()}_RENDER_RECORD.json').write_text(json.dumps(report,indent=2));print('V039_RENDER_COMPLETE',mode,len(records),flush=True)
