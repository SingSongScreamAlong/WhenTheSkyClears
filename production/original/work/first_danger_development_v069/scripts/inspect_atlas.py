"""Read-only alpha/registration inspection; does not edit generated pixels."""
from pathlib import Path
from PIL import Image
import numpy as np,json
from collections import deque
O=Path(__file__).resolve().parents[1];P=O/'textures/WTSC_Painted_Head_Angles_v069.png';im=Image.open(P);a=np.array(im);H,W=a.shape[:2];cw=W//6;ch=H//2;rows=[]
for row,w in enumerate(['BOY','GIRL']):
 for col in range(6):
  ystart,yend=(0,346) if row==0 else (347,H)
  aa=a[ystart:yend,col*cw:(col+1)*cw,3];height=aa.shape[0];mask=aa>128;visited=np.zeros(mask.shape,np.uint8);components=[]
  for sy,sx in zip(*np.where(mask)):
   if visited[sy,sx]:continue
   Q=deque([(int(sy),int(sx))]);visited[sy,sx]=1;pixels=[]
   while Q:
    y,x=Q.popleft();pixels.append((y,x))
    for yy,xx in [(y-1,x),(y+1,x),(y,x-1),(y,x+1)]:
     if 0<=yy<height and 0<=xx<cw and mask[yy,xx] and not visited[yy,xx]:visited[yy,xx]=1;Q.append((yy,xx))
   components.append(pixels)
  p=max(components,key=len);ys=[v[0] for v in p];xs=[v[1] for v in p];top,bottom,left,right=min(ys),max(ys)+1,min(xs),max(xs)+1
  low=[x for y,x in p if y>bottom-30];anchorx=float(np.median(low));anchory=bottom-9
  rows.append({'character':w,'column':col,'cell':[col*cw,ystart,cw,height],'bounds_pixels':[col*cw+left,ystart+top,col*cw+right,ystart+bottom],'neck_anchor_pixels':[col*cw+anchorx,ystart+anchory],'paint_pixels':len(p),'components':len(components)})
out={'path':str(P),'size':[W,H],'mode':im.mode,'alpha_extrema':[int(a[:,:,3].min()),int(a[:,:,3].max())],'heads':rows,'note':'Bounding/neck coordinates only. Generated RGBA pixels preserved unchanged; native UV windows select the atlas cells.'}
(O/'evidence/HEAD_REGISTRATION.json').write_text(json.dumps(out,indent=2));print('HEAD_REGISTRATION_READY',[(x['character'],x['column'],x['neck_anchor_pixels']) for x in rows],flush=True)
