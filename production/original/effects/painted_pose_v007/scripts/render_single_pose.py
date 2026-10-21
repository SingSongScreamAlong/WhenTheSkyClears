import bpy,json,time,sys,os,csv,subprocess,math
from pathlib import Path
P=Path(__file__).resolve().parents[1];s=bpy.data.scenes['FX_PROOF_v007 | distinct painted poses | one blast'];bpy.context.window.scene=s
mode=sys.argv[-1] if sys.argv[-1] in ['poses','motion'] else 'poses';start=time.perf_counter();records=[]
def check_window():
    rows=csv.reader(subprocess.check_output([r'C:\Windows\System32\tasklist.exe','/FI','IMAGENAME eq blender.exe','/FO','CSV','/NH'],text=True,creationflags=subprocess.CREATE_NO_WINDOW).splitlines())
    others=[int(r[1]) for r in rows if r and r[0].lower()=='blender.exe' and int(r[1]) not in [39896,os.getpid()]]
    if others:raise RuntimeError('FX yields before next frame to production Blender PIDs '+str(others))
if mode=='poses':
    source=json.loads((P/'evidence/build_single_pose.json').read_text());frames=[(1824+p['key_age'],P/f'previews/final_pose_{p["drawing"]:02d}.png') for p in source['poses'] if p['kind']=='Blast']
else:
    folder=P/'previews/motion_frames';folder.mkdir(exist_ok=True);frames=[(frame,folder/f'{frame:04d}.png') for frame in range(1818,1914)]
for frame,file in frames:
    if file.exists() and file.read_bytes()[-12:]==b'\x00\x00\x00\x00IEND\xaeB`\x82':continue
    check_window();s.frame_set(math.floor(frame),subframe=frame-math.floor(frame));bpy.context.view_layer.update();s.render.filepath=str(file);t=time.perf_counter();bpy.ops.render.render(write_still=True,scene=s.name);records.append({'frame':frame,'seconds':time.perf_counter()-t,'file':str(file.relative_to(P))})
report={'mode':mode,'fps':24,'pixels':[1920,1080],'renderer':'BLENDER_EEVEE','samples':32,'one_blast':True,'audio':False,'records':records,'this_session_seconds':time.perf_counter()-start,'no_new_simulation':True,'threads':2}
(P/f'evidence/render_{mode}.json').write_text(json.dumps(report,indent=2));print('V007_RENDER_COMPLETE',json.dumps(report),flush=True)
