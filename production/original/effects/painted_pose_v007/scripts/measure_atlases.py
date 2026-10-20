from pathlib import Path
import base64,json,hashlib
from PIL import Image,ImageDraw,ImageFont
import numpy as np
P=Path(__file__).resolve().parents[1]
(P/'assets/Dust_Drawn_Poses_v007.png').write_bytes(base64.b64decode((P/'assets/dust_drawn_original_base64.tmp').read_text()))
out={}
for name,cols,rows in [('Blast_Drawn_Poses_v007.png',3,4),('Dust_Drawn_Poses_v007.png',2,3)]:
    image=Image.open(P/'assets'/name);alpha=np.array(image)[:,:,3];width,height=image.size;cells=[]
    for i in range(cols*rows):
        x0=round((i%cols)*width/cols);x1=round((i%cols+1)*width/cols);y0=round((i//cols)*height/rows);y1=round((i//cols+1)*height/rows)
        sub=alpha[y0:y1,x0:x1];yy,xx=np.where(sub>48)
        cells.append({'index':i,'cell':[x0,y0,x1,y1],'alpha_bounds':[int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())],'baseline_v':float(1-yy.max()/(y1-y0)),'coverage':float((sub>48).mean())})
    out[name]={'pixels':image.size,'grid':[cols,rows],'cells':cells,'sha256':hashlib.sha256((P/'assets'/name).read_bytes()).hexdigest()}
(P/'evidence/atlas_measurements.json').write_text(json.dumps(out,indent=2))
print(json.dumps({name:{'pixels':d['pixels'],'baseline_v':[round(c['baseline_v'],3) for c in d['cells']]} for name,d in out.items()}))
