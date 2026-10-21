import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageChops
P=Path(__file__).resolve().parents[1];E=P/'evidence';V=P/'previews';data=json.loads((E/'KEY_SHAPE_STUDY.json').read_text())
font=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',23);sub=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',17)
board=Image.new('RGB',(1360,6*840),'#202a2c');d=ImageDraw.Draw(board);visual=[]
for i,r in enumerate(data['records']):
 a=Path(r['source']);b=Path(r['key_study']);assert hashlib.sha256(a.read_bytes()).hexdigest()==r['source_sha256'] and hashlib.sha256(b.read_bytes()).hexdigest()==r['key_study_sha256']
 left=Image.open(a).convert('RGB');right=Image.open(b).convert('RGB');box=(660,150,1000,540)
 A=left.crop(box).resize((680,780),Image.Resampling.LANCZOS);B=right.crop(box).resize((680,780),Image.Resampling.LANCZOS)
 y=i*840;board.paste(A,(0,y+43));board.paste(B,(680,y+43))
 d.text((12,y+7),f'v053 SOURCE | F{r["frame"]:03d} {r["phase"]}',font=font,fill='#f0eadf')
 d.text((692,y+7),'v054 KEY-SHAPE STUDY | same pose / painting',font=font,fill='#f0eadf')
 diff=ImageChops.difference(left.crop(box),right.crop(box));visual.append({'frame':r['frame'],'phase':r['phase'],'crop_nonzero_pixels':sum(1 for px in diff.convert('L').tobytes() if px>0)})
out=V/'WTSC_v053_v054_Girl_Torso_Key_Shape_Board.jpg';board.save(out,quality=96)
shot=Image.new('RGB',(2560,2*760),'#202a2c');sd=ImageDraw.Draw(shot)
for j,r in enumerate([data['records'][0],data['records'][3]]):
 a=Image.open(r['source']).convert('RGB');b=Image.open(r['key_study']).convert('RGB');y=j*760
 shot.paste(a,(0,y+40));shot.paste(b,(1280,y+40));sd.text((15,y+6),f'v053 original | F{r["frame"]:03d} {r["phase"]}',font=font,fill='#f0eadf');sd.text((1295,y+6),'v054 contour study | actual shot size',font=font,fill='#f0eadf')
shotfile=V/'WTSC_v053_v054_Girl_Torso_Actual_Shot_Size.jpg';shot.save(shotfile,quality=96)
(E/'KEY_BOARD_ASSEMBLY.json').write_text(json.dumps({'board':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'shot_size_board':str(shotfile),'shot_size_sha256':hashlib.sha256(shotfile.read_bytes()).hexdigest(),'original_crop_box_px':[660,150,1000,540],'crop_scaled_by':2,'key_study_only_no_inbetweens':True,'visual_differences':visual},indent=2));print(out,shotfile)
