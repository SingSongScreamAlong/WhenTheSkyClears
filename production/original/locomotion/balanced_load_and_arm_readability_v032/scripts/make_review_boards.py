from pathlib import Path
import json,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parents[1];OLD=P.parent/'rough_breakdowns_construction_v031';sys.path.insert(0,str(P/'scripts'));import construction_motion as M
BG=(224,221,211)
def font(n):return ImageFont.truetype('C:/Windows/Fonts/arial.ttf',n)
def text(b,xy,s,n=20):ImageDraw.Draw(b).text(xy,s,font=font(n),fill=(24,24,22))
def path(version,f,mode='CLOSE'):return OLD/f'previews/{mode}/{f:04d}.png' if version=='V031' else P/f'previews/PROOF_{mode}/{f:04d}.png'
for first in [1,17]:
    b=Image.new('RGB',(1920,850),BG);text(b,(16,12),f'V032 | ROUGH CONSTRUCTION | consecutive F{first}–{first+15} | 30fps | ART REVIEW OPEN',27)
    for i,f in enumerate(range(first,first+16)):
        x=(i%8)*240;y=60+(i//8)*390;b.paste(Image.open(path('V032',f)).convert('RGB').resize((240,360)),(x,y+24));text(b,(x+8,y),f'F{f:02d}',18)
    b.save(P/f'previews/WTSC_v032_All_Breakdowns_F{first:02d}_{first+15:02d}.png')
for start in [12,28]:
    b=Image.new('RGB',(1920,830),BG);text(b,(16,12),f'Landing comparison | consecutive F{start}–{start+9} | V031 above / V032 below',27)
    for row,version in enumerate(['V031','V032']):
        for i,f in enumerate(range(start,start+10)):
            x=i*192;y=65+row*370;b.paste(Image.open(path(version,f)).convert('RGB').resize((192,288)),(x,y+28));text(b,(x+7,y),f'{version} F{f:02d}',17)
    text(b,(16,791),'Actual matched-camera renders. Head design unchanged; body spacing and arm staging revised. Construction test, not artistic acceptance.',21)
    b.save(P/f'previews/WTSC_v032_Landing_Consecutive_F{start:02d}_{start+9:02d}.png')
b=Image.new('RGB',(1920,790),BG);text(b,(16,12),'Arm / body-mass comparison | actual crops | V031 above / V032 below',29)
for row,version in enumerate(['V031','V032']):
    for i,f in enumerate([17,20,23,26]):
        x=i*480;y=65+row*355;im=Image.open(path(version,f)).convert('RGB').crop((130,180,370,470)).resize((270,326));b.paste(im,(x+95,y+25));text(b,(x+12,y),f'{version} F{f:02d}',20)
b.save(P/'previews/WTSC_v032_Arm_Overlap_Comparison.png')
b=Image.new('RGB',(1920,1620),BG);text(b,(16,12),'V031 → V032 | contact and loading | matched actual whole-body frames',29)
for row,version in enumerate(['V031','V032']):
    for i,f in enumerate([1,4,17,20]):
        x=i*480;y=70+row*770;b.paste(Image.open(path(version,f)).convert('RGB'),(x,y+30));text(b,(x+10,y),f'{version} F{f:02d}',23)
b.save(P/'previews/WTSC_v032_Construction_Comparison_Board.png')
b=Image.new('RGB',(2560,790),BG);text(b,(16,12),'V031 → V032 | selected actual shot-size frames | neutral stage, not production integration',29)
for row,version in enumerate(['V031','V032']):
    for i,f in enumerate([13,17,20,26]):
        x=i*640;y=65+row*355;b.paste(Image.open(path(version,f,'SHOT')).convert('RGB').resize((640,360)),(x,y));text(b,(x+8,y),f'{version} F{f:02d}',19)
b.save(P/'previews/WTSC_v032_Shot_Comparison_Board.png')
metrics={}
for version in ['V031','V032']:
    tops={}
    for f in range(1,38):
        im=np.array(Image.open(path(version,f)).convert('RGB'));mask=np.max(im[:220,140:390,:],axis=2)<70;ys=np.where(mask)[0];assert len(ys);tops[f]=int(ys.min())
    metrics[version]={'actual_head_top_pixels_by_frame':tops,'up_to_contact_head_drop_px':[tops[17]-tops[13],tops[33]-tops[29]],'contact_to_down_head_drop_px':[tops[4]-tops[1],tops[20]-tops[17]],'landing1_consecutive_head_y':[tops[f] for f in range(13,21)],'landing2_consecutive_head_y':[tops[f] for f in range(29,37)]}
model={}
for key in ['hip','rib','neck','waist']:
    vals={f:M.evaluate(f-1)[0][key][1] for f in [1,4,13,17,20,29,33,36]};model[key]={'metres':vals,'projected_up_to_contact_drop_px':[(vals[13]-vals[17])*480/1.1,(vals[29]-vals[33])*480/1.1],'projected_contact_to_down_drop_px':[(vals[1]-vals[4])*480/1.1,(vals[17]-vals[20])*480/1.1]}
report={'scope':'Actual-render head spacing measurement plus authored body-anchor projection. Supporting comparison evidence, not artistic approval.','head_measurement':'Topmost dark head pixel in actual close-frame crop x140..389,y0..219, maxRGB<70. Unchanged preserved head design.','rendered':metrics,'body_anchor_projection':model,'body_contour_widths':'V031 contour width coefficients and thigh/calf widths retained. Body anchor positions and arm silhouettes change; no torso slimming or scale change.'}
(P/'evidence/ACTUAL_FRAME_SPACING_COMPARISON.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:{j:v for j,v in r.items() if j!='actual_head_top_pixels_by_frame'} for k,r in metrics.items()},indent=2))
