import bpy,json,hashlib,datetime
from pathlib import Path
O=Path(r'WTSC_LOCAL_WORKSPACE\locomotion\garment_continuity_v047')
jobs=[('baseline',O/'reference/PRESERVED_v046_INPUT.blend','V046 | AGE10 BONES | restored painted clothing',64,94),('garment',O/'native/WTSC_Age10_Garment_Continuity_v047.blend','V047 | AGE TEN | garment continuity',1,63),('candidate',O/'native/WTSC_Age10_Paired_Reach_v047.blend','V047 | AGE TEN | reach and contact',1,94)]
records=[]
for name,P,sname,lo,hi in jobs:
 H=hashlib.sha256(P.read_bytes()).hexdigest()
 bpy.ops.wm.open_mainfile(filepath=str(P),load_ui=False,use_scripts=False)
 s=bpy.data.scenes[sname];bpy.context.window.scene=s
 s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100
 s.render.threads_mode='FIXED';s.render.threads=2;s.render.dither_intensity=0;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.eevee.taa_render_samples=32
 D=O/'previews'/name;D.mkdir(exist_ok=True)
 for f in range(lo,hi+1):
  s.frame_set(f);s.render.filepath=str(D/f'{f:04d}.png');bpy.ops.render.render(write_still=True,scene=s.name)
 assert hashlib.sha256(P.read_bytes()).hexdigest()==H
 records.append({'variant':name,'cold_opened_native':str(P),'sha256':H,'rendered_range':[lo,hi],'fps':s.render.fps,'resolution':[1280,720],'rendered_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
 (O/'evidence/COLD_RENDER_RECORD.json').write_text(json.dumps(records,indent=2))
print('V047_COLD_SEQUENCE_RENDER_COMPLETE',flush=True)
