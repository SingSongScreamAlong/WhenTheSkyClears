"""Analysis-only crops/contact sheets from actual decoded movie frames."""
import json,subprocess,hashlib,wave
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];F=r'WTSC_LOCAL_USER\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe';receipt=json.loads((R/'notes/world_v016/combined_export_completed_v043.json').read_text());folder=Path(receipt['dense_review_directory']);files=sorted(folder.glob('*.png'));assert len(files)==40
font=ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf',23);sheets=[]
for index in range(5):
    canvas=Image.new('RGB',(2920,1280),(15,15,15));draw=ImageDraw.Draw(canvas)
    for j,path in enumerate(files[index*8:index*8+8]):
        frame=Image.open(path).convert('RGB');assert frame.size==(1920,1080);crop=frame.crop((700,240,1420,840));x=8+(j%4)*728;y=8+(j//4)*636;draw.text((x+8,y+3),f'Actual 8fps sample {index*8+j+1:02d} / ~{75+(index*8+j)/8:.3f}s',font=font,fill='white');canvas.paste(crop,(x,y+30))
    out=folder/f'Actor_Chronology_{index+1:02d}.jpg';canvas.save(out,quality=96);sheets.append(str(out))
movie=Path(receipt['master']);header=subprocess.run([F,'-hide_banner','-i',str(movie)],capture_output=True,text=True).stderr;assert '3840x2160' in header and '24 fps' in header and '48000 Hz, stereo' in header
pcm=subprocess.run([F,'-v','error','-i',str(movie),'-map','0:a:0','-ar','48000','-ac','2','-f','s16le','-'],capture_output=True);assert pcm.returncode==0;actual=np.frombuffer(pcm.stdout,dtype='<i2').astype(float).reshape(-1,2)[:240000]
with wave.open(str(R/'edit/When_The_Sky_Clears_Trailer_Music_100s.wav')) as sound:source=np.frombuffer(sound.readframes(sound.getnframes()),dtype='<i2').astype(float).reshape(-1,2)[75*48000:80*48000]
assert len(actual)==240000;correlation=float(np.corrcoef(actual.reshape(-1),source.reshape(-1))[0,1]);ratio=float(np.sqrt(np.mean(actual*actual))/np.sqrt(np.mean(source*source)));assert correlation>.99 and .97<ratio<1.03,(correlation,ratio)
report={'master':str(movie),'source_sha256':receipt['source_sha256'],'native_cold_export':True,'metadata':[line.strip() for line in header.splitlines() if 'Duration:' in line or 'Stream #' in line],'decoded_frames':120,'duration_seconds':5,'native_audio_75_80_correlation':correlation,'native_audio_rms_ratio':ratio,'analysis_only_actor_sheets':sheets,'sheet_method':'Actual8fps decoded frames, chronological crops with approximate source time labels; no synthetic frames or altered art. Whole movie retained.','art_review_pending':True};(R/'notes/world_v016/combined_media_qa_v043.json').write_text(json.dumps(report,indent=2));print('DENSE_REVIEW_AND_NATIVE_AUDIO_QA_READY',json.dumps({'audio_correlation':correlation,'sheets':sheets}),flush=True)
