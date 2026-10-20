from pathlib import Path
from PIL import Image
import subprocess,json,hashlib,shutil
P=Path(__file__).resolve().parents[1];F=P/'previews/motion_final';ff=r'WTSC_LOCAL_USER\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
for f in range(1,33):
    with Image.open(F/f'{f:04d}.png') as im:im.verify()
movie=P/'previews/WTSC_Squat_Clods_SILHOUETTE_ROUGH_v015.mp4'
subprocess.run([ff,'-hide_banner','-loglevel','error','-y','-framerate','24','-i',str(F/'%04d.png'),'-frames:v','32','-an','-c:v','libx264','-crf','18','-preset','medium','-threads','2','-pix_fmt','yuv420p','-movflags','+faststart',str(movie)],check=True)
dec=subprocess.run([ff,'-hide_banner','-loglevel','error','-i',str(movie),'-progress','pipe:1','-f','null','-'],capture_output=True,text=True,check=True);assert 'frame=32' in dec.stdout
assert movie.stat().st_size<20_000_000
for fr in [6,7,8,9,10,11,12,13,14,15,16,17,19,21,24,28,32]:
    shutil.copyfile(F/f'{fr:04d}.png',P/f'previews/keys/{fr:04d}.png')
report={'frames':32,'fps':24,'duration_seconds':32/24,'pixels':[1920,1080],'impact_frame':7,'fixed_size_primary_clods':True,'first_rising_gaps_scene_frame':10,'video_bytes':movie.stat().st_size,'video_sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),'full_decode':True,'continuous_speed_playback_observed':False,'status':'One requested fixed-size squat-clod silhouette rough for review before polish. No artistic acceptance or production integration.'}
(P/'evidence/preview_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
