"""Native scene-motion preview or full UHD movie; preserve source and verify every encoded frame."""
import subprocess,sys,time,json,re,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BLENDER=r'WTSC_LOCAL_USER\AppData\Local\Programs\Blender\blender-5.2.2-windows-x64\blender.exe'
FFMPEG=r'WTSC_LOCAL_USER\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
SOURCE=ROOT/'shots/world/WTSC_Painted_World_Trailer_v026.blend'
PREVIEW='--preview' in sys.argv
OUT=ROOT/'renders/world_v016'
PARTS=OUT/('preview_parts_v026' if PREVIEW else 'native_parts_v026');PARTS.mkdir(exist_ok=True)
FINAL=OUT/('WTSC_Motion_Excerpts_1080p_v026.mp4' if PREVIEW else 'WTSC_Painted_World_4K_v026.mp4')
assert not FINAL.exists(),FINAL
ranges=[(1,192),(721,816)] if PREVIEW else [(i*600+1,(i+1)*600) for i in range(4)]
workers=[]
for index,(start,end) in enumerate(ranges,1):
    target=PARTS/f'part_{index:02d}.mp4';assert not target.exists(),target
    log=PARTS/f'part_{index:02d}.log';stream=log.open('w',encoding='utf-8')
    expr="import bpy; s=bpy.context.scene; s.render.ffmpeg.audio_codec='NONE'"
    if PREVIEW:expr+='; s.render.resolution_percentage=50'
    args=[BLENDER,'--background','--factory-startup',str(SOURCE),'--threads','4','--scene','WTSC_PAINTED_WORLD_4K_100S_v026','--render-output',str(target),'--frame-start',str(start),'--frame-end',str(end),'--python-expr',expr,'--render-anim']
    proc=subprocess.Popen(args,stdout=stream,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    workers.append({'index':index,'start':start,'end':end,'pid':proc.pid,'output':str(target),'log':str(log),'process':proc,'stream':stream})
manifest={'source':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'mode':'motion excerpts' if PREVIEW else 'full UHD world pass','resolution':[1920,1080] if PREVIEW else [3840,2160],'fps':24,'frames':sum(b-a+1 for a,b in ranges),'timeline_ranges_frames':ranges,'native_scene_render':True,'workers':[{k:v for k,v in w.items() if k not in ['process','stream']} for w in workers]}
note=ROOT/'notes/world_v016'/('preview_workers_v026.json' if PREVIEW else 'native_workers_v026.json');note.write_text(json.dumps(manifest,indent=2))
print(json.dumps({'event':'native_workers_started','preview':PREVIEW,'pids':[w['pid'] for w in workers],'frames':manifest['frames']}),flush=True)
last_print=0
while True:
    rows=[]
    for w in workers:
        log=Path(w['log'])
        with log.open('rb') as f:f.seek(max(0,log.stat().st_size-50000));tail=f.read().decode('utf-8',errors='replace')
        frames=[int(x) for x in re.findall(r'Video append frame (\d+)',tail)];count=max(frames)-w['start']+1 if frames else 0;code=w['process'].poll()
        if code is not None and (code!=0 or 'Traceback (most recent call last)' in tail):
            print(json.dumps({'event':'worker_failed','index':w['index'],'exit':code,'log':w['log']}),flush=True);sys.exit(1)
        rows.append({'worker':w['index'],'rendered':count,'exit_code':code})
    if time.monotonic()-last_print>=30:
        print(json.dumps({'event':'native_render_progress','frames_done':sum(r['rendered'] for r in rows),'frames_total':manifest['frames'],'workers':rows}),flush=True);last_print=time.monotonic()
    if all(w['process'].poll() is not None for w in workers):break
    time.sleep(1)
parts=[]
for w in workers:
    w['stream'].close();p=subprocess.run([FFMPEG,'-v','error','-i',w['output'],'-progress','pipe:1','-f','null','NUL'],capture_output=True,text=True)
    counts=re.findall(r'^frame=(\d+)',p.stdout,re.M);assert p.returncode==0 and counts and int(counts[-1])==w['end']-w['start']+1,(w,p.stderr)
    parts.append(Path(w['output']))
assert manifest['source_sha256']==hashlib.sha256(SOURCE.read_bytes()).hexdigest()
listing=PARTS/'concat.txt';listing.write_text(''.join("file '"+p.as_posix()+"'\n" for p in parts),encoding='utf-8')
args=[FFMPEG,'-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(listing),'-i',str(ROOT/'edit/When_The_Sky_Clears_Trailer_Music_100s.wav')]
if PREVIEW:
    args+=['-filter_complex','[1:a]asplit=2[a][b];[a]atrim=0:8,asetpts=PTS-STARTPTS[a0];[b]atrim=30:34,asetpts=PTS-STARTPTS[a1];[a0][a1]concat=n=2:v=0:a=1[outa]','-map','0:v:0','-map','[outa]','-c:v','copy','-c:a','aac','-b:a','256k','-t','12']
else:
    args+=['-map','0:v:0','-map','1:a:0','-c:v','copy','-af','afade=t=out:st=90:d=10','-c:a','aac','-b:a','320k','-t','100']
args+=['-movflags','+faststart',str(FINAL)]
p=subprocess.run(args,capture_output=True,text=True);assert p.returncode==0,p.stderr
p=subprocess.run([FFMPEG,'-v','error','-i',str(FINAL),'-progress','pipe:1','-f','null','NUL'],capture_output=True,text=True)
counts=re.findall(r'^frame=(\d+)',p.stdout,re.M);assert p.returncode==0 and int(counts[-1])==manifest['frames'],p.stderr
manifest.update({'final':str(FINAL),'bytes':FINAL.stat().st_size,'full_decode_frames':int(counts[-1]),'full_decode_ok':True,'sha256':hashlib.sha256(FINAL.read_bytes()).hexdigest()})
note.with_name('preview_completed_v026.json' if PREVIEW else 'native_completed_v026.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({'event':'movie_completed_and_decoded','path':str(FINAL),'bytes':FINAL.stat().st_size,'frames':int(counts[-1]),'preview':PREVIEW}),flush=True)

