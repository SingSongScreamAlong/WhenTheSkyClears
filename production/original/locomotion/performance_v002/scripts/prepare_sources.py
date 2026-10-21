import sys,json,math,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parents[1];R=P.parents[1]
sys.path.insert(0,str(R/'scripts'))
from prepare_girl_contours import contours
a=np.array(Image.open(R/'characters/Pair_Painterly_Near_Age_v015.png'))[:,:,3]
scale=1.45/851;data={'scale':scale,'base':907,'hands':{},'feet':{},'source_sha256':hashlib.sha256((R/'characters/Pair_Painterly_Near_Age_v015.png').read_bytes()).hexdigest()}
for who,bbox,wrist in [('BOY',(458,525,521,586),(502,527)),('GIRL',(1123,548,1173,604),(1137,553))]:
    x0,y0,x1,y1=bbox;loops=contours(a[y0:y1,x0:x1]>145)
    loop=max(loops,key=lambda c:abs(sum(p[0]*q[1]-q[0]*p[1] for p,q in zip(c,c[1:]+c[:1]))))
    data['hands'][who]={'outline':[[x+x0,y+y0] for x,y in loop],'wrist':wrist}
def hull(points):
    pts=sorted(set(points))
    def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    low=[]
    for q in pts:
        while len(low)>=2 and cross(low[-2],low[-1],q)<=0:low.pop()
        low.append(q)
    return low
for who,side,bbox,cx,ankle in [('BOY','far',(433,825,588,908),636,(493,836)),('BOY','near',(707,825,869,908),636,(751,845)),('GIRL','far',(864,825,1011,909),1010,(915,843)),('GIRL','near',(1115,825,1257,909),1010,(1147,846))]:
    x0,y0,x1,y1=bbox;ys,xs=np.where(a[y0:y1,x0:x1]>145)
    pts=[((x+x0-cx)*scale,(907-(y+y0+1))*scale) for x,y in zip(xs,ys)]
    lo=hull(pts);edges=[(p,q) for p,q in zip(lo,lo[1:]) if q[0]-p[0]>.04 and abs(math.atan2(q[1]-p[1],q[0]-p[0]))<.5]
    heel,toe=max(edges,key=lambda e:e[1][0]-e[0][0]);theta=math.atan2(toe[1]-heel[1],toe[0]-heel[0])
    an=[(ankle[0]-cx)*scale,(907-ankle[1])*scale]
    data['feet'][who+'_'+side]={'heel':heel,'toe':toe,'flatten_angle':theta,'ankle':an,'lower_hull':lo}
(P/'art/native_overlap_sources.json').write_text(json.dumps(data,indent=2))
print('SOURCE_VECTOR_ANALYSIS_READY',[(k,round(v['flatten_angle'],3)) for k,v in data['feet'].items()])
