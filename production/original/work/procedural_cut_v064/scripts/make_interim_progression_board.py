"""Actual native probe montage only. No source painting or native scene edits."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, hashlib
O=Path(r'WTSC_LOCAL_WORKSPACE\work\procedural_cut_v064')
P=O/'previews'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def font(n):
    return ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf',n)
items=[('0001.png','0 s | full painted color'),('1201.png','50 s | shared transition'),('2305.png','96 s | both in charcoal')]
board=Image.new('RGB',(1440,781),(18,20,24));draw=ImageDraw.Draw(board)
draw.text((16,12),'Native cut color progression | actual trailer times | held original poses',font=font(24),fill=(240,241,237))
rows=[]
for i,(name,label) in enumerate(items):
    path=P/'driver_probe_frames'/name
    with Image.open(path) as raw:
        image=raw.convert('RGB')
    assert image.size==(1280,720)
    x=i*480
    draw.text((x+14,58),label,font=font(22),fill=(221,224,218))
    board.paste(image.resize((480,270),Image.Resampling.LANCZOS),(x,88))
    draw.text((x+58,366),'Character crop | same native frame',font=font(18),fill=(195,201,199))
    board.paste(image.crop((460,175,825,540)),(x+58,391))
    rows.append({'file':str(path),'sha256':sha(path),'frame':int(path.stem),'trailer_seconds':(int(path.stem)-1)/24,'dimensions':[1280,720]})
draw.text((16,758),'Interim native review. Original poses are held; the full 106-second movie is still rendering.',font=font(16),fill=(190,196,194))
target=P/'Native_Cut_Color_Progression_Interim_v064.jpg'
assert not target.exists(),str(target)
board.save(target,quality=95,subsampling=0)
report={'board':str(target),'sha256':sha(target),'native_sha256':'caac0a93ddf8f7ae03f5ca7b002a9c1ca14e0d2242d5861165471e88f3af4d35','sources':rows,'character_crop':[460,175,825,540],'montage_only':True,'source_art_edits':False,'limits':'Three native stills at actual trailer times; original held poses. Full movie is rendering. This is not a motion review.'}
(O/'evidence/INTERIM_COLOR_BOARD_v064.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
