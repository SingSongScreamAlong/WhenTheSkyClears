import bpy,json,time
from pathlib import Path
P=Path(__file__).resolve().parents[1];start=time.time();records=[]
def load(path):
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);S=bpy.context.scene;S.render.threads_mode='FIXED';S.render.threads=2;S.render.resolution_percentage=100;return S
def render(S,mode,f,cam,size):
 S.camera=bpy.data.objects[cam];S.render.resolution_x,S.render.resolution_y=size;S.frame_set(f);p=P/'previews'/mode;p.mkdir(exist_ok=True);S.render.filepath=str(p/f'{f:04d}.png');bpy.ops.render.render(write_still=True);records.append({'mode':mode,'frame':f,'size':size});print('V038_STILL',mode,f,round(time.time()-start,1),flush=True)
S=load(P/'native/WTSC_Boy_Full_Color_Readability_v038.blend');render(S,'HERO_COLOR',1,'V024 | CLOSE portrait',(960,1440))
for view,cam,size in [('CLOSE','V024 | CLOSE portrait',(480,720)),('SHOT','V020 | CHILD | SHOT',(1280,720))]:
 for f in [1,4,11,20,27]:render(S,'COLOR_'+view,f,cam,size)
S=load(P/'native/WTSC_Trouser_Root_Repair_Dark_v038.blend')
for f in [11,20]:render(S,'ROOT_REPAIR_DARK_CLOSE',f,'V024 | CLOSE portrait',(480,720))
S=load(P/'reference/PRESERVED_GARMENT_v037.blend');render(S,'HERO_DARK_REFERENCE',1,'V024 | CLOSE portrait',(960,1440));(P/'evidence/STILL_RENDER_RECORD.json').write_text(json.dumps({'records':records,'actual_native_stills':len(records),'hero_frame':1,'key_frames':[1,4,11,20,27],'threads':2,'elapsed_seconds':time.time()-start,'scope':'Actual full-color character stills. Five inherited static coat poses only. No motion/trailer/world render.','dark_baseline':'Existing actual v037 PAINTED_CLOSE/SHOT stills at identical native cameras/frame numbers for matched key views. Dark hero rendered freshly at matching960x1440.'},indent=2));print('V038_COLOR_STILLS_COMPLETE',len(records),flush=True)
