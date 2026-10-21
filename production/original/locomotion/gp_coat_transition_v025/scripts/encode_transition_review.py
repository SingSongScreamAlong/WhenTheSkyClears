from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg,hashlib,json
P=Path(__file__).resolve().parents[1];D=P/'previews';font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',23);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',19)
frames=[]
for f in range(17,33):
    canvas=Image.new('RGB',(1920,1184),'#eee9dd');d=ImageDraw.Draw(canvas)
    for label,mode,x in [('Preserved v024','V024_CLOSE',0),('GP v025 | rough coat','GP_CLOSE',480),('Coat-free loading check','BARE_CLOSE',960)]:
        im=Image.open(D/mode/f'{f:04d}.png').convert('RGB');canvas.paste(im,(x+60,38));d.text((x+12,7),label,font=font,fill='#292622')
    d.text((1450,64),'ONE TRANSITION',font=font,fill='#292622');d.text((1450,106),f'Native F17-32 | F{f}',font=small,fill='#292622');d.text((1450,146),'30fps | no slowdown',font=small,fill='#292622');d.text((1450,202),'Editable GP drawings.',font=small,fill='#292622');d.text((1450,244),'Original identity retained.',font=small,fill='#292622');d.text((1450,300),'Rough cloth paint.',font=small,fill='#292622');d.text((1450,342),'ART APPROVAL OPEN.',font=small,fill='#292622')
    for label,mode,x in [('v024 | same shot framing','V024_SHOT',0),('v025 | same shot framing','GP_SHOT',960)]:
        d.text((x+12,588),label,font=font,fill='#292622');canvas.paste(Image.open(D/mode/f'{f:04d}.png').convert('RGB'),(x,622))
    d.text((12,1164),'Normal-speed half-step comparison. Frame review does not establish continuous-playback acceptance.',font=small,fill='#292622');frames.append(canvas)
def encode(path,images):
    w=imageio_ffmpeg.write_frames(str(path),(1920,1184),fps=30,codec='libx264',pix_fmt_in='rgb24',pix_fmt_out='yuv420p',quality=8,ffmpeg_log_level='error',output_params=['-threads','2','-crf','18','-preset','medium','-movflags','+faststart']);w.send(None)
    for im in images:w.send(im.tobytes())
    w.close()
single=D/'WTSC_v025_GP_Coat_Transition_ONE_PASS_30fps.mp4';encode(single,frames)
replay=D/'WTSC_v025_GP_Coat_Transition_Normal_Speed_4_Replays.mp4';replays=[]
for j in range(4):
    for frame in frames:
        im=frame.copy();d=ImageDraw.Draw(im);d.rectangle((1440,410,1919,560),fill='#eee9dd');d.text((1450,430),f'PASS {j+1}/4',font=font,fill='#292622');d.text((1450,475),'Hard reset after16frames.',font=small,fill='#292622');d.text((1450,513),'This is not a loop test.',font=small,fill='#292622');replays.append(im)
encode(replay,replays)
reader=imageio_ffmpeg.read_frames(str(replay),pix_fmt='rgb24');meta=next(reader);decoded=[Image.frombytes('RGB',meta['size'],raw) for raw in reader]
assert len(decoded)==64 and meta['fps']==30 and replay.stat().st_size<20_000_000
board=Image.new('RGB',(1920,864),'#eee9dd');draw=ImageDraw.Draw(board)
for i in range(16):
    x=(i%8)*240;y=(i//8)*432;im=decoded[i];board.paste(im.crop((540,38,900,578)).resize((240,360)),(x,y+36));draw.text((x+7,y+6),f'F{i+17}',font=small,fill='#292622')
board.save(P/'evidence/ACTUAL_ENCODED_GP_ALL_16_FRAMES.jpg',quality=95)
frames[4].save(D/'WTSC_v025_GP_TRANSITION_MATCHED_COMPARISON.jpg',quality=95)
report={'one_pass':{'filename':single.name,'frames':16,'seconds':16/30,'bytes':single.stat().st_size},'review':{'filename':replay.name,'frames_decoded':len(decoded),'fps':meta['fps'],'seconds':len(decoded)/meta['fps'],'size':meta['size'],'bytes':replay.stat().st_size,'sha256':hashlib.sha256(replay.read_bytes()).hexdigest()},'speed':'Original30fps, no holds, optical interpolation or retiming. Four replays of the16-frame transition, with hard resets explicitly labelled. Not a full cycle or seamless loop.','observation':'Encoded frames inspected, actual real-time playback not observable with exposed tools.'}
(P/'evidence/PREVIEW_VERIFICATION.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
