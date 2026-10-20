import json,numpy as np
from PIL import Image
from pathlib import Path
P=Path(__file__).resolve().parents[1];im=Image.open(P.parent/'benchmark_v002/assets/Native_Foreground_Alpha_1080_v002.png').convert('RGBA');a=np.asarray(im)[:,:,3]/255;rows=[]
for x in range(1230,1831,5):
    coverage=a[700:820,x-8:x+9].mean(axis=1);hits=np.where(coverage>.48)[0];y=int(700+hits[0]) if len(hits) else 747;rows.append([x,y+2])
(P/'evidence/visible_terrain_profile.json').write_text(json.dumps({'source':'Actual original held-shot foreground alpha; first dense grass/terrain edge in a17pixel window, contact seated2pixels into occlusion.','pixels':[1920,1080],'profile':rows},indent=2));print(json.dumps({'samples':rows[::12],'min_contact_y':min(y for x,y in rows),'max_contact_y':max(y for x,y in rows)}))
