"""Trace the owned painting's surviving glass into registered native geometry.
No image synthesis/upscale is presented as new detail; this recovers boundaries.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,json,math,hashlib
O=Path(r'WTSC_LOCAL_USER\Documents\Codex\2026-10-16\task\world_architecture_v049');src=Path(r'WTSC_LOCAL_WORKSPACE\sets\painted_layers\School_v001.png');box=(879,431,986,636);scale=4
im=Image.open(src).convert('RGB').crop(box).resize(((box[2]-box[0])*scale,(box[3]-box[1])*scale),Image.Resampling.BICUBIC);a=np.asarray(im)/255.;lum=a@np.array([.2126,.7152,.0722]);mask=(lum>.18)&((a[:,:,2]-a[:,:,0]>.015)|(lum>.42))
support=Image.new('L',im.size);d=ImageDraw.Draw(support);arc=[(936.5+41.5*math.cos(math.pi-i*math.pi/32),449-13*math.sin(math.pi-i*math.pi/32)) for i in range(33)]+[(978,631),(895,631)];d.polygon([((x-box[0])*scale,(y-box[1])*scale) for x,y in arc],fill=255)
mask&=np.asarray(support)>0
for x0,x1,y0,y1 in [(933,940,431,636),(879,986,482,491),(879,986,548,554),(879,986,594,600)]:mask[max(0,(y0-box[1])*scale):max(0,(y1-box[1])*scale),max(0,(x0-box[0])*scale):max(0,(x1-box[0])*scale)]=False
mask=np.asarray(Image.fromarray((mask*255).astype('uint8')).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3)))>0
H,W=mask.shape;seen=np.zeros_like(mask);components=[]
for y,x in zip(*np.where(mask)):
 if seen[y,x]:continue
 seen[y,x]=True;todo=[(int(x),int(y))];comp=[]
 while todo:
  xx,yy=todo.pop();comp.append((xx,yy))
  for nx,ny in [(xx-1,yy),(xx+1,yy),(xx,yy-1),(xx,yy+1)]:
   if 0<=nx<W and 0<=ny<H and mask[ny,nx] and not seen[ny,nx]:seen[ny,nx]=True;todo.append((nx,ny))
 if len(comp)>=64:components.append(comp)
def rdp(pts,eps):
 if len(pts)<3:return pts
 a=np.array(pts[0],dtype=float);b=np.array(pts[-1],dtype=float);v=b-a;den=float(v@v);dist=[]
 for p in pts[1:-1]:
  q=np.array(p,dtype=float);t=0 if den==0 else max(0,min(1,float((q-a)@v)/den));dist.append(float(np.linalg.norm(q-(a+t*v))))
 if not dist or max(dist)<=eps:return [pts[0],pts[-1]]
 k=dist.index(max(dist))+1;return rdp(pts[:k+1],eps)[:-1]+rdp(pts[k:],eps)
polys=[]
for comp in components:
 pixels=set(comp);edges={}
 for x,y in comp:
  for neighbor,start,end in [((x,y-1),(x,y),(x+1,y)),((x+1,y),(x+1,y),(x+1,y+1)),((x,y+1),(x+1,y+1),(x,y+1)),((x-1,y),(x,y+1),(x,y))]:
   if neighbor not in pixels:edges.setdefault(start,[]).append(end)
 loops=[]
 while edges:
  start=next(iter(edges));p=start;loop=[p]
  for _ in range(20000):
   if p not in edges:break
   q=edges[p].pop()
   if not edges[p]:del edges[p]
   p=q;loop.append(p)
   if p==start:break
  if len(loop)>3 and loop[-1]==start:loops.append(loop)
 if not loops:continue
 area=lambda pp:abs(sum(p[0]*q[1]-q[0]*p[1] for p,q in zip(pp,pp[1:]+pp[:1])))
 loop=max(loops,key=area);simple=rdp(loop[:-1],1.1);poly=[(x/scale+box[0],y/scale+box[1]) for x,y in simple]
 if len(poly)>=3:polys.append(poly)
qa=im.copy();d=ImageDraw.Draw(qa)
for p in polys:d.line([((x-box[0])*scale,(y-box[1])*scale) for x,y in p]+[((p[0][0]-box[0])*scale,(p[0][1]-box[1])*scale)],fill=(255,150,80),width=1)
qa.save(O/'original_glass_contours_QA.png');(O/'original_glass_geometry.json').write_text(json.dumps({'source':str(src),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'polygons':polys,'method':'Owned source-paint glass boundaries,4x sampling only for subpixel contour fit, no newly invented texture detail.','polygon_count':len(polys)},indent=2));print('SOURCE_GLASS_POLYGONS',len(polys),[len(p) for p in polys])
