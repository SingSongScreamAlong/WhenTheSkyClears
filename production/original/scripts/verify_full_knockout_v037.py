import subprocess,json,hashlib,re,wave
from pathlib import Path
import numpy as np
from PIL import Image,ImageFilter
R=Path(__file__).resolve().parents[1]
F=r'WTSC_LOCAL_USER\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
receipt=json.loads((R/'notes/world_v016/full_completed_v037.json').read_text());native=json.loads((R/'notes/world_v016/full_native_audit_v037.json').read_text());build=json.loads((R/'notes/world_v016/full_knockout_build_v037.json').read_text())
movie=Path(receipt['movie']);view=Path(receipt['viewing_copy']['path']);source=Path(receipt['source'])
assert receipt['full_decode_frames']==2544 and receipt['viewing_copy']['frames']==2544 and view.stat().st_size<20_000_000
assert hashlib.sha256(movie.read_bytes()).hexdigest()==receipt['movie_sha256']
assert hashlib.sha256(source.read_bytes()).hexdigest()==receipt['source_sha256']==native['source_sha256']
combine_log=(R/'renders/world_v016/full_parts_v037/combine.log').read_text(errors='replace')
dups=[int(x) for x in re.findall(r'^dup_frames=(\d+)',combine_log,re.M)];drops=[int(x) for x in re.findall(r'^drop_frames=(\d+)',combine_log,re.M)]
assert max(dups or [0])==0 and max(drops or [0])==0
headers={}
for path,shape in [(movie,'3840x2160'),(view,'1280x720')]:
 raw=subprocess.run([F,'-hide_banner','-i',str(path)],capture_output=True,text=True).stderr
 duration=re.search(r'Duration: (\d+):(\d+):([\d.]+)',raw);assert duration
 seconds=3600*int(duration[1])+60*int(duration[2])+float(duration[3])
 assert abs(seconds-106)<(.001 if path==movie else .022) and '24 fps' in raw and shape in raw and '48000 Hz, stereo' in raw
 headers[path.name]=[l.strip() for l in raw.splitlines() if 'Duration:' in l or 'Stream #' in l]
out=R/'renders/world_v016/full_decoded_v037';out.mkdir(exist_ok=True)
def frame(path,t,small=False,dest=None):
 cmd=[F,'-v','error','-ss',str(t),'-i',str(path),'-frames:v','1']
 if small:cmd+=['-vf','scale=384:216']
 if dest:cmd+=['-y',str(dest)]
 else:cmd+=['-pix_fmt','rgb24','-f','rawvideo','-']
 r=subprocess.run(cmd,capture_output=True);assert r.returncode==0,r.stderr
 if dest:return np.asarray(Image.open(dest).convert('RGB'))
 return np.frombuffer(r.stdout,dtype=np.uint8).reshape(216 if small else 2160,384 if small else 3840,3)
samples=[('01_Start',1),('02_Village',241),('03_Village_Empty',481),('04_Woods',841),('05_School',1201),('06_Camp',1609),('07_Battlefield',1921),('08_Ruins',2161),('09_Last_S',2400),('10_Credits_Start',2401),('11_Credits_Last',2544)]
sample_arrays={};mask_qc=[]
for name,f in samples:
 a=frame(movie,(f-1)/24,dest=out/(name+'.png'));assert a.shape==(2160,3840,3);sample_arrays[name]=a
 if f<=2400:
  part=(f-1)//600+1;local=(f-1)%600;mask=frame(R/f'renders/world_v016/full_parts_v037/mask_{part:02d}.mp4',local/24)
  gray=Image.fromarray(mask[:,:,0]);outside=np.asarray(gray.filter(ImageFilter.MaxFilter(17)))==0
  maximum=int(a[outside].max());assert maximum<=6,(f,maximum)
  mask_qc.append({'frame':f,'seconds':(f-1)/24,'far_outside_glyph_max_pixel':maximum,'glyph_alpha_pixels':int(np.count_nonzero(mask[:,:,0]))})
  if f==2400:
   ys,xs=np.where(mask[:,:,0]>127);assert len(xs)>0 and int(xs.max())<50,int(xs.max());mask_qc[-1]['final_S_remaining_rightmost_pixel']=int(xs.max())
assert sample_arrays['01_Start'].max()<=5
assert float(abs(sample_arrays['10_Credits_Start'].astype(float)-sample_arrays['11_Credits_Last']).mean())<.1
credits_native=np.asarray(Image.open(R/'renders/world_v016/full_knockout_checks_v037/2401.png').convert('RGB'));credit_error=float(abs(sample_arrays['10_Credits_Start'].astype(float)-credits_native).mean());assert credit_error<1
# Decode four frames around each native block join. Font masks share the same
# integer frame numbers, so no image/mask timebase drift is allowed.
joins=[]
for f in [601,1201,1801,2401]:
 t=(f-3)/24
 r=subprocess.run([F,'-v','error','-ss',str(t),'-i',str(movie),'-frames:v','4','-vf','scale=384:216','-pix_fmt','rgb24','-f','rawvideo','-'],capture_output=True);assert r.returncode==0
 a=np.frombuffer(r.stdout,dtype=np.uint8).reshape(4,216,384,3).astype(float);diff=[float(abs(a[i+1]-a[i]).mean()) for i in range(3)]
 if f!=2401:assert diff[1]<max(5,3*max(diff[0],diff[2])),(f,diff)
 joins.append({'first_frame':f,'seconds':(f-1)/24,'adjacent_pixel_differences':diff,'intentional_credit_cut':f==2401})
