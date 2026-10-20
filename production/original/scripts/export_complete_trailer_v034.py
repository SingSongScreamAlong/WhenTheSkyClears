import subprocess,time,json,hashlib,re
from pathlib import Path
R=Path(__file__).resolve().parents[1];B=r'WTSC_LOCAL_USER\AppData\Local\Programs\Blender\blender-5.2.2-windows-x64\blender.exe';F=r'WTSC_LOCAL_USER\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
parts=R/'renders/world_v016/complete_parts_v034';parts.mkdir(exist_ok=True);source=R/'shots/world/WTSC_Complete_Trailer_Editable_v034.blend';flags=subprocess.CREATE_NO_WINDOW
def launch(args,log):
 stream=log.open('w',encoding='utf8');p=subprocess.Popen(args,cwd=R,stdout=stream,stderr=subprocess.STDOUT,creationflags=flags);return p,stream
prefix=parts/'centered_cache_0_70.mp4';assert not prefix.exists()
p0,l0=launch([F,'-hide_banner','-nostdin','-i',str(R/'renders/world_v016/WTSC_Painted_World_4K_v030.mp4'),'-t','70','-an','-vf','crop=1920:1080:384:1053:exact=1,scale=3840:2160:flags=lanczos,setsar=1','-c:v','libx264','-preset','fast','-crf','16','-threads','4','-pix_fmt','yuv420p','-r','24','-fps_mode','cfr','-video_track_timescale','24000','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',str(prefix)],parts/'centered_cache.log')
jobs=[]
for i,(a,b) in enumerate([(1681,1752),(1753,1824),(1825,1896),(1897,1968)]):
 out=parts/f'native_{i+1}.mp4';assert not out.exists();log=parts/f'native_{i+1}.log'
 p,stream=launch([B,'--background','--factory-startup',str(source),'--threads','3','--python',str(R/'scripts/render_world_part_v034.py'),'--',str(a),str(b),str(out)],log)
 jobs.append((p,stream,out,a,b,log));print('WORLD_PATCH_START',p.pid,a,b,flush=True)
