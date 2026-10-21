from pathlib import Path
import json
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1];d=json.loads((P/'evidence/native_structure_and_four_poses.json').read_text());m=d['poses'][3]['meshes']['V007_BOY | drawn leg near'];im=Image.open(P.parents[1]/'characters/Pair_Painterly_Near_Age_v015.png').convert('RGBA');uv={v:m['uv'][0][i] for i,v in enumerate(m['loop_vertices'])};out=Image.new('RGB',(380,1056),'#e8e3d6');dr=ImageDraw.Draw(out);rows=[]
for i in range(33):
 a,b=uv[2*i],uv[2*i+1];cols=[]
 for xx in range(240):
  q=xx/239;u=a[0]*(1-q)+b[0]*q;v=a[1]*(1-q)+b[1]*q;c=im.getpixel((round(u*(im.width-1)),round((1-v)*(im.height-1))));cols.append(c)
  dr.line((100+xx,i*32,100+xx,i*32+31),fill=c[:3])
 dr.text((10,i*32+8),str(i),fill='#222222');rows.append({'row':i,'gray_mean':sum(sum(c[:3])/3 for c in cols)/len(cols)})
out.save(P/'evidence/ORIGINAL_LEG_UV_STRIP_QA.png');(P/'evidence/original_uv_row_values.json').write_text(json.dumps(rows,indent=2));print(rows)

