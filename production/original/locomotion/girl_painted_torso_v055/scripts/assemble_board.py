"""Assemble actual v053/v055 key-frame comparisons at crop and shot size."""
import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageChops
P=Path(__file__).resolve().parents[1]
E=P/'evidence';V=P/'previews'
study=json.loads((E/'PAINTED_KEY_PROOF.json').read_text())
source=E.parent.parent/'girl_torso_pose_v054'/'previews'/'key_shape_study'
font=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',23)
board=Image.new('RGB',(1360,6*840),'#202a2c');d=ImageDraw.Draw(board);records=[]
for i,r in enumerate(study['frames']):
    a=source/f'V053_BASE_F{r["frame"]:03d}.png';b=Path(r['render'])
    assert b.exists() and hashlib.sha256(b.read_bytes()).hexdigest()==r['sha256']
    A=Image.open(a).convert('RGB');B=Image.open(b).convert('RGB')
    crop=(660,150,1000,540);y=i*840
    board.paste(A.crop(crop).resize((680,780),Image.Resampling.LANCZOS),(0,y+43))
    board.paste(B.crop(crop).resize((680,780),Image.Resampling.LANCZOS),(680,y+43))
    d.text((12,y+7),f'v053 ORIGINAL | F{r["frame"]:03d} {r["phase"]}',font=font,fill='#f0eadf')
    d.text((692,y+7),'v055 PAINTED TORSO | same pose + contour',font=font,fill='#f0eadf')
    diff=ImageChops.difference(A.crop(crop),B.crop(crop))
    records.append({'frame':r['frame'],'crop_changed_pixel_count':sum(x>0 for x in diff.convert('L').tobytes())})
cropfile=V/'WTSC_v053_v055_Girl_Painted_Key_Board.jpg';board.save(cropfile,quality=96)
shot=Image.new('RGB',(2560,2*760),'#202a2c');sd=ImageDraw.Draw(shot)
for j,r in enumerate((study['frames'][0],study['frames'][3])):
    a=Image.open(source/f'V053_BASE_F{r["frame"]:03d}.png').convert('RGB');b=Image.open(r['render']).convert('RGB');y=j*760
    shot.paste(a,(0,y+40));shot.paste(b,(1280,y+40))
    sd.text((12,y+6),f'v053 source | F{r["frame"]:03d} {r["phase"]}',font=font,fill='#f0eadf')
    sd.text((1292,y+6),'v055 candidate | actual 1280x720 shot size',font=font,fill='#f0eadf')
shotfile=V/'WTSC_v053_v055_Girl_Actual_Shot_Size.jpg';shot.save(shotfile,quality=96)
(E/'KEY_BOARD_ASSEMBLY.json').write_text(json.dumps({'crop_board':str(cropfile),'crop_sha256':hashlib.sha256(cropfile.read_bytes()).hexdigest(),'shot_board':str(shotfile),'shot_sha256':hashlib.sha256(shotfile.read_bytes()).hexdigest(),'source_crop':[660,150,1000,540],'crop_scale':2,'shot_size_px':[1280,720],'records':records},indent=2))
print('V055_BOARDS',cropfile,shotfile)
