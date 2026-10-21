import subprocess,json,hashlib,re,wave
from pathlib import Path
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1];F=r'WTSC_LOCAL_USER\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
receipt=json.loads((R/'notes/world_v016/complete_completed_v034.json').read_text());movie=Path(receipt['movie']);view=Path(receipt['viewing_copy']['path']);native=json.loads((R/'notes/world_v016/complete_native_audit_v034.json').read_text())
assert receipt['full_decode_frames']==2472 and receipt['viewing_copy']['full_decode_frames']==2472
assert view.stat().st_size<20_000_000
assert hashlib.sha256(movie.read_bytes()).hexdigest()==receipt['movie_sha256']
assert hashlib.sha256(Path(receipt['source']).read_bytes()).hexdigest()==receipt['source_sha256']==native['source_sha256']
headers={}
for p,shape in [(movie,'3840x2160'),(view,'1280x720')]:
 raw=subprocess.run([F,'-hide_banner','-i',str(p)],capture_output=True,text=True).stderr
 assert 'Duration: 00:01:43.00' in raw and '24 fps' in raw and shape in raw and '48000 Hz, stereo' in raw
 headers[p.name]=[l.strip() for l in raw.splitlines() if 'Duration:' in l or 'Stream #' in l]
out=R/'renders/world_v016/complete_decoded_v034';out.mkdir(exist_ok=True)
samples=[('01_Village',0),('02_Village_Empty',20),('03_Woods',32),('04_School',44),('05_Camp',59),('06_Battlefield',75),('07_Last_World_Frame',1967/24),('08_Knockout_Start',82),('09_Knockout',89),('10_Last_S',2399/24),('11_Card_Start',100),('12_Card_End',2471/24)]
def frame(t,dest=None,small=False,path=movie):
 cmd=[F,'-v','error','-ss',str(t),'-i',str(path),'-frames:v','1']
 if small:cmd+=['-vf','scale=384:216']
 if dest:cmd+=['-y',str(dest)]
 else:cmd+=['-pix_fmt','rgb24','-f','rawvideo','-']
 r=subprocess.run(cmd,capture_output=True);assert r.returncode==0,r.stderr
 if dest:return np.asarray(Image.open(dest).convert('RGB'))
 return np.frombuffer(r.stdout,dtype=np.uint8).reshape(216 if small else2160,384 if small else3840,3)
sample_arrays={}
for name,t in samples:
 a=frame(t,out/(name+'.png'));assert a.shape==(2160,3840,3);sample_arrays[name]=a
assert sample_arrays['08_Knockout_Start'].max()<=5
assert np.mean(abs(sample_arrays['11_Card_Start'].astype(float)-sample_arrays['12_Card_End']))<.1
# Assembled ending is an exact video-stream reuse of v033: compare actual pixels.
ending=R/'renders/world_v016/WTSC_Knockout_Ending_4K_v033.mp4';ending_matches=[]
for t in [0,7,2399/24-82,18,2471/24-82]:
 a=frame(82+t,small=True);b=frame(t,small=True,path=ending);d=float(np.abs(a.astype(float)-b).mean());assert d<.01,(t,d);ending_matches.append({'global_seconds':82+t,'mean_pixel_difference':d})
# No timebase damage at any copy/render join.82 intentionally cuts to black.
joins=[]
for f in [1681,1753,1825,1897,1969]:
 t=(f-3)/24
 r=subprocess.run([F,'-v','error','-ss',str(t),'-i',str(movie),'-frames:v','4','-vf','scale=384:216','-pix_fmt','rgb24','-f','rawvideo','-'],capture_output=True);assert r.returncode==0
 a=np.frombuffer(r.stdout,dtype=np.uint8).reshape(4,216,384,3).astype(float);diff=[float(abs(a[i+1]-a[i]).mean()) for i in range(3)]
 if f!=1969:assert diff[1]<max(6,3*max(diff[0],diff[2])),(f,diff)
 joins.append({'first_frame':f,'global_seconds':(f-1)/24,'mean_adjacent_differences':diff,'intentional_black_title_cut':f==1969})
