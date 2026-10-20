"""Fresh native UHD world + native lossless Font-alpha; complete106s single-WAV export."""
import subprocess,time,json,hashlib,re
from pathlib import Path
R=Path(__file__).resolve().parents[1];B=r'WTSC_LOCAL_USER\AppData\Local\Programs\Blender\blender-5.2.2-windows-x64\blender.exe';F=r'WTSC_LOCAL_USER\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
source=R/'shots/world/WTSC_Full_Knockout_Trailer_Editable_v037.blend';source_sha=hashlib.sha256(source.read_bytes()).hexdigest();assert source_sha==json.loads((R/'notes/world_v016/full_native_audit_v037.json').read_text())['source_sha256']
parts=R/'renders/world_v016/full_parts_v037';parts.mkdir(exist_ok=True);flags=subprocess.CREATE_NO_WINDOW
statuspath=R/'notes/world_v016/full_render_status_v037.json'
manifest={'source':str(source),'source_sha256':source_sha,'resolution':[3840,2160],'fps':24,'world_frames':2400,'credit_frames':144,'total_frames':2544,'total_seconds':106,'resource_plan':{'maximum_parallel_blender':4,'threads_per_blender':3,'world_eevee_samples':32,'world_and_mask_phases_sequential':True,'shared_UI':False,'effects_pack_dependency':False},'fresh_native_world':True,'cached_old_world_used':False,'split_compositor_proof':'4K split world+raw native Fontalpha matched direct native compositor with mean pixel error0 atframe1609.'}
(R/'notes/world_v016/full_render_workers_v037.json').write_text(json.dumps(manifest,indent=2))
def decode(p,expected):
 r=subprocess.run([F,'-v','error','-i',str(p),'-progress','pipe:1','-f','null','NUL'],capture_output=True,text=True);ns=re.findall(r'^frame=(\d+)',r.stdout,re.M);assert r.returncode==0 and ns and int(ns[-1])==expected,(p,r.stderr,ns[-1:])
def phase(mode):
 jobs=[]
 for i in range(4):
  a=1+i*600;b=a+599;out=parts/f'{mode}_{i+1:02d}.mp4';log=parts/f'{mode}_{i+1:02d}.log';assert not out.exists()
  stream=log.open('w',encoding='utf8');p=subprocess.Popen([B,'--background','--factory-startup',str(source),'--threads','3','--python',str(R/'scripts/render_full_component_v037.py'),'--',mode,str(a),str(b),str(out)],cwd=R,stdout=stream,stderr=subprocess.STDOUT,creationflags=flags);jobs.append({'p':p,'stream':stream,'out':out,'log':log,'start':a,'end':b,'pid':p.pid})
 manifest[mode+'_workers']=[{k:str(v) if isinstance(v,Path) else v for k,v in j.items() if k not in ['p','stream']} for j in jobs];(R/'notes/world_v016/full_render_workers_v037.json').write_text(json.dumps(manifest,indent=2))
 print('FULL_NATIVE_PHASE_STARTED',mode,[j['pid'] for j in jobs],flush=True);last=0
 while True:
  rows=[]
  for j in jobs:
   with j['log'].open('rb') as f:f.seek(max(0,j['log'].stat().st_size-18000));tail=f.read().decode('utf8',errors='replace')
   nums=re.findall(r'Video append frame (\d+)',tail);n=int(nums[-1])-j['start']+1 if nums else 0;code=j['p'].poll();assert code is None or (code==0 and 'Traceback (most recent call last)' not in tail),(j['log'],code)
   rows.append({'pid':j['pid'],'range':[j['start'],j['end']],'done':n,'total':600,'exit':code})
  status={'phase':mode,'completed_frames':sum(j['done'] for j in rows),'total_frames':2400,'workers':rows,'resource_plan':manifest['resource_plan']};statuspath.write_text(json.dumps(status,indent=2))
  if time.monotonic()-last>30:print('FULL_NATIVE_PROGRESS',json.dumps(status),flush=True);last=time.monotonic()
  if all(j['p'].poll() is not None for j in jobs):break
  time.sleep(5)
 for j in jobs:
  j['stream'].close();assert 'COMPONENT_COMPLETED' in j['log'].read_text(errors='replace');decode(j['out'],600)
 assert hashlib.sha256(source.read_bytes()).hexdigest()==source_sha
 listing=parts/f'{mode}_concat.txt';listing.write_text('\n'.join("file '"+j['out'].name+"'" for j in jobs),encoding='utf8');return listing