manifest={'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'new_native_frames':288,'cached_prefix_frames':1680,'reused_ending_frames':504,'total_frames':2472,'center_crop_source_pixels':[384,1053,1920,1080],'center_crop_output':[3840,2160],'native_workers':[{'pid':p.pid,'frames':[a,b],'log':str(log)} for p,_,_,a,b,log in jobs]}
(R/'notes/world_v016/complete_workers_v034.json').write_text(json.dumps(manifest,indent=2))
while any(p.poll() is None for p,_,_,_,_,_ in jobs) or p0.poll() is None:
 rows=[]
 for p,_,_,a,b,log in jobs:
  tail=log.read_text(encoding='utf8',errors='replace')[-14000:];frames=re.findall(r'Video append frame (\d+)',tail);n=int(frames[-1])-a+1 if frames else 0
  assert p.poll() is None or (p.returncode==0 and 'Traceback' not in tail),str(log)
  rows.append({'start':a,'done':n,'total':b-a+1,'exit':p.poll()})
 print('COMPLETE_EXPORT_PROGRESS',json.dumps({'native':rows,'cached_prefix_exit':p0.poll()}),flush=True);time.sleep(25)
l0.close();assert p0.returncode==0,'prefix'
ordered=[prefix]
for p,stream,out,a,b,log in jobs:
 stream.close();assert p.returncode==0 and 'WORLD_PATCH_COMPLETED' in log.read_text(errors='replace'),str(log)
 normalized=out.with_name(out.stem+'_normalized.mp4')
 result=subprocess.run([F,'-v','error','-nostdin','-i',str(out),'-map','0:v:0','-c:v','copy','-an','-video_track_timescale','24000',str(normalized)],capture_output=True,text=True);assert result.returncode==0,result.stderr
 ordered.append(normalized)
ending=parts/'ending_v033_picture_normalized.mp4'
r=subprocess.run([F,'-v','error','-nostdin','-i',str(R/'renders/world_v016/WTSC_Knockout_Ending_4K_v033.mp4'),'-map','0:v:0','-c:v','copy','-an','-video_track_timescale','24000',str(ending)],capture_output=True,text=True);assert r.returncode==0,r.stderr
ordered.append(ending)
for i,p in enumerate(ordered):
 r=subprocess.run([F,'-v','error','-i',str(p),'-progress','pipe:1','-f','null','NUL'],capture_output=True,text=True);ns=re.findall(r'^frame=(\d+)',r.stdout,re.M);expected=1680 if i==0 else 504 if i==5 else 72;assert r.returncode==0 and int(ns[-1])==expected,(p,r.stderr,ns[-1:]);print('SECTION_DECODED',p.name,expected,flush=True)
listing=parts/'concat.txt';listing.write_text('\n'.join("file '"+p.name+"'" for p in ordered),encoding='utf8')
movie=R/'renders/world_v016/WTSC_Complete_Trailer_4K_v034.mp4';assert not movie.exists()
args=[F,'-hide_banner','-nostdin','-f','concat','-safe','0','-i',str(listing),'-i',str(R/'edit/When_The_Sky_Clears_Trailer_Music_100s.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-af','afade=t=out:st=90:d=10,apad=pad_dur=3','-c:a','aac','-b:a','320k','-ar','48000','-t','103','-video_track_timescale','24000','-movflags','+faststart',str(movie)]
r=subprocess.run(args,capture_output=True,text=True);(R/'notes/world_v016/complete_mux_v034.log').write_text(r.stderr);assert r.returncode==0,r.stderr[-3000:]
r=subprocess.run([F,'-v','error','-i',str(movie),'-progress','pipe:1','-f','null','NUL'],capture_output=True,text=True);n=re.findall(r'^frame=(\d+)',r.stdout,re.M);assert r.returncode==0 and int(n[-1])==2472,(r.stderr,n[-1:])
assert manifest['source_sha256']==hashlib.sha256(source.read_bytes()).hexdigest()
manifest.update({'movie':str(movie),'movie_sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),'bytes':movie.stat().st_size,'full_decode_frames':2472,'full_decode_pass':True,'duration':103,'fps':24,'resolution':[3840,2160],'audio_source':'single original suppliedWAV, only one fade90–100;3s silence','frame_retime_or_interpolation':False})
(R/'notes/world_v016/complete_completed_v034.json').write_text(json.dumps(manifest,indent=2));print('COMPLETE_TRAILER_MASTER_READY',json.dumps(manifest),flush=True)
view=R/'renders/world_v016/WTSC_Complete_Trailer_View_v034.mp4';assert not view.exists()
r=subprocess.run([F,'-hide_banner','-nostdin','-i',str(movie),'-vf','scale=1280:720:flags=lanczos','-c:v','libx264','-preset','fast','-b:v','1100k','-maxrate','1200k','-bufsize','2400k','-pix_fmt','yuv420p','-threads','4','-c:a','aac','-b:a','128k','-movflags','+faststart',str(view)],capture_output=True,text=True);(R/'notes/world_v016/complete_view_encode_v034.log').write_text(r.stderr);assert r.returncode==0,r.stderr[-3000:];assert view.stat().st_size<20_000_000
r=subprocess.run([F,'-v','error','-i',str(view),'-progress','pipe:1','-f','null','NUL'],capture_output=True,text=True);n=re.findall(r'^frame=(\d+)',r.stdout,re.M);assert r.returncode==0 and int(n[-1])==2472
manifest['viewing_copy']={'path':str(view),'bytes':view.stat().st_size,'sha256':hashlib.sha256(view.read_bytes()).hexdigest(),'resolution':[1280,720],'full_decode_frames':2472,'under_20000000_bytes':True}
(R/'notes/world_v016/complete_completed_v034.json').write_text(json.dumps(manifest,indent=2));print('FULL_VIEWING_COPY_READY',json.dumps(manifest['viewing_copy']),flush=True)
