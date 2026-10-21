import hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parents[1]
source=P.parent/'girl_torso_pose_v054'/'previews'/'key_shape_study'
records=json.loads((P/'evidence'/'YOKE_KEY_PROOF.json').read_text())['frames']
font=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',23)
board=Image.new('RGB',(1360,6*840),'#202a2c');d=ImageDraw.Draw(board)
for i,r in enumerate(records):
    a=Image.open(source/f'V053_BASE_F{r["frame"]:03d}.png').convert('RGB')
    b=Image.open(r['path']).convert('RGB');crop=(660,150,1000,540);y=i*840
    board.paste(a.crop(crop).resize((680,780),Image.Resampling.LANCZOS),(0,y+43))
    board.paste(b.crop(crop).resize((680,780),Image.Resampling.LANCZOS),(680,y+43))
    d.text((12,y+7),f'v053 ORIGINAL | F{r["frame"]:03d} {r["phase"]}',font=font,fill='#f0eadf')
    d.text((692,y+7),'v056 ORIGINAL-PAINT YOKE | actual Blender key',font=font,fill='#f0eadf')
cropfile=P/'previews'/'WTSC_v053_v056_Girl_Yoke_Key_Board.jpg';board.save(cropfile,quality=96)
shot=Image.new('RGB',(2560,2*760),'#202a2c');sd=ImageDraw.Draw(shot)
for j,r in enumerate((records[0],records[3])):
    a=Image.open(source/f'V053_BASE_F{r["frame"]:03d}.png').convert('RGB');b=Image.open(r['path']).convert('RGB');y=j*760
    shot.paste(a,(0,y+40));shot.paste(b,(1280,y+40))
    sd.text((12,y+6),f'v053 source | F{r["frame"]:03d} {r["phase"]}',font=font,fill='#f0eadf')
    sd.text((1292,y+6),'v056 yoke study | actual 1280x720 shot size',font=font,fill='#f0eadf')
shotfile=P/'previews'/'WTSC_v053_v056_Girl_Yoke_Actual_Shot_Size.jpg';shot.save(shotfile,quality=96)
(P/'evidence'/'KEY_BOARD_ASSEMBLY.json').write_text(json.dumps({'crop':str(cropfile),'crop_sha256':hashlib.sha256(cropfile.read_bytes()).hexdigest(),'shot':str(shotfile),'shot_sha256':hashlib.sha256(shotfile.read_bytes()).hexdigest()},indent=2))
print(cropfile,shotfile)
