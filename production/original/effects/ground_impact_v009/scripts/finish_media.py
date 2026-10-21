import json,subprocess,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parents[1];folder=P/'previews/v009d_motion';files=sorted(folder.glob('*.png'));assert len(files)==120,len(files)
for i,f in enumerate(files,1):assert f.name==f'{i:04d}.png' and f.read_bytes()[-12:]==b'\x00\x00\x00\x00IEND\xaeB`\x82'
ff=r'WTSC_LOCAL_USER\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
video=P/'previews/WTSC_Ground_First_Impact_Debris_Proof_v009d.mp4'
cmd=[ff,'-hide_banner','-loglevel','warning','-y','-framerate','24','-start_number','1','-i',str(folder/'%04d.png'),'-frames:v','120','-an','-c:v','libx264','-threads','2','-preset','medium','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(video)]
subprocess.run(cmd,check=True);assert video.stat().st_size<20_000_000
decode=subprocess.run([ff,'-hide_banner','-i',str(video),'-map','0:v:0','-f','null','-'],capture_output=True,text=True,check=True)
(P/'evidence/video_full_decode.txt').write_text(decode.stderr)
frames=[7,8,9,10,12,16,20,24,28,32,36,40,44,52,64,120]
sheet=Image.new('RGB',(1920,4*304),(22,25,25));draw=ImageDraw.Draw(sheet)
for i,fr in enumerate(frames):
    im=Image.open(folder/f'{fr:04d}.png').convert('RGB').resize((480,270),Image.Resampling.LANCZOS);x=(i%4)*480;y=(i//4)*304;sheet.paste(im,(x,y));draw.text((x+10,y+276),f'frame {fr:03d} / impact +{fr-7:03d}',fill=(220,220,212))
sheet.save(P/'previews/WTSC_Ground_Proof_Actual_Frame_Sheet_v009d.jpg',quality=94)
Image.open(folder/'0120.png').save(P/'previews/WTSC_Ground_Proof_Aftermath_v009d.png')
evidence={'video':video.name,'bytes':video.stat().st_size,'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'fps':24,'frames':120,'duration_seconds':5,'audio':False,'pixels':[1920,1080],'full_decode_returncode':decode.returncode,'source_png_count':len(files),'contact_sheet_actual_frames':frames,'source':'Actual isolated Blender renders; no AI-generated video frames, speed changes, camera shake or audio.'}
(P/'evidence/media_validation_v009d.json').write_text(json.dumps(evidence,indent=2));print(json.dumps(evidence,indent=2))
