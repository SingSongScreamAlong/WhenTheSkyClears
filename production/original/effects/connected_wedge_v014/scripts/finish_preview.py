from pathlib import Path
from PIL import Image
import subprocess,json,hashlib
P=Path(__file__).resolve().parents[1];F=P/'previews/motion';ff=r'WTSC_LOCAL_USER\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
for f in range(1,33):
    with Image.open(F/f'{f:04d}.png') as im:im.verify()
movie=P/'previews/WTSC_Connected_Soil_Wedge_TWO_TONE_ROUGH_v014.mp4'
subprocess.run([ff,'-hide_banner','-loglevel','error','-y','-framerate','24','-i',str(F/'%04d.png'),'-frames:v','32','-an','-c:v','libx264','-crf','18','-preset','medium','-threads','2','-pix_fmt','yuv420p','-movflags','+faststart',str(movie)],check=True)
dec=subprocess.run([ff,'-hide_banner','-loglevel','error','-i',str(movie),'-progress','pipe:1','-f','null','-'],capture_output=True,text=True,check=True);assert 'frame=32' in dec.stdout
assert movie.stat().st_size<20_000_000
report={'frames':32,'fps':24,'duration_seconds':32/24,'pixels':[1920,1080],'impact_frame':7,'connected_frames':[7,14],'first_separation_frames':[15,16],'video_bytes':movie.stat().st_size,'video_sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),'full_decode':True,'continuous_speed_playback_observed':False,'status':'One requested two-tone rough for review before any polish. No artistic acceptance or production integration.'}
(P/'evidence/preview_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
