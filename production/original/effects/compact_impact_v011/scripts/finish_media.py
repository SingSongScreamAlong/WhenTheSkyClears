import json,subprocess,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1];folder=P/'previews/motion_final';files=sorted(folder.glob('*.png'));assert len(files)==72,len(files)
for i,f in enumerate(files,1):assert f.name==f'{i:04d}.png' and f.read_bytes()[-12:]==b'\x00\x00\x00\x00IEND\xaeB`\x82'
ff=r'WTSC_LOCAL_USER\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe';video=P/'previews/WTSC_Compact_Low_Smoke_Test_v011.mp4'
subprocess.run([ff,'-hide_banner','-loglevel','warning','-y','-framerate','24','-start_number','1','-i',str(folder/'%04d.png'),'-frames:v','72','-an','-c:v','libx264','-threads','2','-preset','medium','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True);assert video.stat().st_size<20_000_000
result=subprocess.run([ff,'-hide_banner','-i',str(video),'-map','0:v:0','-f','null','-'],capture_output=True,text=True,check=True);(P/'evidence/video_full_decode.txt').write_text(result.stderr)
frames=[6,7,8,9,10,14,18,22,28,36,48,72];sheet=Image.new('RGB',(1920,3*304),(23,26,26));d=ImageDraw.Draw(sheet)
for i,fr in enumerate(frames):
    im=Image.open(folder/f'{fr:04d}.png').convert('RGB').resize((480,270),Image.Resampling.LANCZOS);x=(i%4)*480;y=(i//4)*304;sheet.paste(im,(x,y));d.text((x+10,y+276),f'frame{fr:03d} / impact{fr-7:+d}',fill=(225,225,215))
sheet.save(P/'previews/WTSC_Compact_Actual_Frame_Sheet_v011.jpg',quality=95);Image.open(folder/'0072.png').save(P/'previews/WTSC_Compact_Aftermath_v011.png')
report={'video':video.name,'bytes':video.stat().st_size,'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'fps':24,'frames':72,'seconds':3,'pixels':[1920,1080],'muted':True,'full_decode_returncode':result.returncode,'actual_frame_sheet':frames,'source':'72 actual Blender frames. No speed changes, audio, camera shake or generated video interpolation.'}
(P/'evidence/media_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
