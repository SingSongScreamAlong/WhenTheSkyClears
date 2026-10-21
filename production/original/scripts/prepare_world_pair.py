import json,sys
import numpy as np
from PIL import Image
from pathlib import Path
from prepare_girl_contours import contours,simplify
from create_native_drawings import call
ROOT=Path(__file__).resolve().parents[1]
im=np.asarray(Image.open(ROOT/'characters/Pair_Static_Imagegen_v001.png').convert('RGBA'))
mask=im[:,:,3]>145
loops=contours(mask)
main=max(loops,key=lambda a:abs(sum(p[0]*q[1]-q[0]*p[1] for p,q in zip(a,a[1:]+a[:1]))))
split=len(main)//2
main=simplify(main[:split+1],1.3)[:-1]+simplify(main[split:]+main[:1],1.3)[:-1]
xy=np.asarray(main);low=xy.min(axis=0);high=xy.max(axis=0)
scale=1.4/(high[1]-low[1]);center=(low[0]+high[0])/2
def coords(loop):return [[round((x-center)*scale,6),-.36,round((high[1]-y)*scale,6)] for x,y in loop]
blue=(im[:,:,2].astype(float)>im[:,:,0]*1.4)&(im[:,:,1]>35)&mask
color=[.008,.01,.014,1]
strokes=[{'points':coords(main),'material_name':'Pair_Charcoal','color':color,'fill_color':color,'cyclic':True,'show_stroke':False,'radius':.001}]
for c in contours(blue):
    strokes.append({'points':coords(c),'material_name':'Pair_Ribbon_Blue','color':[.06,.15,.23,1],'fill_color':[.06,.15,.23,1],'cyclic':True,'show_stroke':False,'radius':.001})
if '--reuse-empty' not in sys.argv:
    call('blender_grease_pencil__create_object',{'name':'GP_Pair_STATIC_world_scale'})
call('blender_grease_pencil__add_drawing',{'object_name':'GP_Pair_STATIC_world_scale','layer_name':'Held silhouette | no limb animation','frame':1,'strokes':strokes,'use_lights':False})
(ROOT/'characters/Pair_Static_Vector_Contours_v001.json').write_text(json.dumps({'points':coords(main),'source':'Pair_Static_Imagegen_v001.png','motion':'translation only; no pose animation'},indent=2))
print('Static pair native GP vector outline',len(main),'points,',len(strokes),'strokes')
