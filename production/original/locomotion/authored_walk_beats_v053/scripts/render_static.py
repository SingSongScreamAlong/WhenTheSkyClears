import bpy,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];E=P/'evidence';V=P/'previews'
cold=json.loads((E/'COLD_CHECK.json').read_text())
for file,h in cold['source_hashes'].items():assert hashlib.sha256(Path(file).read_bytes()).hexdigest()==h
old=json.loads((ROOT/'locomotion/coat_fluidity_v051/evidence/ACTUAL_V051_MOTION_RENDER.json').read_text())
ref={r['frame']:r for r in old['records'] if r['version']=='V051' and r['view']=='FULL'}
frames=[1,5,9,13,17,21,25,29,33];records=[]
for f in frames:
 r=ref[f];assert hashlib.sha256(Path(r['file']).read_bytes()).hexdigest()==r['sha256']
 records.append({'version':'V051','frame':f,'file':r['file'],'sha256':r['sha256']})
file=P/'native/WTSC_Authored_Walk_Beats_v053.blend';bpy.ops.wm.open_mainfile(filepath=str(file),load_ui=False,use_scripts=False);S=bpy.data.scenes['V053 | AUTHORED WALK BEATS | v051 grounded feet'];bpy.context.window.scene=S
S.render.resolution_x=1280;S.render.resolution_y=720;S.render.resolution_percentage=100;S.render.threads_mode='FIXED';S.render.threads=2;S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB';S.render.dither_intensity=0;assert S.render.fps==30
out=V/'static_V053';out.mkdir(exist_ok=True)
for f in frames:
 S.frame_set(f);path=out/('FRAME_%04d.png'%f);S.render.filepath=str(path);bpy.ops.render.render(write_still=True,scene=S.name);records.append({'version':'V053','frame':f,'file':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
for file,h in cold['source_hashes'].items():assert hashlib.sha256(Path(file).read_bytes()).hexdigest()==h
(E/'STATIC_RENDER.json').write_text(json.dumps({'matched_actual_frames':frames,'native_resolution':[1280,720],'fps':30,'records':records,'sources_unchanged':True},indent=2));print('V053_MATCHED_STATIC_RENDER_COMPLETE')
