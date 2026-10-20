"""Read imagegen alpha contours as vector geometry; never modify source pixels."""
import json
import math
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]

def simplify(points, epsilon=0.75):
    if len(points) < 3:
        return points
    a, b = np.array(points[0]), np.array(points[-1])
    v = b - a
    q = np.asarray(points) - a
    distance = np.abs(v[0]*q[:,1]-v[1]*q[:,0]) / max(np.linalg.norm(v), 1e-8)
    index = int(np.argmax(distance))
    if distance[index] > epsilon:
        return simplify(points[:index+1],epsilon)[:-1] + simplify(points[index:],epsilon)
    return [points[0],points[-1]]

def contours(mask):
    edges = {}
    ys, xs = np.nonzero(mask)
    h,w = mask.shape
    for x,y in zip(xs.tolist(),ys.tolist()):
        if y==0 or not mask[y-1,x]: edges.setdefault((x,y),[]).append((x+1,y))
        if x==w-1 or not mask[y,x+1]: edges.setdefault((x+1,y),[]).append((x+1,y+1))
        if y==h-1 or not mask[y+1,x]: edges.setdefault((x+1,y+1),[]).append((x,y+1))
        if x==0 or not mask[y,x-1]: edges.setdefault((x,y+1),[]).append((x,y))
    loops=[]
    while edges:
        start = next(iter(edges)); p=start; loop=[start]
        for _ in range(len(xs)*4+1):
            if p not in edges: break
            n=edges[p].pop()
            if not edges[p]: del edges[p]
            p=n; loop.append(p)
            if p==start: break
        if len(loop)>20:
            area=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(loop,loop[1:]))/2
            if area>30: # clockwise exterior in image coordinates
                split=len(loop)//2
                loops.append(simplify(loop[:split+1])[:-1]+simplify(loop[split:])[:-1])
    return sorted(loops,key=lambda a:len(a),reverse=True)

def main():
    image = np.asarray(Image.open(ROOT/'characters/Girl_Parts_Imagegen_v001.png').convert('RGBA'))
    regions = {
      'head':(0,0,362,360),'dress':(362,0,724,360),'braid':(724,0,1086,360),
      'upper_arm_near':(0,360,362,610),'forearm_near':(362,360,724,610),
      'upper_arm_far':(724,360,1086,610),'forearm_far':(1086,360,1448,610),
      'thigh_near':(0,610,362,825),'shin_near':(362,610,724,825),
      'shoe_near':(724,610,1086,825),'thigh_far':(1086,610,1448,825),
      'shin_far':(0,825,362,1086),'shoe_far':(362,825,724,1086),
    }
    parts={}
    for name,(x0,y0,x1,y1) in regions.items():
        crop=image[y0:y1,x0:x1]
        loops=contours(crop[:,:,3]>100)
        assert loops, name
        main_loop=max(loops,key=lambda a:abs(sum(p[0]*q[1]-q[0]*p[1] for p,q in zip(a,a[1:]+a[:1]))))
        coords=np.asarray(main_loop)
        low=coords.min(axis=0); high=coords.max(axis=0)
        parts[name]={'bounds': [int(low[0]),int(low[1]),int(high[0]),int(high[1])],
                     'source_region':[x0,y0,x1,y1], 'outline':main_loop}
        if name=='braid':
            blue=(crop[:,:,2].astype(float)>crop[:,:,0]*1.25)&(crop[:,:,1]>35)&(crop[:,:,3]>100)
            parts[name]['ribbon_contours']=contours(blue)
    out={'source':'Girl_Parts_Imagegen_v001.png','source_size':[image.shape[1],image.shape[0]],
         'status':'provisional_unapproved','parts':parts}
    target=ROOT/'characters/Girl_Parts_Contours_v001.json'
    target.write_text(json.dumps(out,indent=2),encoding='utf-8')
    print(json.dumps({name:len(data['outline']) for name,data in parts.items()}))
    return out

if __name__=='__main__': main()
