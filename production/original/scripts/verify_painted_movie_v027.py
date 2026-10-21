"""Final artifact QC; full-frame decode receipt comes from the native render controller."""
import subprocess,json,re,hashlib,wave
from pathlib import Path
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1]
F=r'WTSC_LOCAL_USER\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
movie=R/'renders/world_v016/WTSC_Painted_World_4K_v027.mp4'
completed=json.loads((R/'notes/world_v016/native_completed_v027.json').read_text())
assert completed['full_decode_ok'] and completed['full_decode_frames']==2400
assert completed['sha256']==hashlib.sha256(movie.read_bytes()).hexdigest()
assert completed['source_sha256']==hashlib.sha256(Path(completed['source']).read_bytes()).hexdigest()
header=subprocess.run([F,'-hide_banner','-i',str(movie)],capture_output=True,text=True)
metadata=[x.strip() for x in header.stderr.splitlines() if 'Duration:' in x or 'Stream #' in x]
assert any('3840x2160' in x and '24 fps' in x for x in metadata),metadata
assert any('Duration: 00:01:40.00' in x for x in metadata),metadata
assert any('Audio: aac' in x and '48000 Hz, stereo' in x for x in metadata),metadata
out=R/'renders/world_v016/decoded_review_v027';out.mkdir(exist_ok=True)
samples=[('01_Village',0),('02_Village_Empty',20),('03_Woods',32),('04_School',44),('05_Camp',59),('06_Battlefield',74),('07_Title',96),('08_Fade_98s',98),('09_Fade_99s',99),('10_Fade_99p75s',99.75),('11_Last_Frame',2399/24)]
means={}
for name,t in samples:
    dest=out/(name+'.png');assert not dest.exists(),dest
    p=subprocess.run([F,'-v','error','-ss',str(t),'-i',str(movie),'-frames:v','1',str(dest)],capture_output=True,text=True);assert p.returncode==0,p.stderr
    im=Image.open(dest);assert im.size==(3840,2160);arr=np.asarray(im);means[name]=float(arr.mean())
last=np.asarray(Image.open(out/'11_Last_Frame.png'));assert int(last.max())<=2
assert means['08_Fade_98s']>means['09_Fade_99s']>means['10_Fade_99p75s']>means['11_Last_Frame']
pcm=subprocess.run([F,'-v','error','-i',str(movie),'-map','0:a:0','-ar','48000','-ac','2','-t','100','-f','s16le','-'],capture_output=True);assert pcm.returncode==0
audio=np.frombuffer(pcm.stdout,dtype='<i2').astype(np.float64).reshape(-1,2)
with wave.open(str(R/'edit/When_The_Sky_Clears_Trailer_Music_100s.wav')) as w:
    assert w.getframerate()==48000 and w.getnchannels()==2 and w.getsampwidth()==2
    original=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float64).reshape(-1,2)
def rms(a):return float(np.sqrt(np.mean(a*a)))
windows=[]
for a,b in [(10,11),(89,90),(92,93),(96,97),(99,100),(99.9,100)]:
    ref=rms(original[int(a*48000):int(b*48000)]);got=rms(audio[int(a*48000):int(b*48000)]);windows.append({'seconds':[a,b],'source_rms':ref,'output_rms':got,'relative_rms':got/max(ref,1e-8)})
assert windows[0]['output_rms']>0
assert windows[-2]['relative_rms']<.1 and windows[-1]['relative_rms']<.02
boundaries=[]
for first in [601,1201,1801]:
    p=subprocess.run([F,'-v','error','-ss',str((first-3)/24),'-i',str(movie),'-frames:v','4','-vf','scale=384:216','-pix_fmt','rgb24','-f','rawvideo','-'],capture_output=True);assert p.returncode==0
    a=np.frombuffer(p.stdout,dtype=np.uint8).reshape(4,216,384,3).astype(float);diff=[float(np.mean(abs(a[i+1]-a[i]))) for i in range(3)];assert diff[1]<max(5,3*max(diff[0],diff[2])),(first,diff);boundaries.append({'first_new_frame':first,'adjacent_mean_differences':diff})
report={'movie':str(movie),'source':completed['source'],'source_sha256':completed['source_sha256'],'movie_sha256':completed['sha256'],'bytes':movie.stat().st_size,'resolution':[3840,2160],'fps':24,'frames':2400,'duration_seconds':100,'full_decode':'2400 video frames decoded successfully in render controller; source hash frozen across render','metadata':metadata,'picture_fade_means':means,'last_frame_max_pixel':int(last.max()),'audio_fade_windows':windows,'chunk_boundaries':boundaries,'decoded_review_frames':[str(out/(name+'.png')) for name,_ in samples],'scope':'World animation pass, held painterly children; artistic finish and performance remain subject to review.'}
(R/'notes/world_v016/movie_verification_v027.json').write_text(json.dumps(report,indent=2))
print('FINAL_MOVIE_QC_PASSED',json.dumps({k:v for k,v in report.items() if k not in ['metadata','decoded_review_frames']}),flush=True)