world=phase('world');mask=phase('mask')
masked=parts/'native_masked_100s.mp4';assert not masked.exists();statuspath.write_text(json.dumps({'phase':'combining fresh world with native alpha','total_frames':2400},indent=2))
args=[F,'-hide_banner','-nostdin','-f','concat','-safe','0','-i',str(world),'-f','concat','-safe','0','-i',str(mask),'-filter_complex','[0:v]format=gbrp[w];[1:v]format=gbrp[m];[w][m]blend=all_mode=multiply:shortest=1[v]','-map','[v]','-an','-c:v','libx264','-preset','fast','-crf','16','-threads','6','-pix_fmt','yuv420p','-r','24','-fps_mode','cfr','-t','100','-video_track_timescale','24000','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-progress','pipe:1','-nostats',str(masked)]
log=parts/'combine.log';stream=log.open('w',encoding='utf8');p=subprocess.Popen(args,stdout=stream,stderr=subprocess.STDOUT,creationflags=flags)
while p.poll() is None:
 tail=log.read_text(errors='replace')[-10000:];ns=re.findall(r'^frame=(\d+)',tail,re.M);print('COMBINE_PROGRESS',int(ns[-1]) if ns else 0,2400,flush=True);time.sleep(25)
stream.close();assert p.returncode==0,log.read_text()[-4000:];decode(masked,2400)
combine_receipt=log.read_text(errors='replace');dup=[int(x) for x in re.findall(r'^dup_frames=(\d+)',combine_receipt,re.M)];drop=[int(x) for x in re.findall(r'^drop_frames=(\d+)',combine_receipt,re.M)];assert max(dup or [0])==0 and max(drop or [0])==0
card=parts/'credits_6s.mp4';r=subprocess.run([F,'-hide_banner','-nostdin','-loop','1','-framerate','24','-i',str(R/'renders/world_v016/full_knockout_checks_v037/2401.png'),'-t','6','-an','-c:v','libx264','-preset','fast','-crf','16','-threads','4','-pix_fmt','yuv420p','-video_track_timescale','24000','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',str(card)],capture_output=True,text=True);assert r.returncode==0,r.stderr[-2500:];decode(card,144)
listing=parts/'final_concat.txt';listing.write_text("file 'native_masked_100s.mp4'\nfile 'credits_6s.mp4'",encoding='utf8')
movie=R/'renders/world_v016/WTSC_Full_Knockout_Trailer_4K_v037.mp4';assert not movie.exists()
r=subprocess.run([F,'-hide_banner','-nostdin','-f','concat','-safe','0','-i',str(listing),'-i',str(R/'edit/When_The_Sky_Clears_Trailer_Music_100s.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-af','afade=t=out:st=90:d=10,apad=pad_dur=6','-c:a','aac','-b:a','320k','-ar','48000','-t','106','-video_track_timescale','24000','-movflags','+faststart',str(movie)],capture_output=True,text=True);(R/'notes/world_v016/full_mux_v037.log').write_text(r.stderr);assert r.returncode==0,r.stderr[-3000:];decode(movie,2544)
manifest.update({'movie':str(movie),'movie_sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),'bytes':movie.stat().st_size,'full_decode_frames':2544,'full_decode_pass':True,'audio':'One original suppliedWAV, single90–100fade, silent100–106','credit_source':'Native4K frame2401 held144frames, no interpolation','frame_duplication_in_moving_portion':False,'frame_interpolation':False});(R/'notes/world_v016/full_completed_v037.json').write_text(json.dumps(manifest,indent=2));print('FULL_106S_MASTER_COMPLETED',json.dumps({k:v for k,v in manifest.items() if not k.endswith('_workers')}),flush=True)
view=R/'renders/world_v016/WTSC_Full_Knockout_Trailer_View_v037.mp4';assert not view.exists();statuspath.write_text(json.dumps({'phase':'encoding under20MB viewing copy','master_complete':True},indent=2))
r=subprocess.run([F,'-hide_banner','-nostdin','-i',str(movie),'-vf','scale=1280:720:flags=lanczos','-c:v','libx264','-preset','fast','-b:v','1100k','-maxrate','1200k','-bufsize','2400k','-threads','4','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-movflags','+faststart',str(view)],capture_output=True,text=True);(R/'notes/world_v016/full_view_encode_v037.log').write_text(r.stderr);assert r.returncode==0,r.stderr[-2500:];assert view.stat().st_size<20_000_000;decode(view,2544)
manifest['viewing_copy']={'path':str(view),'bytes':view.stat().st_size,'sha256':hashlib.sha256(view.read_bytes()).hexdigest(),'resolution':[1280,720],'frames':2544,'under20000000bytes':True,'full_decode_pass':True};(R/'notes/world_v016/full_completed_v037.json').write_text(json.dumps(manifest,indent=2));statuspath.write_text(json.dumps({'phase':'complete','master':str(movie),'view':str(view),'frames':2544,'seconds':106},indent=2));print('FULL_106S_VIEW_READY',json.dumps(manifest['viewing_copy']),flush=True)
