"""Run only after the preserved v037 production workload is complete."""
import subprocess,json,time,re,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];B=r'WTSC_LOCAL_USER\AppData\Local\Programs\Blender\blender-5.2.2-windows-x64\blender.exe';F=r'WTSC_LOCAL_USER\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
status=json.loads((R/'notes/world_v016/full_render_status_v037.json').read_text());assert status['phase']=='complete','Preserve production: wait until037 finishes'
receipt=json.loads((R/'notes/world_v016/full_completed_v037.json').read_text());assert receipt.get('viewing_copy')
source=R/'shots/world/WTSC_Camp_Light_Ground_Benchmark_v039.blend';source_sha=hashlib.sha256(source.read_bytes()).hexdigest();folder=R/'renders/world_v016/camp_benchmark_v039';folder.mkdir(exist_ok=True);world=folder/'WTSC_Camp_World_64_69_v039.mp4';assert not world.exists()
log=folder/'native_world.log';stream=log.open('w',encoding='utf8');p=subprocess.Popen([B,'--background','--factory-startup',str(source),'--threads','3','--python',str(R/'scripts/render_full_component_v037.py'),'--','world','1537','1656',str(world),'039'],cwd=R,stdout=stream,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
print('CAMP_NATIVE_5S_STARTED',p.pid,1537,1656,flush=True)
while p.poll() is None:
 tail=log.read_text(errors='replace')[-10000:];n=re.findall(r'Video append frame (\d+)',tail);done=int(n[-1])-1536 if n else 0;(R/'notes/world_v016/camp_render_status_v039.json').write_text(json.dumps({'phase':'native five-second benchmark','pid':p.pid,'done':done,'total':120,'global_frames':[1537,1656],'maximum_parallel_blender':1},indent=2));print('CAMP_BENCHMARK_PROGRESS',done,120,flush=True);time.sleep(25)
stream.close();assert p.returncode==0 and 'COMPONENT_COMPLETED' in log.read_text(errors='replace'),log.read_text()[-2500:]
def run(args):
 r=subprocess.run([F,'-hide_banner','-nostdin']+args,capture_output=True,text=True,cwd=r'C:\Windows\Fonts');assert r.returncode==0,r.stderr[-3500:];return r.stderr
def decode(p):
 r=subprocess.run([F,'-v','error','-i',str(p),'-progress','pipe:1','-f','null','NUL'],capture_output=True,text=True);n=re.findall(r'^frame=(\d+)',r.stdout,re.M);assert r.returncode==0 and int(n[-1])==120,(p,r.stderr,n[-1:])
decode(world)
masked=folder/'WTSC_Camp_Knockout_64_69_v039.mp4'
run(['-i',str(world),'-ss','14','-t','5','-i',str(R/'renders/world_v016/full_parts_v037/mask_03.mp4'),'-filter_complex','[0:v]format=gbrp[a];[1:v]format=gbrp[b];[a][b]blend=all_mode=multiply:shortest=1[v]','-map','[v]','-an','-c:v','libx264','-crf','16','-preset','fast','-threads','4','-pix_fmt','yuv420p','-r','24','-t','5',str(masked)]);decode(masked)
baseline_world=folder/'Baseline_v037_World_64_69.mp4';baseline_mask=folder/'Baseline_v037_Knockout_64_69.mp4'
for source_movie,offset,out in [(R/'renders/world_v016/full_parts_v037/world_03.mp4',14,baseline_world),(Path(receipt['movie']),64,baseline_mask)]:
 run(['-ss',str(offset),'-i',str(source_movie),'-t','5','-an','-c:v','libx264','-preset','fast','-crf','16','-threads','4','-pix_fmt','yuv420p','-r','24',str(out)]);decode(out)
comparison=folder/'WTSC_Camp_5s_Baseline_vs_Study_v039.mp4'
inputs=[]
for f in [baseline_world,world,baseline_mask,masked]:inputs+=['-i',str(f)]
labels=['BASELINE v037 | WORLD | 64-69s','STUDY v039 | WORLD | 64-69s','BASELINE v037 | KNOCKOUT','STUDY v039 | KNOCKOUT']
filters=[]
for i,text in enumerate(labels):filters.append(f"[{i}:v]scale=960:540,drawbox=x=0:y=0:w=iw:h=34:color=black@0.75:t=fill,drawtext=fontfile=arial.ttf:text='{text}':fontsize=23:fontcolor=white:x=14:y=5[p{i}]")
filters+=['[p0][p1]hstack=inputs=2[top]','[p2][p3]hstack=inputs=2[bottom]','[top][bottom]vstack=inputs=2[v]']
run(inputs+['-ss','64','-t','5','-i',str(R/'edit/When_The_Sky_Clears_Trailer_Music_100s.wav'),'-filter_complex',';'.join(filters),'-map','[v]','-map','4:a:0','-t','5','-c:v','libx264','-crf','18','-preset','fast','-threads','4','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',str(comparison)]);decode(comparison)
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_sha
manifest={'benchmark_seconds':[64,69],'frames':[1537,1656],'decoded_frames':120,'fps':24,'source':str(source),'source_sha256':source_sha,'baseline_movie':receipt['movie'],'baseline_world':str(baseline_world),'baseline_knockout':str(baseline_mask),'study_world':str(world),'study_knockout':str(masked),'comparison':str(comparison),'comparison_resolution':[1920,1080],'comparison_bytes':comparison.stat().st_size,'comparison_sha256':hashlib.sha256(comparison.read_bytes()).hexdigest(),'native_study_resolution':[3840,2160],'source_audio':'Original global64–69 segment in comparison only; no timing change to full film','mask_source':'Exact unchanged nativeFontalpha fromv037 at source global64–69; no obsoleteworld reused in study.','v001_pack_used':False,'stage':'Actual moving comparison ready for visual QA, no artistic approval inferred. Full updated film still pending propagation/QA.'}
(R/'notes/world_v016/camp_comparison_completed_v039.json').write_text(json.dumps(manifest,indent=2));(R/'notes/world_v016/camp_render_status_v039.json').write_text(json.dumps({'phase':'comparison ready','comparison':str(comparison)},indent=2));print('CAMP_5S_COMPARISON_READY',json.dumps(manifest),flush=True)
