from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont,ImageChops
P=Path(__file__).resolve().parents[1];OLD=P.parent/'upper_body_pose_refinement_v028';BG=(224,221,211)
def font(n):return ImageFont.truetype('C:/Windows/Fonts/arial.ttf',n)
def text(b,xy,s,n=21):ImageDraw.Draw(b).text(xy,s,font=font(n),fill=(24,24,22))
for first in [1,17]:
    b=Image.new('RGB',(1920,480),BG);text(b,(16,10),f'V033 | actual consecutive shoe / sole / cuff review | F{first:02d}–F{first+15:02d}',26)
    for i,f in enumerate(range(first,first+16)):
        x=(i%8)*240;y=55+(i//8)*205;im=Image.open(P/f'previews/PROOF_CLOSE/{f:04d}.png').convert('RGB').crop((60,440,435,705)).resize((240,170));b.paste(im,(x,y+25));text(b,(x+8,y),f'F{f:02d}',18)
    b.save(P/f'previews/WTSC_v033_Shoe_Joins_F{first:02d}_{first+15:02d}.png')
b=Image.new('RGB',(1920,1580),BG);text(b,(16,10),'V028 preferred movement → V033 same movement / consistent footwear',30)
for row,ver in enumerate(['V028','V033']):
    for i,f in enumerate([1,11,17,27]):
        path=OLD/f'previews/CLOSE/{f:04d}.png' if ver=='V028' else P/f'previews/PROOF_CLOSE/{f:04d}.png';y=60+row*755;b.paste(Image.open(path).convert('RGB'),(i*480,y+28));text(b,(i*480+10,y),f'{ver} F{f:02d}',22)
b.save(P/'previews/WTSC_v033_Matched_Preferred_Movement_Board.png')
if (P/'previews/FLAT_SHARED_PAIR.png').exists():
    b=Image.new('RGB',(1280,940),BG);text(b,(16,10),'V028 movement retained | one consistent painted shoe design',28);text(b,(16,50),'Original V028 shoe drawings, normalized to flat for design inspection',21);b.paste(Image.open(P/'previews/FLAT_OLD_PAIR.png').convert('RGB'),(0,80));text(b,(16,495),'V033: one shared mesh / UV / paint / sole; far shoe uniformly97% for perspective',21);b.paste(Image.open(P/'previews/FLAT_SHARED_PAIR.png').convert('RGB'),(0,530));b.save(P/'previews/WTSC_v033_Consistent_Shoe_Design_Board.png')
diff=[]
for f in range(1,33):
    a=Image.open(OLD/f'previews/CLOSE/{f:04d}.png').convert('RGB');b=Image.open(P/f'previews/PROOF_CLOSE/{f:04d}.png').convert('RGB');ex=ImageChops.difference(a,b).crop((0,0,480,450)).getextrema();diff.append({'frame':f,'max_upper_body_RGB_difference':max(v[1] for v in ex)})
(P/'evidence/RENDERED_UPPER_BODY_REFERENCE_COMPARISON.json').write_text(json.dumps({'scope':'Matched actual V028/V033 frame crop comparison, not artistic acceptance','crop':[0,0,480,450],'maximum_RGB_channel_difference':max(r['max_upper_body_RGB_difference'] for r in diff),'frames':diff},indent=2));print('V033_BOARDS_SAVED',max(r['max_upper_body_RGB_difference'] for r in diff))
