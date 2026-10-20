"""Analysis sheets/crops and exact-frame review encode; original art untouched."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,subprocess,hashlib
P=Path(__file__).resolve().parents[1]
folder=P/'previews/consecutive_native4Kcrop_v015c'
files=[folder/f'{f}.png'for f in range(1824,1849)]
for p in files:
    im=Image.open(p);assert im.size==(1600,1320),(p,im.size);im.verify()
sheet=Image.new('RGB',(2000,5*354),(24,24,24));d=ImageDraw.Draw(sheet)
for i,p in enumerate(files):
    im=Image.open(p).convert('RGB');x=i%5*400;y=i//5*354
    sheet.paste(im.resize((400,330),Image.Resampling.LANCZOS),(x,y+24))
    age=int(p.stem)-1824;phase='IGN'if age<1 else('IGN/TEAR'if age<5 else('TEAR/FAN'if age<10 else('FAN'if age<14 else('FAN/COLL'if age<22 else'COLL'))))
    d.text((x+6,y+6),f'{p.stem} | age{age} | {phase}',fill='white')
sheet.save(P/'previews/Actual_Consecutive_Native4K_Crops_1824_1848_v015c.jpg',quality=94)
for a,b in[(1825,1826),(1829,1830),(1836,1837)]:
    pair=Image.new('RGB',(2500,1080),(24,24,24));draw=ImageDraw.Draw(pair)
    for j,f in enumerate([a,b]):
        im=Image.open(folder/f'{f}.png').crop((200,150,1450,1200)).convert('RGB')
        pair.paste(im,(j*1250,30));draw.text((j*1250+12,8),f'ACTUAL NATIVE4K PIXELS | frame{f} | age{f-1824}',fill='white')
    pair.save(P/f'previews/Native4K_Phase_Cut_{a}_{b}_v015c.jpg',quality=95)
keys=json.loads((P/'evidence/render_keys_v015c.json').read_text())['rows']
sheet=Image.new('RGB',(1920,4*568),(24,24,24));draw=ImageDraw.Draw(sheet)
for i,row in enumerate(keys):
    p=Path(row['path'])
    if row['frame']==1901:p=P/'previews/native4K_keys_v015c/1901.png'
    im=Image.open(p);assert im.size==(3840,2160)
    x=i%2*960;y=i//2*568
    sheet.paste(im.resize((960,540),Image.Resampling.LANCZOS),(x,y+28))
    draw.text((x+10,y+8),f"ACTUAL NATIVE4K | frame{row['frame']} | v015c scar selected at1901",fill='white')
sheet.save(P/'previews/Painted_Impact_Actual4K_Whole_Shot_Keys_v015c.jpg',quality=94)
ff=Path(r'WTSC_LOCAL_USER\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe')
movie=P/'previews/WTSC_Painted_Impact_Consecutive_Native4KCrop_v015c.mp4'
cmd=[str(ff),'-v','error','-y','-framerate','24','-start_number','1824','-i',str(folder/'%04d.png'),'-frames:v','25','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-an',str(movie)]
subprocess.run(cmd,check=True);subprocess.run([str(ff),'-v','error','-i',str(movie),'-f','null','-'],check=True)
report={'actual_native4K_crops_verified':25,'actual_crop_pixels':[1600,1320],'native_canvas':[3840,2160],
 'movie':str(movie),'movie_frames':25,'fps':24,'audio':False,'upscaled':False,
 'source_frames_interpolated':False,'movie_full_decode':True,'sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),
 'sheets_are_analysis_derivatives':True,'continuous_speed_playback_observed':False}
(P/'evidence/review_media_v015c.json').write_text(json.dumps(report,indent=2))
print('ACTUAL_NATIVE4K_CROP_REVIEW_READY',json.dumps(report))
