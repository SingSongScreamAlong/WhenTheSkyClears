"""Fresh v040 native UHD world; exact unchanged native glyph alpha from v037."""
import subprocess,time,json,hashlib,re
from pathlib import Path
R=Path(__file__).resolve().parents[1]
B=r'WTSC_LOCAL_USER\AppData\Local\Programs\Blender\blender-5.2.2-windows-x64\blender.exe'
F=r'WTSC_LOCAL_USER\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
audit=json.loads((R/'notes/world_v016/full_native_audit_v040.json').read_text())
assert audit['unchanged_mask_and_credits_signature'] and audit['unchanged_character_geometry_topology_uv']
source=Path(audit['source']);source_sha=hashlib.sha256(source.read_bytes()).hexdigest();assert source_sha==audit['source_sha256']
parts=R/'renders/world_v016/full_parts_v040';parts.mkdir(exist_ok=True);flags=subprocess.CREATE_NO_WINDOW
statuspath=R/'notes/world_v016/full_render_status_v040.json'
manifest={'source':str(source),'source_sha256':source_sha,'resolution':[3840,2160],'fps':24,'world_frames':2400,'credit_frames':144,'total_frames':2544,'total_seconds':106,'resource_plan':{'maximum_parallel_blender':4,'threads_per_blender':3,'world_eevee_samples':32,'shared_UI':False},'fresh_native_world':True,'cached_old_world_used':False,'mask_reuse':'Unchanged native UHD glyph alpha from preserved v037; native geometry/font/animation signature compared against v038. All world pixels freshly rendered from v040.','benchmark_comparison':'notes/world_v016/camp_comparison_completed_v039.json','v001_pack_used':False}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def decode(p,n):
    r=subprocess.run([F,'-v','error','-i',str(p),'-progress','pipe:1','-f','null','NUL'],capture_output=True,text=True);ns=re.findall(r'^frame=(\d+)',r.stdout,re.M);assert r.returncode==0 and ns and int(ns[-1])==n,(p,r.stderr,ns[-1:])
def command(args,log):
    with log.open('w',encoding='utf8') as stream:
        p=subprocess.Popen([F,'-hide_banner','-nostdin']+args,stdout=stream,stderr=subprocess.STDOUT,creationflags=flags)
        while p.poll() is None:
            tail=log.read_text(errors='replace')[-6000:];ns=re.findall(r'^frame=(\d+)',tail,re.M);print('ENCODE_PROGRESS',log.name,int(ns[-1]) if ns else 0,flush=True);time.sleep(25)
    assert p.returncode==0,log.read_text(errors='replace')[-3500:]
jobs=[]
for i in range(4):
    a=1+i*600;b=a+599;out=parts/f'world_{i+1:02d}.mp4';log=parts/f'world_{i+1:02d}.log';assert not out.exists()
    stream=log.open('w',encoding='utf8');p=subprocess.Popen([B,'--background','--factory-startup',str(source),'--threads','3','--python',str(R/'scripts/render_full_component_v037.py'),'--','world',str(a),str(b),str(out),'040'],cwd=R,stdout=stream,stderr=subprocess.STDOUT,creationflags=flags);jobs.append({'p':p,'stream':stream,'out':out,'log':log,'start':a,'end':b,'pid':p.pid})
manifest['world_workers']=[{k:str(v) if isinstance(v,Path) else v for k,v in j.items() if k not in ['p','stream']} for j in jobs]
(R/'notes/world_v016/full_render_workers_v040.json').write_text(json.dumps(manifest,indent=2));print('FULL_V040_WORLD_STARTED',[j['pid'] for j in jobs],flush=True)
while True:
    rows=[]
    for j in jobs:
        with j['log'].open('rb') as f:f.seek(max(0,j['log'].stat().st_size-18000));tail=f.read().decode('utf8',errors='replace')
        ns=re.findall(r'Video append frame (\d+)',tail);n=int(ns[-1])-j['start']+1 if ns else 0;code=j['p'].poll();assert code is None or (code==0 and 'Traceback (most recent call last)' not in tail),(j['log'],code)
        rows.append({'pid':j['pid'],'range':[j['start'],j['end']],'done':n,'total':600,'exit':code})
    status={'phase':'world','completed_frames':sum(j['done'] for j in rows),'total_frames':2400,'workers':rows,'resource_plan':manifest['resource_plan']};statuspath.write_text(json.dumps(status,indent=2));print('FULL_V040_PROGRESS',json.dumps(status),flush=True)
    if all(j['p'].poll() is not None for j in jobs):break
    time.sleep(30)
