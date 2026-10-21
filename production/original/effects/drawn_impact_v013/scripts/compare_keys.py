from pathlib import Path
from PIL import Image,ImageDraw
import json
P=Path(__file__).resolve().parents[1]
for name,frames,crop in [('Onset',[7,8,9,10],(1300,605,1790,790)),('Contacts',[18,22,30,36],(1260,600,1810,795))]:
    out=Image.new('RGB',(1600,430),(24,26,27));d=ImageDraw.Draw(out)
    for row,ver in enumerate([12,13]):
        for col,fr in enumerate(frames):
            path=P.parent/f'drawn_impact_v0{ver}/previews/painted_keys/{fr:04d}.png'
            im=Image.open(path).convert('RGB').crop(crop);im.thumbnail((395,175))
            x=col*400;y=row*215;out.paste(im,(x,y+28));d.text((x+8,y+7),f'v0{ver} actual frame {fr}',fill=(220,220,220))
    out.save(P/f'previews/WTSC_v012_v013_{name}_Actual_Comparison.jpg',quality=94)
print('ACTUAL_COMPARISONS_SAVED')
