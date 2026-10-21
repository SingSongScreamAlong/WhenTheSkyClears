import bpy,json,hashlib,time
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];E=P/'evidence';V=P/'previews';cold=json.loads((E/'COLD_CHECK.json').read_text())
for file,h in cold['source_hashes'].items():assert hashlib.sha256(Path(file).read_bytes()).hexdigest()==h
ref=json.loads((ROOT/'locomotion/coat_fluidity_v051/evidence/ACTUAL_V051_MOTION_RENDER.json').read_text())
base={r['frame']:r for r in ref['records'] if r['version']=='V051' and r['view']=='FULL'};records=[]
for f in range(1,130):
 r=base[f];assert hashlib.sha256(Path(r['file']).read_bytes()).hexdigest()==r['sha256'];records.append({'version':'V051','frame':f,'file':r['file'],'sha256':r['sha256'],'method':'verified frozen v051 actual native frame'})
file=P/'native/WTSC_Support_Linked_Upper_Body_v052.blend';bpy.ops.wm.open_mainfile(filepath=str(file),load_ui=False,use_scripts=False);S=bpy.data.scenes['V052 | SUPPORT LINKED UPPER BODY | v051 contacts'];bpy.context.window.scene=S
S.render.resolution_x=1280;S.render.resolution_y=720;S.render.resolution_percentage=100;S.render.threads_mode='FIXED';S.render.threads=2;S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB';S.render.dither_intensity=0;assert S.render.fps==30
out=V/'frames_V052';out.mkdir(exist_ok=True);begin=time.time()
for f in range(1,130):
 S.frame_set(f);path=out/('FRAME_%04d.png'%f);S.render.filepath=str(path);bpy.ops.render.render(write_still=True,scene=S.name);records.append({'version':'V052','frame':f,'file':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'method':'actual isolated native v052 timeline frame'})
for file,h in cold['source_hashes'].items():assert hashlib.sha256(Path(file).read_bytes()).hexdigest()==h
(E/'ACTUAL_MOTION_RENDER.json').write_text(json.dumps({'source_hashes':cold['source_hashes'],'frame_range':[1,129],'fps':30,'native_resolution':[1280,720],'threads':2,'elapsed_seconds':time.time()-begin,'records':records,'source_unchanged':True},indent=2));print('V052_ACTUAL_NORMAL_SPEED_RENDER_COMPLETE')