for j in jobs:
    j['stream'].close();assert 'COMPONENT_COMPLETED' in j['log'].read_text(errors='replace');decode(j['out'],600)
assert sha(source)==source_sha
world=parts/'world_concat.txt';world.write_text('\n'.join("file '"+j['out'].name+"'" for j in jobs),encoding='utf8')
mask=R/'renders/world_v016/full_parts_v037/mask_concat.txt';mask_hashes={}
for i in range(4):
    p=mask.parent/f'mask_{i+1:02d}.mp4';decode(p,600);mask_hashes[str(p)]=sha(p)
manifest['mask_component_hashes']=mask_hashes
masked=parts/'native_masked_100s.mp4';assert not masked.exists();statuspath.write_text(json.dumps({'phase':'compositing fresh UHD world through native letters','total_frames':2400},indent=2))
command(['-f','concat','-safe','0','-i',str(world),'-f','concat','-safe','0','-i',str(mask),'-filter_complex','[0:v]format=gbrp[w];[1:v]format=gbrp[m];[w][m]blend=all_mode=multiply:shortest=1[v]','-map','[v]','-an','-c:v','libx264','-preset','fast','-crf','16','-threads','6','-pix_fmt','yuv420p','-r','24','-fps_mode','cfr','-t','100','-video_track_timescale','24000','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-progress','pipe:1','-nostats',str(masked)],parts/'combine.log');decode(masked,2400)
log=(parts/'combine.log').read_text(errors='replace');assert max([int(x) for x in re.findall(r'^dup_frames=(\d+)',log,re.M)] or [0])==0 and max([int(x) for x in re.findall(r'^drop_frames=(\d+)',log,re.M)] or [0])==0
card=R/'renders/world_v016/full_parts_v037/credits_6s.mp4';decode(card,144)
listing=parts/'final_concat.txt';listing.write_text("file 'native_masked_100s.mp4'\nfile '"+card.as_posix()+"'",encoding='utf8')
movie=R/'renders/world_v016/WTSC_Full_Knockout_Trailer_4K_v040.mp4';assert not movie.exists();statuspath.write_text(json.dumps({'phase':'final master mux','frames':2544},indent=2))
command(['-f','concat','-safe','0','-i',str(listing),'-i',str(R/'edit/When_The_Sky_Clears_Trailer_Music_100s.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-af','afade=t=out:st=90:d=10,apad=pad_dur=6','-c:a','aac','-b:a','320k','-ar','48000','-t','106','-video_track_timescale','24000','-movflags','+faststart',str(movie)],parts/'mux.log');decode(movie,2544)
manifest.update({'movie':str(movie),'movie_sha256':sha(movie),'bytes':movie.stat().st_size,'full_decode_frames':2544,'full_decode_pass':True,'audio':'One original WAV, one90–100fade, silent100–106','credit_source':'Exact unchanged native4K card fromv037 held144frames','frame_duplication_in_moving_portion':False,'frame_interpolation':False});(R/'notes/world_v016/full_completed_v040.json').write_text(json.dumps(manifest,indent=2))
view=R/'renders/world_v016/WTSC_Full_Knockout_Trailer_View_v040.mp4';assert not view.exists();statuspath.write_text(json.dumps({'phase':'encoding under20MB viewing copy','master_complete':True},indent=2))
command(['-i',str(movie),'-vf','scale=1280:720:flags=lanczos','-c:v','libx264','-preset','fast','-b:v','1100k','-maxrate','1200k','-bufsize','2400k','-threads','4','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-movflags','+faststart',str(view)],parts/'view.log');assert view.stat().st_size<20_000_000;decode(view,2544)
manifest['viewing_copy']={'path':str(view),'bytes':view.stat().st_size,'sha256':sha(view),'resolution':[1280,720],'frames':2544,'under20000000bytes':True,'full_decode_pass':True};assert sha(source)==source_sha
(R/'notes/world_v016/full_completed_v040.json').write_text(json.dumps(manifest,indent=2));statuspath.write_text(json.dumps({'phase':'complete','master':str(movie),'view':str(view),'frames':2544,'seconds':106},indent=2));print('FULL_V040_MASTER_AND_VIEW_READY',json.dumps(manifest['viewing_copy']),flush=True)
