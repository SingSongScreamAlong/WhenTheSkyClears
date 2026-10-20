"""Prepare indexed crops of the twelve observed side-profile photographs."""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parents[1];R=P/'reference';R.mkdir(exist_ok=True)
path=R/'Muybridge_Animal_Locomotion_Plate_2_1887.jpg';im=Image.open(path).convert('RGB')
assert im.size==(3782,2166),im.size
board=Image.new('RGB',(4*340,3*600),'#e9e1cc');d=ImageDraw.Draw(board)
font=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',22)
records=[]
for i in range(12):
    x0=30+round(i*(im.width-60)/12);x1=30+round((i+1)*(im.width-60)/12)
    rect=(x0,32,x1,620)
    crop=im.crop(rect);crop.thumbnail((330,560))
    x=i%4*340;y=i//4*600
    board.paste(crop,(x,y+30));d.text((x+8,y+3),str(i+1),fill='black',font=font)
    records.append({'phase':i+1,'source_crop':rect,'board_position':(x,y+30)})
out=R/'Muybridge_Plate2_Side_12_Phases_Board.jpg';board.save(out,quality=93)
(R/'PHOTO_SOURCE.json').write_text(json.dumps({'source_url':'https://commons.wikimedia.org/wiki/File:Animal_locomotion._Plate_2_(Boston_Public_Library).jpg',
 'original_file_url':'https://upload.wikimedia.org/wikipedia/commons/e/e5/Animal_locomotion._Plate_2_%28Boston_Public_Library%29.jpg',
 'creator':'Eadweard Muybridge','date':1887,'status':'Wikimedia Commons public-domain mark; twelve observed side-profile photos only',
 'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'size':list(im.size),'side_phase_crops':records,
 'limits':'No verified capture rate, no continuous footage, no child subject; timing and all inbetweens must be adapted.'},indent=2))
print('V057_PHOTO_PLATE_INSPECTED',out)