native_checks=[]
for f in [241,841,1201,1609,2161]:
 actual=frame(movie,(f-1)/24);ref=np.asarray(Image.open(R/f'renders/world_v016/full_knockout_checks_v037/{f}.png').convert('RGB'));difference=float(abs(actual.astype(float)-ref).mean());assert difference<3,(f,difference);native_checks.append({'frame':f,'movie_vs_native_compositor_mean_error':difference})
pcm=subprocess.run([F,'-v','error','-i',str(movie),'-map','0:a:0','-ar','48000','-ac','2','-f','s16le','-'],capture_output=True);assert pcm.returncode==0
audio=np.frombuffer(pcm.stdout,dtype='<i2').astype(float).reshape(-1,2)
with wave.open(str(R/'edit/When_The_Sky_Clears_Trailer_Music_100s.wav')) as wav:
 assert wav.getframerate()==48000 and wav.getnchannels()==2 and wav.getsampwidth()==2
 original=np.frombuffer(wav.readframes(wav.getnframes()),dtype='<i2').astype(float).reshape(-1,2)
def rms(a):return float(np.sqrt(np.mean(a*a)))
windows=[]
for a,b in [(10,11),(24.5,25.5),(49.5,50.5),(74.5,75.5),(81.5,82.5),(89,90),(92,93),(96,97),(99,100),(99.9,100),(100.05,105.95)]:
 got=audio[int(a*48000):int(b*48000)];ref=original[int(a*48000):int(b*48000)];v={'global_seconds':[a,b],'output_rms':rms(got),'source_rms':rms(ref) if len(ref) else None,'relative_to_source':rms(got)/max(rms(ref),1e-8) if len(ref) else None}
 if b<=90:
  correlation=float(np.corrcoef(got.reshape(-1),ref.reshape(-1))[0,1]);assert correlation>.99 and .97<v['relative_to_source']<1.03,(a,v,correlation);v['source_sample_alignment_correlation']=correlation
 windows.append(v)
assert windows[-1]['output_rms']==0 and windows[-2]['relative_to_source']<.02 and windows[-3]['relative_to_source']<.1
expected=['WHEN THE','SKY CLEARS.','The Animated Series.','2027.','A Two Truck Productions project.'];assert build['card_exact_lines']==expected and sorted(native['exact_card_bodies'])==sorted(expected)
preserved={}
for rel,sha in [('shots/world/WTSC_Painted_World_Trailer_v030.blend','b68e097922883c9cb409da4d5a999a889be2ffc9768627824087f44745574bb6'),('renders/world_v016/WTSC_Painted_World_4K_v030.mp4','64729abab8e899cf717781f664d82ff1f3b6a8a02afaee82ec947c59f29b6999'),('shots/world/WTSC_Knockout_Ending_Editable_v033.blend','a63d3b6a5780f6347f4f9db5b424709927f0009ba509caaf816657e8e4c0ee7b'),('renders/world_v016/WTSC_Knockout_Ending_4K_v033.mp4','58d0c802e00b147a0074533af0cad61a7f51babaab1c2def348a8665c05ab2ef'),('shots/world/WTSC_World_Spatial_Corrections_v035.blend','c2310b87557e94ce403ac562d3ded61d7e84e34d3047136751c189b0aec9dd1b')]:
 got=hashlib.sha256((R/rel).read_bytes()).hexdigest();assert got==sha,(rel,got);preserved[rel]=got
report={**receipt,'metadata':headers,'mask_black_checks':mask_qc,'native_compositor_matches':native_checks,'render_boundaries':joins,'credit_native_mean_error':credit_error,'exact_credit_lines':expected,'audio_timing_and_fade_checks':windows,'native_audit':'notes/world_v016/full_native_audit_v037.json','preserved_prior_files':preserved,'review_frames':[str(out/(n+'.png')) for n,_ in samples],'picture_scope':'All100seconds fresh native4K correctedworld through native4K FontAlpha. No output scaling/interpolation; source paintings mostly1672x941. Same held painterlypair.','scope':'Technical delivery verification and actualdecodedframe inspection; not final artistic acceptance.'}
(R/'notes/world_v016/full_verification_v037.json').write_text(json.dumps(report,indent=2));print('FULL_106S_TRAILER_QC_PASSED',json.dumps({'movie':str(movie),'viewing_copy':receipt['viewing_copy'],'mask_qc':mask_qc,'joins':joins,'audio':windows}),flush=True)
