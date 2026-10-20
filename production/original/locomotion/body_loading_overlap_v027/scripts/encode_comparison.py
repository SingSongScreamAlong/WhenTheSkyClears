"""Normal-speed matched comparison. Reuse original baseline PNGs; no retiming.
All movie frames are decoded after encoding, without keeping the movie in RAM.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg,json,hashlib,numpy as np
P=Path(__file__).resolve().parents[1];D=P/'previews';OLD=P.parent/'gp_extended_review_v026/previews'
if not (OLD/'CLOSE/0001.png').exists():OLD=D/'BASELINE'
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',22);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',19)
def writer(path):
    w=imageio_ffmpeg.write_frames(str(path),(1280,800),fps=30,codec='libx264',pix_fmt_in='rgb24',pix_fmt_out='yuv420p',quality=8,ffmpeg_log_level='error',output_params=['-threads','2','-crf','18','-preset','medium','-movflags','+faststart']);w.send(None);return w
def load(folder,mode,f):
    im=Image.open(folder/mode/f'{f:04d}.png').convert('RGB');assert im.size==((480,720) if mode=='CLOSE' else (1280,720));return im
def canvas():return Image.new('RGB',(1280,800),'#eee9dd')
def footer(im,f,label):
    ImageDraw.Draw(im).text((14,768),f'{label} | cycle {(f-1)//31+1}/9 | phase {(f-1)%31+1}/31 | {(f-1)/30:.2f}s | ART OPEN',font=small,fill='#292622')
movie=D/'WTSC_v027_vs_v026_Loading_Comparison_27p9s.mp4';w=writer(movie)
for segment in ['CLOSE_MATCH','BASELINE_SHOT','CANDIDATE_SHOT']:
    for f in range(1,280):
        im=canvas();d=ImageDraw.Draw(im)
        if segment=='CLOSE_MATCH':
            im.paste(load(OLD,'CLOSE',f),(80,40));im.paste(load(D,'CLOSE',f),(720,40));d.text((80,7),'V026 | PRESERVED BASELINE',font=font,fill='#292622');d.text((720,7),'V027 | LOADING / PASSIVE HEM',font=font,fill='#292622')
        else:
            candidate=segment=='CANDIDATE_SHOT';im.paste(load(D if candidate else OLD,'SHOT',f),(0,40));d.text((14,7),f'{"V027 LOADING" if candidate else "V026 BASELINE"} | ORIGINAL SHOT FRAMING | NORMAL SPEED / 30fps',font=font,fill='#292622')
        footer(im,f,'MATCHED MOTION / 30fps' if segment=='CLOSE_MATCH' else 'UNCHANGED CAMERA / TRAVEL');w.send(im.tobytes())
    print('COMPARISON_SEGMENT_ENCODED',segment,flush=True)
w.close();segments=[]
for mode in ['CLOSE','SHOT']:
    path=D/f'WTSC_v027_{mode}_9p3s_Normal_Speed.mp4';sw=writer(path)
    for f in range(1,280):
        im=canvas();im.paste(load(D,mode,f),(400 if mode=='CLOSE' else 0,40));ImageDraw.Draw(im).text((14,7),f'V027 | {mode} | NORMAL SPEED / 30fps | LOADING + PASSIVE HEM',font=font,fill='#292622');footer(im,f,'UNINTERRUPTED CANDIDATE');sw.send(im.tobytes())
    sw.close();segments.append({'filename':path.name,'frames':279,'seconds':9.3,'bytes':path.stat().st_size})
reader=imageio_ffmpeg.read_frames(str(movie),pix_fmt='rgb24');meta=next(reader);count=0;decoded={};blue=[]
chosen=[30,31,32,61,62,63,92,93,94,247,248,249,278,279]
wanted=set(range(32))|{f-1 for f in chosen}|{279+f-1 for f in [1,4,9,17,20,27,31]}|{558+f-1 for f in [1,4,9,17,20,27,31]}
for i,raw in enumerate(reader):
    count+=1
    if i in wanted:decoded[i]=Image.frombytes('RGB',meta['size'],raw)
    a=np.frombuffer(raw,np.uint8).reshape((800,1280,3)).astype(np.int16)
    if ((a[:,:,2]>150)&(a[:,:,2]>a[:,:,0]+60)&(a[:,:,2]>a[:,:,1]+60)).any():blue.append(i+1)
assert count==837 and meta['fps']==30 and movie.stat().st_size<20_000_000 and not blue
# Every unique phase from the actual encoded side-by-side segment.
board=Image.new('RGB',(1920,864),'#eee9dd');d=ImageDraw.Draw(board)
for i in range(32):
    x=(i%8)*240;y=(i//8)*216;sample=decoded[i]
    # Keep the normal aspect ratio: each 120x180 thumbnail represents one view.
    left=sample.crop((80,40,560,760)).resize((120,180));right=sample.crop((720,40,1200,760)).resize((120,180))
    board.paste(left,(x,y+36));board.paste(right,(x+120,y+36));d.text((x+5,y+8),f'F{i+1} | 026 / 027',font=small,fill='#292622')
board.save(P/'evidence/ACTUAL_ENCODED_FIRST_CYCLE_COMPARISON.jpg',quality=95)
for f in [4,20,26]:decoded[f-1].save(P/f'evidence/ACTUAL_ENCODED_MATCHED_F{f:03d}.png')
board=Image.new('RGB',(1920,800),'#eee9dd');d=ImageDraw.Draw(board)
for i,f in enumerate(chosen):
    x=(i%8)*240;y=(i//8)*400;board.paste(decoded[f-1].crop((720,40,1200,760)).resize((240,360)),(x,y+40));d.text((x+6,y+6),f'V027 | F{f}',font=small,fill='#292622')
board.save(P/'evidence/ACTUAL_ENCODED_LATE_JOINS.jpg',quality=95)
board=Image.new('RGB',(2240,800),'#eee9dd');d=ImageDraw.Draw(board)
for row,offset in [(0,279),(1,558)]:
    for i,f in enumerate([1,4,9,17,20,27,31]):
        x=i*320;y=row*400;sample=decoded[offset+f-1];board.paste(sample.crop((0,40,1280,760)).resize((320,180)),(x,y+40));board.paste(sample.crop((480,200,800,600)).resize((160,200)),(x+80,y+200));d.text((x+8,y+7),f'{"V026" if row==0 else "V027"} SHOT | F{f}',font=small,fill='#292622')
board.save(P/'evidence/ACTUAL_ENCODED_MATCHED_SHOT_FRAMES.jpg',quality=95)
report={'filename':movie.name,'bytes':movie.stat().st_size,'sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),'frames_decoded':count,'fps':meta['fps'],'duration_seconds':count/meta['fps'],'dimensions':meta['size'],'candidate_only_segments':segments,'comparison_segments':[{'start_seconds':0,'seconds':9.3,'view':'matched close, baseline left / v027 right'},{'start_seconds':9.3,'seconds':9.3,'view':'baseline shot framing'},{'start_seconds':18.6,'seconds':9.3,'view':'v027 shot framing'}],'cycles_per_segment':9,'native_period_frames':31,'duplicate_boundary_frames':False,'retiming_or_generated_inbetweens':False,'blue_fill_artifact_frames':blue,'continuous_playback_observed':False,'visual_review_status':'Decoded all837frames; contact-sheet visual inspection follows. This is not observed continuous playback.'}
(P/'evidence/PREVIEW_VERIFICATION.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
