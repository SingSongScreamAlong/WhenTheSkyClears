import json, subprocess, hashlib, re, zipfile
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np
P=Path(__file__).resolve().parents[1]
F=Path(r'WTSC_LOCAL_USER\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe')
manifest=json.loads((P/'evidence/preview_manifest.json').read_text());movies=[]
def run(args,log):
    r=subprocess.run([str(F),'-hide_banner','-nostdin',*args],capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
    (P/'evidence'/log).write_text(r.stderr);assert r.returncode==0,r.stderr
def encode(folder,count,path):
    run(['-y','-framerate','24','-start_number','1','-i',str(folder/'%04d.png'),'-frames:v',str(count),'-an','-c:v','libx264','-preset','fast','-crf','20','-threads','2','-pix_fmt','yuv420p','-movflags','+faststart',str(path)],path.stem+'_encode.log')
for row in manifest:
    path=P/f'WTSC_{row["clip"].title()}_Preview_v001.mp4';folder=P/row['folder'];files=sorted(folder.glob('[0-9][0-9][0-9][0-9].png'))
    assert len(files)==row['frames'],(folder,len(files),row)
    for f in files:
        im=Image.open(f);im.load();assert im.size==(960,540)
    if row['clip'] in ['CAUTION_CROUCH','CARE_REACH']:
        annotated=P/'previews'/('labelled_'+row['clip'].lower());annotated.mkdir(exist_ok=True)
        font=ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf',18)
        for f in files:
            im=Image.open(f).convert('RGB');d=ImageDraw.Draw(im);d.rectangle((0,0,960,38),fill=(75,39,28));d.text((20,7),'BLOCKING ONLY / hidden sleeves and joint artwork need redraws',font=font,fill=(255,227,195));im.save(annotated/f.name)
        folder=annotated
    encode(folder,row['frames'],path);movies.append((path,row['frames']))
concat=P/'previews/reel_concat.txt';concat.write_text('\n'.join("file '"+str(p).replace('\\','/')+"'" for p,_ in movies[:2]))
reel=P/'WTSC_Locomotion_First_Pack_Reel_v001.mp4'
run(['-y','-f','concat','-safe','0','-i',str(concat),'-c','copy','-movflags','+faststart',str(reel)],'reel_concat.log')
movies.append((reel,sum(n for _,n in movies[:2])))
blocking=P/'WTSC_Acting_Blocking_Studies_v001.mp4';concat2=P/'previews/blocking_concat.txt';concat2.write_text('\n'.join("file '"+str(p).replace('\\','/')+"'" for p,_ in movies[2:4]))
run(['-y','-f','concat','-safe','0','-i',str(concat2),'-c','copy','-movflags','+faststart',str(blocking)],'blocking_concat.log');movies.append((blocking,112))

# Neutral walk and the actual Blender-rendered production glyph alpha side by side.
folder=P/'previews/readability';folder.mkdir(exist_ok=True);coverages=[]
for f in range(1,97):
    src=Image.open(P/f'previews/walk/{f:04d}.png').convert('RGB');mask=Image.open(P/f'previews/native_mask/{f:04d}.png').getchannel('A')
    masked=Image.composite(src,Image.new('RGB',src.size,'black'),mask)
    canvas=Image.new('RGB',(1920,584),(20,24,27));canvas.paste(src,(0,44));canvas.paste(masked,(960,44));d=ImageDraw.Draw(canvas)
    font=ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf',20)
    d.text((20,10),'NEUTRAL WALK / actual Blender render',font=font,fill=(222,217,203));d.text((980,10),'COPIED PRODUCTION LETTERING / accelerated readability study',font=font,fill=(222,217,203))
    canvas.save(folder/f'{f:04d}.png');coverages.append(float(np.asarray(mask).mean()/255))
readability=P/'WTSC_Walk_Knockout_Readability_v001.mp4';encode(folder,96,readability);movies.append((readability,96))

font=ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf',24);small=ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf',18)
sheet=Image.new('RGB',(1280,842),(24,29,33));d=ImageDraw.Draw(sheet)
d.text((25,17),'WHEN THE SKY CLEARS / LOCOMOTION FIRST PACK v001',font=font,fill=(230,224,209))
choices=[('walk',1,'WALK / contact and retiming tested'),('walk',9,'WALK / passing pose'),('caution_crouch',24,'CAUTION CROUCH / BLOCKING ONLY'),('care_reach',32,'CARE REACH / BLOCKING ONLY')]
for i,(foldername,f,label) in enumerate(choices):
    im=Image.open(P/f'previews/{foldername}/{f:04d}.png').convert('RGB').resize((620,349),Image.Resampling.LANCZOS);x=10+(i%2)*640;y=63+(i//2)*390;sheet.paste(im,(x,y));d.text((x+5,y+354),label,font=small,fill=(201,207,205))
sheet.save(P/'WTSC_Locomotion_Contact_Sheet_v001.jpg',quality=92)

video_checks=[]
for path,count in movies:
    r=subprocess.run([str(F),'-v','error','-nostdin','-threads','2','-i',str(path),'-progress','pipe:1','-f','null','NUL'],capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
    fs=re.findall(r'^frame=(\d+)',r.stdout,re.M);assert r.returncode==0 and int(fs[-1])==count,(path,r.stderr,fs)
    assert path.stat().st_size<20_000_000
    video_checks.append({'file':path.name,'bytes':path.stat().st_size,'decoded_frames':count,'fps':24,'seconds':count/24,'under_20MB':True,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
append=json.loads((P/'evidence/append_validation.json').read_text())
result={'native':'native/WTSC_Locomotion_Library_v001.blend','preview':'WTSC_Locomotion_First_Pack_Reel_v001.mp4','movies':video_checks,
 'contact_validation':'evidence/append_validation.json','visible_support':'evidence/visible_support_samples.json','source_preservation':json.loads((P/'evidence/source_preservation.json').read_text()),
 'readability_mean_glyph_coverage_range':[min(coverages),max(coverages)],
 'completed_tested':['Two native editable planar character rigs using current packed v015 paint','Neutral walk and weary trudge loops, planted shoes and native NLA retiming','Fresh append, root placement/scale, in-place and root-motion controls','Actual CPU Blender previews and copied-production-lettering readability reel'],
 'blocking_not_completed':['Protective crouch and paired reaching; native keys/contact checked, but sleeve/underarm artwork missing at large bends. Labelled separately.'],
 'planned_not_completed':['skip/frolic','run','crawl','stumble/recovery','fall/get-up','helping lift from the ground','walk-to-crouch and walk-to-care contact-matched production transitions'],
 'limits':['First motion pack, not artistic or production acceptance','Visible art is native skinned/rigid flat 2D painted meshes; exact source GP outline retained hidden, not newly drawn frame-by-frame GP animation','Single profile source lacks hidden-surface redraws; extreme bends need dedicated artwork','Current crouch/reach are bounded first acting studies, not finished narrative performances','CARE_REACH authored for 0.66m hip spacing; retain that spacing for the hand-contact study','Readability study accelerates copied production glyphs over neutral stage; no final trailer/world integration','Regeneration scripts assume original project workspace; imported native library is self-contained'],
 'resources':'One sequential Blender process at a time; Cycles CPU only, two threads, no shared UI/GPU, no production scene writes'}
(P/'evidence/delivery_validation.json').write_text(json.dumps(result,indent=2))
archive=P/'WTSC_Locomotion_First_Pack_v001.zip'
files=[]
for foldername in ['native','scripts']:
    files.extend(p for p in (P/foldername).rglob('*') if p.is_file() and p.suffix not in ['.blend1','.pyc'])
files.extend(p for p in (P/'evidence').glob('*.json') if 'library' not in p.name)
files.extend([P/'IMPORT_GUIDE.txt',P/'MOTION_STATUS.txt',P/'WTSC_Locomotion_Contact_Sheet_v001.jpg',reel,readability,blocking])
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in files:z.write(p,p.relative_to(P))
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print(json.dumps({'archive':str(archive),'archive_bytes':archive.stat().st_size,'movies':video_checks,'files':len(files)},indent=2))
