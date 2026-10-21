"""Read source alpha into editable vector contours; never rewrite source PNGs."""
import json
from pathlib import Path
import numpy as np
from PIL import Image

R=Path(__file__).resolve().parents[1]
P=R/'characters/head_turn_v047'

def simplify(points, eps=2.5):
    if len(points)<3:return points
    a=np.array(points[0],float);b=np.array(points[-1],float)
    v=b-a;length=float(v@v)
    p=np.array(points,float)
    t=np.clip(((p-a)@v)/(length or 1),0,1)
    distance=np.linalg.norm(p-a-t[:,None]*v,axis=1)
    i=int(np.argmax(distance))
    if distance[i]<=eps:return [points[0],points[-1]]
    return simplify(points[:i+1],eps)[:-1]+simplify(points[i:],eps)

result={}
for path in P.glob('Girl_*.png'):
    a=np.array(Image.open(path).getchannel('A'))
    mask=a>40
    # Enlarge only the vector tracing envelope. The original RGBA stays intact.
    for _ in range(2):
        b=np.pad(mask,1)
        mask=b[1:-1,1:-1]|b[:-2,1:-1]|b[2:,1:-1]|b[1:-1,:-2]|b[1:-1,2:]
    p=np.pad(mask,1);edges={}
    def edge(start,end):edges.setdefault(start,[]).append(end)
    ys,xs=np.where(mask & ~p[:-2,1:-1])
    for y,x in zip(ys,xs):edge((int(x),int(y)),(int(x+1),int(y)))
    ys,xs=np.where(mask & ~p[1:-1,2:])
    for y,x in zip(ys,xs):edge((int(x+1),int(y)),(int(x+1),int(y+1)))
    ys,xs=np.where(mask & ~p[2:,1:-1])
    for y,x in zip(ys,xs):edge((int(x+1),int(y+1)),(int(x),int(y+1)))
    ys,xs=np.where(mask & ~p[1:-1,:-2])
    for y,x in zip(ys,xs):edge((int(x),int(y+1)),(int(x),int(y)))
    loops=[]
    while edges:
        start=next(iter(edges));point=start;loop=[]
        while point in edges:
            loop.append(point);n=edges[point].pop()
            if not edges[point]:del edges[point]
            point=n
            if point==start:break
        if len(loop)>20:loops.append(loop)
    def area(loop):return abs(sum(x*v-u*y for (x,y),(u,v) in zip(loop,loop[1:]+loop[:1])))
    outer=max(loops,key=area)
    # Split closed contour before RDP so coincident endpoints do not collapse it.
    mid=len(outer)//2
    contour=simplify(outer[:mid+1])+simplify(outer[mid:]+[outer[0]])[1:-1]
    result[path.name]={'size':list(Image.open(path).size),'contour':contour,'vertices':len(contour)}
    print(path.name,len(contour),flush=True)
    pts=' '.join(f'{x},{y}' for x,y in contour)
    (P/(path.stem+'_EditableOutline.svg')).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {a.shape[1]} {a.shape[0]}"><polygon points="{pts}" fill="none" stroke="#202020" stroke-width="2"/></svg>')
(P/'contours.json').write_text(json.dumps(result,indent=2))
