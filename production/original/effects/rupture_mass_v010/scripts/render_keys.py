import bpy,sys,time,json,csv,subprocess,os
from pathlib import Path
P=Path(__file__).resolve().parents[1];s=bpy.data.scenes['FXv010 | joined rupture and ground dust'];bpy.context.window.scene=s
phase=Path(bpy.data.filepath).stem;folder=P/'previews'/phase;folder.mkdir(exist_ok=True)
frames=[6,8,10,16,24,40,56,120];records=[]
for fr in frames:
    rows=csv.reader(subprocess.check_output([r'C:\Windows\System32\tasklist.exe','/FI','IMAGENAME eq blender.exe','/FO','CSV','/NH'],text=True,creationflags=subprocess.CREATE_NO_WINDOW).splitlines());others=[int(r[1]) for r in rows if r and r[0].lower()=='blender.exe' and int(r[1]) not in [39896,os.getpid()]]
    if others:raise RuntimeError('Render deferred to concurrent Blender worker '+str(others))
    s.frame_set(fr);bpy.context.view_layer.update();s.render.filepath=str(folder/f'{fr:04d}.png');t=time.perf_counter();bpy.ops.render.render(write_still=True,scene=s.name);records.append({'frame':fr,'seconds':time.perf_counter()-t})
(P/f'evidence/keys_{phase}.json').write_text(json.dumps({'frames':frames,'records':records,'fps':24,'pixels':[1920,1080],'actual_renders':True},indent=2));print('FEW_KEYS_DONE',phase,flush=True)
