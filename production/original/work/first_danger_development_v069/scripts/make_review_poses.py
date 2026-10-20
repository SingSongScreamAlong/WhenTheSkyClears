from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
O=Path(__file__).resolve().parents[1];R=O.parents[1];B=json.loads((O/'evidence/BUILD.json').read_text());tag=Path(B['native']).stem.split('_')[-1];font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',26)
board=Image.new('RGB',(2160,670),'#111820');d=ImageDraw.Draw(board)
for i,(p,label) in enumerate([(R/'work/first_danger_rough_v068/renders/uhd_E/world/0991.png','BEFORE | v068 rough'),(O/f'renders/uhd_{tag}/world/0991.png','AFTER | v069 development')]):
 im=Image.open(p).convert('RGB').crop((840,450,3000,1710)).resize((1080,630),Image.Resampling.LANCZOS);d.text((i*1080+15,7),label,font=font,fill='white');board.paste(im,(i*1080,40))
board.save(O/'previews/Native_Grip_Before_After_v069.jpg',quality=94);print('NATIVE_MATCHED_POSE_READY',flush=True)
