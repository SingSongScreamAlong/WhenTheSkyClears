import json,subprocess,re,hashlib,zipfile,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parents[1];R=P.parents[1]
F=Path(r'WTSC_LOCAL_USER\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe')
previews=json.loads((P/'evidence/preview_manifest.json').read_text());proj=json.loads((P/'evidence/projection_samples.json').read_text());lookup={(r['clip'],r['frame']):r for r in proj}
def gray(im):return np.array(im.convert('L'),dtype=np.float32)
def corr(a,b):
    a=a-a.mean();b=b-b.mean();return float((a*b).sum()/max(1e-9,np.sqrt((a*a).sum()*(b*b).sum())))
def shift(a,b,box):
    x0,y0,x1,y1=box;tpl=a[y0:y1,x0:x1]
    if tpl.size==0 or tpl.std()<1:return None
    scored=[(corr(tpl,b[y0:y1,x0+dx:x1+dx]),dx) for dx in range(-12,13) if x0+dx>=0 and x1+dx<b.shape[1]]
    return max(scored)
metrics=[];videos=[]
for row in previews:
    folder=P/row['folder'];files=sorted(folder.glob('[0-9][0-9][0-9][0-9].png'));assert len(files)==row['frames']
    previous=None;previous_meta=None;matches=[];gaps=[]
    for f,path in enumerate(files,1):
        im=Image.open(path);im.load();assert im.size==(960,540);a=gray(im);meta=lookup[row['clip'],f];floor=meta['floor_row_pixels']
        for ft in meta['feet']:
            if ft['contact']:
                x0,_,x1,_=ft['bounds_pixels'];x0=max(0,int(x0));x1=min(959,int(x1)+1);y0=max(0,int(floor)-6);y1=min(539,int(floor)+4)
                ys,xs=np.where(a[y0:y1,x0:x1]<95)
                if len(ys):gaps.append(float(floor-(ys.max()+y0)))
        if previous is not None:
            gy=int(round(meta['ground_row_pixels']));g=shift(previous,a,(100,gy-1,860,gy+2))
            for ft in meta['feet']:
                before=next(q for q in previous_meta['feet'] if q['who']==ft['who'] and q['side']==ft['side'])
                if not (ft['contact'] and before['contact'] and abs(ft['pitch'])<1e-5 and abs(before['pitch'])<1e-5):continue
                x0,_,x1,_=before['bounds_pixels'];x0=max(15,int(math.floor(x0))+3);x1=min(944,int(math.ceil(x1))-3)
                if x1-x0<17:continue
                y1=int(math.floor(floor))-1;y0=y1-19;shoe=shift(previous,a,(x0,y0,x1,y1))
                if shoe and g and shoe[0]>.65 and g[0]>.45:matches.append({'frame':f,'who':ft['who'],'side':ft['side'],'shoe_dx_px':shoe[1],'ground_dx_px':g[1],'error_px':shoe[1]-g[1],'shoe_correlation':shoe[0],'ground_correlation':g[0]})
        previous=a;previous_meta=meta
    err=[abs(m['error_px']) for m in matches]
    metrics.append({'clip':row['clip'],'method':'Independent normalized pixel-patch cross-correlation on actual rendered flat planted boot versus visible ground ticks, consecutive frames. Rolling/airborne frames excluded.','matches':len(matches),'median_abs_delta_error_pixels':float(np.median(err)) if err else None,'max_abs_delta_error_pixels':max(err) if err else None,'contact_paint_gap_pixels_range':[min(gaps),max(gaps)] if gaps else None,'samples':matches})
    path=P/('WTSC_'+row['clip']+'_Reel_v005.mp4')
    cmd=[str(F),'-hide_banner','-nostdin','-y','-framerate','24','-start_number','1','-i',str(folder/'%04d.png'),'-frames:v',str(row['frames']),'-an','-c:v','libx264','-preset','fast','-crf','18','-threads','2','-pix_fmt','yuv420p','-movflags','+faststart',str(path)]
    rr=subprocess.run(cmd,capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW);assert rr.returncode==0,rr.stderr
    rr=subprocess.run([str(F),'-v','error','-nostdin','-threads','2','-i',str(path),'-progress','pipe:1','-f','null','NUL'],capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW);frames=re.findall(r'^frame=(\d+)',rr.stdout,re.M);assert rr.returncode==0 and int(frames[-1])==row['frames']
    assert path.stat().st_size<20_000_000;videos.append({'path':path.name,'bytes':path.stat().st_size,'decoded_frames':row['frames'],'fps':24,'seconds':row['frames']/24,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
(P/'evidence/rendered_contact_review.json').write_text(json.dumps(metrics,indent=2))
(P/'evidence/video_validation.json').write_text(json.dumps(videos,indent=2))

font=ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf',25);small=ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf',19)
for cid,frames in [('BATTLEFIELD_WEARY_STUMBLE',[1,16,24,31,39,44,51,61,71,81,101,120])]:
    folder=next(P/r['folder'] for r in previews if r['clip']==cid);sheet=Image.new('RGB',(1920,1604),(24,28,31));d=ImageDraw.Draw(sheet)
    d.text((24,16),'WHEN THE SKY CLEARS / '+cid.replace('_',' ')+' / v005 ARTISTIC REVIEW',font=font,fill=(230,224,208))
    for i,f in enumerate(frames):
        x=10+(i%3)*640;y=62+(i//3)*381
        # 720x405 crop and 620x349 display retain the native16:9 proportions.
        # Includes the highest hair tips and visible ground below the soles.
        im=Image.open(folder/f'{f:04d}.png').convert('RGB').crop((120,90,840,495)).resize((620,349),Image.Resampling.LANCZOS)
        sheet.paste(im,(x,y));d.text((x+8,y+354),f'FRAME {f:02d} / {(f-1)/24:.3f}s',font=small,fill=(208,214,209))
    sheet.save(P/('WTSC_'+cid+'_Contact_Sheet_v005.jpg'),quality=94)
print(json.dumps({'videos':videos,'rendered_contact_metrics':[{k:v for k,v in m.items() if k!='samples'} for m in metrics]},indent=2))


