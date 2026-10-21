from PIL import Image
import numpy as np,json
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1]
for name,path,ys,xrange in [('ORIGINAL',ROOT/'characters/Pair_Painterly_Near_Age_v015.png',range(190,291,5),(1000,1110)),('GENERATED',P/'textures/WTSC_Girl_Face_Finish_Study_v050.png',range(450,951,25),(800,1184))]:
 a=np.array(Image.open(path));rows=[]
 for y in ys:
  good=np.flatnonzero(a[y,xrange[0]:xrange[1],3]>.75*255)
  rows.append([y,int(good[-1]+xrange[0]) if len(good) else None])
 print(name,a.shape,rows)
