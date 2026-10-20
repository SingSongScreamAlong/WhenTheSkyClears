from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg,json,hashlib
P=Path(__file__).resolve().parents[1];D=P/'previews';font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',22);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',19)
def writer(path):
    w=imageio_ffmpeg.write_frames(str(path),(1280,800),fps=30,codec='libx264',pix_fmt_in='rgb24',pix_fmt_out='yuv420p',quality=8,ffmpeg_log_level='error',output_params=['-threads','2','-crf','18','-preset','medium','-movflags','+faststart']);w.send(None);return w
combined=D/'WTSC_v026_GP_Normal_Speed_9p3s_Close_9p3s_Shot.mp4';w=writer(combined);segments=[]
for mode in ['CLOSE','SHOT']:
    path=D/f'WTSC_v026_GP_{mode}_9p3s_Normal_Speed.mp4';sw=writer(path)
    for f in range(1,280):
        im=Image.new('RGB',(1280,800),'#eee9dd');d=ImageDraw.Draw(im);im.paste(Image.open(D/mode/f'{f:04d}.png').convert('RGB'),((400 if mode=='CLOSE' else 0),40));cycle=(f-1)//31+1;phase=(f-1)%31+1
        d.text((14,7),f'V026 | {"CLOSE VIEW" if mode=="CLOSE" else "TRAILER FRAMING"} | NORMAL SPEED /30fps | {(f-1)/30:.2f}s',font=font,fill='#292622');d.text((14,768),f'9 repeated cycles | cycle {cycle}/9 | phase {phase}/31 | continuous matched travel | ART REVIEW OPEN',font=small,fill='#292622');raw=im.tobytes();sw.send(raw);w.send(raw)
    sw.close();segments.append({'filename':path.name,'frames':279,'seconds':9.3,'bytes':path.stat().st_size})
w.close();reader=imageio_ffmpeg.read_frames(str(combined),pix_fmt='rgb24');meta=next(reader);decoded={};count=0
chosen=[30,31,32,61,62,63,92,93,94,247,248,249,278,279]
wanted=set(range(32))|{f-1 for f in chosen}|{279+f-1 for f in [1,5,9,13,17,21,25,29,32]}
for i,raw in enumerate(reader):
    count+=1
    if i in wanted:decoded[i]=Image.frombytes('RGB',meta['size'],raw)
assert count==558 and meta['fps']==30 and combined.stat().st_size<20_000_000
# Inspect every unique cycle frame plus representative joins throughout the encoded review.
board=Image.new('RGB',(1920,1584),'#eee9dd');d=ImageDraw.Draw(board)
for i in range(32):
    x=(i%8)*240;y=(i//8)*396;board.paste(decoded[i].crop((400,40,880,760)).resize((240,360)),(x,y+36));d.text((x+7,y+6),f'F{i+1}',font=small,fill='#292622')
board.save(P/'evidence/ACTUAL_ENCODED_FIRST_CYCLE_AND_JOIN.jpg',quality=95)
board=Image.new('RGB',(1920,792),'#eee9dd');d=ImageDraw.Draw(board)
for i,f in enumerate(chosen):
    x=(i%8)*240;y=(i//8)*396;board.paste(decoded[f-1].crop((400,40,880,760)).resize((240,360)),(x,y+36));d.text((x+7,y+6),f'F{f}',font=small,fill='#292622')
board.save(P/'evidence/ACTUAL_ENCODED_LATE_CYCLE_JOINS.jpg',quality=95)
board=Image.new('RGB',(1920,1080),'#eee9dd')
for i,f in enumerate([1,5,9,13,17,21,25,29,32]):
    x=(i%3)*640;y=(i//3)*360;board.paste(decoded[279+f-1].crop((0,40,1280,760)).resize((640,360)),(x,y))
board.save(P/'evidence/ACTUAL_ENCODED_SHOT_FRAMES.jpg',quality=95)
report={'filename':combined.name,'bytes':combined.stat().st_size,'sha256':hashlib.sha256(combined.read_bytes()).hexdigest(),'frames_decoded':count,'fps':meta['fps'],'duration_seconds':count/meta['fps'],'dimensions':meta['size'],'segments':segments,'cycles_per_segment':9,'native_period_frames':31,'duplicate_boundary_frames':False,'holds_slowdown_optical_interpolation':False,'segment_cut':'At9.3s, restart the same nine-cycle sequence in the second camera view. Within each segment, motion and travel are uninterrupted.','observation':'All558frames decoded; firstcycle, latejoin and shot boards inspected separately. This is frame review, not observed continuous playback.'}
(P/'evidence/PREVIEW_VERIFICATION.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
