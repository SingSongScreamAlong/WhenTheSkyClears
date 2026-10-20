from PIL import Image,ImageDraw
from pathlib import Path
O=Path(r'WTSC_LOCAL_WORKSPACE\work\procedural_cut_v064\previews')
im=Image.open(O/'Native_Opening_4K_v064.png').convert('RGB')
board=Image.new('RGB',(950,820),(22,23,25));d=ImageDraw.Draw(board)
for title,box,xy in [('Boy face and neck | native 4K pixels',(1510,540,1850,960),(0,24)),('Girl face and collar | native 4K pixels',(1920,570,2260,960),(370,24)),('Hands and forearms | native 4K pixels',(1740,900,2220,1220),(0,480))]:
 # Independent review crops only; no change to source artwork.
 crop=im.crop(box);board.paste(crop,xy);d.text((xy[0]+4,xy[1]-18),title,fill=(240,240,240))
board.save(O/'Native_Opening_Review_Details_v064.png')
print('V064_REVIEW_CROPS_READY')
