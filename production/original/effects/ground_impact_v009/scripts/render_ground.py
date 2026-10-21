import bpy,json,time,sys,os,csv,subprocess
from pathlib import Path
P=Path(__file__).resolve().parents[1];s=bpy.data.scenes['FXv009 | ground debris proof'];bpy.context.window.scene=s
mode=sys.argv[-1] if sys.argv[-1] in ['keys','motion','aftermath'] else 'keys'
phase=Path(bpy.data.filepath).stem.split('_')[-1]
folder=P/f'previews/{phase}_{mode}';folder.mkdir(exist_ok=True)
frames=[6,7,8,9,10,12,16,20,24,28,32,36,40,44,52,64,96,120] if mode=='keys' else ([192] if mode=='aftermath' else list(range(1,121)))
records=[];start=time.perf_counter()
for fr in frames:
    file=folder/f'{fr:04d}.png'
    if file.exists() and file.read_bytes()[-12:]==b'\x00\x00\x00\x00IEND\xaeB`\x82':continue
    rows=csv.reader(subprocess.check_output([r'C:\Windows\System32\tasklist.exe','/FI','IMAGENAME eq blender.exe','/FO','CSV','/NH'],text=True,creationflags=subprocess.CREATE_NO_WINDOW).splitlines())
    others=[int(r[1]) for r in rows if r and r[0].lower()=='blender.exe' and int(r[1]) not in [39896,os.getpid()]]
    if others:raise RuntimeError('Deferred at next frame for Blender jobs '+str(others))
    s.frame_set(fr);bpy.context.view_layer.update();s.render.filepath=str(file);t=time.perf_counter();bpy.ops.render.render(write_still=True,scene=s.name);records.append({'frame':fr,'seconds':time.perf_counter()-t})
report={'mode':mode,'frames':frames,'fps':24,'seconds':time.perf_counter()-start,'records':records,'audio':False,'smoke':False,'renderer':s.render.engine,'threads':2}
(P/f'evidence/render_{phase}_{mode}.json').write_text(json.dumps(report,indent=2));print('GROUND_RENDER_DONE',json.dumps(report),flush=True)
