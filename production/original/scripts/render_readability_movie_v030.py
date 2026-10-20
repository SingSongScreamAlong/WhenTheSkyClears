"""Native correction render plus verified unchanged native-frame reuse; no scaling/interpolation."""
import subprocess,sys,time,json,re,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
B=r'WTSC_LOCAL_USER\AppData\Local\Programs\Blender\blender-5.2.2-windows-x64\blender.exe'
F=r'WTSC_LOCAL_USER\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
source=R/'shots/world/WTSC_Painted_World_Trailer_v030.blend';parent=R/'renders/world_v016/WTSC_Painted_World_4K_v027.mp4';final=R/'renders/world_v016/WTSC_Painted_World_4K_v030.mp4';assert not final.exists()
proof=json.loads((R/'notes/world_v016/readability_and_reuse_v030.json').read_text());oldqa=json.loads((R/'notes/world_v016/movie_verification_v027.json').read_text())
source_sha=hashlib.sha256(source.read_bytes()).hexdigest();assert source_sha==proof['source_sha256'];assert hashlib.sha256(parent.read_bytes()).hexdigest()==oldqa['movie_sha256']
parts=R/'renders/world_v016/native_parts_v030';parts.mkdir(exist_ok=True);workers=[]
for index in range(4):
    start=301+index*393;end=start+392;target=parts/f'part_{index+1:02d}.mp4';assert not target.exists()
    log=parts/f'part_{index+1:02d}.log';stream=log.open('w',encoding='utf-8')
    args=[B,'--background','--factory-startup',str(source),'--threads','4','--scene','WTSC_PAINTED_WORLD_4K_100S_v030','--render-output',str(target),'--frame-start',str(start),'--frame-end',str(end),'--python-expr',"import bpy; bpy.context.scene.render.ffmpeg.audio_codec='NONE'",'--render-anim']
    p=subprocess.Popen(args,stdout=stream,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW);workers.append({'index':index+1,'start':start,'end':end,'pid':p.pid,'output':str(target),'log':str(log),'process':p,'stream':stream})
manifest={'source':str(source),'source_sha256':source_sha,'resolution':[3840,2160],'fps':24,'frames':2400,'new_native_frames':1572,'reused_native_frames':828,'reuse_ranges_frames':proof['reuse_ranges_frames'],'reuse_proof':'notes/world_v016/readability_and_reuse_v030.json','reused_source_movie':str(parent),'reused_source_movie_sha256':oldqa['movie_sha256'],'workers':[{k:v for k,v in w.items() if k not in ['process','stream']} for w in workers]}
(R/'notes/world_v016/native_workers_v030.json').write_text(json.dumps(manifest,indent=2));print(json.dumps({'event':'readability_native_render_started','new_frames':1572,'reused_frames':828,'pids':[w['pid'] for w in workers]}),flush=True)
last=0
while True:
    rows=[]
    for w in workers:
        log=Path(w['log'])
        with log.open('rb') as f:f.seek(max(0,log.stat().st_size-50000));tail=f.read().decode('utf-8',errors='replace')
        frames=[int(x) for x in re.findall(r'Video append frame (\d+)',tail)];count=max(frames)-w['start']+1 if frames else 0;code=w['process'].poll()
        assert code is None or (code==0 and 'Traceback (most recent call last)' not in tail),(w['index'],code,w['log'])
        rows.append({'worker':w['index'],'rendered':count,'exit_code':code})
    if time.monotonic()-last>=30:print(json.dumps({'event':'readability_render_progress','new_done':sum(v['rendered'] for v in rows),'new_total':1572,'workers':rows}),flush=True);last=time.monotonic()
    if all(w['process'].poll() is not None for w in workers):break
    time.sleep(1)
for w in workers:
    w['stream'].close();p=subprocess.run([F,'-v','error','-i',w['output'],'-progress','pipe:1','-f','null','NUL'],capture_output=True,text=True);counts=re.findall(r'^frame=(\d+)',p.stdout,re.M);assert p.returncode==0 and int(counts[-1])==393,(w,p.stderr)
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_sha
args=[F,'-hide_banner','-loglevel','error','-t','12.5','-i',str(parent)]
for w in workers:args+=['-i',w['output']]
args+=['-ss','78','-t','22','-i',str(parent),'-i',str(R/'edit/When_The_Sky_Clears_Trailer_Music_100s.wav')]
filters=';'.join(f'[{i}:v]setpts=PTS-STARTPTS[v{i}]' for i in range(6))+';'+''.join(f'[v{i}]' for i in range(6))+'concat=n=6:v=1:a=0[video];[6:a]afade=t=out:st=90:d=10[audio]'
args+=['-filter_complex',filters,'-map','[video]','-map','[audio]','-c:v','libx264','-preset','fast','-crf','16','-threads','8','-pix_fmt','yuv420p','-r','24','-fps_mode','cfr','-c:a','aac','-b:a','320k','-t','100','-movflags','+faststart','-progress','pipe:1','-nostats',str(final)]
log=parts/'final_encode.log';stream=log.open('w',encoding='utf-8');p=subprocess.Popen(args,stdout=stream,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW);last=0
print(json.dumps({'event':'corrected_full_movie_encoding','resolution':[3840,2160],'frames':2400,'native_new':1572,'native_reused':828}),flush=True)
while p.poll() is None:
    if time.monotonic()-last>=30:
        text=log.read_text(errors='replace');f=re.findall(r'^frame=(\d+)',text,re.M);print(json.dumps({'event':'corrected_movie_encode_progress','frames':int(f[-1]) if f else 0,'total':2400}),flush=True);last=time.monotonic()
    time.sleep(1)
stream.close();assert p.returncode==0,log.read_text()[-4000:]
p=subprocess.run([F,'-v','error','-i',str(final),'-progress','pipe:1','-f','null','NUL'],capture_output=True,text=True);frames=re.findall(r'^frame=(\d+)',p.stdout,re.M);assert p.returncode==0 and int(frames[-1])==2400,p.stderr
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_sha
manifest.update({'final':str(final),'bytes':final.stat().st_size,'full_decode_frames':2400,'full_decode_ok':True,'sha256':hashlib.sha256(final.read_bytes()).hexdigest(),'encoding':'Single CFR H264 encode of native UHD frame sections; no scaling, no frame interpolation. Original music remuxed with fade.'})
(R/'notes/world_v016/native_completed_v030.json').write_text(json.dumps(manifest,indent=2));print(json.dumps({'event':'corrected_movie_completed_and_decoded','path':str(final),'bytes':final.stat().st_size,'frames':2400}),flush=True)
