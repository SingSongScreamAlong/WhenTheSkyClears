import bpy,sys,time,json,csv,subprocess,os
from pathlib import Path
P=Path(__file__).resolve().parents[1];s=bpy.data.scenes['FXv011 | compact brief impact low dust'];bpy.context.window.scene=s;mode=('motion_final' if '--final' in sys.argv else 'motion') if '--motion' in sys.argv else ('painted_keys' if '--painted' in sys.argv else 'keys');folder=P/'previews'/mode;folder.mkdir(exist_ok=True)
frames=list(range(1,73)) if mode.startswith('motion') else [6,7,8,10,14,20,28,48,72];records=[]
for fr in frames:
    file=folder/f'{fr:04d}.png'
    if file.exists() and file.read_bytes()[-12:]==b'\x00\x00\x00\x00IEND\xaeB`\x82':continue
    rows=csv.reader(subprocess.check_output([r'C:\Windows\System32\tasklist.exe','/FI','IMAGENAME eq blender.exe','/FO','CSV','/NH'],text=True,creationflags=subprocess.CREATE_NO_WINDOW).splitlines());others=[int(r[1]) for r in rows if r and r[0].lower()=='blender.exe' and int(r[1]) not in [39896,os.getpid()]]
    if others:raise RuntimeError('Deferred before next frame for concurrent Blender '+str(others))
    s.frame_set(fr);bpy.context.view_layer.update();s.render.filepath=str(file);t=time.perf_counter();bpy.ops.render.render(write_still=True,scene=s.name);records.append({'frame':fr,'seconds':time.perf_counter()-t})
(P/f'evidence/render_{mode}.json').write_text(json.dumps({'frames':frames,'fps':24,'pixels':[1920,1080],'records':records,'audio':False},indent=2));print('COMPACT_RENDER_DONE',mode,flush=True)
