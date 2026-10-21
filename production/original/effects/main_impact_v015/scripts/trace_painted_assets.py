"""Analyze original RGBA into editable vectors. Never modify source pixels."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parents[1]
source=P/'assets/Painted_Soil_Rupture_4Stages_v015b.png'
image=Image.open(source);a=np.asarray(image.getchannel('A'));W,H=image.size
def simplify(p,eps=1.2):
    if len(p)<3:return p
    v=np.asarray(p[-1],float)-p[0];q=np.asarray(p,float)-p[0]
    t=np.clip((q@v)/(float(v@v) or 1),0,1)
    dist=np.linalg.norm(q-t[:,None]*v,axis=1);i=int(np.argmax(dist))
    if dist[i]<=eps:return[p[0],p[-1]]
    return simplify(p[:i+1],eps)[:-1]+simplify(p[i:],eps)
def area(p):return abs(sum(x*v-u*y for(x,y),(u,v)in zip(p,p[1:]+p[:1])))/2
def contours(mask,min_area=12):
    # Dilating the VECTOR tracing envelope retains partially transparent bristle
    # edges. The raster itself and its native alpha remain unchanged.
    for _ in range(2):
        p=np.pad(mask,1)
        mask=p[1:-1,1:-1]|p[:-2,1:-1]|p[2:,1:-1]|p[1:-1,:-2]|p[1:-1,2:]
    p=np.pad(mask,1);edges={}
    def add(x,y,u,v):edges.setdefault((int(x),int(y)),[]).append((int(u),int(v)))
    ys,xs=np.where(mask&~p[:-2,1:-1])
    for y,x in zip(ys,xs):add(x,y,x+1,y)
    ys,xs=np.where(mask&~p[1:-1,2:])
    for y,x in zip(ys,xs):add(x+1,y,x+1,y+1)
    ys,xs=np.where(mask&~p[2:,1:-1])
    for y,x in zip(ys,xs):add(x+1,y+1,x,y+1)
    ys,xs=np.where(mask&~p[1:-1,:-2])
    for y,x in zip(ys,xs):add(x,y+1,x,y)
    loops=[]
    while edges:
        start=next(iter(edges));cur=start;loop=[]
        while cur in edges:
            loop.append(cur);nxt=edges[cur].pop()
            if not edges[cur]:del edges[cur]
            cur=nxt
            if cur==start:break
        if len(loop)<8 or area(loop)<min_area:continue
        mid=len(loop)//2
        q=simplify(loop[:mid+1])+simplify(loop[mid:]+[loop[0]])[1:-1]
        loops.append({'contour':q,'pixel_area':area(loop)})
    return sorted(loops,key=lambda v:v['pixel_area'],reverse=True)
stages=[]
for name,left,right,height,age in [('Ignition',0,330,.43,[0,2]),('RisingTear',330,811,1.05,[2,6]),('MainFan',811,1451,1.75,[6,13]),('Collapse',1451,W,1.08,[13,27])]:
    mask=(a>22);mask[:,:left]=False;mask[:,right:]=False
    loops=contours(mask)
    assert loops
    ys,xs=np.where(mask);bbox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
    anchor=[(bbox[0]+bbox[2])/2.,bbox[3]-2]
    scale=height/(anchor[1]-bbox[1])
    stages.append({'name':name,'region_x':[left,right],'bbox':bbox,'anchor':anchor,'height_m':height,'metres_per_pixel':scale,'age_exposure':age,'islands':loops})
scar_mask=(a>22);scar_mask[:,:1451]=False;scar_mask[:639,:]=False
scar=contours(scar_mask,35)
result={'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'size':[W,H],
        'transparent_fraction':float((a==0).mean()),'all_original_RGBA_preserved':True,'stages':stages,
        'scar':{'native_UV_band_only':[1451,639,W,H],'anchor':stages[-1]['anchor'],'metres_per_pixel':stages[-1]['metres_per_pixel'],'islands':scar}}
(P/'assets/painted_contours.json').write_text(json.dumps(result,indent=2))
paths=[]
for stage in stages:
    for island in stage['islands']:
        paths.append('<polygon points="'+' '.join(f'{x},{y}' for x,y in island['contour'])+'" fill="none" stroke="#222" stroke-width="1"/>')
(P/'assets/Painted_Rupture_Editable_Outlines.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">'+''.join(paths)+'</svg>')
print(json.dumps({'stages':[{'name':v['name'],'islands':len(v['islands']),'bbox':v['bbox'],'height_m':v['height_m']}for v in stages],'scar_islands':len(scar)}))
