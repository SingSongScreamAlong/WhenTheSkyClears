"""Review-only comparisons of actual matched pixels; no production raster edits."""
import json,hashlib,subprocess,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
R=Path(__file__).resolve().parents[1];F=r'WTSC_LOCAL_USER\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe';probe='--probe' in sys.argv;frames=([1901] if '--single' in sys.argv else [1849,1901]) if probe else [1842,1849,1856,1881,1901,1920];folder=R/'renders/world_v016/art_v045d';output=folder/('comparisons_probe' if probe else 'comparisons');output.mkdir(exist_ok=True);refs=folder/'v044_actual_reference_pngs';refs.mkdir(exist_ok=True);base=R/'renders/world_v016/integration_v044/WTSC_Drawn_Open_75_80_4K_v044.mp4';assert hashlib.sha256(base.read_bytes()).hexdigest()=='33397c2a362ae914fcf534e7b68b28002c59f4ae61bf3a5c9e7d6dddd928d39d'
font=ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf',28);small=ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf',18);thumb=Image.new('RGB',(656,len(frames)*216),(16,16,16));thumbgray=thumb.copy();rows=[]
for index,frame in enumerate(frames):
 ref=refs/f'v044_{frame}_4K.png'
 if not ref.exists():
  r=subprocess.run([F,'-v','error','-i',str(base),'-vf',f'select=eq(n\\,{frame-1801})','-frames:v','1','-threads','2',str(ref)],capture_output=True,text=True);assert r.returncode==0,r.stderr
 art=folder/f'{"Probe_" if probe else ""}Art_v045d_{frame}_4K.png';old=Image.open(ref).convert('RGB');new=Image.open(art).convert('RGB');assert old.size==new.size==(3840,2160)
 normal=Image.new('RGB',(3840,1132),(16,16,16));d=ImageDraw.Draw(normal)
 for column,(label,im) in enumerate([('v044 original',old),('v045d art only',new)]):
  x=column*1920;d.text((x+18,10),f'{label} | frame{frame} | {(frame-1)/24:.3f}s',font=font,fill='white');normal.paste(im.resize((1920,1080),Image.Resampling.LANCZOS),(x,52))
 normalpath=output/f'Matched_Color_{frame}_v044_vs_v045d.jpg';normal.save(normalpath,quality=96)
 gray=ImageOps.grayscale(normal).convert('RGB');graypath=output/f'Matched_Grayscale_{frame}_v044_vs_v045d.jpg';gray.save(graypath,quality=96)
 for sheet,grayflag in [(thumb,False),(thumbgray,True)]:
  dd=ImageDraw.Draw(sheet);y=index*216;dd.text((8,y+3),f'{frame} / {(frame-1)/24:.3f}s | v044 left / v045d right',font=small,fill='white')
  for column,im in enumerate([old,new]):
   preview=im.resize((320,180),Image.Resampling.LANCZOS);preview=ImageOps.grayscale(preview).convert('RGB') if grayflag else preview;sheet.paste(preview,(8+column*328,y+28))
 bankpath=None
 if frame in [1849,1901]:
  bank=Image.new('RGB',(3000,796),(16,16,16));dd=ImageDraw.Draw(bank)
  for i,(label,im) in enumerate([('v044 original | native-pixel bank crop',old),('v045d | native-pixel bank crop',new)]):dd.text((12,i*398+8),label,font=font,fill='white');bank.paste(im.crop((400,1470,3400,1820)),(0,i*398+48))
  bankpath=output/f'Bank_{frame}_Native_Pixels.jpg';bank.save(bankpath,quality=98)
 rows.append({'frame':frame,'seconds':(frame-1)/24,'actual_art_png':str(art),'art_png_sha256':hashlib.sha256(art.read_bytes()).hexdigest(),'v044_actual_source_png':str(ref),'color_comparison':str(normalpath),'grayscale_comparison':str(graypath),'native_bank_crop':str(bankpath) if bankpath else None})
colorpath=output/'Thumbnail_Color_v044_vs_v045d.jpg';graypath=output/'Thumbnail_Grayscale_v044_vs_v045d.jpg';thumb.save(colorpath,quality=97);thumbgray.save(graypath,quality=97)
report={'status':'Actual PNG comparisons ready for visual inspection, no artistic acceptance inferred.','probe_only':probe,'frames':frames,'comparisons':rows,'color_thumbnail_sheet':str(colorpath),'grayscale_thumbnail_sheet':str(graypath),'normal_panels':'Each1920x1080from actual3840x2160source, labels outsideart.','thumbnail_panels':[320,180],'grayscale':'Review-only grayscale of actual pixels; native production art unchanged.','baseline':'Exact v044actual movie frames, zero-based index=globalframe-1801.','no_movie_rendered':True};(R/f'notes/world_v016/art_comparisons_v045d{"_probe" if probe else ""}.json').write_text(json.dumps(report,indent=2));print('V045B_ACTUAL_COMPARISONS_READY',str(output),flush=True)
