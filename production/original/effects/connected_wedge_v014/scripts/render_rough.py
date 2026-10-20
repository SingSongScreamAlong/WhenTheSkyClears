import bpy,time,json,csv,subprocess,os,sys
from pathlib import Path
P=Path(__file__).resolve().parents[1];s=bpy.data.scenes['FXv014 | connected wedge TWO TONE ROUGH'];bpy.context.window.scene=s;mode='motion' if '--motion' in sys.argv else 'keys';folder=P/'previews'/mode;folder.mkdir(exist_ok=True);frames=list(range(1,33)) if mode=='motion' else [6,7,8,9,10,11,12,13,14,15,16,17,19,21,24,28,32];records=[]
for fr in frames:
    f=folder/f'{fr:04d}.png'
    if f.exists() and '--force' not in sys.argv and f.read_bytes()[-12:]==b'\x00\x00\x00\x00IEND\xaeB`\x82':continue
    rows=csv.reader(subprocess.check_output([r'C:\Windows\System32\tasklist.exe','/FI','IMAGENAME eq blender.exe','/FO','CSV','/NH'],text=True,creationflags=subprocess.CREATE_NO_WINDOW).splitlines());others=[int(x[1]) for x in rows if x and x[0].lower()=='blender.exe' and int(x[1]) not in [39896,os.getpid()]]
    if others:raise RuntimeError('Deferred before next frame for another Blender '+str(others))
    s.frame_set(fr);bpy.context.view_layer.update();s.render.filepath=str(f);t=time.perf_counter();bpy.ops.render.render(write_still=True,scene=s.name);records.append({'frame':fr,'seconds':time.perf_counter()-t})
(P/f'evidence/render_{mode}.json').write_text(json.dumps({'frames':frames,'records':records},indent=2));print('CONNECTED_ROUGH_RENDER_DONE',mode,flush=True)
