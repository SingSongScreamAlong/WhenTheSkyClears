import subprocess,json,re,hashlib,wave,sys
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
FFMPEG=r'WTSC_LOCAL_USER\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
version=sys.argv[1] if len(sys.argv)>1 else 'v006'
assert version in ['v004','v006','v010']
movie=ROOT/f'renders/living_world/WTSC_Living_World_4K_{version}.mp4' if version=='v010' else ROOT/f'renders/world/WTSC_World_Atmosphere_4K_{version}.mp4'
assert movie.is_file()
decode=subprocess.run([FFMPEG,'-hide_banner','-i',str(movie),'-progress','pipe:1','-f','null','NUL'],capture_output=True,text=True)
assert decode.returncode==0,decode.stderr[-2000:]
counts=re.findall(r'^frame=(\d+)',decode.stdout,re.M)
assert counts and int(counts[-1])==2400
metadata=[s.strip() for s in decode.stderr.splitlines() if 'Duration:' in s or 'Stream #' in s]
assert any('3840x2160' in s and '24 fps' in s for s in metadata)
assert any('Duration: 00:01:40.00' in s for s in metadata)
assert any('Audio: aac' in s and '48000 Hz, stereo' in s for s in metadata)

qa=ROOT/f'renders/living_world/decoded_review_{version}' if version=='v010' else ROOT/f'renders/world/decoded_review_{version}'
qa.mkdir(exist_ok=True)
samples=[('01_Village',0),('02_Woods',36),('03_School',52),('04_Camp',62),('05_Battlefield',74),('06_Title',95),('07_Last_Frame',2399/24)]
for name,seconds in samples:
    dest=qa/(name+'.png')
    p=subprocess.run([FFMPEG,'-v','error','-ss',str(seconds),'-i',str(movie),'-frames:v','1','-y',str(dest)],capture_output=True,text=True)
    assert p.returncode==0,p.stderr
    assert Image.open(dest).size==(3840,2160)
last=np.asarray(Image.open(qa/'07_Last_Frame.png'))
assert int(last.max())<=2,('last frame not black',int(last.max()))

pcm=subprocess.run([FFMPEG,'-v','error','-i',str(movie),'-map','0:a:0','-ar','48000','-ac','2','-t','100','-f','s16le','-'],capture_output=True)
assert pcm.returncode==0
audio=np.frombuffer(pcm.stdout,dtype='<i2').astype(np.float64).reshape(-1,2)
with wave.open(str(ROOT/'edit/When_The_Sky_Clears_Trailer_Music_100s.wav')) as w:
    original=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float64).reshape(-1,2)
def rms(a):return float(np.sqrt(np.mean(a*a)))
windows=[]
for start,end in [(10,11),(89,90),(92,93),(96,97),(99,100),(99.9,100)]:
    a=int(start*48000);b=int(end*48000)
    ref=rms(original[a:b]);got=rms(audio[a:b]);windows.append({'seconds':[start,end],'source_rms':ref,'export_rms':got,'relative_rms':got/max(ref,1e-8)})
assert windows[0]['export_rms']>0
assert windows[-2]['relative_rms']<.10
assert windows[-1]['relative_rms']<.02
boundaries=[]
if version in ['v006','v010']:
    for first_new_frame in ([1081,1411,1741,2071] if version=='v006' else [601,1201,1801]):
        p=subprocess.run([FFMPEG,'-v','error','-ss',str((first_new_frame-3)/24),'-i',str(movie),'-frames:v','4','-vf','scale=384:216','-pix_fmt','rgb24','-f','rawvideo','-'],capture_output=True)
        assert p.returncode==0
        a=np.frombuffer(p.stdout,dtype=np.uint8).reshape(4,216,384,3).astype(float)
        differences=[float(np.mean(abs(a[i+1]-a[i]))) for i in range(3)]
        assert differences[1]<max(5,3*max(differences[0],differences[2])),(first_new_frame,differences)
        boundaries.append({'first_new_frame':first_new_frame,'adjacent_frame_mean_differences':differences})
report={'path':str(movie),'sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),'bytes':movie.stat().st_size,
        'decode_exit_code':decode.returncode,'decoded_frames':2400,'fps':24,'resolution':[3840,2160],
        'duration_seconds':100.0,'metadata':metadata,'last_frame_max_pixel':int(last.max()),
        'audio_fade_windows':windows,'render_boundaries':boundaries,'review_frames':[str(qa/(name+'.png')) for name,_ in samples],
        'native_character_motion':'one held GP drawing, location channels only; no limb animation',
        'review_status':'Technical decode/duration/source persistence verified. Artistic approval not granted.'}
(ROOT/'notes/world_movie_verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
(ROOT/f'notes/world_movie_verification_{version}.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
if version=='v010':(ROOT/'notes/living_world/movie_verification_v010.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ['review_frames','metadata']}))
