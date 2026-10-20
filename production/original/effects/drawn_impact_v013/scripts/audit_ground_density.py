from pathlib import Path
from PIL import Image
import numpy as np,json
P=Path(__file__).resolve().parents[1]
a=np.array(Image.open(P.parent/'benchmark_v002/assets/Native_Foreground_Alpha_1080_v002.png').convert('RGBA'))[:,:,3]/255
rows=[]
for x in [1310,1340,1350,1380,1460,1517,1660,1710,1750]:
    means=a[700:820,x-8:x+9].mean(axis=1);out={'x':x}
    for thresh in [.48,.85,.95,.98]:
        hit=next((i for i in range(len(means)-12) if (means[i:i+12]>thresh).all()),None);out[str(thresh)]=700+hit if hit is not None else None
    rows.append(out)
(P/'evidence/ground_density_audit.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows))
