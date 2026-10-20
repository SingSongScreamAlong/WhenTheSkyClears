from pathlib import Path
import json,hashlib,subprocess,re,array,math
from PIL import Image,ImageChops
import imageio_ffmpeg
O=Path(r'WTSC_LOCAL_WORKSPACE\work\production_review_v059');R=O.parents[1];F=imageio_ffmpeg.get_ffmpeg_exe()
p=O/'WTSC_Recovery_Benchmark_v059_720p.mp4'
def pcm(args):
 q=subprocess.run([F,'-v','error']+args+['-ac','1','-ar','48000','-f','s16le','pipe:1'],capture_output=True,check=True);a=array.array('h');a.frombytes(q.stdout);return a
a=pcm(['-i',str(p),'-map','0:a:0','-t','5'])
b=pcm(['-ss','75','-i',str(R/'edit/When_The_Sky_Clears_Trailer_Music_100s.wav'),'-t','5'])
n=min(len(a),len(b));mean_a=sum(a[:n])/n;mean_b=sum(b[:n])/n
num=sum((x-mean_a)*(y-mean_b) for x,y in zip(a[:n],b[:n]));da=sum((x-mean_a)**2 for x in a[:n]);db=sum((x-mean_b)**2 for x in b[:n]);corr=num/math.sqrt(da*db)
q=subprocess.run([F,'-hide_banner','-i',str(p)],capture_output=True,text=True)
duration=re.search(r'Duration:\s*([0-9:.]+)',q.stderr).group(1)
assert corr>.99,(corr,n)
assert duration=='00:00:05.00',duration
im1=Image.open(O/'native_master_frame101.png').convert('RGB');im2=Image.open(O/'frames_world/1901.png').convert('RGB');exact=ImageChops.difference(im1,im2).getbbox() is None;assert exact
sfx=json.loads((O/'integration_v059b.json').read_text())['painted_impact']
assert hashlib.sha256(Path(sfx['path']).read_bytes()).hexdigest()==sfx['sha256']
refs=json.loads((O/'integration_inspection.json').read_text())['sources'];assert all(hashlib.sha256(Path(k).read_bytes()).hexdigest()==v for k,v in refs.items())
native=O/'WTSC_Production_Benchmark_v059.blend';package=json.loads((O/'final_package_verification.json').read_text());assert hashlib.sha256(native.read_bytes()).hexdigest()==package['file_sha256']
names=['WTSC_Production_Benchmark_v059.blend','WTSC_Recovery_Benchmark_v059_720p.mp4','WTSC_Recovery_Benchmark_v059_Review.mp4','WTSC_Before_After_v048a_v059.mp4','Hand_Contact_Before_After_v059.jpg','Title_Visibility_Review_CORRECTED_v059.jpg','START_HERE_v059.txt']
manifest={'files':{name:{'bytes':(O/name).stat().st_size,'sha256':hashlib.sha256((O/name).read_bytes()).hexdigest()} for name in names},'audio':{'original_excerpt_seconds':[75,80],'decoded_samples_compared':n,'sample_rate':48000,'correlation_to_original_excerpt':corr,'actual_movie_duration':duration},'native_master_frame101_exact_world1901_rgb':exact,'original_sources_and_painted_effect_source_unchanged':True,'full_film_finished':False,'artistic_acceptance':False,'title_diagnostic':'Title_Visibility_Review_CORRECTED_v059.jpg supersedes earlier stale-clock diagnostic.'}
(O/'DELIVERY_MANIFEST_v059.json').write_text(json.dumps(manifest,indent=2))
print('FINAL_DELIVERY_VERIFIED',json.dumps({'audio_correlation':corr,'duration':duration,'native_master_pixel_exact':exact,'native_bytes':native.stat().st_size}),flush=True)
