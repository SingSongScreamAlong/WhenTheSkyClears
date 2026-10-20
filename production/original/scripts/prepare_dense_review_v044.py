"""Analysis-only unpainted crops/sheets of actual decoded EEVEE output."""
import json,hashlib,subprocess,wave
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];F=r'WTSC_LOCAL_USER\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe';receipt=json.loads((R/'notes/world_v016/export_completed_v044.json').read_text());folder=R/'renders/world_v016/integration_v044';font=ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf',22);small=ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf',19)
dense=folder/'decoded_dense';files=sorted(dense.glob('*.png'));assert len(files)==40;sheets=[]
for index in range(5):
 canvas=Image.new('RGB',(2920,1280),(15,15,15));draw=ImageDraw.Draw(canvas)
 for j,path in enumerate(files[index*8:index*8+8]):
  im=Image.open(path).convert('RGB');crop=im.crop((700,240,1420,840));x=8+(j%4)*728;y=8+(j//4)*636;draw.text((x+8,y+3),f'Actual 8fps {75+(index*8+j)/8:.3f}s',font=font,fill='white');canvas.paste(crop,(x,y+30))
 path=dense/f'Actor_Chronology_{index+1:02d}.jpg';canvas.save(path,quality=97);sheets.append(str(path))
critical=folder/'critical_native_crops';critical.mkdir();cropdirs={v:Path(receipt['native_crop_directories'][v]) for v in ['v043','v044']}
def native(version,frame):return Image.open(cropdirs[version]/f'{frame:04d}.png').convert('RGB')
criticalframes=list(range(1837,1859));boots=[];hands=[]
for group,chunk in enumerate([criticalframes[i:i+8] for i in range(0,len(criticalframes),8)],1):
 canvas=Image.new('RGB',(2680,1000),(15,15,15));d=ImageDraw.Draw(canvas)
 for j,f in enumerate(chunk):
  x=8+(j%4)*670;y=8+(j//4)*498;d.text((x,y),f'{f} / {(f-1)/24:.3f}s  v043 | v044',font=font,fill='white')
  for k,v in enumerate(['v043','v044']):canvas.paste(native(v,f).crop((185,680,510,1120)),(x+k*330,y+32))
 path=critical/f'Boy_Boot_Overlap_{group:02d}_Native_Pixels.jpg';canvas.save(path,quality=98);boots.append(str(path))
for group,chunk in enumerate([criticalframes[i:i+6] for i in range(0,len(criticalframes),6)],1):
 canvas=Image.new('RGB',(1740,1300),(15,15,15));d=ImageDraw.Draw(canvas)
 for j,f in enumerate(chunk):
  x=8+(j%3)*580;y=8+(j//3)*646;d.text((x,y),f'{f} / {(f-1)/24:.3f}s  v043 | v044',font=small,fill='white')
  for k,v in enumerate(['v043','v044']):
   im=native(v,f);canvas.paste(im.crop((460,560,740,840)),(x+k*286,y+32));canvas.paste(im.crop((1060,570,1340,850)),(x+k*286,y+342))
  d.text((x,y+312),'Boy above / girl below',font=small,fill='white')
 path=critical/f'Hands_Fingers_{group:02d}_Native_Pixels.jpg';canvas.save(path,quality=98);hands.append(str(path))
poststop=list(range(1881,1921,3));poststop.append(1920) if poststop[-1]!=1920 else None;settlesheets=[]
for group,chunk in enumerate([poststop[i:i+4] for i in range(0,len(poststop),4)],1):
 canvas=Image.new('RGB',(2920,1280),(15,15,15));d=ImageDraw.Draw(canvas)
 for j,f in enumerate(chunk):
  x=8+(j%2)*1456;y=8+(j//2)*636;d.text((x,y),f'{f} / {(f-1)/24:.3f}s   v043 previous | v044 corrected',font=font,fill='white')
  for k,v in enumerate(['v043','v044']):canvas.paste(native(v,f).resize((720,600),Image.Resampling.LANCZOS),(x+k*728,y+30))
 path=critical/f'Recovery_Breathing_Matched_{group:02d}.jpg';canvas.save(path,quality=97);settlesheets.append(str(path))
movie=Path(receipt['master']['path']);header=subprocess.run([F,'-hide_banner','-i',str(movie)],capture_output=True,text=True).stderr;assert '3840x2160' in header and '24 fps' in header and '48000 Hz, stereo' in header
pcm=subprocess.run([F,'-v','error','-i',str(movie),'-map','0:a:0','-ar','48000','-ac','2','-f','s16le','-'],capture_output=True);assert pcm.returncode==0;actual=np.frombuffer(pcm.stdout,dtype='<i2').astype(float).reshape(-1,2)[:240000]
with wave.open(str(R/'edit/When_The_Sky_Clears_Trailer_Music_100s.wav')) as sound:original=np.frombuffer(sound.readframes(sound.getnframes()),dtype='<i2').astype(float).reshape(-1,2)[75*48000:80*48000]
correlation=float(np.corrcoef(actual.reshape(-1),original.reshape(-1))[0,1]);ratio=float(np.sqrt(np.mean(actual*actual))/np.sqrt(np.mean(original*original)));assert correlation>.99 and .97<ratio<1.03
for name,sha in receipt['preserved_inputs'].items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==sha
assert hashlib.sha256(Path(receipt['source']['path']).read_bytes()).hexdigest()==receipt['source']['sha256']
qa={'source_sha256':receipt['source']['sha256'],'master_sha256':receipt['master']['sha256'],'native_4K_actual_frames':120,'fps':24,'seconds':5,'metadata':[line.strip() for line in header.splitlines() if 'Duration:' in line or 'Stream #' in line],'original_audio_75_80_correlation':correlation,'audio_rms_ratio':ratio,'dense_actual_8fps_sheets':sheets,'critical_actual_24fps_frames':criticalframes,'critical_range_seconds':[76.5,(1858-1)/24],'native_pixel_boot_sheets':boots,'native_pixel_hand_sheets':hands,'poststop_actual_frames':poststop,'poststop_matched_sheets':settlesheets,'native_crops':'All120frames per version cropped from actual3840x2160 movie at1:1source pixel density, no enlargement/repainting or synthetic frames.','native_crop_size':[1440,1200],'all_preserved_input_hashes_match':True,'artistic_review_pending':True}
(R/'notes/world_v016/media_qa_v044.json').write_text(json.dumps(qa,indent=2));print('V044_DENSE_REVIEW_AND_AUDIO_QA_READY',json.dumps({'audio_correlation':correlation,'boot_sheets':boots,'hand_sheets':hands,'poststop_sheets':settlesheets}),flush=True)
