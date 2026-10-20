from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
P=Path(__file__).resolve().parents[1]
report=json.loads((P/'evidence/render_keys.json').read_text())
sheet=Image.new('RGB',(1920,4*568),(25,25,25));d=ImageDraw.Draw(sheet)
for i,row in enumerate(report['rows']):
    im=Image.open(row['path']);assert im.size==(3840,2160);im.verify()
    im=Image.open(row['path']).convert('RGB')
    col=i%2;rr=i//2
    sheet.paste(im.resize((960,540),Image.Resampling.LANCZOS),(col*960,rr*568+28))
    d.text((col*960+12,rr*568+8),f"ACTUAL NATIVE4K | frame {row['frame']} | v014 REJECTED DIAGNOSTIC",fill='white')
sheet.save(P/'previews/Actual_Native4K_Key_Review_REJECTED_v014.jpg',quality=92)
for fr in (1828,1840,1901):
    im=Image.open(P/f'previews/native4K_keys/{fr}.png')
    im.crop((2360,660,3590,1550)).save(P/f'previews/Native4KPixels_FX_{fr}.png')
print('NATIVE4K_DIAGNOSTIC_SHEET_READY')
