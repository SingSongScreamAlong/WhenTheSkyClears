import bpy,json,time
from pathlib import Path
P=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Connected_Garment_Retained_Fabric_v037.blend'),load_ui=False,use_scripts=False);S=bpy.context.scene;ctrl=bpy.data.objects['V037 | garment review values | static pose selector'];S.render.threads_mode='FIXED';S.render.threads=2;S.render.resolution_percentage=100;t=time.time();records=[]
for mode,value in [('CONSTRUCTION',0),('PAINTED',1)]:
 ctrl['painted']=value;ctrl.update_tag();bpy.context.view_layer.update()
 for view,cam,size in [('CLOSE','V024 | CLOSE portrait',(480,720)),('SHOT','V020 | CHILD | SHOT',(1280,720))]:
  S.camera=bpy.data.objects[cam];S.render.resolution_x,S.render.resolution_y=size;p=P/'previews'/(mode+'_'+view);p.mkdir(exist_ok=True)
  for f in [1,4,11,20,27]:
   S.frame_set(f);S.render.filepath=str(p/f'{f:04d}.png');bpy.ops.render.render(write_still=True);records.append({'mode':mode,'view':view,'frame':f,'size':size})
 print('V037_VARIANT_COMPLETE',mode,round(time.time()-t,1),flush=True)
(P/'evidence/STILL_RENDER_RECORD.json').write_text(json.dumps({'actual_native_stills':records,'count':len(records),'main_frames':[1,4,11,20],'overlap_frame':27,'threads':2,'elapsed_seconds':time.time()-t,'source':'Unchanged v036 actual saved CLOSE/SHOT frames with matching native cameras, frame numbers and dimensions. No timing/pose edits.','no_movie_or_trailer_render':True},indent=2));print('V037_STILLS_COMPLETE',len(records),flush=True)
