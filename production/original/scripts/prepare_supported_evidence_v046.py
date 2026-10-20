"""Actual pixel review sheets/crops/audio QA; no production artwork edits."""
import json,subprocess,hashlib,wave
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];F=r'WTSC_LOCAL_USER\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe';receipt=json.loads((R/'notes/world_v016/export_completed_v046.json').read_text());folder=R/'renders/world_v016/integration_v046';out=folder/'review_evidence';out.mkdir(exist_ok=True);font=ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf',23);small=ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf',18)
def canvas(size):return Image.new('RGB',size,(15,15,15))
def save(im,name):p=out/name;im.save(p,quality=97);return str(p)
dense=Path(receipt['dense_directory']);files=sorted(dense.glob('*.png'));assert len(files)==40;chronology=[]
for group in range(5):
 im=canvas((2920,1280));d=ImageDraw.Draw(im)
 for j,p in enumerate(files[group*8:group*8+8]):
  x=8+(j%4)*728;y=8+(j//4)*636;d.text((x,y),f'Actual1080p8fps sample / ~{75+(group*8+j)/8:.3f}s',font=font,fill='white');im.paste(Image.open(p).convert('RGB').crop((700,240,1420,840)),(x,y+30))
 chronology.append(save(im,f'Actor_Chronology_{group+1:02d}.jpg'))
crops={k:Path(v) for k,v in receipt['actor_crop_directories'].items()}
def hd(v,f):return Image.open(crops[v]/f'{f:04d}.png').convert('RGB')
critical=list(range(1837,1859));bootHD=[]
for group,start in enumerate(range(0,len(critical),8),1):
 im=canvas((2216,680));d=ImageDraw.Draw(im)
 for j,f in enumerate(critical[start:start+8]):
  x=8+(j%4)*552;y=8+(j//4)*334;d.text((x,y),f'{f} / {(f-1)/24:.3f}s v006 | v007',font=small,fill='white')
  for col,v in enumerate(['v006','v007']):im.paste(hd(v,f).crop((70,310,340,600)),(x+col*276,y+30))
 bootHD.append(save(im,f'Boot_Critical_HD_24fps_{group:02d}.jpg'))
native={r['frame']:r for r in receipt['critical_actual_4K_frames']}
def nativeim(which,f):return Image.open(native[f][which+'_4K']['path']).convert('RGB')
for f in native:
 for which in ['baseline','candidate']:nativeim(which,f).crop((1400,480,2840,1680)).save(out/f'{which}_Actor_{f}_Native4KCrop.png')
im=canvas((1800,1264));d=ImageDraw.Draw(im)
for col,f in enumerate([1844,1845,1846]):
 for row,which in enumerate(['baseline','candidate']):
  x=col*600;y=row*632;d.text((x+8,y+4),f'{which} {f} / {(f-1)/24:.3f}s',font=font,fill='white');im.paste(nativeim(which,f).crop((2000,600,2600,1200)),(x,y+32))
head4K=save(im,'Head_Turn_1844_1845_1846_Native4KPixels.jpg')
im=canvas((1220,1660));d=ImageDraw.Draw(im)
for row,f in enumerate([1842,1849,1856]):
 y=row*552;d.text((10,y+4),f'{f} / {(f-1)/24:.3f}s | v006 left / v007 right | native4Kcrop',font=small,fill='white')
 for col,which in enumerate(['baseline','candidate']):im.paste(nativeim(which,f).crop((1500,1130,2100,1630)),(col*610,y+34))
boot4K=save(im,'Boot_Negative_Space_Native4KPixels.jpg');rise=[]
for f in [1889,1901,1920]:
 im=canvas((2896,1240));d=ImageDraw.Draw(im)
 for col,which in enumerate(['baseline','candidate']):
  x=col*1448;d.text((x+8,5),f'{which} {f} / {(f-1)/24:.3f}s | native4Kcrop',font=font,fill='white');im.paste(nativeim(which,f).crop((1400,480,2840,1680)),(x,40))
 rise.append(save(im,f'Support_Preparation_Rise_{f}_Native4KPixels.jpg'))
im=canvas((1336,352));d=ImageDraw.Draw(im)
for col,f in enumerate([1889,1901,1920]):
 x=col*448;d.text((x+5,4),f'{f} | projected light cue only',font=small,fill='white');im.paste(nativeim('candidate',f).crop((1850,940,2290,1250)),(x,36))
hands=save(im,'Projected_Fingertip_Cue_Native4KPixels.jpg')
poststop=list(range(1881,1921,3));poststop.append(1920) if poststop[-1]!=1920 else None;settle=[]
for group,start in enumerate(range(0,len(poststop),4),1):
 im=canvas((2920,1280));d=ImageDraw.Draw(im)
 for j,f in enumerate(poststop[start:start+4]):
  x=8+(j%2)*1456;y=8+(j//2)*636;d.text((x,y),f'{f} / {(f-1)/24:.3f}s v006 | v007 actual1080p',font=font,fill='white')
  for col,v in enumerate(['v006','v007']):im.paste(hd(v,f),(x+col*728,y+30))
 settle.append(save(im,f'Post_Stop_Chronology_{group:02d}.jpg'))
shotframes=[1801,1825,1844,1846,1856,1889,1901,1920];select='+'.join(f'eq(n\\,{f-1801})' for f in shotframes)
for version,path in [('v006',receipt['baseline']['path']),('v007',receipt['candidate']['path'])]:
 dest=out/('full_HD_keys_'+version);dest.mkdir(exist_ok=True);r=subprocess.run([F,'-v','error','-i',path,'-vf','select='+select,'-fps_mode','vfr','-frames:v','8','-threads','2',str(dest/'%02d.png')],capture_output=True,text=True);assert r.returncode==0,r.stderr
shot=[]
for group in range(2):
 im=canvas((1296,1632));d=ImageDraw.Draw(im)
 for row,f in enumerate(shotframes[group*4:group*4+4]):
  y=row*408;d.text((8,y+5),f'{f} / {(f-1)/24:.3f}s | v006 left / v007 right | samev045cart',font=small,fill='white')
  for col,v in enumerate(['v006','v007']):im.paste(Image.open(out/f'full_HD_keys_{v}/{group*4+row+1:02d}.png').convert('RGB').resize((640,360),Image.Resampling.LANCZOS),(8+col*648,y+36))
 shot.append(save(im,f'Shot_Size_Comparison_{group+1:02d}.jpg'))
def audio(path):
 r=subprocess.run([F,'-v','error','-i',path,'-map','0:a:0','-ar','48000','-ac','2','-f','s16le','-'],capture_output=True);assert r.returncode==0;return np.frombuffer(r.stdout,dtype='<i2').astype(float).reshape(-1,2)[:240000]
baseaudio=audio(receipt['baseline']['path']);newaudio=audio(receipt['candidate']['path'])
with wave.open(str(R/'edit/When_The_Sky_Clears_Trailer_Music_100s.wav')) as music:original=np.frombuffer(music.readframes(music.getnframes()),dtype='<i2').astype(float).reshape(-1,2)[75*48000:80*48000]
corr=float(np.corrcoef(original.reshape(-1),newaudio.reshape(-1))[0,1]);ratio=float(np.sqrt(np.mean(newaudio*newaudio))/np.sqrt(np.mean(original*original)));assert corr>.99 and .97<ratio<1.03;assert len(newaudio)==240000
for row in receipt['critical_actual_4K_frames']:
 for which in ['baseline_4K','candidate_4K']:assert Image.open(row[which]['path']).size==(3840,2160)
for name,expected in receipt['preserved_inputs'].items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==expected,name
assert hashlib.sha256(Path(receipt['source']['path']).read_bytes()).hexdigest()==receipt['source']['sha256']
qa={'source_sha256':receipt['source']['sha256'],'actual_preview_frames':120,'fps':24,'review_resolution':[1920,1080],'native_critical_resolution':[3840,2160],'dense_8fps_actual_samples':40,'chronology_sheets':chronology,'critical_HD24fps_boot_frames':critical,'critical_HD_boot_sheets':bootHD,'native4K_head_exposure_sheet':head4K,'native4K_boot_negative_space_sheet':boot4K,'native4K_support_rise_sheets':rise,'native4K_fingertip_cue_sheet':hands,'poststop_HD_frames':poststop,'poststop_sheets':settle,'shot_size_comparison_sheets':shot,'audio_original_75_80_correlation':corr,'audio_rms_ratio':ratio,'baseline_candidate_audio_max_sample_difference':float(np.max(np.abs(baseaudio-newaudio))),'all_preserved_hashes_match':True,'method':'Actual native4Kcrop pixels and actual1080p decoded movie samples. Analysis-only crops/sheets; no synthetic motion, frame interpolation, repaint or enlarged substitute for4K.','artistic_review_pending':True}
(R/'notes/world_v016/media_qa_v046.json').write_text(json.dumps(qa,indent=2));print('V046_ACTUAL_REVIEW_EVIDENCE_READY',json.dumps({'head':head4K,'boots':boot4K,'rise':rise,'shot_size':shot,'audio_correlation':corr}),flush=True)
