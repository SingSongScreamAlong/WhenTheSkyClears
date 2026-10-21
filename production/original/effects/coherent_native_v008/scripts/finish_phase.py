import json,subprocess,re,hashlib,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parents[1];phase=sys.argv[1];assert phase in ['silhouette','painted','painted_final'];label='Painted' if phase.startswith('painted') else 'Silhouette';version='v008b' if phase=='painted_final' else 'v008'
folder=P/f'previews/{phase}_motion_coherent';files=sorted(folder.glob('*.png'));assert {int(f.stem) for f in files}==set(range(1818,1938))
for f in files:
    with Image.open(f) as im:im.load();assert im.size==(1920,1080)
F=Path(r'WTSC_LOCAL_USER\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe')
def run(args,log):
    r=subprocess.run([str(F),'-hide_banner','-nostdin','-y',*args],capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW);(P/'evidence'/log).write_text(r.stderr);assert r.returncode==0,r.stderr;return r
video=P/f'WTSC_Coherent_{label}_{version}_MUTED.mp4'
run(['-framerate','24','-start_number','1818','-i',str(folder/'%04d.png'),'-frames:v','120','-an','-c:v','libx264','-crf','17','-preset','fast','-threads','2','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],f'encode_{phase}.log')
r=run(['-v','error','-i',str(video),'-progress','pipe:1','-f','null','NUL'],f'decode_{phase}.log');assert int(re.findall(r'^frame=(\d+)',r.stdout,re.M)[-1])==120;assert video.stat().st_size<20_000_000
frames=[1824,1825,1826,1827,1829,1832,1836,1842,1848,1856,1868,1884,1908,1937]
font=ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf',18);sheet=Image.new('RGB',(1600,1690),(22,26,29));draw=ImageDraw.Draw(sheet);draw.text((14,10),f'ONE COHERENT BLAST / {phase.upper()} /24fps / actual consecutive geometry, no pose dissolves',font=font,fill=(222,221,209))
for i,frame in enumerate(frames):
    x=(i%4)*400;y=45+(i//4)*408;im=Image.open(folder/f'{frame}.png').crop((1080,180,1920,785)).resize((400,288),Image.Resampling.LANCZOS);sheet.paste(im,(x,y+28));draw.text((x+8,y+5),f'f{frame} / age{frame-1824}',font=font,fill=(222,221,209))
sheet.save(P/f'WTSC_Coherent_{label}_Frames_{version}.jpg',quality=95)
audit=P/f'previews/decoded_{phase}';audit.mkdir(exist_ok=True);chosen=[1825,1827,1836,1848,1868,1908,1937];selector="select='"+'+'.join(f'eq(n,{f-1818})' for f in chosen)+"'"
run(['-i',str(video),'-vf',selector,'-fps_mode','passthrough',str(audit/'%02d.png')],f'extract_{phase}.log')
report={'phase':phase,'video':video.name,'bytes':video.stat().st_size,'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'fps':24,'pixels':[1920,1080],'frames':120,'seconds':5,'audio':False,'camera_shake':False,'all120_native_pngs_decoded':True,'full_video_decode':True,'review_frames':frames,'decoded_frames':chosen,'pose_dissolves':False}
(P/f'evidence/media_{phase}.json').write_text(json.dumps(report,indent=2));print('COHERENT_PHASE_MEDIA_VALIDATED',json.dumps(report),flush=True)
