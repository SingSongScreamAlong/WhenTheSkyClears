"""Read new imagegen alpha as vector contours; never edit source pixels."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from prepare_girl_contours import contours, simplify

root = Path(__file__).resolve().parents[1]
path = root / "characters/Pair_Painterly_Near_Age_v015.png"
image = np.asarray(Image.open(path).convert("RGBA"))
loops = contours(image[:, :, 3] > 145)
main = max(loops, key=lambda a: abs(sum(p[0]*q[1]-q[0]*p[1] for p,q in zip(a,a[1:]+a[:1]))))
xy = np.asarray(main)
low, high = xy.min(axis=0), xy.max(axis=0)
scale = 1.45 / (high[1] - low[1])
center = (low[0] + high[0]) / 2
points = [[float((x-center)*scale), -.36, float((high[1]-y)*scale)] for x,y in main]
uv = [[float(x/image.shape[1]), float(1-y/image.shape[0])] for x,y in main]
start = next(i for i,p in enumerate(points) if p[2] > .20)
groups, run = [], []
for p in points[start:] + points[:start]:
    if p[2] < .20:
        run.append(p)
    elif run:
        groups.append(run)
        run = []
soles = []
for group in groups:
    if len(group) < 3:
        continue
    min_z = min(v[2] for v in group)
    low_points = [v for v in group if v[2] < min_z+.017]
    if max(v[0] for v in group)-min(v[0] for v in group) > .07:
        soles.append({"x": float(np.mean([v[0] for v in low_points])), "z": min_z,
                      "width": min(.24, max(.13, max(v[0] for v in low_points)-min(v[0] for v in low_points)+.07))})
assert len(soles) == 4, soles
mask = image[:, :, 3] > 145
split = int((low[0]+high[0])/2)
boy_y = np.where(mask[:, :split])[0].min()
girl_y = np.where(mask[:, split:])[0].min()
result = {"source": str(path), "source_size": [image.shape[1],image.shape[0]],
          "bounds_pixels": [int(low[0]),int(low[1]),int(high[0]),int(high[1])],
          "points": points, "uv": uv, "soles": soles,
          "height_m": 1.45, "boy_height_m": float((high[1]-boy_y)*scale),
          "girl_height_m": float((high[1]-girl_y)*scale),
          "style": "Near-black painted grayscale, tiny nonglowing off-white eye marks",
          "motion": "Held pose only, as user explicitly requested",
          "status": "User-directed proportion/style revision; original approved ink-and-wash image missing"}
(root / "characters/Pair_Painterly_Near_Age_Vector_v015.json").write_text(json.dumps(result,indent=2))
print(json.dumps({k:v for k,v in result.items() if k not in ["points","uv"]}))
