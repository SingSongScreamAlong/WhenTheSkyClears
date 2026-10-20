"""Full native UHD render from immutable source; no frame interpolation/scaling."""
import subprocess,sys,time,json,re,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BLENDER=r'WTSC_LOCAL_USER\AppData\Local\Programs\Blender\blender-5.2.2-windows-x64\blender.exe'
FFMPEG=r'WTSC_LOCAL_USER\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
SOURCE=ROOT/'shots/world/WTSC_Living_World_v010.blend';OUT=ROOT/'renders/living_world';PARTS=OUT/'native_parts_v010';PARTS.mkdir(exist_ok=True)
FINAL=OUT/'WTSC_Living_World_4K_v010.mp4';assert not FINAL.exists()
workers=[]
for index in range(4):
    start=index*600+1;end=(index+1)*600
    target=PARTS/f'part_{index+1:02d}.mp4';assert not target.exists(),target
    log=PARTS/f'part_{index+1:02d}.log';stream=log.open('w',encoding='utf-8')
    args=[BLENDER,'--background','--factory-startup',str(SOURCE),'--threads','4','--scene','WTSC_MASTER_4K_100S',
          '--render-output',str(target),'--frame-start',str(start),'--frame-end',str(end),'--python-expr',
          "import bpy; bpy.context.scene.render.ffmpeg.audio_codec='NONE'",'--render-anim']
    proc=subprocess.Popen(args,stdout=stream,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    workers.append({'index':index+1,'start':start,'end':end,'pid':proc.pid,'output':str(target),'log':str(log),'process':proc,'stream':stream})
manifest={'source':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'resolution':[3840,2160],'fps':24,'frames':2400,
          'workers':[{k:v for k,v in w.items() if k not in ['process','stream']} for w in workers]}
(ROOT/'notes/living_world/native_render_workers_v010.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({'event':'living_world_native_workers_started','pids':[w['pid'] for w in workers],'frames':2400}),flush=True)
last_print=0
while True:
    rows=[]
    for w in workers:
        log=Path(w['log'])
        with log.open('rb') as f:f.seek(max(0,log.stat().st_size-100000));tail=f.read().decode('utf-8',errors='replace')
        frames=[int(x) for x in re.findall(r'Video append frame (\d+)',tail)];count=max(frames)-w['start']+1 if frames else 0;code=w['process'].poll()
        if code is not None and code!=0:
            print(json.dumps({'event':'worker_failed','index':w['index'],'exit':code,'log':w['log']}),flush=True);sys.exit(1)
        rows.append({'worker':w['index'],'rendered':count,'exit_code':code})
    if time.monotonic()-last_print>=30:
        print(json.dumps({'event':'native_render_progress','frames_done':sum(r['rendered'] for r in rows),'frames_total':2400,'workers':rows}),flush=True);last_print=time.monotonic()
    if all(w['process'].poll() is not None for w in workers):break
    time.sleep(1)
parts=[]
for w in workers:
    w['stream'].close();p=subprocess.run([FFMPEG,'-v','error','-i',w['output'],'-progress','pipe:1','-f','null','NUL'],capture_output=True,text=True)
    counts=re.findall(r'^frame=(\d+)',p.stdout,re.M);assert p.returncode==0 and counts and int(counts[-1])==600,(w,p.stderr)
    parts.append(Path(w['output']))
assert manifest['source_sha256']==hashlib.sha256(SOURCE.read_bytes()).hexdigest()
listing=PARTS/'concat.txt';listing.write_text(''.join("file '"+p.as_posix()+"'\n" for p in parts),encoding='utf-8')
p=subprocess.run([FFMPEG,'-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(listing),
    '-i',str(ROOT/'edit/When_The_Sky_Clears_Trailer_Music_100s.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy',
    '-af','afade=t=out:st=90:d=10','-c:a','aac','-b:a','320k','-t','100','-movflags','+faststart',str(FINAL)],capture_output=True,text=True)
assert p.returncode==0,p.stderr
print(json.dumps({'event':'living_world_movie_completed','path':str(FINAL),'bytes':FINAL.stat().st_size}),flush=True)
