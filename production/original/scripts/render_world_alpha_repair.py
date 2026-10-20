"""Render the corrected field section natively; preserve the verified first 45s.
The two repaired planes cannot enter the camera before frame 1143, independently
verified by native camera projection. All frames 1081-2400 are rendered afresh.
"""
import subprocess,sys,time,json,re,os,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BLENDER=r'WTSC_LOCAL_USER\AppData\Local\Programs\Blender\blender-5.2.2-windows-x64\blender.exe'
FFMPEG=r'WTSC_LOCAL_USER\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
SOURCE=ROOT/'shots/world/WTSC_World_First_v006.blend'
OUT=ROOT/'renders/world';PARTS=OUT/'native_render_parts_v006';PARTS.mkdir(exist_ok=True)
FINAL=OUT/'WTSC_World_Atmosphere_4K_v006.mp4'
assert not FINAL.exists()
workers=[]
for index in range(4):
    start=1081+index*330;end=start+329
    target=PARTS/f'part_{index+1:02d}.mp4';assert not target.exists(),target
    log=PARTS/f'part_{index+1:02d}.log';stream=log.open('w',encoding='utf-8')
    args=[BLENDER,'--background','--factory-startup',str(SOURCE),'--threads','4',
          '--scene','WTSC_MASTER_4K_100S','--render-output',str(target),
          '--frame-start',str(start),'--frame-end',str(end),'--python-expr',
          "import bpy; bpy.context.scene.render.ffmpeg.audio_codec='NONE'",'--render-anim']
    proc=subprocess.Popen(args,stdout=stream,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    workers.append({'index':index+1,'start':start,'end':end,'pid':proc.pid,'output':str(target),'log':str(log),'process':proc,'stream':stream})
manifest={'source':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          'resolution':[3840,2160],'fps':24,'frames_new_native':1320,'frames_reused_native':1080,
          'reused_source':'renders/world/WTSC_World_Atmosphere_4K_v004.mp4',
          'reuse_proof':'notes/world_field_entry.json; repaired planes first possible visibility at frames 1143 and 1150',
          'workers':[{k:v for k,v in w.items() if k not in ['process','stream']} for w in workers]}
(ROOT/'notes/world_render_workers_v006.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({'event':'corrected_native_workers_started','pids':[w['pid'] for w in workers],'frames':1320}),flush=True)
prefix=PARTS/'prefix_frames_0001_1080.mp4';assert not prefix.exists()
prefix_log=(PARTS/'prefix.log').open('w',encoding='utf-8')
prefix_proc=subprocess.Popen([FFMPEG,'-v','error','-i',str(OUT/'WTSC_World_Atmosphere_4K_v004.mp4'),
    '-an','-frames:v','1080','-c:v','libx264','-preset','fast','-crf','16','-threads','4',
    '-pix_fmt','yuv420p','-movflags','+faststart',str(prefix)],stdout=prefix_log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
last_print=0
while True:
    rows=[]
    for w in workers:
        log=Path(w['log'])
        with log.open('rb') as f:
            f.seek(max(0,log.stat().st_size-100000));tail=f.read().decode('utf-8',errors='replace')
        frames=[int(x) for x in re.findall(r'Video append frame (\d+)',tail)]
        count=max(frames)-w['start']+1 if frames else 0;code=w['process'].poll()
        if code is not None and code!=0:
            print(json.dumps({'event':'worker_failed','worker':w['index'],'exit_code':code,'log':w['log']}),flush=True);sys.exit(1)
        rows.append({'worker':w['index'],'rendered':count,'exit_code':code})
    if time.monotonic()-last_print>=20:
        print(json.dumps({'event':'progress','frames_done':sum(r['rendered'] for r in rows),'frames_total':1320,'workers':rows}),flush=True);last_print=time.monotonic()
    if all(w['process'].poll() is not None for w in workers):break
    time.sleep(1)
for w in workers:w['stream'].close()
assert prefix_proc.wait()==0,(PARTS/'prefix.log').read_text();prefix_log.close()
parts=[prefix]+[Path(w['output']) for w in workers]
for pth,count in zip(parts,[1080,330,330,330,330]):
    p=subprocess.run([FFMPEG,'-v','error','-i',str(pth),'-progress','pipe:1','-f','null','NUL'],capture_output=True,text=True)
    counts=re.findall(r'^frame=(\d+)',p.stdout,re.M)
    assert p.returncode==0 and counts and int(counts[-1])==count,(pth,p.stderr,p.stdout)
print(json.dumps({'event':'corrected_parts_decoded','frames':2400}),flush=True)
listing=PARTS/'concat.txt';listing.write_text(''.join("file '"+p.as_posix()+"'\n" for p in parts),encoding='utf-8')
p=subprocess.run([FFMPEG,'-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(listing),
    '-i',str(ROOT/'edit/When_The_Sky_Clears_Trailer_Music_100s.wav'),'-map','0:v:0','-map','1:a:0',
    '-c:v','copy','-af','afade=t=out:st=90:d=10','-c:a','aac','-b:a','320k','-t','100','-movflags','+faststart',str(FINAL)],capture_output=True,text=True)
assert p.returncode==0,p.stderr
print(json.dumps({'event':'corrected_movie_muxed','path':str(FINAL),'bytes':FINAL.stat().st_size}),flush=True)
