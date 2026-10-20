import subprocess,json,hashlib,wave,re
from pathlib import Path
import numpy as np
from PIL import Image,ImageFilter
R=Path(__file__).resolve().parents[1];F=r'WTSC_LOCAL_USER\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
movie=R/'renders/world_v016/WTSC_Knockout_Ending_4K_v033.mp4'
out=R/'renders/world_v016/ending_decoded_v033';out.mkdir(exist_ok=True)
completed=json.loads((R/'notes/world_v016/ending_completed_v033.json').read_text())
assert completed['sha256']==hashlib.sha256(movie.read_bytes()).hexdigest()
meta=subprocess.run([F,'-hide_banner','-i',str(movie)],capture_output=True,text=True).stderr
assert '3840x2160' in meta and '24 fps' in meta and 'Duration: 00:00:21.00' in meta
assert '48000 Hz, stereo' in meta
def decode(f,name):
 p=out/(name+'.png');r=subprocess.run([F,'-v','error','-ss',str((f-1969)/24),'-i',str(movie),'-frames:v','1','-y',str(p)],capture_output=True);assert r.returncode==0
 im=Image.open(p);assert im.size==(3840,2160);return np.asarray(im)
frames={}
for f,n in [(1969,'01_start'),(2033,'02_WHEN'),(2137,'03_THE'),(2257,'04_SKY_CLEARS'),(2399,'05_last_S'),(2400,'06_last_S_fragment'),(2401,'07_card_start'),(2472,'08_card_end')]:frames[n]=decode(f,n)
native=np.asarray(Image.open(R/'renders/world_v016/ending_checks_4K_v033/2137.png').convert('RGB'))
mask=Image.open(R/'renders/world_v016/ending_checks_4K_v033/mask_2137.png').convert('L')
outside=np.asarray(mask.filter(ImageFilter.MaxFilter(15)))==0
assert int(native[outside].max())==0
ys,xs=np.where(np.asarray(mask)>127)
cap_height_pixels=int(ys.max()-ys.min()+1);assert .98<=cap_height_pixels/2160<=1
card_native=np.asarray(Image.open(R/'renders/world_v016/ending_checks_4K_v033/2401.png').convert('L'))
cy,cx=np.where(card_native>127)
card_box=[int(cx.min()),int(cy.min()),int(cx.max()),int(cy.max())]
assert (cy.max()-cy.min()+1)/2160>=.98 and (cx.max()-cx.min()+1)/3840>=.97
encoded=frames['03_THE'];outside_encoded_max=int(encoded[outside].max());assert outside_encoded_max<=5,outside_encoded_max
master_path=R/'renders/world_v016/ending_checks_4K_v033/master_2137.png'
master_diff=None
if master_path.exists():
 master=np.asarray(Image.open(master_path).convert('RGB'));master_diff=float(np.abs(master.astype(float)-native).mean());assert master_diff<.01,master_diff
assert frames['01_start'].max()<=5
assert np.mean(abs(frames['07_card_start'].astype(float)-frames['08_card_end']))<.1
pcm=subprocess.run([F,'-v','error','-i',str(movie),'-map','0:a:0','-f','s16le','-ar','48000','-ac','2','-'],capture_output=True);assert pcm.returncode==0
audio=np.frombuffer(pcm.stdout,dtype='<i2').astype(float).reshape(-1,2)
with wave.open(str(R/'edit/When_The_Sky_Clears_Trailer_Music_100s.wav')) as w:
 original=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float).reshape(-1,2)
def rms(a):return float(np.sqrt(np.mean(a*a)))
audio_qc=[]
for a,b in [(0,1),(7,8),(10,11),(14,15),(17,18),(18.05,20.95)]:
 got=audio[int(a*48000):int(b*48000)];ref=original[int((a+82)*48000):int((b+82)*48000)]
 audio_qc.append({'preview_seconds':[a,b],'rms':rms(got),'relative_to_original':rms(got)/max(rms(ref),1e-8) if len(ref) else None})
assert audio_qc[0]['rms']>0 and audio_qc[-1]['rms']<1
assert audio_qc[-2]['relative_to_original']<.1
preserved={}
for rel,expected in [('shots/world/WTSC_Painted_World_Editable_v031.blend','ff2158da0174ba6b6ad985f82195d668857d84caded6c71101a7d6ca8f655bc4'),('shots/world/WTSC_Painted_World_Trailer_v030.blend','b68e097922883c9cb409da4d5a999a889be2ffc9768627824087f44745574bb6'),('renders/world_v016/WTSC_Painted_World_4K_v030.mp4','64729abab8e899cf717781f664d82ff1f3b6a8a02afaee82ec947c59f29b6999')]:
 actual=hashlib.sha256((R/rel).read_bytes()).hexdigest();assert actual==expected;preserved[rel]=actual
for rel,expected in [('shots/world/WTSC_Knockout_Ending_Editable_v032.blend','b71b3ec247a60e5d022121444c95ce47f3c1cbd7d1668233327e87e8da1df352'),('renders/world_v016/WTSC_Knockout_Ending_4K_v032.mp4','63145d7075fd4b1b3ab0072ffb799fecf489566068a150c331ac1cec53320183')]:
 actual=hashlib.sha256((R/rel).read_bytes()).hexdigest();assert actual==expected;preserved[rel]=actual
report={**completed,'metadata':[l.strip() for l in meta.splitlines() if 'Duration:' in l or 'Stream #' in l],'native_outside_mask_max':0,'encoded_far_outside_mask_max':outside_encoded_max,'native_master_vs_ending_mean_error':master_diff,'audio_qc':audio_qc,'prior_deliverables_unchanged':preserved,'decoded_stills':[str(p) for p in out.glob('*.png')],'visual_scope':'Native glyph alpha and card at4K. Clean cached world52–70 fills global82–100 via uniform2x crop; effective picture detail1920x1080. Children held. Only ending preview exported; full103s native edit prepared.'}
report['edge_filling_typography']={'scroll_cap_ink_height_pixels':cap_height_pixels,'scroll_cap_height_fraction':cap_height_pixels/2160,'final_card_white_ink_bbox':card_box,'final_card_width_fraction':float((cx.max()-cx.min()+1)/3840),'final_card_height_fraction':float((cy.max()-cy.min()+1)/2160),'native_fonts':'Arial Black scrolling / Impact final card; uniform XYZ font scale'}
(R/'notes/world_v016/ending_verification_v033.json').write_text(json.dumps(report,indent=2));print('ENDING_QC_PASSED',json.dumps({k:v for k,v in report.items() if k not in ['decoded_stills','prior_deliverables_unchanged']}),flush=True)
