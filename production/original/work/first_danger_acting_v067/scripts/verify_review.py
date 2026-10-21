import subprocess,json,re,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
import imageio_ffmpeg
O=Path(__file__).resolve().parents[1];FF=imageio_ffmpeg.get_ffmpeg_exe();D=json.loads((O/'evidence/DELIVERY.json').read_text());F=subprocess.CREATE_NO_WINDOW
def run(args):return subprocess.run([FF,'-hide_banner','-nostdin',*args],capture_output=True,timeout=90,creationflags=F)
records=[]
for row in D['outputs']:
 p=Path(row['path']);r=run(['-v','info','-i',str(p),'-map','0:v:0','-vf','showinfo','-f','null','NUL']);assert r.returncode==0
 log=r.stderr.decode(errors='replace');frames=[(int(n),float(t)) for n,t in re.findall(r'\bn:\s*(\d+)\s+pts:\s*-?\d+\s+pts_time:\s*([\d.eE+-]+)',log)]
 assert len(frames)==168,(p,len(frames));maxerror=max(abs(t-n/24) for n,t in frames);assert maxerror<.00001
 audio=run(['-v','error','-i',str(p),'-map','0:a:0','-ac','1','-ar','24000','-f','f32le','pipe:1']);assert audio.returncode==0
 signal=np.frombuffer(audio.stdout,dtype=np.float32);assert len(signal)>=7*24000
 ref=run(['-v','error','-ss','38','-t','7','-i',D['audio'],'-ac','1','-ar','24000','-f','f32le','pipe:1']);assert ref.returncode==0
 source=np.frombuffer(ref.stdout,dtype=np.float32);n=min(len(source),len(signal));corr=float(np.corrcoef(source[:n],signal[:n])[0,1]);assert corr>.99,(p,corr)
 records.append({'path':str(p),'actual_frames':len(frames),'max_timestamp_error_seconds':maxerror,'audio_source_correlation':corr,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
after=O/'previews/WTSC_First_Danger_Acting_v067_Unmasked_24fps.mp4';keys=[957,990,1016]
expr='+'.join(f'eq(n\\,{g-913})' for g in keys)
r=run(['-v','error','-i',str(after),'-vf',f'select={expr}','-fps_mode','vfr','-pix_fmt','rgb24','-f','rawvideo','pipe:1']);assert r.returncode==0
arr=np.frombuffer(r.stdout,dtype=np.uint8).reshape(3,720,1280,3);color=[]
for i,g in enumerate(keys):
 ref=np.array(Image.open(O/f'renders/final_review/world/{g:04d}.png').convert('RGB'));err=arr[i].astype(float)-ref.astype(float);mae=float(abs(err).mean());bias=float(err.mean());assert mae<3 and abs(bias)<1.5
 color.append({'global_frame':g,'RGB_mean_absolute_error':mae,'RGB_signed_mean_error':bias})
assert all(Image.open(O/f'renders/uhd_C/final/{g:04d}.png').size==(3840,2160) for g in keys)
B=json.loads((O/'evidence/BUILD.json').read_text());source_ok=hashlib.sha256(Path(B['source']).read_bytes()).hexdigest()==B['source_sha256'];native_ok=hashlib.sha256(Path(B['native']).read_bytes()).hexdigest()==B['native_sha256'];assert source_ok and native_ok
out={'outputs':records,'encoded_to_actual_render_color':color,'UHD_keys':keys,'source_unchanged':source_ok,'candidate_unchanged':native_ok,'passed':True,'artistic_review':'Decoded chronological images, matched key comparisons and actual UHD keys inspected; user normal-speed approval pending.'}
(O/'evidence/REVIEW_QA.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
