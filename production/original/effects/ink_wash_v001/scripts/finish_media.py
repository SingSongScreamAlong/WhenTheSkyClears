import json,subprocess,re,hashlib,zipfile
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parents[1];R=P.parents[1]
F=Path(r'WTSC_LOCAL_USER\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe')
video=P/'WTSC_FX_Reel_v001.mp4'
args=[str(F),'-hide_banner','-nostdin','-y','-framerate','24','-start_number','1','-i',str(P/'previews/reel_frames%04d.png'),'-frames:v','144','-an','-c:v','libx264','-preset','fast','-crf','19','-threads','2','-pix_fmt','yuv420p','-movflags','+faststart',str(video)]
e=subprocess.run(args,capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW);(P/'evidence/reel_encode.log').write_text(e.stderr);assert e.returncode==0,e.stderr
e=subprocess.run([str(F),'-v','error','-nostdin','-i',str(video),'-progress','pipe:1','-f','null','NUL'],capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
frames=re.findall(r'^frame=(\d+)',e.stdout,re.M);assert e.returncode==0 and int(frames[-1])==144,(e.stderr,frames)
assert video.stat().st_size<20_000_000
sequences=json.loads((P/'evidence/sequence_manifest.json').read_text());checks=[];tiles=[]
font=ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf',21);small=ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf',16)
for i,spec in enumerate(sequences):
    folder=P/spec['folder'];files=sorted(folder.glob('*.png'));assert len(files)==spec['frame_range'][1]
    edge=0;amin=255;amax=0;bbox=None;nonempty=0
    for f in files:
        im=Image.open(f);assert im.mode=='RGBA' and im.size==tuple(spec['pixels']),str(f)
        a=np.array(im)[:,:,3];amin=min(amin,int(a.min()));amax=max(amax,int(a.max()));edge=max(edge,int(a[0].max()),int(a[-1].max()),int(a[:,0].max()),int(a[:,-1].max()));nonempty+=int(a.max()>0)
    idx=32 if spec['collection'].startswith('FX01') else 16 if spec['collection'].startswith('FX06') else 48;im=Image.open(folder/f'{idx:04}.png').convert('RGBA');a=np.array(im)[:,:,3];ys,xs=np.where(a>4)
    bbox=[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())] if len(xs) else None
    assert amax>0 and amin==0 and edge<=2,(spec['collection'],amin,amax,edge)
    last_alpha=int(np.array(Image.open(files[-1]))[:,:,3].max())
    if not spec['loop']:assert last_alpha==0,(spec['collection'],last_alpha)
    checks.append({'collection':spec['collection'],'count':len(files),'all_png_decoded':True,'alpha_min':amin,'alpha_max':amax,'max_outer_edge_alpha':edge,'nonempty_frames':nonempty,'sample_frame':idx,'sample_alpha_bounds':bbox,'last_frame_alpha_max':last_alpha})

assets=json.loads((P/'evidence/asset_manifest.json').read_text())['assets']
for spec in assets:
    im=Image.open(P/'previews/native_assets'/f"{spec['collection']}.png").convert('RGBA')
    tile=Image.new('RGB',(400,352),(25,30,34));d=ImageDraw.Draw(tile)
    checker=Image.new('RGBA',(300,260),(143,148,148,255));cd=ImageDraw.Draw(checker)
    for y in range(0,260,20):
        for x in range(0,300,20):
            if (x//20+y//20)%2:cd.rectangle([x,y,x+19,y+19],fill=(161,164,161,255))
    layer=im.resize((260,260),Image.Resampling.LANCZOS);checker.alpha_composite(layer,(20,0));tile.paste(checker.convert('RGB'),(50,12))
    label=spec['collection'].replace('_',' ').replace('Explosion ','Burst ')
    d.text((20,285),label,font=small,fill=(226,221,204));d.text((20,314),f"24fps  |  {spec['frames']} frames  |  {'LOOP' if spec['loop'] else 'ONE SHOT'}",font=small,fill=(156,163,164));tiles.append(tile)
sheet=Image.new('RGB',(1200,1150),(25,30,34));d=ImageDraw.Draw(sheet);d.text((30,22),'WHEN THE SKY CLEARS  /  INK + WASH FX v001',font=font,fill=(229,222,200));d.text((30,58),'Native collections + straight-alpha working sequences  /  checkerboard shows transparency',font=small,fill=(164,173,175))
for i,t in enumerate(tiles):sheet.paste(t,((i%3)*400,92+(i//3)*352))
sheet.save(P/'WTSC_FX_Contact_Sheet_v001.jpg',quality=92)
source_before=json.loads((P/'evidence/project_inspection.json').read_text())['source_fingerprints'];unchanged={p:hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in source_before.items()};assert all(unchanged.values())
report={'reel':{'filename':video.name,'bytes':video.stat().st_size,'decoded_frames':144,'fps':24,'seconds':6,'pixels':[960,540],'sound':False,'under20MB':True,'resource_handoff':'Uses first144 complete frames; own Eevee process stopped when parent asked for CPU-only. Subsequent rendering sequential two-thread CPU only.'},'sequences':checks,'total_png_frames':sum(x['count'] for x in checks),'source_hashes_unchanged':unchanged,'tested':'Append nine collections; independent Append timing/materials; Link dependency load; loop numeric seam; actual world read-only render; all RGBA PNG decode, alpha bounds, complete H264 decode.','limitations':['Three complete256px CPU working sequences; remaining six effects native plus512px transparent stills','Artistic first pass; no production placement approval','Link hierarchy overrides not tested; linked animation is shared','World integration uses low-resolution CPU Cycles; GP rendering can differ from production Eevee','No live production scene mutation or shared UI control']}
(P/'evidence/delivery_validation.json').write_text(json.dumps(report,indent=2))
# Deliver only this effects work. Omit large temporary representative-reel PNGs,
# Blender backups, raw diagnostic logs, and Library identity from the archive.
archive=P/'WTSC_Ink_Wash_FX_Pack_v001.zip'
included=[]
for folder in ['native','sequences','scripts']:
    included.extend(p for p in (P/folder).rglob('*') if p.is_file() and p.suffix not in ['.blend1','.pyc'])
included.extend((P/'evidence').glob('*.json'))
included.extend((P/'previews/native_assets').glob('*.png'))
included.extend([P/'IMPORT_GUIDE.txt',video,P/'WTSC_FX_Contact_Sheet_v001.jpg',P/'previews/WTSC_FX_Actual_World_Integration_v001.png'])
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(included):z.write(p,p.relative_to(P))
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print('FX_DELIVERY_VALIDATED',json.dumps({'archive_bytes':archive.stat().st_size,'reel':report['reel'],'total_png_frames':report['total_png_frames'],'archive_files':len(included),'source_hashes_unchanged':unchanged}),flush=True)
