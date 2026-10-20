import bpy,time,json,csv,subprocess,os,sys
from pathlib import Path
P=Path(__file__).resolve().parents[1];s=bpy.data.scenes['FXv012 | drawn expansion and seated contacts'];bpy.context.window.scene=s;r=bpy.data.objects['FXv012 | terrain anchor and controls'];phase='painted' if r['painted']>.5 else 'plain';mode='motion' if '--motion' in sys.argv else 'keys';folder=P/'previews'/f'{phase}_{mode}';folder.mkdir(exist_ok=True)
frames=list(range(1,73)) if mode=='motion' else list(range(6,16))+[18,22,26,30,36,72];records=[]
for fr in frames:
    f=folder/f'{fr:04d}.png'
    if f.exists() and f.read_bytes()[-12:]==b'\x00\x00\x00\x00IEND\xaeB`\x82':continue
    rows=csv.reader(subprocess.check_output([r'C:\Windows\System32\tasklist.exe','/FI','IMAGENAME eq blender.exe','/FO','CSV','/NH'],text=True,creationflags=subprocess.CREATE_NO_WINDOW).splitlines());others=[int(x[1]) for x in rows if x and x[0].lower()=='blender.exe' and int(x[1]) not in [39896,os.getpid()]]
    if others:raise RuntimeError('Deferred before next frame for other Blender '+str(others))
    s.frame_set(fr);bpy.context.view_layer.update();s.render.filepath=str(f);t=time.perf_counter();bpy.ops.render.render(write_still=True,scene=s.name);records.append({'frame':fr,'seconds':time.perf_counter()-t})
(P/f'evidence/render_{phase}_{mode}.json').write_text(json.dumps({'frames':frames,'records':records,'fps':24,'pixels':[1920,1080]},indent=2));print('DRAWN_RENDER_DONE',phase,mode,flush=True)
