from pathlib import Path
from PIL import Image,ImageDraw
import json,math
P=Path(__file__).resolve().parents[1];data=json.loads((P/'evidence/build_drawn.json').read_text());events=[v for v in data['debris'] if v['piece'] in [0,2,4,5]]
sheet=Image.new('RGB',(1600,820),(24,26,27));d=ImageDraw.Draw(sheet);records=[]
for row,v in enumerate(events):
    start=math.ceil(v['landing_age']+7)
    for col,fr in enumerate([start-1,start,start+1,start+3]):
        im=Image.open(P/f'previews/painted_motion/{fr:04d}.png').convert('RGB').crop((1260,615,1810,790));im.thumbnail((395,155));x=col*400;y=row*205;sheet.paste(im,(x,y+30));d.text((x+7,y+6),f"Piece {v['piece']} | actual frame {fr}",fill=(220,220,220));records.append({'piece':v['piece'],'frame':fr})
sheet.save(P/'previews/WTSC_Drawn_Impact_Actual_Contact_Peaks_v013.jpg',quality=94)
(P/'evidence/contact_peak_frames.json').write_text(json.dumps(records,indent=2));print('CONTACT_PEAK_SHEET_DONE')
