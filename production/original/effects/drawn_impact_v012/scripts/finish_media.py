from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,subprocess
P=Path(__file__).resolve().parents[1];F=P/'previews/painted_motion'
ff=r'WTSC_LOCAL_USER\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
frames=list(range(1,73))
for f in frames:
    with Image.open(F/f'{f:04d}.png') as im:im.verify()
movie=P/'previews/WTSC_Drawn_Compact_Impact_Review_v012.mp4'
subprocess.run([ff,'-hide_banner','-loglevel','error','-y','-framerate','24','-i',str(F/'%04d.png'),'-frames:v','72','-an','-c:v','libx264','-crf','19','-preset','medium','-threads','2','-pix_fmt','yuv420p','-movflags','+faststart',str(movie)],check=True)
decode=subprocess.run([ff,'-hide_banner','-loglevel','error','-i',str(movie),'-progress','pipe:1','-f','null','-'],check=True,capture_output=True,text=True)
assert 'frame=72' in decode.stdout,decode.stdout
assert movie.stat().st_size<20_000_000
shots=Image.new('RGB',(1920,1120),(24,26,27));d=ImageDraw.Draw(shots)
for i,f in enumerate([6,8,9,10,22,72]):
    im=Image.open(F/f'{f:04d}.png').convert('RGB');im.thumbnail((960,540));x=(i%2)*960;y=(i//2)*373
    im.thumbnail((960,348));shots.paste(im,(x,y+24));d.text((x+8,y+6),f'Actual shot | frame {f}',fill=(220,220,220))
shots.save(P/'previews/WTSC_Drawn_Impact_Shot_Context_v012.jpg',quality=93)
sheet=Image.new('RGB',(1600,880),(24,26,27));d=ImageDraw.Draw(sheet)
for i,f in enumerate([14,15,16,17,18,19,20,21,22,23,24,25,28,30,32,72]):
    im=Image.open(F/f'{f:04d}.png').convert('RGB').crop((1280,610,1810,790));im.thumbnail((395,190))
    x=(i%4)*400;y=(i//4)*220;sheet.paste(im,(x,y+25));d.text((x+8,y+6),f'Actual contact | frame {f}',fill=(220,220,220))
sheet.save(P/'previews/WTSC_Drawn_Impact_Landings_v012.jpg',quality=94)
report={'movie':str(movie),'bytes':movie.stat().st_size,'sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),'fps':24,'frames':72,'seconds':3,'pixels':[1920,1080],'audio':False,'all_source_pngs_verified':True,'full_mp4_decode':True,'continuous_speed_playback_observed':False}
(P/'evidence/media_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
