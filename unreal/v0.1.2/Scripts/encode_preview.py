from pathlib import Path
import hashlib,json,subprocess
import imageio_ffmpeg
from PIL import Image

root=Path(__file__).resolve().parents[1];ev=root/'Evidence'
receipt=json.loads((ev/'GameplayReplay.json').read_text());assert receipt['passed'] and len(receipt['events'])==8
count=int(receipt['recorded_frames']);assert count>150
for i in range(count):
    p=ev/'Frames'/f'Frame{i:05d}.png';assert p.is_file(),p
    with Image.open(p) as im:assert im.size==(1600,900);im.verify()
out=ev/'WTSC_Shelter_Playable_Preview.mp4'
args=[imageio_ffmpeg.get_ffmpeg_exe(),'-y','-framerate','5','-start_number','0','-i',str(ev/'Frames/Frame%05d.png'),'-frames:v',str(count),'-c:v','libx264','-preset','veryfast','-crf','22','-pix_fmt','yuv420p','-threads','2','-movflags','+faststart',str(out)]
with (ev/'VideoEncode.log').open('w',encoding='utf8') as log:subprocess.run(args,stdout=log,stderr=subprocess.STDOUT,check=True)
record={'source':'Actual Unreal FScreenshotRequest game viewport frames, 1600x900','frame_count':count,'encoded_fps':5,'video_seconds':count/5,'simulation_seconds':receipt['game_seconds'],'initial_settle_seconds_omitted':3,'file':str(out),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'silent':True,'ai_generated_gameplay':False,'input_delivery':'Simulated native engine key events; not OS input or a human playtest'}
(ev/'VideoReceipt.json').write_text(json.dumps(record,indent=2),encoding='utf8');print(json.dumps(record,indent=2))
