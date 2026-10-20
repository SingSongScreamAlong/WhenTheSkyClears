from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
O=Path(r'WTSC_LOCAL_WORKSPACE\work\production_review_v059')
paths=sorted(O.glob('integrated_*.png'))
out=Image.new('RGB',(960,310*len(paths)),(18,18,20));d=ImageDraw.Draw(out)
for j,p in enumerate(paths):
 im=Image.open(p).convert('RGB');im.thumbnail((960,280));out.paste(im,(0,j*310+25));d.text((12,j*310+6),p.stem,fill='white')
out.save(O/'integration_keys.jpg',quality=91)
print('BOARD_READY',len(paths))