pcm=subprocess.run([F,'-v','error','-i',str(movie),'-map','0:a:0','-ar','48000','-ac','2','-f','s16le','-'],capture_output=True);assert pcm.returncode==0
audio=np.frombuffer(pcm.stdout,dtype='<i2').astype(float).reshape(-1,2)
with wave.open(str(R/'edit/When_The_Sky_Clears_Trailer_Music_100s.wav')) as w:
 assert w.getframerate()==48000 and w.getnchannels()==2 and w.getsampwidth()==2
 original=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float).reshape(-1,2)
def rms(a):return float(np.sqrt(np.mean(a*a)))
windows=[]
for a,b in [(10,11),(69,70),(81.5,82.5),(89,90),(92,93),(96,97),(99,100),(99.9,100),(100.05,102.95)]:
 got=audio[int(a*48000):int(b*48000)];ref=original[int(a*48000):int(b*48000)];gr=rms(got)
 row={'global_seconds':[a,b],'rms':gr,'source_rms':rms(ref) if len(ref) else None,'relative_to_source':gr/max(rms(ref),1e-8) if len(ref) else None}
 if b<=90:
  corr=float(np.corrcoef(got.reshape(-1),ref.reshape(-1))[0,1]);assert corr>.99 and .97<row['relative_to_source']<1.03,(a,row,corr);row['sample_alignment_correlation']=corr
 windows.append(row)
assert windows[-1]['rms']==0 and windows[-2]['relative_to_source']<.02 and windows[-3]['relative_to_source']<.1
# Master's72-card frames have no soundtrack; there is no82s split/restart.
assert next(x for x in windows if x['global_seconds']==[81.5,82.5])['sample_alignment_correlation']>.99
preserved={}
for rel,sha in [('shots/world/WTSC_Painted_World_Trailer_v030.blend','b68e097922883c9cb409da4d5a999a889be2ffc9768627824087f44745574bb6'),('renders/world_v016/WTSC_Painted_World_4K_v030.mp4','64729abab8e899cf717781f664d82ff1f3b6a8a02afaee82ec947c59f29b6999'),('shots/world/WTSC_Painted_World_Editable_v031.blend','ff2158da0174ba6b6ad985f82195d668857d84caded6c71101a7d6ca8f655bc4'),('shots/world/WTSC_Knockout_Ending_Editable_v032.blend','b71b3ec247a60e5d022121444c95ce47f3c1cbd7d1668233327e87e8da1df352'),('shots/world/WTSC_Knockout_Ending_Editable_v033.blend','a63d3b6a5780f6347f4f9db5b424709927f0009ba509caaf816657e8e4c0ee7b'),('renders/world_v016/WTSC_Knockout_Ending_4K_v033.mp4','58d0c802e00b147a0074533af0cad61a7f51babaab1c2def348a8665c05ab2ef')]:
 got=hashlib.sha256((R/rel).read_bytes()).hexdigest();assert got==sha;preserved[rel]=got
report={**receipt,'headers':headers,'native_camera_audit':'complete_native_audit_v034.json','picture_scope':'0–70 cached2x crop (effective1080);70–82 native UHD matching crop;82–103 exactv033 ending reuse (4K text,1080 cached fill). Pair shared center and size held through82. No retime/interpolation.','transition82':'Intentional cut to black at82 as text starts entering; clean52–70 scenery reused inside knockout, so geography restarts rather than continuing battlefield. Framing center/size remains consistent.','joins':joins,'exact_ending_pixel_checks':ending_matches,'audio_windows':windows,'preserved_prior_sha256':preserved,'decoded_review_stills':[str(out/(name+'.png')) for name,_ in samples],'quality_scope':'Technically complete bounded trailer revision with held characters; does not establish final artistic approval.'}
(R/'notes/world_v016/complete_verification_v034.json').write_text(json.dumps(report,indent=2));print('COMPLETE_TRAILER_QC_PASSED',json.dumps({'movie':str(movie),'frames':2472,'seconds':103,'viewing_copy':receipt['viewing_copy'],'joins':joins,'audio_windows':windows}),flush=True)
