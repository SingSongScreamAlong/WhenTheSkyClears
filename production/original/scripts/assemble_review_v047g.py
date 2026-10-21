"""Assemble unchanged47 actual4K frames plus the73 newly rendered matching-profile frames."""
import subprocess,json,hashlib,re
from pathlib import Path
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1];N=R/'notes/improvement_v047';D=R/'renders/refinement_v047g'
F=r'WTSC_LOCAL_USER\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
log=(N/'movie_v047g.log').read_text(errors='replace');assert 'V047_RENDER_COMPLETED v047g tail' in log and 'Traceback' not in log
prefix=R/'renders/refinement_v047f/WTSC_Refinement_v047f_75_80_4K.mp4';tail=D/'WTSC_Refinement_v047g_Tail_1848_1920_4K.mp4';out=D/'WTSC_Refinement_v047g_75_80_4K.mp4';assert not out.exists()
audits=[]
for frame in [1842,1844,1846]:
 a=np.array(Image.open(R/f'renders/refinement_v047f/Head_{frame}_Native4KPixels.png')).astype(int)
 b=np.array(Image.open(D/f'Head_{frame}_Native4KPixels.png')).astype(int)
 maximum=int(np.max(np.abs(a-b)));assert maximum==0,(frame,maximum)
 audits.append({'frame':frame,'native_head_image_max_channel_difference':maximum})
filters='[0:v]trim=end_frame=47,setpts=PTS-STARTPTS[a];[1:v]setpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=1:a=0[v]'
args=[F,'-v','error','-nostdin','-i',str(prefix),'-i',str(tail),'-ss','75','-t','5','-i',str(R/'edit/When_The_Sky_Clears_Trailer_Music_100s.wav'),'-filter_complex',filters,'-map','[v]','-map','2:a:0','-frames:v','120','-c:v','libx264','-crf','17','-preset','fast','-threads','4','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(out)]
result=subprocess.run(args,capture_output=True,text=True);assert result.returncode==0,result.stderr[-3000:]
result=subprocess.run([F,'-v','error','-i',str(out),'-progress','pipe:1','-f','null','NUL'],capture_output=True,text=True);assert result.returncode==0,result.stderr
counts=re.findall(r'^frame=(\d+)',result.stdout,re.M);assert counts and int(counts[-1])==120
def item(p):return {'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
receipt={'status':'Actual4K review assembled and120frames fully decoded.',
 'prefix':item(prefix),'prefix_native_frames':[1801,1847],'prefix_frame_count':47,
 'new_native_tail':item(tail),'tail_frames':[1848,1920],'tail_frame_count':73,
 'output':item(out),'frames':120,'fps':24,'resolution':[3840,2160],
 'native_unchanged_prefix_key_audits':audits,
 'method':'First47 unchanged nativeF4K frames plus73 newly rendered nativeG4K frames, decoded and encoded as one review movie. Original75-80second WAV segment remuxed as AAC. No scaling, frame interpolation or invented frames.',
 'native_current_file':'shots/world/WTSC_Open_Battlefield_Refinement_v047g.blend','artistic_acceptance':False}
(N/'assembly_v047g.json').write_text(json.dumps(receipt,indent=2));print('V047G_NATIVE_REVIEW_ASSEMBLED',json.dumps(receipt),flush=True)
