"""One owned GPU job, then actual-frame matched local review artifacts."""
import subprocess,time,json,re,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];B=r'WTSC_LOCAL_USER\AppData\Local\Programs\Blender\blender-5.2.2-windows-x64\blender.exe';F=r'WTSC_LOCAL_USER\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
folder=R/'renders/world_v016/integration_v044';build=json.loads((R/'notes/world_v016/motion_trial_build_v044.json').read_text());source=Path(build['source']);log=folder/'native_movie.log';assert not log.exists();stream=log.open('w',encoding='utf8')
p=subprocess.Popen([B,'--background','--factory-startup',str(source),'--threads','2','--python',str(R/'scripts/verify_render_v044.py')],cwd=R,stdout=stream,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
print('V044_OWNED_NATIVE_JOB',p.pid,flush=True)
while p.poll() is None:
 tail=log.read_text(errors='replace')[-14000:];counts=re.findall(r'Video append frame (\d+)',tail);done=int(counts[-1])-1800 if counts else 0
 (R/'notes/world_v016/render_status_v044.json').write_text(json.dumps({'phase':'native4K120frameexport','pid':p.pid,'completed_frames':done,'total_frames':120,'engine':'BLENDER_EEVEE','one_GPU_job':True,'threads':2},indent=2));print('V044_PROGRESS',done,120,flush=True);time.sleep(20)
stream.close();logtext=log.read_text(errors='replace');assert p.returncode==0 and 'V044_NATIVE_120F_EXPORT_COMPLETED' in logtext and 'Traceback (most recent call last)' not in logtext,logtext[-4000:]
def run(args):
 r=subprocess.run([F,'-hide_banner','-nostdin',*args],capture_output=True,text=True,cwd=r'C:\Windows\Fonts');assert r.returncode==0,r.stderr[-4000:];return r.stderr
def decode(path):
 r=subprocess.run([F,'-v','error','-i',str(path),'-progress','pipe:1','-f','null','NUL'],capture_output=True,text=True);counts=re.findall(r'^frame=(\d+)',r.stdout,re.M);assert r.returncode==0 and counts and int(counts[-1])==120,(str(path),r.stderr,counts[-1:])
movie=folder/'WTSC_Drawn_Open_75_80_4K_v044.mp4';decode(movie);view=folder/'WTSC_Drawn_Open_75_80_View_v044.mp4'
run(['-i',str(movie),'-vf','scale=1920:1080:flags=lanczos','-c:v','libx264','-crf','18','-preset','fast','-threads','3','-c:a','aac','-b:a','160k','-movflags','+faststart',str(view)]);decode(view)
baseline=R/'renders/world_v016/integration_v043/WTSC_Combined_Open_75_80_4K_v043.mp4';decode(baseline);comparison=folder/'WTSC_v043_vs_v044_Matched_EEVEE_75_80.mp4'
filters="[0:v]scale=1920:1080:flags=lanczos,drawbox=x=0:y=0:w=iw:h=42:color=black@0.8:t=fill,drawtext=fontfile=arial.ttf:text='v043 | previous performance':fontsize=27:fontcolor=white:x=16:y=7[a];[1:v]scale=1920:1080:flags=lanczos,drawbox=x=0:y=0:w=iw:h=42:color=black@0.8:t=fill,drawtext=fontfile=arial.ttf:text='v044 | corrected v006 drawn performance':fontsize=27:fontcolor=white:x=16:y=7[b];[a][b]hstack=inputs=2,drawbox=x=0:y=ih-42:w=iw:h=42:color=black@0.8:t=fill,drawtext=fontfile=arial.ttf:text='Same actual 120 frames / 75-80s. Fixed camera - route - EEVEE renderer - world - light - FX.':fontsize=27:fontcolor=white:x=(w-tw)/2:y=h-34[v]"
run(['-i',str(baseline),'-i',str(movie),'-filter_complex',filters,'-map','[v]','-map','1:a:0','-frames:v','120','-c:v','libx264','-crf','18','-preset','fast','-threads','4','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',str(comparison)]);decode(comparison)
assert view.stat().st_size<=20_000_000 and comparison.stat().st_size<=20_000_000
dense=folder/'decoded_dense';dense.mkdir();run(['-i',str(movie),'-vf','fps=8,scale=1920:1080:flags=lanczos','-frames:v','40',str(dense/'%03d.png')])
for version,path in [('v043',baseline),('v044',movie)]:
 cropped=folder/('native_actor_crops_'+version);cropped.mkdir();run(['-i',str(path),'-vf','crop=1440:1200:1400:480','-frames:v','120','-start_number','1801','-threads','2',str(cropped/'%04d.png')]);assert len(list(cropped.glob('*.png')))==120
for name,sha in build['preserved_inputs'].items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==sha,name
assert hashlib.sha256(source.read_bytes()).hexdigest()==build['source_sha256']
def item(path):return {'path':str(path),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
report={'status':'Native120frame export and matched review ready; dense artistic review pending.','source':item(source),'world_scene':build['world_scene'],'master_scene':build['master_scene'],'master':item(movie),'view':item(view),'matched_comparison':item(comparison),'reference_v043':item(baseline),'frames':[1801,1920],'frame_count':120,'fps':24,'seconds':5,'native_master_resolution':[3840,2160],'view_resolution':[1920,1080],'comparison_resolution':[3840,1080],'comparison_method':'Actual corresponding source frames, same EEVEE renderer/camera/travel/world/light/FX. Only performance and its associated material binding changed.','dense_directory':str(dense),'native_crop_directories':{v:str(folder/('native_actor_crops_'+v)) for v in ['v043','v044']},'crop_native_pixels':[1400,480,1440,1200],'preserved_inputs':build['preserved_inputs'],'library':'Local only; no upload attempted or bypass.'}
(R/'notes/world_v016/export_completed_v044.json').write_text(json.dumps(report,indent=2));(R/'notes/world_v016/render_status_v044.json').write_text(json.dumps({'phase':'exported; matched comparison and actual-frame crops ready','review':str(view),'comparison':str(comparison)},indent=2));print('V044_REVIEW_EXPORT_READY',json.dumps(report),flush=True)
