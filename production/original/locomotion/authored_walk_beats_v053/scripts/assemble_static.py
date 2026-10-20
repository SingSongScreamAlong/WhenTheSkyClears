import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parents[1];E=P/'evidence';V=P/'previews';data=json.loads((E/'STATIC_RENDER.json').read_text())
lookup={(r['version'],r['frame']):r for r in data['records']}
def load(tag,f):
 r=lookup[(tag,f)];path=Path(r['file']);assert hashlib.sha256(path.read_bytes()).hexdigest()==r['sha256'];return Image.open(path).convert('RGB')
font=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',19);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',13)
frames=[1,5,9,13,17,21,25,29,33];sheet=Image.new('RGB',(1920,2460),'#202a2c');d=ImageDraw.Draw(sheet)
for j,f in enumerate(frames):
 x=(j%3)*640;y=(j//3)*820;left=load('V051',f).resize((640,360),Image.Resampling.LANCZOS);right=load('V053',f).resize((640,360),Image.Resampling.LANCZOS)
 # Each cell shows the same actual pose at matching full-shot scale.
 pair=Image.new('RGB',(640,820),'#202a2c');pair.paste(left,(0,28));pair.paste(right,(0,418));pd=ImageDraw.Draw(pair);pd.text((10,3),f'F{f:02d} | v051 frozen body timing',font=font,fill='#f0eadf');pd.text((10,390),'v053 authored contact / loading / passing / push-off',font=small,fill='#f0eadf')
 sheet.paste(pair,(x,y))
out=V/'WTSC_v051_v053_Matched_Pose_Beats.jpg';sheet.save(out,quality=93)
print(out)
