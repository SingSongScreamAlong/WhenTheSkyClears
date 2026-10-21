import bpy,json,time,sys,os,csv,subprocess
from pathlib import Path
P=Path(__file__).resolve().parents[1]
s=next(sc for sc in bpy.data.scenes if sc.name.startswith('FXv008 | coherent'));bpy.context.window.scene=s
root=bpy.data.objects['FXv008 | fixed world impact and controls'];phase='painted_final' if root['painted']>.5 and bpy.data.filepath.endswith('v008b.blend') else ('painted' if root['painted']>.5 else 'silhouette')
mode=sys.argv[-1] if sys.argv[-1] in ['keys','motion','aftermath'] else 'keys';folder=P/f'previews/{phase}_{mode}_coherent';folder.mkdir(exist_ok=True)
frames=[1824,1825,1826,1827,1829,1832,1836,1842,1848,1856,1868,1884,1908,1937] if mode=='keys' else ([2064] if mode=='aftermath' else list(range(1818,1938)));start=time.perf_counter();records=[]
for frame in frames:
    file=folder/f'{frame:04d}.png'
    if file.exists() and file.read_bytes()[-12:]==b'\x00\x00\x00\x00IEND\xaeB`\x82':continue
    rows=csv.reader(subprocess.check_output([r'C:\Windows\System32\tasklist.exe','/FI','IMAGENAME eq blender.exe','/FO','CSV','/NH'],text=True,creationflags=subprocess.CREATE_NO_WINDOW).splitlines())
    others=[int(row[1]) for row in rows if row and row[0].lower()=='blender.exe' and int(row[1]) not in [39896,os.getpid()]]
    if others:raise RuntimeError('FX yielded before next frame to other Blender PIDs '+str(others))
    s.frame_set(frame);bpy.context.view_layer.update();s.render.filepath=str(file);t=time.perf_counter();bpy.ops.render.render(write_still=True,scene=s.name);records.append({'frame':frame,'seconds':time.perf_counter()-t})
report={'phase':phase,'mode':mode,'folder':str(folder.relative_to(P)),'frames':frames,'fps':24,'pixels':[1920,1080],'renderer':s.render.engine,'samples':s.eevee.taa_render_samples,'threads':2,'seconds':time.perf_counter()-start,'records':records,'audio':False,'single_blast':True,'camera_shake':False}
(P/f'evidence/render_{phase}_{mode}.json').write_text(json.dumps(report,indent=2));print('COHERENT_RENDER_DONE',json.dumps(report),flush=True)
